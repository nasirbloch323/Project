from flask import Flask, request, jsonify

app = Flask(__name__)

# Temporary in-memory task storage
# Data server restart hone par reset ho jayega.
tasks = []

# New task ke liye unique ID
next_id = 1


# Home route
# Browser mein / open karne par static/index.html show hoga.
@app.route("/")
def home():
    return app.send_static_file("index.html")


# Health check
# API running hai ya nahi check karne ke liye.
@app.route("/health")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "todo-api"
    })


# GET /tasks
# Saare tasks return karta hai.
@app.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify(tasks)


# POST /tasks
# New task create karta hai.
@app.route("/tasks", methods=["POST"])
def add_task():
    global next_id

    # Request se JSON data lena
    data = request.get_json(silent=True) or {}

    # JSON se title lena
    title = data.get("title")

    # Title validation
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({
            "error": "title is required and must be a non-empty string"
        }), 400

    # New task create karna
    task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }

    # Task ko list mein add karna
    tasks.append(task)

    # Next task ke liye ID increase karna
    next_id += 1

    # Created task return karna
    return jsonify(task), 201


# PATCH /tasks/<id>
# Existing task ka title ya done status update karta hai.
@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}

    task = next(
        (t for t in tasks if t["id"] == task_id),
        None
    )

    if task is None:
        return jsonify({
            "error": f"task with id {task_id} not found"
        }), 404

    if "title" in data:
        title = data["title"]

        if not isinstance(title, str) or not title.strip():
            return jsonify({
                "error": "title must be a non-empty string"
            }), 400

        task["title"] = title.strip()

    if "done" in data:
        task["done"] = bool(data["done"])

    return jsonify(task), 200


# PATCH /tasks/<id>/done
# Existing task ko completed mark karta hai.
@app.route("/tasks/<int:task_id>/done", methods=["PATCH"])
def mark_done(task_id):

    # Task ID search karna
    task = next(
        (t for t in tasks if t["id"] == task_id),
        None
    )

    # Task nahi mila
    if task is None:
        return jsonify({
            "error": f"task with id {task_id} not found"
        }), 404

    # Task complete karna
    task["done"] = True

    return jsonify(task)


# DELETE /tasks/<id>
# Task ko list se permanently remove karta hai.
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks

    task = next(
        (t for t in tasks if t["id"] == task_id),
        None
    )

    if task is None:
        return jsonify({
            "error": f"task with id {task_id} not found"
        }), 404

    tasks = [t for t in tasks if t["id"] != task_id]

    return jsonify({"deleted": task_id}), 200


# Application start
if __name__ == "__main__":
    import os

    # Environment PORT available ho to use karega,
    # warna 3000 default port hai.
    port = int(os.environ.get("PORT", 3000))

    # 0.0.0.0 Docker/container ke bahar se access allow karta hai.
    app.run(
        host="0.0.0.0",
        port=port
    )
