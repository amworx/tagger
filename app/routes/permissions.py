from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import (User, Resource, Permission, PermissionGroup, UserPermission, 
                       RolePermission, PermissionType, PermissionAudit)
from app.utils.decorators import requires_permission, log_permission_change
from app import db

bp = Blueprint('permissions', __name__)

@bp.route('/permissions/manage/<int:user_id>')
@login_required
@requires_permission('user_management', PermissionType.MANAGE)
def manage_user_permissions(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.can_manage_user(user):
        flash('You do not have permission to manage this user\'s permissions.', 'danger')
        return redirect(url_for('main.user_list'))
    
    resources = Resource.query.all()
    groups = PermissionGroup.query.all()
    
    return render_template('permissions/manage.html', 
                         user=user, 
                         resources=resources,
                         groups=groups,
                         PermissionType=PermissionType)

@bp.route('/permissions/groups')
@login_required
@requires_permission('permission_groups', PermissionType.READ)
def permission_groups():
    groups = PermissionGroup.query.all()
    return render_template('permissions/groups.html', groups=groups)

@bp.route('/permissions/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
@requires_permission('permission_groups', PermissionType.MANAGE)
def edit_group(group_id):
    group = PermissionGroup.query.get_or_404(group_id)
    if request.method == 'POST':
        group.name = request.form['name']
        group.description = request.form['description']
        
        # Update permissions
        new_permissions = request.form.getlist('permissions')
        group.permissions = Permission.query.filter(Permission.id.in_(new_permissions)).all()
        
        db.session.commit()
        log_permission_change(
            None, current_user.id, 'modify_group', 
            group_id=group.id, 
            details={'name': group.name, 'permissions': new_permissions}
        )
        
        flash('Group updated successfully.', 'success')
        return redirect(url_for('permissions.permission_groups'))
    
    resources = Resource.query.all()
    return render_template('permissions/edit_group.html', 
                         group=group, 
                         resources=resources,
                         PermissionType=PermissionType)

@bp.route('/permissions/update', methods=['POST'])
@login_required
@requires_permission('user_management', PermissionType.MANAGE)
def update_permissions():
    user_id = request.form.get('user_id')
    user = User.query.get_or_404(user_id)
    
    if not current_user.can_manage_user(user):
        return jsonify({'success': False, 'error': 'Insufficient permissions'})
    
    try:
        # Update direct permissions
        new_permissions = request.form.getlist('permissions')
        current_permissions = UserPermission.query.filter_by(user_id=user.id).all()
        
        # Remove old permissions
        for perm in current_permissions:
            if str(perm.permission_id) not in new_permissions:
                db.session.delete(perm)
                log_permission_change(
                    user.id, current_user.id, 'revoke', 
                    permission_id=perm.permission_id
                )
        
        # Add new permissions
        existing_perm_ids = [p.permission_id for p in current_permissions]
        for perm_id in new_permissions:
            if int(perm_id) not in existing_perm_ids:
                new_perm = UserPermission(
                    user_id=user.id,
                    permission_id=int(perm_id),
                    granted_by_id=current_user.id
                )
                db.session.add(new_perm)
                log_permission_change(
                    user.id, current_user.id, 'grant', 
                    permission_id=int(perm_id)
                )
        
        # Update groups
        new_groups = request.form.getlist('groups')
        user.groups = PermissionGroup.query.filter(PermissionGroup.id.in_(new_groups)).all()
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}) 

@bp.route('/permissions/audit-log')
@login_required
@requires_permission('user_management', PermissionType.READ)
def audit_log():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = PermissionAudit.query\
        .join(User, PermissionAudit.user_id == User.id)\
        .join(User, PermissionAudit.actor_id == User.id, aliased=True)\
        .order_by(PermissionAudit.timestamp.desc())
    
    if not current_user.is_superadmin():
        # Non-superadmins can only see logs related to users they can manage
        query = query.filter(
            (PermissionAudit.actor_id == current_user.id) |
            (User.role.notin_(['admin', 'superadmin']))
        )
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    return render_template('permissions/audit_log.html',
                         audits=pagination.items,
                         pagination=pagination)