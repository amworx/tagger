from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, Response, send_file
from flask_login import login_required, current_user
from app.models import AssetType, Building, Department, User, UserRole, Setting, DataType
from app import db, bcrypt
from app.forms import AssetTypeForm, BuildingForm, DepartmentForm, SettingsForm, UserForm, SuperadminEditForm
import csv
from io import StringIO
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import shutil
import io
import zipfile
from werkzeug.security import generate_password_hash
from flask import Flask
import tempfile

bp = Blueprint('main', __name__)

# Add this function to include current_app in all template renders
def render_template_with_current_app(*args, **kwargs):
    return render_template(*args, **kwargs, current_app=current_app)

@bp.route('/')
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

# Update the existing index route to redirect to dashboard
@bp.route('/index')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@bp.route('/database_operations')
@login_required
def database_operations():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    models = [AssetType, Building, Department, User]
    model_counts = {model.__name__: model.query.count() for model in models}
    
    return render_template('database_operations.html', models=[m.__name__ for m in models], model_counts=model_counts)

@bp.route('/clear_table/<string:model_name>')
@login_required
def clear_table(model_name):
    if not current_user.is_admin():
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    
    model = globals()[model_name]
    db.session.query(model).delete()
    db.session.commit()
    flash(f'{model_name} table cleared successfully', 'success')
    return redirect(url_for('main.database_operations'))

@bp.route('/check_db_connection')
def check_db_connection():
    try:
        db.session.query("1").from_statement("SELECT 1").all()
        return jsonify({"connected": True})
    except:
        return jsonify({"connected": False})

@bp.route('/generate_tag', methods=['GET', 'POST'])
@login_required
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
                
                if not room_number:
                    raise ValueError('Room Number is required for office assets')
                
                # Validate inputs
                if not (1 <= int(asset_number) <= 9999):
                    raise ValueError('Asset Number must be between 1 and 9999')
                if not (1 <= int(room_number) <= 999):
                    raise ValueError('Room Number must be between 1 and 999')
                
                # Generate tag
                tag = f"{int(asset_number):04d}-{asset_type}-{building}-RN{int(room_number):03d}"
            
            elif asset_category == 'employee':
                department = request.form['department']
                employee_id = request.form['employee_id']
                
                if not employee_id:
                    raise ValueError('Employee ID is required for employee-held assets')
                
                # Validate inputs
                if not (0 <= int(asset_number) <= 9999):
                    raise ValueError('Asset Number must be between 0 and 9999')
                if not (1 <= int(employee_id) <= 999):
                    raise ValueError('Employee ID must be between 1 and 999')
                
                # Generate tag
                tag = f"{int(asset_number):04d}-{asset_type}-{department}-ID{int(employee_id):03d}"
            
            else:
                raise ValueError('Invalid asset category')
            
            return render_template_with_current_app('generate_tag.html', 
                                   asset_types=asset_types, 
                                   buildings=buildings, 
                                   departments=departments, 
                                   generated_tag=tag,
                                   success_message="Tag generated successfully!",
                                   form=request.form)  # Pass the form data back to the template
        
        except ValueError as e:
            flash(str(e), 'error')
            return render_template_with_current_app('generate_tag.html', 
                                   asset_types=asset_types, 
                                   buildings=buildings, 
                                   departments=departments,
                                   form=request.form)  # Pass the form data back to the template in case of error
    
    return render_template_with_current_app('generate_tag.html', 
                           asset_types=asset_types, 
                           buildings=buildings, 
                           departments=departments)

# CRUD routes for AssetType
@bp.route('/asset_types')
@login_required
def asset_type_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    query = AssetType.query

    # Apply search if provided
    if search_query:
        query = query.filter(
            db.or_(
                AssetType.title.ilike(f'%{search_query}%'),
                AssetType.code.ilike(f'%{search_query}%')
            )
        )

    # Apply sorting
    if hasattr(AssetType, sort):
        sort_column = getattr(AssetType, sort)
        if order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    total_items = pagination.total
    total_pages = (total_items + per_page - 1) // per_page

    form = AssetTypeForm()
    return render_template_with_current_app('list_view.html',
                           title='Asset Types',
                           model_name='asset_type',
                           headers=['Title', 'Code'],
                           item_fields=['title', 'code'],
                           items=pagination.items,
                           page=page,
                           per_page=per_page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev,
                           total_items=total_items,
                           total_pages=total_pages,
                           search_query=search_query,
                           sort=sort,
                           order=order,
                           form=form)

