from flask import Flask, request, jsonify, render_template
import time
from threading import Thread

app = Flask(__name__)

# Store jobs and their progress and result
jobs = {}

def process_job(job_id, input_string):
    """Simulate job progress and count letters in the input string."""
    letter_count = sum(1 for char in input_string if char.isalpha())  # Count letters only
    for i in range(10):  # Simulate work by sleeping
        time.sleep(1)
        jobs[job_id]['progress'] = (i + 1) * 10  # Update job progress (10%, 20%, ..., 100%)
    jobs[job_id]['letter_count'] = letter_count  # Store the result

@app.route('/')
def index():
    """Serve the HTML page."""
    return render_template('index.html')

@app.route('/submit-job', methods=['POST'])
def submit_job():
    """Receive a job submission."""
    data = request.get_json()
    input_string = data.get('input_string', '')
    
    job_id = str(len(jobs) + 1)  # Generate a new job ID
    jobs[job_id] = {'progress': 0, 'letter_count': None}  # Initial progress is 0%

    # Start job in background using a thread
    thread = Thread(target=process_job, args=(job_id, input_string))
    thread.start()

    return jsonify({"job_id": job_id}), 202  # Return job ID

@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Return the progress of the job."""
    if job_id in jobs:
        return jsonify({"job_id": job_id, "progress": jobs[job_id]['progress'], "letter_count": jobs[job_id]['letter_count']})
    else:
        return jsonify({"error": "Job not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
