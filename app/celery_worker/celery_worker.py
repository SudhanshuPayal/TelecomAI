from datetime import datetime
from . import celery 

# Import the app factory *inside* the task function to avoid circular imports.
# We have moved the import from the top of the file to here.
# from .. import create_app  <-- REMOVED FROM HERE

@celery.task(bind=True)
def process_validation_task(self, db_task_id: int, run_id: str, cii_data: dict):
    """
    The main asynchronous task.
    It now pre-processes the cii_data to extract metadata and the
    list of received packet names.
    """
    
    # Manually create and push an app context to avoid RuntimeError
    from .. import create_app
    app = create_app()
    with app.app_context():
        
        # Imports that require the app context are placed inside
        from ..services.llm_service import llm_service
        from ..database import db
        from ..tasks.task_validation import ValidationTask

        print(f"Starting AI processing for task ID: {db_task_id} (run_id: {run_id})")
        
        task = ValidationTask.query.get(db_task_id)
        if not task:
            print(f"Error: Task with ID {db_task_id} not found.")
            return

        try:
            # 1. Update status to PROCESSING
            task.status = 'PROCESSING'
            task.celery_task_id = self.request.id
            db.session.commit()
            print(f"Task {run_id} status updated to PROCESSING.")

            # 2. --- UPDATED PRE-PROCESSING LOGIC ---
            metadata = {
                "templateId": cii_data.get("templateId"),
                "templateName": cii_data.get("templateName"),
                "carrier": cii_data.get("carrier")
            }
            
            received_packets = []
            if "messages" in cii_data and isinstance(cii_data["messages"], list):
                for message_obj in cii_data["messages"]:
                    if isinstance(message_obj, dict):
                        message_name = next(iter(message_obj), None)
                        if message_name:
                            # --- THIS IS THE FIX ---
                            # Strip the prefix to get the canonical name
                            canonical_name = message_name.replace("ims-3gpp-VoIP-", "")
                            received_packets.append(canonical_name)
                            # --- END OF FIX ---
            
            print(f"Extracted {len(received_packets)} normalized packet names.")
            # --- END OF PRE-PROCESSING ---

            # 3. Call the LLM service to perform the validation
            print(f"Generating validation report for run_id: {run_id}")
            validation_report = llm_service.generate_validation_report(
                run_id=run_id,
                rag_metadata=metadata,
                received_packets=received_packets
            )
            print("LLM validation complete.")
            
            # 4. Update status to SUCCESS and store the result
            task.status = 'SUCCESS'
            task.result = validation_report 
            task.completed_at = datetime.utcnow()
            db.session.commit()
            print(f"Task {run_id} completed successfully.")

        except Exception as e:
            # If an error occurs, update status to FAILURE
            print(f"Error processing task {run_id}: {e}")
            db.session.rollback()
            db.session.remove()
            task = ValidationTask.query.get(db_task_id)
            task.status = 'FAILURE'
            task.result = f"An error occurred: {str(e)}"
            task.completed_at = datetime.utcnow()
            db.session.commit()

