from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
import json

def requires_permission(resource_name, permission_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(resource_name, permission_type):
                if not current_user.is_authenticated:
                    return redirect(url_for('auth.login'))
                flash('You do not have permission to access this resource.', 'danger')
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_permission_change(user_id, actor_id, action, permission_id=None, group_id=None, details=None):
    from app.models import PermissionAudit, db
    
    audit = PermissionAudit(
        user_id=user_id,
        actor_id=actor_id,
        action=action,
        permission_id=permission_id,
        group_id=group_id,
        details=json.dumps(details) if details else None
    )
    db.session.add(audit)
    db.session.commit() 