import os
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List
from app.models import model_loader
from app.config import VECTOR_DB_PATH

class VectorDBService:
    """
    Service for managing interactions with the Chroma vector database.
    This service uses "lazy loading" for the database connection
    to prevent file locks during ingestion.
    """
    def __init__(self):
        print("Initializing VectorDB Service...")
        self.embedding_model = model_loader.embedding_model
        
        # --- THIS IS THE FIX ---
        # Do NOT initialize the DB connection here.
        # It will be loaded on demand.
        self.db = None
        # --- END OF FIX ---

    def _get_db_connection(self):
        """
        Lazily gets or creates the database connection.
        This ensures we only connect when we're ready.
        """
        if self.db is None:
            print("Creating new ChromaDB persistent connection...")
            # Ensure the directory exists before trying to connect
            if not os.path.exists(VECTOR_DB_PATH):
                os.makedirs(VECTOR_DB_PATH)
                
            self.db = Chroma(
                persist_directory=VECTOR_DB_PATH,
                embedding_function=self.embedding_model
            )
            print("ChromaDB connection established.")
        return self.db

    def recreate_db(self):
        """
        Deletes the entire vector database directory and re-initializes
        an empty one. This is used for a full, clean re-ingestion.
        """
        print(f"--- Clearing existing vector database at: {VECTOR_DB_PATH} ---")
        
        # 1. Explicitly set self.db to None to "close" our handle
        self.db = None 
        
        # 2. Clear the directory
        if os.path.exists(VECTOR_DB_PATH):
            try:
                shutil.rmtree(VECTOR_DB_PATH)
                print("Database cleared successfully.")
            except Exception as e:
                print(f"Error clearing database: {e}. Please check file permissions.")
                return
        else:
            print("No existing database to clear.")
        
        # 3. Re-create the directory
        os.makedirs(VECTOR_DB_PATH, exist_ok=True) 
        
        # 4. Get a fresh connection, which will create the new files
        self.db = self._get_db_connection()
        print("--- Empty vector database re-initialized ---")

    def ingest_documents(self, documents: List[Document]):
        """
        Chunks, embeds, and stores a list of documents in the vector database.
        """
        # Get the database connection
        db = self._get_db_connection()
        
        print(f"Received {len(documents)} documents for ingestion.")
        if not documents:
            print("No documents to ingest.")
            return

        # 1. Split Documents into Chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunked_docs = text_splitter.split_documents(documents)
        print(f"Split documents into {len(chunked_docs)} chunks.")

        # 2. Add documents to the Chroma database
        print(f"Adding {len(chunked_docs)} chunks to the vector database...")
        db.add_documents(chunked_docs)
        print("Ingestion complete. Vector database is updated.")

    def get_retriever(self, k_results=3):
        """
        Returns a retriever object for querying the vector database.
        """
        # Get the database connection
        db = self._get_db_connection()
        return db.as_retriever(search_kwargs={"k": k_results})

# Create a single, globally accessible instance of the service
vector_db_service = VectorDBService()