@bp.route('/asset_type/add', methods=['POST'])
@login_required
def add_asset_type():
    form = AssetTypeForm()
    if form.validate_on_submit():
        asset_type = AssetType(title=form.title.data, code=form.code.data)
        db.session.add(asset_type)
        db.session.commit()
        flash('Asset Type added successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}', 'danger')
    return redirect(url_for('main.asset_type_list'))

@bp.route('/asset_type/edit/<int:id>', methods=['GET', 'POST'])
def edit_asset_type(id):
    asset_type = AssetType.query.get_or_404(id)
    form = AssetTypeForm(obj=asset_type)
    if form.validate_on_submit():
        asset_type.title = form.title.data
        asset_type.code = form.code.data
        db.session.commit()
        flash('Asset Type updated successfully', 'success')
        return redirect(url_for('main.asset_type_list'))  # Changed from 'main.asset_types'
    return render_template_with_current_app('asset_type_form.html', form=form, title='Edit Asset Type')

@bp.route('/asset_type/delete/<int:id>')
def delete_asset_type(id):
    asset_type = AssetType.query.get_or_404(id)
    db.session.delete(asset_type)
    db.session.commit()
    flash('Asset Type deleted successfully', 'success')
    return redirect(url_for('main.asset_type_list'))  # Changed from 'main.asset_types'

# CRUD routes for Building
@bp.route('/buildings')
@login_required
def building_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    query = Building.query

    # Apply search if provided
    if search_query:
        search_terms = search_query.split()
        for term in search_terms:
            search_filter = db.or_(
                Building.title.ilike(f'%{term}%'),
                Building.code.ilike(f'%{term}%')
            )
            query = query.filter(search_filter)

    # Apply sorting
    if hasattr(Building, sort):
        sort_column = getattr(Building, sort)
        if order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

    # Apply pagination
    try:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    except Exception as e:
        current_app.logger.error(f"Pagination error: {str(e)}")
        pagination = query.paginate(page=1, per_page=10, error_out=False)

    total_items = pagination.total
    total_pages = (total_items + per_page - 1) // per_page

    form = BuildingForm()
    return render_template_with_current_app('list_view.html',
                           title='Buildings',
                           model_name='building',
                           headers=['Title', 'Code'],
                           item_fields=['title', 'code'],
                           items=pagination.items,
                           page=page,
                           per_page=per_page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev,
                           total_items=total_items,
                           total_pages=total_pages,
                           search_query=search_query,
                           sort=sort,
                           order=order,
                           form=form)

@bp.route('/building/add', methods=['POST'])
@login_required
def add_building():
    form = BuildingForm()
    if form.validate_on_submit():
        building = Building(title=form.title.data, code=form.code.data)
        db.session.add(building)
        db.session.commit()
        flash('Building added successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}', 'danger')
    return redirect(url_for('main.building_list'))

@bp.route('/building/edit/<int:id>', methods=['GET', 'POST'])
def edit_building(id):
    building = Building.query.get_or_404(id)
    form = BuildingForm(obj=building)
    if form.validate_on_submit():
        building.title = form.title.data
        building.code = form.code.data
        db.session.commit()
        flash('Building updated successfully', 'success')
        return redirect(url_for('main.building_list'))  # Changed from 'main.buildings'
    return render_template_with_current_app('building_form.html', form=form, title='Edit Building')

@bp.route('/building/delete/<int:id>')
def delete_building(id):
    building = Building.query.get_or_404(id)
    db.session.delete(building)
    db.session.commit()
    flash('Building deleted successfully', 'success')
    return redirect(url_for('main.building_list'))  # Changed from 'main.buildings'

