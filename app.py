from flask import Flask, request, send_file, abort
import os
from gen_map2 import generate_html_report

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h2>Job Scraper API</h2>
    <p>Use <code>/jobs?role=Data Scientist</code> to get job report</p>
    """

@app.route('/jobs')
def jobs():
    job_title = request.args.get("role")
    if not job_title:
        return "❌ Missing 'role' query parameter", 400

    # Normalize job_title for filename usage
    safe_title = job_title.replace(" ", "_")
    output_file = f"{safe_title}_report.html"

    try:
        # Only scrape & generate if the file doesn't already exist
        if not os.path.exists(output_file):
            generate_html_report(job_title=job_title, pages=2, create_heatmap=True)

        if os.path.exists(output_file):
            return send_file(output_file)
        else:
            return f"⚠️ Failed to generate report for '{job_title}'", 500

    except Exception as e:
        return f"❌ Error generating job report: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
