"""
Production-ready Flask Web Application for Google Form & Sheet Automation.
Allows selecting fixed fields once and rapidly submitting multiple timings.
Supports local execution, Docker, Render, Railway, Vercel, and Cloud deployments.
"""

import os
import time
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, send_file
from form_config import get_options, sync_live_options, VIEW_URL
from form_submitter import (
    submit_entry,
    normalize_duration,
    calculate_duration_from_timestamps,
    get_submission_history,
    LOG_FILE
)

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    options = get_options()
    return render_template("index.html", options=options, form_url=VIEW_URL)

@app.route("/health", methods=["GET"])
@app.route("/ping", methods=["GET"])
def health_check():
    """Healthcheck endpoint for cloud providers and monitors."""
    return jsonify({
        "status": "healthy",
        "service": "production-task-entry-automation",
        "timestamp": time.time()
    }), 200

@app.route("/api/config", methods=["GET"])
def api_config():
    options = get_options()
    return jsonify({
        "status": "success",
        "options": options,
        "form_url": VIEW_URL
    })

@app.route("/api/sync", methods=["POST"])
def api_sync():
    options = sync_live_options()
    return jsonify({
        "status": "success",
        "message": "Options synchronized from Google Form",
        "options": options
    })

@app.route("/api/submit", methods=["POST"])
def api_submit():
    data = request.get_json() or {}
    
    date = data.get("date", "").strip()
    shift = data.get("shift", "").strip()
    camera = data.get("camera", "").strip()
    location = data.get("location", "").strip()
    recorder = data.get("recorder", "").strip()
    scene = data.get("scene", "").strip()
    task = data.get("task", "").strip()
    duration = data.get("duration", "").strip()

    if not all([shift, camera, location, recorder, scene, task, duration]):
        return jsonify({
            "success": False,
            "message": "Missing required fields. Please ensure fixed fields and duration are provided."
        }), 400

    result = submit_entry(
        date=date,
        shift=shift,
        camera=camera,
        location=location,
        recorder=recorder,
        scene=scene,
        task=task,
        duration=duration
    )
    return jsonify(result)

@app.route("/api/submit-batch", methods=["POST"])
def api_submit_batch():
    data = request.get_json() or {}
    
    date = data.get("date", "").strip()
    shift = data.get("shift", "").strip()
    camera = data.get("camera", "").strip()
    location = data.get("location", "").strip()
    recorder = data.get("recorder", "").strip()
    scene = data.get("scene", "").strip()
    task = data.get("task", "").strip()
    durations = data.get("durations", [])

    if not all([shift, camera, location, recorder, scene, task]) or not durations:
        return jsonify({
            "success": False,
            "message": "Missing fixed fields or no durations provided."
        }), 400

    results = []
    success_count = 0
    fail_count = 0

    for dur in durations:
        dur = str(dur).strip()
        if not dur:
            continue
        res = submit_entry(
            date=date,
            shift=shift,
            camera=camera,
            location=location,
            recorder=recorder,
            scene=scene,
            task=task,
            duration=dur
        )
        if res.get("success"):
            success_count += 1
        else:
            fail_count += 1
        results.append(res)
        time.sleep(0.35)  # Safe throttle between submissions

    return jsonify({
        "success": fail_count == 0,
        "total": len(results),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results
    })

@app.route("/api/calculate-duration", methods=["POST"])
def api_calculate():
    data = request.get_json() or {}
    start = data.get("start", "")
    end = data.get("end", "")
    try:
        dur = calculate_duration_from_timestamps(start, end)
        return jsonify({"success": True, "duration": dur})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/history", methods=["GET"])
def api_history():
    history = get_submission_history(limit=100)
    return jsonify({"history": history})

@app.route("/api/download-log", methods=["GET"])
def api_download_log():
    if os.path.exists(LOG_FILE):
        return send_file(LOG_FILE, as_attachment=True, download_name="production_entries_log.csv")
    return jsonify({"error": "No log file found"}), 404

def start_server():
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    is_cloud = "PORT" in os.environ or os.environ.get("NO_BROWSER", "").lower() in ("1", "true")

    if not is_cloud:
        def _open():
            time.sleep(1.2)
            webbrowser.open(f"http://127.0.0.1:{port}")
        threading.Thread(target=_open, daemon=True).start()

    print(f"\n=======================================================")
    print(f"🚀 Production Task Automation Server Active!")
    print(f"👉 Local Access:   http://127.0.0.1:{port}")
    print(f"👉 Network Access: http://{host}:{port}")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    start_server()