# CRUD routes for Department
@bp.route('/departments')
@login_required
def department_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    query = Department.query

    if search_query:
        query = query.filter(
            db.or_(
                Department.title.ilike(f'%{search_query}%'),
                Department.code.ilike(f'%{search_query}%')
            )
        )

    if hasattr(Department, sort):
        sort_column = getattr(Department, sort)
        if order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    total_items = pagination.total
    total_pages = (total_items + per_page - 1) // per_page

    form = DepartmentForm()
    return render_template_with_current_app('list_view.html',
                           title='Departments',
                           model_name='department',
                           headers=['Title', 'Code'],
                           item_fields=['title', 'code'],
                           items=pagination.items,
                           page=page,
                           per_page=per_page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev,
                           total_items=total_items,
                           total_pages=total_pages,
                           search_query=search_query,
                           sort=sort,
                           order=order,
                           form=form)

@bp.route('/department/add', methods=['POST'])
@login_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(title=form.title.data, code=form.code.data)
        db.session.add(department)
        db.session.commit()
        flash('Department added successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}', 'danger')
    return redirect(url_for('main.department_list'))

@bp.route('/department/edit/<int:id>', methods=['GET', 'POST'])
def edit_department(id):
    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.title = form.title.data
        department.code = form.code.data
        db.session.commit()
        flash('Department updated successfully', 'success')
        return redirect(url_for('main.department_list'))  # Changed from 'main.departments'
    return render_template_with_current_app('department_form.html', form=form, title='Edit Department')

@bp.route('/department/delete/<int:id>')
def delete_department(id):
    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully', 'success')
    return redirect(url_for('main.department_list'))  # Changed from 'main.departments'

# Import/Export routes
@bp.route('/import/<string:model_name>', methods=['POST'])
def import_data_for_model(model_name):
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('main.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('main.index'))
    
    if file and file.filename.endswith('.csv'):
        csv_data = file.read().decode('utf-8')
        csv_file = StringIO(csv_data)
        csv_reader = csv.DictReader(csv_file)
        
        model = globals()[model_name]
        for row in csv_reader:
            item = model(**row)
            db.session.add(item)
        
        db.session.commit()
        flash(f'{model_name} data imported successfully', 'success')
    else:
        flash('Invalid file format. Please upload a CSV file.', 'error')
    
    return redirect(url_for('main.index'))

@bp.route('/export/<string:model_name>')
@login_required
def export_data(model_name):
    if not current_user.is_admin():
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    
    model = globals()[model_name]
    data = model.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([column.name for column in model.__table__.columns])
    
    # Write data
    for item in data:
        writer.writerow([getattr(item, column.name) for column in model.__table__.columns])
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={model_name.lower()}_export.csv"}
    )

