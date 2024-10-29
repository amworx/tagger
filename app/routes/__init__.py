from flask import Blueprint

bp = Blueprint('main', __name__)

from app.routes import routes  # Import routes first
from app.routes import permissions  # Then import permissions