from flask import Flask, request, jsonify, render_template
import os
from threading import Thread, Lock
from data_analysis.step1_xtc_handling import xtc_to_pdb, write_pdb_list, run_p2rank
from data_analysis.step2_pocketscsv import merge_to_csv
from data_analysis.config import pdb_dir, processed_dir, p2rank_processed_dir
from datetime import datetime
import logging
import sqlite3
import uuid

app = Flask(__name__)

# Directory for uploaded files and job-specific folders
BASE_UPLOAD_FOLDER = 'jobs'
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

# Thread-safe job storage
jobs = {}
job_lock = Lock()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

# SQLite database setup
DB_FILE = 'jobs.db'


def init_db():
    """
    Initialize the SQLite database for storing job metadata.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT,
                progress INTEGER,
                step1_result TEXT,
                step2_result TEXT,
                job_start_time TEXT,
                job_end_time TEXT,
                error TEXT
            )
        ''')
        conn.commit()


def save_job_to_db(job_id, job_data):
    """
    Save job data to the SQLite database.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO jobs (job_id, status, progress, step1_result, step2_result, job_start_time, job_end_time, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            job_data['status'],
            job_data['progress'],
            str(job_data['step1_result']),
            str(job_data['step2_result']),
            job_data['job_start_time'],
            job_data['job_end_time'],
            job_data.get('error')
        ))
        conn.commit()


def process_job(job_id, xtc_path, topology_path, job_folder):
    try:
        logging.info(f"Starting job {job_id} with xtc: {xtc_path} and topology: {topology_path}")
        jobs[job_id]['status'] = 'in-progress'
        jobs[job_id]['job_start_time'] = datetime.now().isoformat()

        # Create a subfolder for the xtc_to_pdb outputs under the job folder
        xtc_to_pdb_folder = os.path.join(job_folder, 'xtc_to_pdb_outputs')
        os.makedirs(xtc_to_pdb_folder, exist_ok=True)

        # Step 1: Process XTC and Generate PDBs
        jobs[job_id]['progress'] = 10
        jobs[job_id]['status'] = 'generating xtc files into pdb files...'
        pdb_files = xtc_to_pdb(xtc_path, topology_path, xtc_to_pdb_folder)  # Save outputs in the job-specific folder
        logging.debug(f"Generated PDB files: {pdb_files}")

        jobs[job_id]['progress'] = 20
        jobs[job_id]['status'] = 'merging pdb files...'
        pdb_list_file = write_pdb_list(xtc_to_pdb_folder, os.path.join(xtc_to_pdb_folder, "pdb_list.ds"))  # Save the list in the same folder
        logging.debug(f"Written PDB list file: {pdb_list_file}")

        jobs[job_id]['progress'] = 30
        jobs[job_id]['status'] = 'detecting binding pockets...'
        run_p2rank(pdb_list_file, xtc_to_pdb_folder)  # Save the p2rank output within the job folder
        logging.info(f"p2rank processed in the job folder: {xtc_to_pdb_folder}")
        jobs[job_id]['step1_result'] = {"Step is completed, now proceeding to step 2..."}


        # Step 2: Analyze pockets.csv
        jobs[job_id]['progress'] = 40
        jobs[job_id]['status'] = 'filtering pockets...'
        pockets_csv = merge_to_csv(xtc_to_pdb_folder,pdb_list_file)
        logging.debug(f"Pockets data saved to {pockets_csv}")


        jobs[job_id]['step2_result'] = {"Step is completed, now proceeding to step 3..."}

        # Step 3: Clustering and choosing representatives...
        jobs[job_id]['progress'] = 50
        jobs[job_id]['status'] = 'analyzing pockets...'
        #pockets_csv = merge_to_csv(xtc_to_pdb_folder,pdb_list_file)
        #logging.debug(f"Pockets data saved to {pockets_csv}")


        # Finalize
        jobs[job_id]['progress'] = 100
        jobs[job_id]['status'] = "completed"
        jobs[job_id]['job_end_time'] = datetime.now().isoformat()
        logging.info(f"Job {job_id} completed successfully")

    except Exception as e:
        jobs[job_id]['status'] = "failed"
        jobs[job_id]['error'] = str(e)
        logging.error(f"Job {job_id} failed with error: {e}")
    
    finally:
        save_job_to_db(job_id, jobs[job_id])




@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/submit-job', methods=['POST'])
def submit_job():
    """
    Handle job submissions with file uploads.
    """
    # Check if both XTC and topology files are present in the request
    if 'xtc_file' not in request.files or 'topology_file' not in request.files:
        return jsonify({"error": "Both xtc_file and topology_file are required"}), 400

    xtc_file = request.files['xtc_file']
    topology_file = request.files['topology_file']

    # Validate the files
    if xtc_file.filename == '' or topology_file.filename == '':
        return jsonify({"error": "Both files must be selected"}), 400

    # Generate a random job ID
    job_id = str(uuid.uuid4())

    # Create a folder for the job
    job_folder = os.path.join(BASE_UPLOAD_FOLDER, job_id)
    os.makedirs(job_folder, exist_ok=True)

    # Save the uploaded files to the job folder
    xtc_path = os.path.join(job_folder, xtc_file.filename)
    topology_path = os.path.join(job_folder, topology_file.filename)
    xtc_file.save(xtc_path)
    topology_file.save(topology_path)

    # Create a new job
    with job_lock:
        jobs[job_id] = {
            'progress': 0,
            'status': 'pending',
            'step1_result': None,
            'step2_result': None,
            'job_start_time': None,
            'job_end_time': None,
        }
        save_job_to_db(job_id, jobs[job_id])

    # Start processing in the background
    thread = Thread(target=process_job, args=(job_id, xtc_path, topology_path, job_folder))
    thread.start()

    return jsonify({"job_id": job_id}), 202  # Return job ID for tracking


@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    """
    Check the status and progress of a specific job.
    """
    with job_lock:
        if job_id in jobs:
            # Ensure all values are serializable
            job_data = jobs[job_id]
            # Convert sets to lists
            for key, value in job_data.items():
                if isinstance(value, set):
                    job_data[key] = list(value)

            return jsonify(job_data)
        else:
            return jsonify({"error": "Job not found"}), 404



@app.errorhandler(500)
def internal_server_error(e):
    """Global error handler for unexpected issues."""
    return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
