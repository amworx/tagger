from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, Response, send_file
from flask_login import login_required, current_user
from app.routes import bp
from app.models import (AssetType, Building, Department, User, UserRole, Setting, 
                       DataType, PermissionType)
from app import db, bcrypt
from app.forms import AssetTypeForm, BuildingForm, DepartmentForm, SettingsForm, UserForm
from app.utils.decorators import requires_permission
import csv
from io import StringIO
import os
from datetime import datetime
import json

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

@bp.route('/generate_tag', methods=['GET', 'POST'])
@login_required
@requires_permission('tag_generation', PermissionType.READ)
def generate_tag():
    asset_types = AssetType.query.all()
    buildings = Building.query.all()
    departments = Department.query.all()
    
    if request.method == 'POST':
        # Your existing generate_tag POST logic here
        pass
    
    return render_template('generate_tag.html', 
                         asset_types=asset_types,
                         buildings=buildings,
                         departments=departments)

@bp.route('/user_list')
@login_required
@requires_permission('user_management', PermissionType.READ)
def user_list():
    users = User.query.all()
    return render_template('user_management.html', users=users)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@requires_permission('settings', PermissionType.MANAGE)
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        # Your existing settings POST logic here
        pass
    
    # Pre-populate form
    form.app_name.data = current_app.config.get('APP_NAME', 'Tagger')
    form.interface_theme.data = current_app.config.get('INTERFACE_THEME', 'theme-light')
    form.app_font.data = current_app.config.get('APP_FONT', 'Inter')
    
    return render_template('settings.html', form=form)

# Add all your other routes here (asset_type_list, building_list, department_list, etc.)

def update_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        new_setting = Setting(key=key, value=value)
        db.session.add(new_setting)

def get_setting(key, default):
    setting = Setting.query.filter_by(key=key).first()
    return setting.value if setting else default