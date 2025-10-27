from flask import Blueprint

# Create the Blueprint object. All routes in this package will be registered to this.
# We also add a url_prefix so all routes in this file start with /api.
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import the routes module at the bottom. This is crucial.
# It attaches the defined routes (like /query) to the api_bp object.
from . import routes