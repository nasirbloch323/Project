from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage. This list lives in RAM only - it resets to empty
# every time the server restarts. No database is used, on purpose.
tasks = []
next_id = 1


@app.route('/', methods=['GET'])
def health_check():
    """Simple health check so we can confirm the server/container is alive."""
    return jsonify({"status": "ok", "service": "todo-api"})


@app.route('/tasks', methods=['GET'])
def list_tasks():
    """Return every task currently stored."""
    return jsonify(tasks)


@app.route('/tasks', methods=['POST'])
def add_task():
    """
    Add a new task.
    Expects JSON body like: { "title": "Buy milk" }
    """
    global next_id

    data = request.get_json(silent=True) or {}
    title = data.get('title')

    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required and must be a non-empty string"}), 400

    task = {
        "id": next_id,
        "title": title.strip(),
        "done": False,
    }
    tasks.append(task)
    next_id += 1

    return jsonify(task), 201


@app.route('/tasks/<int:task_id>/done', methods=['PATCH'])
def mark_done(task_id):
    """Mark a single task as done, by id."""
    task = next((t for t in tasks if t["id"] == task_id), None)

    if task is None:
        return jsonify({"error": f"task with id {task_id} not found"}), 404

    task["done"] = True
    return jsonify(task)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
