from flask import request, jsonify
from app.api import api_bp
from app.database import db
from app.tasks.task_validation import ValidationTask
from app.celery_worker.celery_worker import process_validation_task

@api_bp.route('/validate', methods=['POST'])
def start_validation():
    """
    Endpoint to start a new validation task.
    Receives a 'run_id' and enqueues a background task for processing.
    """
    data = request.get_json()
    if not data or 'run_id' not in data:
        return jsonify({"error": "Missing 'run_id' in request body"}), 400

    run_id = data['run_id']

    # Check if a task with this run_id already exists
    existing_task = ValidationTask.query.filter_by(run_id=run_id).first()
    if existing_task:
        return jsonify({"error": f"Task with run_id '{run_id}' already exists."}), 409

    # 1. Create a new task record in the database (Step 2 in diagram)
    new_task = ValidationTask(run_id=run_id, status='PENDING')
    db.session.add(new_task)
    db.session.commit()
    print(f"Created new task record for run_id: {run_id} with DB ID: {new_task.id}")

    # 2. Enqueue the task for asynchronous processing (Step 3 in diagram)
    task_result = process_validation_task.delay(new_task.id)
    
    # 3. Store the Celery task ID for future reference
    new_task.celery_task_id = task_result.id
    db.session.commit()
    print(f"Enqueued Celery task {task_result.id} for DB ID: {new_task.id}")

    # 4. Respond to the client immediately
    return jsonify({
        "message": "Validation task has been successfully queued.",
        "task_id": new_task.id,
        "run_id": new_task.run_id,
        "status_endpoint": f"/api/tasks/{new_task.id}"
    }), 202

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Endpoint to check the status and result of a validation task.
    """
    task = ValidationTask.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    response = {
        "task_id": task.id,
        "run_id": task.run_id,
        "status": task.status,
        "created_at": task.created_at.isoformat() + "Z",
        "result": task.result
    }
    
    if task.completed_at:
        response["completed_at"] = task.completed_at.isoformat() + "Z"

    return jsonify(response)

