AI Telecom Validation Engine

This project is an AI-powered validation engine for telecom CII (Call-Identifying Information) messages, as described in the project architecture. It uses a Flask API, a Celery worker, and a RAG (Retrieval-Augmented Generation) pipeline with an LLM to validate signaling data.

1. Prerequisites

Before you begin, ensure you have the following software installed on your system:

Python 3.10 or newer

pip and venv

Git

PostgreSQL: The application's main database.

Redis: The message broker for Celery.

2. Initial Project Setup

These steps only need to be performed once when first setting up the project.

Step 2.1: Clone and Set Up Virtual Environment

# Clone the repository (if you haven't already)
git clone <your-repo-url>
cd AI_VALIDATION_ENGINE

# Create a Python virtual environment
python -m venv env_name

# Activate the virtual environment
# On Linux/macOS:
source ai_telecom_env/bin/activate


Step 2.2: Install Python Dependencies

# Install all required Python packages
pip install -r requirements.txt


Step 2.3: Set Up Environment Variables

This file contains all your secret keys and database URLs.

Create a file named .env in the root (AI_VALIDATION_ENGINE) directory.

Copy the contents of .env.example (or the example I provided) into it.

Fill in your actual credentials, especially:

HUGGING_FACE_TOKEN

DB_USER

DB_PASSWORD

DB_NAME

3. Database and Services Setup (One-Time)

Step 3.1: Install and Run Redis

These commands are for Debian-based Linux (e.g., Ubuntu).

# Install the Redis server
sudo apt-get update
sudo apt-get install redis-server

# Start the service and enable it to run on boot
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify that Redis is running
redis-cli ping
# You should see: PONG


Step 3.2: Set Up PostgreSQL Database

The application cannot create the database for you. You must do this manually.

Log in to psql as the postgres superuser.

Create the database and user specified in your .env file.

/* Example psql commands: */
CREATE DATABASE ai_telecom;
CREATE USER ai_telecom WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_telecom TO ai_telecom;
\c ai_telecom
GRANT ALL PRIVILEGES ON SCHEMA public TO ai_telecom;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ai_telecom;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ai_telecom;
\q


Step 3.3: Run Database Migrations

This creates the validation_tasks table in your database.

# Step 1: Initialize the migrations folder (run this only ONCE ever)
flask db init

# Step 2: Generate the migration script
flask db migrate -m "Initial migration: Create validation_tasks table"

# Step 3: Apply the migration to the database
flask db upgrade


4. Knowledge Base Ingestion

This step "teaches" your AI by loading your documents into the vector database.

Place all your scenario files (e.g., scenario_definitions.json, atis.pdf) into the document_store/ directory.

Run the ingestion script.

# This will clear the old vector DB and build a new one
python run_ingestion.py


Note: You must re-run this script every time you update the files in document_store.

5. Running the Application

You must run two processes in two separate terminals.

Terminal 1: Start the Flask API Server

# Make sure your virtual environment is active
python run.py


You should see the server start on http://127.0.0.1:5000. This server does not load the AI models.

Terminal 2: Start the Celery Worker

This is the process that loads the AI models and does the heavy lifting.

# Make sure your virtual environment is active
celery -A app.celery_worker.celery worker --loglevel=info

or 

# These environment variables are REQUIRED to prevent the worker from freezing
TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 celery -A app.celery_worker.celery worker --loglevel=info
