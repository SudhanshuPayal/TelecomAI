from app.database import db
from datetime import datetime

class ValidationTask(db.Model):
    """
    Represents a validation task in the database.
    This model stores the state and result of an asynchronous validation process,
    aligning with the workflow diagram.
    """
    __tablename__ = 'validation_tasks'

    # Primary key for the task record
    id = db.Column(db.Integer, primary_key=True)

    # The unique run_id provided by the CDCS/CAST system
    run_id = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # The ID of the associated Celery task for status tracking
    celery_task_id = db.Column(db.String(255), nullable=True, index=True)

    # The current status of the validation task (e.g., PENDING, PROCESSING, SUCCESS, FAILURE)
    status = db.Column(db.String(50), nullable=False, default='PENDING')

    # The final validation report, likely stored as a JSON string
    result = db.Column(db.Text, nullable=True)

    # Timestamps for tracking
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<ValidationTask {self.run_id} [{self.status}]>'

