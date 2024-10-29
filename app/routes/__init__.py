from flask import Blueprint

bp = Blueprint('main', __name__)

from app.routes import permissions
from . import routes  # Import your main routes 