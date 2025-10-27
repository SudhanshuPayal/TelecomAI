import time
from datetime import datetime
from celery import Celery
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Create a standalone Celery instance. It does not know about Flask yet.
celery = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery.task(bind=True)
def process_validation_task(self, db_task_id):
    """
    The main asynchronous task. The Flask app context will be injected
    by the app factory when the application starts.
    """
    # Imports that require the app context are placed inside the task function.
    from app.database import db
    from app.tasks.task_validation import ValidationTask

    print(f"Starting AI processing for task ID: {db_task_id}")
    
    task = ValidationTask.query.get(db_task_id)
    if not task:
        print(f"Error: Task with ID {db_task_id} not found.")
        return

    try:
        task.status = 'PROCESSING'
        task.celery_task_id = self.request.id
        db.session.commit()
        print(f"Task {task.run_id} status updated to PROCESSING.")

        # Simulate the long-running AI processing steps
        print(f"Simulating AI analysis for task {task.run_id}...")
        time.sleep(15)
        print("AI analysis simulation complete.")
        
        mock_report = {
            "run_id": task.run_id,
            "validation_summary": "All checks passed.",
            "discrepancies_found": 0,
            "confidence_score": 0.98
        }
        
        task.status = 'SUCCESS'
        task.result = str(mock_report)
        task.completed_at = datetime.utcnow()
        db.session.commit()
        print(f"Task {task.run_id} completed successfully.")

    except Exception as e:
        print(f"Error processing task {task.run_id}: {e}")
        db.session.rollback()
        task.status = 'FAILURE'
        task.result = f"An error occurred: {str(e)}"
        task.completed_at = datetime.utcnow()
        db.session.commit()