@bp.route('/import', methods=['POST'])
@login_required
def import_data():
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': 'You do not have permission to perform this action.'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload a CSV file.'})
    
    try:
        model_name = request.form.get('model')
        import_mode = request.form.get('import_mode', 'append')
        
        if not model_name:
            return jsonify({'success': False, 'error': 'No model specified'})
        
        # Get the model class
        model = globals().get(model_name)
        if not model:
            return jsonify({'success': False, 'error': f'Invalid model name: {model_name}'})
        
        # Read the CSV file first to validate its structure
        csv_data = file.read().decode('utf-8')
        csv_file = StringIO(csv_data)
        csv_reader = csv.DictReader(csv_file)
        
        # Get the headers from the CSV
        headers = csv_reader.fieldnames
        if not headers:
            return jsonify({'success': False, 'error': 'CSV file is empty or has no headers'})
        
        # Define expected headers for each model
        expected_headers = {
            'AssetType': ['title', 'code'],
            'Building': ['title', 'code'],
            'Department': ['title', 'code'],
            'User': ['username', 'email', 'role']
        }
        
        # Validate that this is the correct type of CSV for this model
        if model_name not in expected_headers:
            return jsonify({'success': False, 'error': f'Unsupported model type: {model_name}'})
        
        required_headers = expected_headers[model_name]
        missing_headers = [h for h in required_headers if h not in headers]
        
        if missing_headers:
            return jsonify({
                'success': False, 
                'error': f'Invalid CSV format for {model_name}. Missing required columns: {", ".join(missing_headers)}'
            })
        
        # If overwrite mode, clear the table first
        if import_mode == 'overwrite':
            if model_name == 'User':
                model.query.filter(model.id != current_user.id).delete()
            else:
                model.query.delete()
            db.session.commit()
        
        # Get the valid columns for the model
        valid_columns = [column.name for column in model.__table__.columns]
        
        records_added = 0
        records_updated = 0
        records_skipped = 0
        
        for row in csv_reader:
            try:
                # Filter out any columns that don't exist in the model
                filtered_data = {k: v for k, v in row.items() if k in valid_columns and k not in ['created_at', 'updated_at', 'data_type']}
                
                # Remove the id field if it exists
                filtered_data.pop('id', None)
                
                # Set the data_type based on the model
                if model_name == 'AssetType':
                    filtered_data['data_type'] = DataType.ASSET_TYPE
                elif model_name == 'Building':
                    filtered_data['data_type'] = DataType.BUILDING
                elif model_name == 'Department':
                    filtered_data['data_type'] = DataType.DEPARTMENT
                
                # Let SQLAlchemy handle the timestamps
                filtered_data['created_at'] = datetime.utcnow()
                filtered_data['updated_at'] = datetime.utcnow()
                
                if import_mode == 'replace':
                    existing_record = model.query.filter_by(code=filtered_data.get('code')).first()
                    if existing_record:
                        for key, value in filtered_data.items():
                            if key not in ['created_at']:  # Don't update created_at
                                setattr(existing_record, key, value)
                        records_updated += 1
                    else:
                        new_record = model(**filtered_data)
                        db.session.add(new_record)
                        records_added += 1
                
                elif import_mode == 'append':
                    existing_record = model.query.filter(
                        db.or_(
                            model.code == filtered_data.get('code'),
                            db.and_(
                                model.title == filtered_data.get('title'),
                                model.code == filtered_data.get('code')
                            )
                        )
                    ).first()
                    
                    if existing_record:
                        records_skipped += 1
                    else:
                        new_record = model(**filtered_data)
                        db.session.add(new_record)
                        records_added += 1
                
                else:  # overwrite mode
                    new_record = model(**filtered_data)
                    db.session.add(new_record)
                    records_added += 1
                
            except Exception as e:
                current_app.logger.error(f'Error processing row: {row}. Error: {str(e)}')
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'error': f'Error processing row: {str(e)}'
                })
        
        # Commit all records
        db.session.commit()
        
        message = f'Successfully imported {records_added} new records'
        if records_updated > 0:
            message += f', updated {records_updated} existing records'
        if records_skipped > 0:
            message += f', skipped {records_skipped} duplicate records'
        message += f' in {model_name}'
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Import error: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Error importing data: {str(e)}'
        })

@bp.route('/backup', methods=['GET'])
@login_required
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

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_superadmin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

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

    # Pre-populate form fields
    form.app_name.data = get_setting('APP_NAME', 'Tagger')
    form.interface_theme.data = get_setting('INTERFACE_THEME', 'theme-light')
    form.app_font.data = get_setting('APP_FONT', 'Inter')

    return render_template('settings.html', form=form)

def get_colors_for_scheme(scheme):
    color_schemes = {
        'default': ('#FF0040', '#7e34ff'),
        'blue_green': ('#3498db', '#2ecc71'),
        'red_orange': ('#e74c3c', '#f39c12'),
        'purple_blue': ('#9b59b6', '#3498db')
    }
    return color_schemes.get(scheme, color_schemes['default'])

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

@bp.route('/users')
@login_required
def user_list():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    query = User.query

    if search_query:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                User.role.ilike(f'%{search_query}%')
            )
        )

    if hasattr(User, sort):
        sort_column = getattr(User, sort)
        if order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    total_items = pagination.total
    total_pages = (total_items + per_page - 1) // per_page

    form = UserForm()
    return render_template_with_current_app('list_view.html',
                           title='Users',
                           model_name='user',
                           headers=['Username', 'Email', 'Role'],
                           item_fields=['username', 'email', 'role'],
                           items=pagination.items,
                           page=page,
                           per_page=per_page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev,
                           total_items=total_items,
                           total_pages=total_pages,
                           search_query=search_query,
                           sort=sort,
                           order=order,
                           form=form)

