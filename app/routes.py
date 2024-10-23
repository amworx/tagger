from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import AssetType, Building, Department, User, UserRole, Setting
from app import db, bcrypt
from app.forms import AssetTypeForm, BuildingForm, DepartmentForm, SettingsForm, UserForm, SuperadminEditForm
import csv
from io import StringIO
import os
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

# Add this function to include current_app in all template renders
def render_template_with_current_app(*args, **kwargs):
    return render_template(*args, **kwargs, current_app=current_app)

@bp.route('/')
@login_required
def index():
    return redirect(url_for('main.generate_tag'))

@bp.route('/database_operations')
@login_required
def database_operations():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    return render_template_with_current_app('database_operations.html')

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
    per_page = 10
    pagination = AssetType.query.paginate(page=page, per_page=per_page, error_out=False)
    asset_types = pagination.items
    form = AssetTypeForm()  # Create an instance of the form
    return render_template_with_current_app('list_view.html', 
                           title='Asset Types',
                           model_name='asset_type',
                           headers=['Title', 'Code'],
                           item_fields=['title', 'code'],
                           items=asset_types,
                           page=page,
                           per_page=per_page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev,
                           form=form)  # Pass the form to the template

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
    per_page = 10
    pagination = Building.query.paginate(page=page, per_page=per_page, error_out=False)
    buildings = pagination.items
    form = BuildingForm()  # Create an instance of the form
    return render_template_with_current_app('list_view.html', 
                           title='Buildings',
                           model_name='building',
                           headers=['Title', 'Code'],
                           item_fields=['title', 'code'],
                           items=buildings,
                           page=page,
                           per_page=per_page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev,
                           form=form)  # Pass the form to the template

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
    per_page = 10
    pagination = Department.query.paginate(page=page, per_page=per_page, error_out=False)
    departments = pagination.items
    form = DepartmentForm()  # Create an instance of the form
    return render_template_with_current_app('list_view.html', 
                           title='Departments',
                           model_name='department',
                           headers=['Title', 'Code'],
                           item_fields=['title', 'code'],
                           items=departments,
                           page=page,
                           per_page=per_page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev,
                           form=form)  # Pass the form to the template

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
def import_data(model_name):
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
def export_data(model_name):
    model = globals()[model_name]
    items = model.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([column.name for column in model.__table__.columns])
    
    # Write data
    for item in items:
        writer.writerow([getattr(item, column.name) for column in model.__table__.columns])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename={model_name.lower()}_export.csv'
    }

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    form = SettingsForm()
    if form.validate_on_submit():
        app_name = form.app_name.data or 'Tagger'
        current_app.config['APP_NAME'] = app_name
        current_app.config['INTERFACE_THEME'] = form.interface_theme.data
        
        # Save the app name to a persistent storage (e.g., database)
        setting = Setting.query.filter_by(key='APP_NAME').first()
        if setting:
            setting.value = app_name
        else:
            setting = Setting(key='APP_NAME', value=app_name)
            db.session.add(setting)
        
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('main.settings'))
    elif request.method == 'GET':
        form.app_name.data = current_app.config.get('APP_NAME', '')
        form.interface_theme.data = current_app.config.get('INTERFACE_THEME', 'system')
    return render_template_with_current_app('settings.html', form=form)

@bp.route('/users')
@login_required
def user_list():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    form = UserForm()  # Create an instance of the form
    return render_template_with_current_app('list_view.html', 
                           title='Users',
                           model_name='user',
                           headers=['Username', 'Email', 'Role'],
                           item_fields=['username', 'email', 'role'],
                           items=users,
                           page=page,
                           per_page=per_page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev,
                           form=form)  # Pass the form to the template

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

