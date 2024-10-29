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
    total_asset_types = AssetType.query.count()
    total_buildings = Building.query.count()
    total_departments = Department.query.count()
    total_users = User.query.count()

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
        asset_category = request.form['asset_category']
        asset_number = request.form['asset_number']
        asset_type = request.form['asset_type']
        
        try:
            if asset_category == 'office':
                building = request.form['building']
                room_number = request.form['room_number']
                tag = f"{int(asset_number):04d}-{asset_type}-{building}-RN{int(room_number):03d}"
            elif asset_category == 'employee':
                department = request.form['department']
                employee_id = request.form['employee_id']
                tag = f"{int(asset_number):04d}-{asset_type}-{department}-ID{int(employee_id):03d}"
            else:
                raise ValueError('Invalid asset category')
            
            return render_template('generate_tag.html', 
                               asset_types=asset_types, 
                               buildings=buildings, 
                               departments=departments, 
                               generated_tag=tag,
                               success_message="Tag generated successfully!",
                               form=request.form)
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('generate_tag.html', 
                         asset_types=asset_types,
                         buildings=buildings,
                         departments=departments)

@bp.route('/asset_type_list')
@login_required
@requires_permission('asset_types', PermissionType.READ)
def asset_type_list():
    asset_types = AssetType.query.all()
    form = AssetTypeForm()
    return render_template('list_view.html',
                         title='Asset Types',
                         model_name='asset_type',
                         items=asset_types,
                         form=form)

@bp.route('/building_list')
@login_required
@requires_permission('buildings', PermissionType.READ)
def building_list():
    buildings = Building.query.all()
    form = BuildingForm()
    return render_template('list_view.html',
                         title='Buildings',
                         model_name='building',
                         items=buildings,
                         form=form)

@bp.route('/department_list')
@login_required
@requires_permission('departments', PermissionType.READ)
def department_list():
    departments = Department.query.all()
    form = DepartmentForm()
    return render_template('list_view.html',
                         title='Departments',
                         model_name='department',
                         items=departments,
                         form=form)

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
        app_name = form.app_name.data or 'Tagger'
        interface_theme = form.interface_theme.data
        app_font = form.app_font.data

        update_setting('APP_NAME', app_name)
        update_setting('INTERFACE_THEME', interface_theme)
        update_setting('APP_FONT', app_font)

        current_app.config['APP_NAME'] = app_name
        current_app.config['INTERFACE_THEME'] = interface_theme
        current_app.config['APP_FONT'] = app_font

        db.session.commit()
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('main.settings'))

    form.app_name.data = current_app.config.get('APP_NAME', 'Tagger')
    form.interface_theme.data = current_app.config.get('INTERFACE_THEME', 'theme-light')
    form.app_font.data = current_app.config.get('APP_FONT', 'Inter')

    return render_template('settings.html', form=form)

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