from dotenv import load_dotenv
import os
import sys

# Load environment variables from a .env file at the project root
# This is crucial so that model_loader can authenticate with Hugging Face.
load_dotenv()

# We must add the project root to the Python path so we can import 'app'
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now that the path is set and .env is loaded, we can import our modules
from app.tasks.ingestion import ingest_data

# Define the path to the 'Document Store'
DOCUMENT_STORE_PATH = os.path.join(project_root, 'document_store')

def main():
    """
    Main function to run the manual ingestion process.
    """
    print("Starting MANUAL knowledge base ingestion...")
    print("WARNING: This will delete the existing vector database and rebuild it.")
    
    try:
        # Call the ingestion logic directly
        print(f"--- Loading and ingesting all documents from: {DOCUMENT_STORE_PATH} ---")
        ingest_data(DOCUMENT_STORE_PATH)
        print("--- Knowledge base ingestion complete. ---")
        
    except Exception as e:
        print(f"\nAn error occurred during ingestion: {e}")
        print("Please check your file permissions, .env file, and document contents.")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure the document_store directory exists
    if not os.path.exists(DOCUMENT_STORE_PATH):
        os.makedirs(DOCUMENT_STORE_PATH)
        print(f"Created 'document_store' directory at: {DOCUMENT_STORE_PATH}")
        print("Please add your ATIS standards, JSON schemas, and scenario CSVs to this directory.")
        print("Re-run this script once files are in place.")
        sys.exit(0)
    
    # Run the main ingestion function
    main()

