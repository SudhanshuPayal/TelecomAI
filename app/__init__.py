from flask import Flask
from . import config
from .database import db, migrate
from .tasks.task_validation import ValidationTask
from .celery_worker.celery_worker import celery
from .config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, SQLALCHEMY_DATABASE_URI
def create_app():
    """
    Application factory function. Creates and configures the Flask app.
    """
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Update Celery configuration from the Flask app's config
    celery.conf.update(
        broker_url=CELERY_BROKER_URL,
        result_backend=CELERY_RESULT_BACKEND
    )

    # Subclass Celery's Task class to run tasks within the Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask

    # Initialize extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    # --- Register Blueprints ---
    # Import the blueprint object from the api package and register it with the app.
    with app.app_context():
        from .api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        print("Flask app created and blueprints registered.")

    return app

