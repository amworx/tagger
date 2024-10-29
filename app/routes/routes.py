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
import shutil
import tempfile

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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    asset_types = AssetType.query.paginate(page=page, per_page=per_page)
    form = AssetTypeForm()
    
    return render_template('list_view.html',
                         title='Asset Types',
                         model_name='asset_type',
                         items=asset_types.items,
                         page=page,
                         per_page=per_page,
                         total_pages=asset_types.pages,
                         form=form)

@bp.route('/building_list')
@login_required
@requires_permission('buildings', PermissionType.READ)
def building_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    buildings = Building.query.paginate(page=page, per_page=per_page)
    form = BuildingForm()
    
    return render_template('list_view.html',
                         title='Buildings',
                         model_name='building',
                         items=buildings.items,
                         page=page,
                         per_page=per_page,
                         total_pages=buildings.pages,
                         form=form)

@bp.route('/department_list')
@login_required
@requires_permission('departments', PermissionType.READ)
def department_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    departments = Department.query.paginate(page=page, per_page=per_page)
    form = DepartmentForm()
    
    return render_template('list_view.html',
                         title='Departments',
                         model_name='department',
                         items=departments.items,
                         page=page,
                         per_page=per_page,
                         total_pages=departments.pages,
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

@bp.route('/database_operations')
@login_required
@requires_permission('database_operations', PermissionType.READ)
def database_operations():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    models = [AssetType, Building, Department, User]
    model_counts = {model.__name__: model.query.count() for model in models}
    
    return render_template('database_operations.html', 
                         models=[m.__name__ for m in models], 
                         model_counts=model_counts)

@bp.route('/clear_table/<string:model_name>')
@login_required
@requires_permission('database_operations', PermissionType.MANAGE)
def clear_table(model_name):
    if not current_user.is_admin():
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    
    model = globals()[model_name]
    db.session.query(model).delete()
    db.session.commit()
    flash(f'{model_name} table cleared successfully', 'success')
    return redirect(url_for('main.database_operations'))

@bp.route('/backup')
@login_required
@requires_permission('database_operations', PermissionType.MANAGE)
def backup_database():
    if not current_user.is_admin():
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        # Get the database file path
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        if not db_uri.startswith('sqlite:///'):
            return jsonify({'success': False, 'error': 'Unsupported database type'})
        
        db_path = os.path.join(current_app.root_path, db_uri.replace('sqlite:///', ''))
        if not os.path.exists(db_path):
            return jsonify({'success': False, 'error': f'Database file not found: {db_path}'})

        # Ensure all changes are written to disk
        db.session.commit()
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'tagger_backup_{timestamp}.db'
        
        # Send the database file directly
        return send_file(
            db_path,
            mimetype='application/x-sqlite3',
            as_attachment=True,
            download_name=backup_filename
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/restore', methods=['POST'])
@login_required
@requires_permission('database_operations', PermissionType.MANAGE)
def restore_database():
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': 'You do not have permission to perform this action.'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file']
    if not file.filename or not file.filename.endswith('.db'):
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload a .db file'})
    
    try:
        # Get the current database path
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        if not db_uri.startswith('sqlite:///'):
            return jsonify({'success': False, 'error': 'Unsupported database type'})
        
        db_path = os.path.join(current_app.root_path, db_uri.replace('sqlite:///', ''))
        
        # Close all database connections
        db.session.remove()
        db.engine.dispose()
        
        # Create a backup of the current database
        current_backup = f"{db_path}.bak"
        shutil.copy2(db_path, current_backup)
        
        try:
            # Save the uploaded file as the new database
            file.save(db_path)
            
            # Test the restored database
            with current_app.app_context():
                db.engine.connect()
                # Try a simple query to verify the database is working
                User.query.first()
            
            return jsonify({'success': True})
            
        except Exception as e:
            # If something goes wrong, restore the original database
            shutil.copy2(current_backup, db_path)
            return jsonify({'success': False, 'error': f'Error restoring database: {str(e)}'})
        
        finally:
            # Clean up the temporary backup
            if os.path.exists(current_backup):
                os.remove(current_backup)
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing backup file: {str(e)}'})

@bp.route('/create_user', methods=['GET', 'POST'])
@login_required
@requires_permission('user_management', PermissionType.WRITE)
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('main.user_list'))
    return render_template('user_form.html', form=form, title='Create User')

@bp.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_permission('user_management', PermissionType.WRITE)
def edit_user(id):
    user = User.query.get_or_404(id)
    if not current_user.can_manage_user(user):
        flash('You do not have permission to edit this user.', 'danger')
        return redirect(url_for('main.user_list'))
    
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.role = form.role.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('main.user_list'))
    return render_template('user_form.html', form=form, title='Edit User', user=user)

