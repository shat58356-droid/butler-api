from flask import Flask, request, jsonify
import time, uuid

app = Flask(__name__)

jobs = {}
approvals = []
@app.route("/chat/message", methods=["POST"])
def chat_message():
    """
    Simple 'chat' endpoint for UI:
    - takes a natural language message
    - creates a mock GENERATE_VIDEO job
    - returns job_id and suggested next actions
    """
    body = request.json or {}
    message = (body.get("message") or "").strip()
    project_id = body.get("project_id", "proj_001")
    platform = body.get("platform", "youtube")
    duration_sec = int(body.get("duration_sec", 8))

    if not message:
        return jsonify({"ok": False, "error": "MESSAGE_REQUIRED"}), 400

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    jobs[job_id] = {
        "job_id": job_id,
        "status": "QUEUED",
        "created_at": time.time(),
        "type": "GENERATE_VIDEO",
        "project_id": project_id,
        "payload": {
            "prompt": message,
            "platform": platform,
            "duration_sec": duration_sec
        }
    }

    return jsonify({
        "ok": True,
        "reply": "✅ Job created. Check status, then send result to approvals.",
        "job": {
            "job_id": job_id,
            "status": "QUEUED",
            "platform": platform,
            "duration_sec": duration_sec
        },
        "next": [
            {"action": "CHECK_JOB", "method": "GET", "url": f"/jobs/{job_id}"},
            {"action": "CREATE_APPROVAL", "method": "POST", "url": "/approvals/create"}
        ]
    })
@app.route("/health")
def health():
    return {"ok": True, "name": "Butler API"}

@app.route("/tasks/create", methods=["POST"])
def create_task():
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    jobs[job_id] = {
        "job_id": job_id,
        "status": "QUEUED",
        "created_at": time.time()
    }
    return jsonify({"ok": True, "job_id": job_id})

@app.route("/jobs/<job_id>")
def job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return {"error": "not found"}, 404

    age = time.time() - job["created_at"]
    if age > 15:
        job["status"] = "DONE"
        job["result"] = {
            "asset_id": f"as_{uuid.uuid4().hex[:6]}",
            "preview_url": "https://picsum.photos/300/600"
        }
    return job

@app.route("/approvals/queue")
def approvals_queue():
    return {"items": approvals}

@app.route("/approvals/create", methods=["POST"])
def approvals_create():
    body = request.json or {}
    approvals.insert(0, {
        "approval_id": f"ap_{uuid.uuid4().hex[:8]}",
        "status": "PENDING",
        "asset_id": body.get("asset_id"),
    })
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
