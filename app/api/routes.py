from flask import request, jsonify
from app.api import api_bp
from app.database import db
from app.tasks.task_validation import ValidationTask
from app.celery_worker.celery_worker import process_validation_task 

@api_bp.route('/validate', methods=['POST'])
def start_validation():
    """
    Endpoint to start a new validation task.
    Receives a single JSON object (like the '1955709_response_runvalue.json' file)
    as the entire request body.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON request body"}), 400
    
    # --- Updated to use fields from your new JSON structure ---
    
    # Get the run_id from *inside* the JSON
    if 'runId' not in data:
        return jsonify({"error": "Missing 'runId' in request body"}), 400
    run_id = data['runId']

    # Check for other necessary fields
    if 'templateId' not in data:
        return jsonify({"error": "Missing 'templateId' in request body"}), 400
    if 'messages' not in data:
        return jsonify({"error": "Missing 'messages' in request body"}), 400
    if 'carrier' not in data:
        # We can make this an optional field, but it's good to check
        print("Warning: 'carrier' field not present in request body.")
        data['carrier'] = 'Unknown' # Assign a default if missing
    # --- End of new field checks ---

    # Check if a task with this run_id already exists
    existing_task = ValidationTask.query.filter_by(run_id=run_id).first()
    if existing_task:
        # We can either error, or return the existing task
        # For now, we'll return the existing task ID
        return jsonify({
            "message": "Task with this run_id already exists.",
            "task_id": existing_task.id,
            "run_id": existing_task.run_id,
            "status_endpoint": f"/api/tasks/{existing_task.id}"
        }), 409

    # 1. Create a new task record in the database
    new_task = ValidationTask(run_id=run_id, status='PENDING')
    db.session.add(new_task)
    db.session.commit()
    print(f"Created new task record for run_id: {run_id} with DB ID: {new_task.id}")

    # 2. Enqueue the task, passing the ENTIRE JSON object as the cii_data
    task_result = process_validation_task.delay(
        db_task_id=new_task.id,
        run_id=run_id,
        cii_data=data  # Pass the entire JSON body to the worker
    )
    
    # 3. Store the Celery task ID
    new_task.celery_task_id = task_result.id
    db.session.commit()
    print(f"Enqueued Celery task {task_result.id} for DB ID: {new_task.id}")

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
        "result": task.result # This will be null until the task is complete
    }
    
    if task.completed_at:
        response["completed_at"] = task.completed_at.isoformat() + "Z"

    return jsonify(response)
