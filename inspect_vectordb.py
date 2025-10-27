import chromadb
import pprint
from app.config import VECTOR_DB_PATH

# Configuration
DB_PATH = VECTOR_DB_PATH
# By default, LangChain creates a collection named "langchain"
COLLECTION_NAME = "langchain"

def inspect_database():
    """
    Connects to the persistent ChromaDB and retrieves a sample of its contents.
    """
    print(f"--- Connecting to vector database at: {DB_PATH} ---")
    
    try:
        # 1. Create a persistent client pointing to the DB directory
        client = chromadb.PersistentClient(path=DB_PATH)
        
        # 2. Get the collection
        print(f"--- Accessing collection: {COLLECTION_NAME} ---")
        collection = client.get_collection(name=COLLECTION_NAME)
        
        # 3. Get the total count of items
        count = collection.count()
        print(f"Database contains {count} document chunks.")
        
        if count == 0:
            print("Database is empty. Run 'python run_ingestion.py' to add documents.")
            return

        # 4. Retrieve a sample of the items (e.g., the first 5)
        print("\n--- Retrieving a sample of 5 items: ---")
        sample = collection.get(
            limit=5,
            include=["metadatas", "documents"]  # We want to see the text and its source
        )
        
        # 5. Pretty-print the results
        pprint.pprint(sample)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("This often happens if the collection doesn't exist or the database is empty.")
        print("Please run 'python run_ingestion.py' first to create and populate the database.")

if __name__ == "__main__":
    inspect_database()
    
