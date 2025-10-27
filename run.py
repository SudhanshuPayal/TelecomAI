from app import create_app
from dotenv import load_dotenv
import os

# --- Load Environment Variables ---
# This line looks for a .env file in the root directory and loads its variables
# into the environment. This must be done BEFORE any part of the app that needs
# these variables (like the model loader) is imported.
load_dotenv()

# --- Create and Run the Application ---
# Now, when create_app() is called, it will trigger the model loading process.
# The model loader will have access to the HUGGING_FACE_TOKEN from the environment.
app = create_app()

if __name__ == "__main__":
    # For production, it's better to use a WSGI server like Gunicorn.
    # Example: gunicorn --workers 4 --bind 0.0.0.0:5000 "run:app"
    app.run(host='0.0.0.0', port=5000, debug=True)

