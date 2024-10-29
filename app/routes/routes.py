from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.routes import bp
from app.models import AssetType, Building, Department, User

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@bp.route('/dashboard')
@login_required
def dashboard():
    # Gather statistics
    total_asset_types = AssetType.query.count()
    total_buildings = Building.query.count()
    total_departments = Department.query.count()
    total_users = User.query.count()

    # Get the latest added items
    latest_asset_types = AssetType.query.order_by(AssetType.id.desc()).limit(5).all()
    latest_buildings = Building.query.order_by(Building.id.desc()).limit(5).all()
    latest_departments = Department.query.order_by(Department.id.desc()).limit(5).all()

    return render_template('dashboard.html',
                         total_asset_types=total_asset_types,
                         total_buildings=total_buildings,
                         total_departments=total_departments,
                         total_users=total_users,
                         latest_asset_types=latest_asset_types,
                         latest_buildings=latest_buildings,
                         latest_departments=latest_departments)

# Add other routes from your original routes.py file here 