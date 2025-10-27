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
    Handles ingestion, retrieval, and re-creation.
    """
    def __init__(self):
        print("Initializing VectorDB Service...")
        
        # --- THIS IS THE FIX ---
        # Changed from: model_loader.get_embedding_model()
        # To:           model_loader.embedding_model
        self.embedding_model = model_loader.embedding_model
        # --- END OF FIX ---

        # Ensure the DB directory exists
        if not os.path.exists(VECTOR_DB_PATH):
            os.makedirs(VECTOR_DB_PATH)
            
        # Load the persistent vector store
        self.db = Chroma(
            persist_directory=VECTOR_DB_PATH,
            embedding_function=self.embedding_model
        )
        print("Vector database loaded and retriever is ready.")

    def recreate_db(self):
        """
        Deletes the entire vector database directory and re-initializes
        an empty one. This is used for a full, clean re-ingestion.
        """
        print(f"--- Clearing existing vector database at: {VECTOR_DB_PATH} ---")
        if os.path.exists(VECTOR_DB_PATH):
            try:
                shutil.rmtree(VECTOR_DB_PATH)
                print("Database cleared successfully.")
            except Exception as e:
                print(f"Error clearing database: {e}")
                return
        else:
            print("No existing database to clear.")

        # Re-initialize the database
        print("Re-initializing empty vector database...")
        # We must re-create the directory after deleting it
        os.makedirs(VECTOR_DB_PATH, exist_ok=True) 
        self.db = Chroma(
            persist_directory=VECTOR_DB_PATH,
            embedding_function=self.embedding_model
        )
        print("--- Empty vector database re-initialized ---")

    def ingest_documents(self, documents: List[Document]):
        """
        Chunks, embeds, and stores a list of documents in the vector database.
        """
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
        self.db.add_documents(chunked_docs)
        print("Ingestion complete. Vector database is updated.")

    def get_retriever(self, k_results=3):
        """
        Returns a retriever object for querying the vector database.
        """
        return self.db.as_retriever(search_kwargs={"k": k_results})

# Create a single, globally accessible instance of the service
vector_db_service = VectorDBService()