@bp.route('/edit_building/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_permission('buildings', PermissionType.WRITE)
def edit_building(id):
    building = Building.query.get_or_404(id)
    form = BuildingForm(obj=building)
    if form.validate_on_submit():
        building.title = form.title.data
        building.code = form.code.data
        db.session.commit()
        flash('Building updated successfully!', 'success')
        return redirect(url_for('main.building_list'))
    return render_template('form.html', form=form, title='Edit Building')

@bp.route('/edit_department/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_permission('departments', PermissionType.WRITE)
def edit_department(id):
    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.title = form.title.data
        department.code = form.code.data
        db.session.commit()
        flash('Department updated successfully!', 'success')
        return redirect(url_for('main.department_list'))
    return render_template('form.html', form=form, title='Edit Department')

@bp.route('/edit_asset_type/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_permission('asset_types', PermissionType.WRITE)
def edit_asset_type(id):
    asset_type = AssetType.query.get_or_404(id)
    form = AssetTypeForm(obj=asset_type)
    if form.validate_on_submit():
        asset_type.title = form.title.data
        asset_type.code = form.code.data
        db.session.commit()
        flash('Asset Type updated successfully!', 'success')
        return redirect(url_for('main.asset_type_list'))
    return render_template('form.html', form=form, title='Edit Asset Type')

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@requires_permission('user_management', PermissionType.DELETE)
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.can_manage_user(user):
        flash('You do not have permission to delete this user.', 'danger')
        return redirect(url_for('main.user_list'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.user_list'))

@bp.route('/delete_building/<int:id>', methods=['POST'])
@login_required
@requires_permission('buildings', PermissionType.DELETE)
def delete_building(id):
    building = Building.query.get_or_404(id)
    db.session.delete(building)
    db.session.commit()
    flash('Building deleted successfully!', 'success')
    return redirect(url_for('main.building_list'))

@bp.route('/delete_department/<int:id>', methods=['POST'])
@login_required
@requires_permission('departments', PermissionType.DELETE)
def delete_department(id):
    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('main.department_list'))

@bp.route('/delete_asset_type/<int:id>', methods=['POST'])
@login_required
@requires_permission('asset_types', PermissionType.DELETE)
def delete_asset_type(id):
    asset_type = AssetType.query.get_or_404(id)
    db.session.delete(asset_type)
    db.session.commit()
    flash('Asset Type deleted successfully!', 'success')
    return redirect(url_for('main.asset_type_list'))

@bp.route('/add_building', methods=['POST'])
@login_required
@requires_permission('buildings', PermissionType.WRITE)
def add_building():
    form = BuildingForm()
    if form.validate_on_submit():
        building = Building(title=form.title.data, code=form.code.data)
        try:
            db.session.add(building)
            db.session.commit()
            flash('Building added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding building: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}', 'danger')
    return redirect(url_for('main.building_list'))

@bp.route('/add_department', methods=['POST'])
@login_required
@requires_permission('departments', PermissionType.WRITE)
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(title=form.title.data, code=form.code.data)
        try:
            db.session.add(department)
            db.session.commit()
            flash('Department added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding department: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}', 'danger')
    return redirect(url_for('main.department_list'))

@bp.route('/add_asset_type', methods=['POST'])
@login_required
@requires_permission('asset_types', PermissionType.WRITE)
def add_asset_type():
    form = AssetTypeForm()
    if form.validate_on_submit():
        asset_type = AssetType(title=form.title.data, code=form.code.data)
        try:
            db.session.add(asset_type)
            db.session.commit()
            flash('Asset Type added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding asset type: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}', 'danger')
    return redirect(url_for('main.asset_type_list'))

# Add these routes to handle export/import
@bp.route('/export_asset_type')
@login_required
@requires_permission('asset_types', PermissionType.READ)
def export_asset_type():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['title', 'code'])  # Headers
    
    for item in AssetType.query.all():
        writer.writerow([item.title, item.code])
    
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=asset_types.csv'}
    )

@bp.route('/export_building')
@login_required
@requires_permission('buildings', PermissionType.READ)
def export_building():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['title', 'code'])  # Headers
    
    for item in Building.query.all():
        writer.writerow([item.title, item.code])
    
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=buildings.csv'}
    )

@bp.route('/export_department')
@login_required
@requires_permission('departments', PermissionType.READ)
def export_department():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['title', 'code'])  # Headers
    
    for item in Department.query.all():
        writer.writerow([item.title, item.code])
    
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=departments.csv'}
    )

@bp.route('/import_asset_type', methods=['POST'])
@login_required
@requires_permission('asset_types', PermissionType.WRITE)
def import_asset_type():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'Please upload a CSV file'})
    
    try:
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        
        for row in reader:
            asset_type = AssetType(title=row['title'], code=row['code'])
            db.session.add(asset_type)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/import_building', methods=['POST'])
@login_required
@requires_permission('buildings', PermissionType.WRITE)
def import_building():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'Please upload a CSV file'})
    
    try:
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        
        for row in reader:
            building = Building(title=row['title'], code=row['code'])
            db.session.add(building)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/import_department', methods=['POST'])
@login_required
@requires_permission('departments', PermissionType.WRITE)
def import_department():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'Please upload a CSV file'})
    
    try:
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        
        for row in reader:
            department = Department(title=row['title'], code=row['code'])
            db.session.add(department)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})