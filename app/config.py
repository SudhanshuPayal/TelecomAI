import os
from dotenv import load_dotenv

load_dotenv()

HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

# --- Model Configuration ---
# Embedding Model: Used to convert text chunks into vectors.
# We use a top-performing open-source model from Hugging Face's MTEB leaderboard.
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"

# Generative LLM: The model that will answer questions based on retrieved context.
# We're using Llama 3 8B Instruct, a powerful and efficient instruction-following model.
# NOTE: You must request access to this model on Hugging Face and log in via `huggingface-cli login`.
LLM_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

# --- Vector Database Configuration ---
# The path where the persistent ChromaDB will be stored.
VECTOR_DB_PATH = "./vector_db"

# --- Data Source Configuration ---
# The directory containing the source documents to be ingested.
DATA_PATH = "./data"

STATIC_INTERCEPT_FILES_PATH = "./intercept_files"

# --- PostgreSQL Database Configuration ---
# These settings connect to your relational database.
# Make sure to set these variables in your .env file.
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ai_telecom")
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
print(f"Database URI: {SQLALCHEMY_DATABASE_URI}")

# --- Celery and Redis Configuration ---
# These settings connect to your message broker for asynchronous tasks.
# Make sure the Redis server is running.
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
print(f"Celery Broker URL: {CELERY_BROKER_URL}")