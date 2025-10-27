from app import create_app
from dotenv import load_dotenv
from app.tasks.ingestion import ingest_data
from app.services.vector_db import vector_db_service
import os
import sys

# Define the path to the 'Document Store'
DOCUMENT_STORE_PATH = os.path.join(os.path.dirname(__file__), 'document_store')

def main():
    """
    Main function to initialize the app and run the ingestion process.
    This script is for MANUAL re-ingestion of the knowledge base.
    It will DELETE the old database and create a new one.
    """
    print("Starting MANUAL knowledge base ingestion...")
    print("WARNING: This will delete the existing vector database and rebuild it.")
    
    # Load environment variables
    load_dotenv()
    
    # Create a Flask app instance to establish an application context
    app = create_app()
    
    # Run the ingestion logic within the app's context
    with app.app_context():
        if not os.path.exists(DOCUMENT_STORE_PATH) or not os.listdir(DOCUMENT_STORE_PATH):
            print(f"Error: 'document_store' at '{DOCUMENT_STORE_PATH}' is empty or missing.")
            print("Please add documents before running manual ingestion.")
            sys.exit(1)
            
        # 1. CLEAR THE EXISTING DATABASE
        # This calls the recreate_db() method from the vector_db_service
        vector_db_service.recreate_db()

        # 2. INGEST NEW DOCUMENTS
        print(f"--- Loading and ingesting all documents from: {DOCUMENT_STORE_PATH} ---")
        ingest_data(DOCUMENT_STORE_PATH)
    
    print("Manual knowledge base ingestion complete. Vector database has been rebuilt.")

if __name__ == "__main__":
    # This script is intended to be run directly and manually
    main()

