import os
import glob
from langchain_community.document_loaders import (
    JSONLoader,
    CSVLoader,
    TextLoader,
    PyPDFLoader  # Import the PDF loader
)
from app.services.vector_db import vector_db_service

# Define the supported document types and their corresponding loaders
LOADER_MAPPING = {
    ".json": (JSONLoader, {"jq_schema": '.', "text_content": False}),
    ".csv": (CSVLoader, {}),
    ".md": (TextLoader, {}),
    ".txt": (TextLoader, {}),
    ".asn": (TextLoader, {}),  # Treat .asn files as plain text
    ".pdf": (PyPDFLoader, {}), # Add PDF loader
}

def load_documents_from_directory(directory_path: str):
    """
    Loads all supported documents from the specified directory,
    recursively searching subfolders.
    """
    all_docs = []
    print(f"Scanning for documents in {directory_path}...")
    
    for ext, (Loader, kwargs) in LOADER_MAPPING.items():
        # Find all files with the current extension, searching recursively
        file_paths = glob.glob(os.path.join(directory_path, f"**/*{ext}"), recursive=True)
        
        for file_path in file_paths:
            try:
                print(f"Loading {file_path}...")
                # Special handling for PDF to load page by page
                if ext == ".pdf":
                    loader = Loader(file_path, **kwargs)
                    pages = loader.load_and_split()
                    all_docs.extend(pages)
                else:
                    loader = Loader(file_path, **kwargs)
                    all_docs.extend(loader.load())
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
    
    print(f"Loaded a total of {len(all_docs)} documents.")
    return all_docs

def ingest_data(directory_path: str):
    """
    Main ingestion function called by run_ingestion.py.
    Loads all documents and passes them to the vector DB service for processing.
    """
    # 1. Load documents from the 'document_store'
    documents = load_documents_from_directory(directory_path)
    
    if not documents:
        print("No documents found to ingest. Please add files to the 'document_store' directory.")
        return

    # 2. Pass the loaded documents to the vector DB service
    #    The service will handle chunking, embedding, and storing.
    print("Processing documents and ingesting into vector database...")
    vector_db_service.ingest_documents(documents)
    
    print("Document ingestion and processing complete.")