@bp.route('/user/add', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin():
        return jsonify({'success': False, 'errors': {'_': ['Only admins can add new users.']}})
    
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'errors': form.errors})

@bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    
    if user.is_superadmin():
        form = SuperadminEditForm(user.email, obj=user)
        if form.validate_on_submit():
            user.email = form.email.data
            if form.password.data:
                user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.commit()
            flash('Superadmin account updated successfully', 'success')
            return redirect(url_for('main.user_list'))
    else:
        form = UserForm(obj=user)
        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            if form.password.data:
                user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.role = form.role.data
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('main.user_list'))
    
    if request.method == 'GET':
        form.email.data = user.email
    
    return render_template_with_current_app('user_form.html', form=form, title='Edit User', user=user)

@bp.route('/user/delete/<int:id>')
@login_required
def delete_user(id):
    if not current_user.is_superadmin():
        flash('Only superadmin can delete users.', 'danger')
        return redirect(url_for('main.user_list'))  # Changed from 'main.users'
    user = User.query.get_or_404(id)
    if user.is_superadmin():
        flash('The superadmin account cannot be deleted.', 'danger')
        return redirect(url_for('main.user_list'))  # Changed from 'main.users'
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('main.user_list'))  # Changed from 'main.users'
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('main.user_list'))  # Changed from 'main.users'

@bp.route('/wipe_table/<string:model_name>', methods=['POST'])
@login_required
def wipe_table(model_name):
    if not current_user.is_admin():
        return jsonify({
            'success': False, 
            'error': 'You do not have permission to perform this action.'
        })
    
    try:
        # Prevent wiping the User table if it would delete the last admin
        if model_name == 'User':
            admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
            if admin_count <= 1 and current_user.is_admin():
                return jsonify({
                    'success': False,
                    'error': 'Cannot wipe Users table: This would delete the last admin account.'
                })

        # Get the model class
        model = globals().get(model_name)
        if not model:
            return jsonify({
                'success': False,
                'error': f'Invalid model name: {model_name}'
            })

        # Delete all records except the current user if it's the User table
        if model_name == 'User':
            model.query.filter(model.id != current_user.id).delete()
        else:
            model.query.delete()

        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{model_name} table has been wiped successfully.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error wiping table: {str(e)}'
        })

@bp.route('/<string:model_name>_list')
@login_required
def generic_list(model_name):
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    
    # Get the model class
    model = globals().get(model_name.capitalize())
    if not model:
        flash(f'Invalid model: {model_name}', 'danger')
        return redirect(url_for('main.index'))
    
    # Build the query
    query = model.query
    
    # Apply search if provided
    if search_query:
        search_filters = []
        for column in model.__table__.columns:
            if isinstance(column.type, db.String):
                search_filters.append(column.ilike(f'%{search_query}%'))
        if search_filters:
            query = query.filter(db.or_(*search_filters))
    
    # Apply sorting
    if hasattr(model, sort):
        sort_column = getattr(model, sort)
        if order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
    
    # Execute query with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    total_items = pagination.total
    total_pages = (total_items + per_page - 1) // per_page
    
    # Get form for adding new records
    form_class = globals().get(f'{model_name.capitalize()}Form')
    form = form_class() if form_class else None
    
    return render_template('list_view.html',
                         title=f'{model_name.title()}s',
                         model_name=model_name.lower(),
                         headers=['Title', 'Code'],
                         item_fields=['title', 'code'],
                         items=items,
                         page=page,
                         per_page=per_page,
                         has_next=pagination.has_next,
                         has_prev=pagination.has_prev,
                         total_items=total_items,
                         total_pages=total_pages,
                         search_query=search_query,
                         sort=sort,
                         order=order,
                         form=form,
                         max=max,  # Add built-in max function
                         min=min)  # Add built-in min function

