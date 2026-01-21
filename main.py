from flask import Flask, request, jsonify
import time, uuid

app = Flask(__name__)

jobs = {}
approvals = []

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
