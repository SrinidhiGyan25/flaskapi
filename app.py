from flask import Flask, request, send_file, abort, jsonify
import os
import traceback
from gen_map2 import generate_html_report

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h2>Job Scraper API</h2>
    <p>Use <code>/jobs?role=Data Scientist</code> to get job report</p>
    <p>Status: <a href="/health">Health Check</a></p>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test if Chrome is available
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        
        return jsonify({
            "status": "healthy",
            "chrome": "available",
            "selenium": "working"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/jobs')
def jobs():
    job_title = request.args.get("role")
    if not job_title:
        return jsonify({"error": "Missing 'role' query parameter"}), 400

    safe_title = job_title.replace(" ", "_")
    output_file = f"{safe_title}_report.html"

    try:
        if not os.path.exists(output_file):
            result = generate_html_report(job_title=job_title, pages=2, create_heatmap=True)
            if not result:
                return jsonify({"error": "Failed to scrape jobs"}), 500

        if os.path.exists(output_file):
            return send_file(output_file)
        else:
            return jsonify({"error": f"Report not generated for '{job_title}'"}), 500

    except Exception as e:
        return jsonify({
            "error": f"Error generating job report: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)