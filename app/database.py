from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy for ORM (Object Relational Mapping) capabilities.
# This object will be used to define models and interact with the database.
db = SQLAlchemy()

# Initialize Flask-Migrate to handle database schema migrations.
# This allows you to update your database schema as your models change over time.
migrate = Migrate()

