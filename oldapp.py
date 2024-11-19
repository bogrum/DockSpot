from flask import Flask, request, jsonify, render_template
import os
from threading import Thread, Lock
from data_analysis.step1_xtc_handling import xtc_to_pdb, write_pdb_list, run_p2rank
#from data_analysis.step2_pocketscsv import step2_pockets_csv
from data_analysis.config import pdb_dir, processed_dir, p2rank_processed_dir
from datetime import datetime

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Thread-safe job storage
jobs = {}
job_lock = Lock()

# Set upload folder for Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def process_job(job_id, file_path):
    """
    Run the job's steps sequentially, updating progress and results.
    """
    try:
        jobs[job_id]['status'] = 'in-progress'
        jobs[job_id]['job_start_time'] = datetime.now().isoformat()

        # Step 1: Process XTC and Generate PDBs
        jobs[job_id]['progress'] = 10
        pdb_files = xtc_to_pdb(file_path, pdb_dir)
        pdb_list_file = write_pdb_list(pdb_dir, f"{processed_dir}/pdb_list.ds")
        run_p2rank(pdb_list_file, p2rank_processed_dir)
        jobs[job_id]['step1_result'] = {"pdb_files": pdb_files}

        # Step 2: Generate pockets.csv
        jobs[job_id]['progress'] = 50
        #csv_file = step2_pockets_csv(p2rank_processed_dir)
        #jobs[job_id]['step2_result'] = {"csv_file": csv_file}

        # Finalize
        jobs[job_id]['progress'] = 100
        jobs[job_id]['status'] = "completed"
        jobs[job_id]['job_end_time'] = datetime.now().isoformat()

    except Exception as e:
        jobs[job_id]['status'] = "failed"
        jobs[job_id]['error'] = str(e)


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/submit-job', methods=['POST'])
def submit_job():
    """
    Handle job submissions with file uploads.
    """
    if 'xtc_file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    xtc_file = request.files['xtc_file']
    if xtc_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], xtc_file.filename)
    xtc_file.save(file_path)

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
    thread = Thread(target=process_job, args=(job_id, file_path))
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
