from flask import Flask, request, jsonify, render_template
import time
from threading import Thread
from data_analysis.step1_xtc_handling import step1_xtc_handling
from data_analysis.step2_pocketscsv import step2_pockets_csv

app = Flask(__name__)

# Store jobs and their progress and results
jobs = {}

def process_job(job_id, input_data):
    """
    Simulate job progress and run scripts sequentially.
    """
    try:
        # Step 1
        jobs[job_id]['progress'] = 10
        step1_output = step1_xtc_handling(input_data)  # Call Step 1 function
        jobs[job_id]['step1_result'] = step1_output
        time.sleep(1)  # Simulate delay

        # Step 2
        jobs[job_id]['progress'] = 50
        step2_output = step2_pockets_csv(step1_output)  # Use Step 1's output as input for Step 2
        jobs[job_id]['step2_result'] = step2_output
        time.sleep(1)  # Simulate delay

        # Finalize
        jobs[job_id]['progress'] = 100
        jobs[job_id]['status'] = "completed"
    except Exception as e:
        jobs[job_id]['status'] = "failed"
        jobs[job_id]['error'] = str(e)

@app.route('/')
def index():
    """Serve the HTML page."""
    return render_template('index.html')

@app.route('/submit-job', methods=['POST'])
def submit_job():
    """Receive a job submission."""
    data = request.get_json()
    input_data = data.get('input_data', {})  # Replace with actual expected input format

    job_id = str(len(jobs) + 1)  # Generate a new job ID
    jobs[job_id] = {'progress': 0, 'status': 'in-progress', 'step1_result': None, 'step2_result': None}  # Initial state

    # Start job in background using a thread
    thread = Thread(target=process_job, args=(job_id, input_data))
    thread.start()

    return jsonify({"job_id": job_id}), 202  # Return job ID

@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Return the progress of the job."""
    if job_id in jobs:
        return jsonify(jobs[job_id])
    else:
        return jsonify({"error": "Job not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
