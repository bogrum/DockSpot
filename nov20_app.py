from flask import Flask, request, jsonify, render_template
import os
from threading import Thread, Lock
from data_analysis.step1_xtc_handling import xtc_to_pdb, write_pdb_list, run_p2rank
#from data_analysis.step2_pocketscsv import step2_pockets_csv
from data_analysis.config import pdb_dir, processed_dir, p2rank_processed_dir
from datetime import datetime
import logging

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Thread-safe job storage
jobs = {}
job_lock = Lock()

# Set upload folder for Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

def process_job(job_id, xtc_path, topology_path):
    try:
        logging.info(f"Starting job {job_id} with xtc: {xtc_path} and topology: {topology_path}")
        jobs[job_id]['status'] = 'in-progress'
        jobs[job_id]['job_start_time'] = datetime.now().isoformat()

        # Step 1: Process XTC and Generate PDBs
        jobs[job_id]['progress'] = 10
        logging.debug("Calling xtc_to_pdb...")
        jobs[job_id]['status'] = 'generating xtc files into pdb files...'
        pdb_files = xtc_to_pdb(xtc_path, topology_path, pdb_dir)
        logging.debug(f"Generated PDB files: {pdb_files}")

        jobs[job_id]['progress'] = 20
        jobs[job_id]['status'] = 'merging pdb files...'
        pdb_list_file = write_pdb_list(pdb_dir, f"{processed_dir}/pdb_list.ds")
        
        logging.debug(f"Written PDB list file: {pdb_list_file}")

        jobs[job_id]['progress'] = 30
        jobs[job_id]['status'] = 'detecting binding pockets...'
        run_p2rank(pdb_list_file, p2rank_processed_dir)
        logging.info(f"p2rank processed directory: {p2rank_processed_dir}")
        jobs[job_id]['step1_result'] = {"pdb_files": pdb_files}

        # Step 2: Generate pockets.csv
        jobs[job_id]['progress'] = 40
        logging.debug("Skipping step 2 (uncomment if needed)")

        # Finalize
        jobs[job_id]['progress'] = 100
        jobs[job_id]['status'] = "completed"
        jobs[job_id]['job_end_time'] = datetime.now().isoformat()
        logging.info(f"Job {job_id} completed successfully")

    except Exception as e:
        jobs[job_id]['status'] = "failed"
        jobs[job_id]['error'] = str(e)
        logging.error(f"Job {job_id} failed with error: {e}")




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

    # Save the uploaded files
    xtc_path = os.path.join(app.config['UPLOAD_FOLDER'], xtc_file.filename)
    topology_path = os.path.join(app.config['UPLOAD_FOLDER'], topology_file.filename)
    xtc_file.save(xtc_path)
    topology_file.save(topology_path)

    # Create a new job
    with job_lock:
        job_id = str(len(jobs) + 1)
        jobs[job_id] = {
            'progress': 0,
            'status': 'pending',
            'step1_result': None,
            'step2_result': None,
            'job_start_time': None,
            'job_end_time': None,
        }

    # Start processing in the background
    thread = Thread(target=process_job, args=(job_id, xtc_path, topology_path))
    thread.start()

    return jsonify({"job_id": job_id}), 202  # Return job ID for tracking



@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    """
    Check the status and progress of a specific job.
    """
    with job_lock:
        if job_id in jobs:
            return jsonify(jobs[job_id])
        else:
            return jsonify({"error": "Job not found"}), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Global error handler for unexpected issues."""
    return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
