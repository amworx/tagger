from enum import Enum
from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event  # Add this import

class DataType(Enum):
    ASSET_TYPE = 'asset_type'
    BUILDING = 'building'
    DEPARTMENT = 'department'

class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @declared_attr
    def data_type(cls):
        return db.Column(db.Enum(DataType), nullable=False)
    
    @classmethod
    def get_metadata(cls):
        raise NotImplementedError
    
    def validate_code(self):
        raise NotImplementedError
    
    @staticmethod
    def _uppercase_code(target, value, oldvalue, initiator):
        if value is None:
            return None
        return value.upper()

class AssetType(BaseModel):
    __tablename__ = 'asset_type'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = DataType.ASSET_TYPE
    
    @classmethod
    def get_metadata(cls):
        return {
            'code_suffix': 'A',
            'required_fields': ['title', 'code'],
            'export_fields': ['title', 'code'],
            'import_fields': ['title', 'code'],
            'validation_rules': {
                'code': lambda x: x.endswith('A'),
                'title': lambda x: len(x) >= 2
            }
        }
    
    def validate_code(self):
        if not self.code.endswith('A'):
            raise ValueError("Asset Type code must end with 'A'")

class Building(BaseModel):
    __tablename__ = 'building'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = DataType.BUILDING
    
    @classmethod
    def get_metadata(cls):
        return {
            'code_suffix': 'B',
            'required_fields': ['title', 'code'],
            'export_fields': ['title', 'code'],
            'import_fields': ['title', 'code'],
            'validation_rules': {
                'code': lambda x: x.endswith('B'),
                'title': lambda x: len(x) >= 2
            }
        }
    
    def validate_code(self):
        if not self.code.endswith('B'):
            raise ValueError("Building code must end with 'B'")

class Department(BaseModel):
    __tablename__ = 'department'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = DataType.DEPARTMENT
    
    @classmethod
    def get_metadata(cls):
        return {
            'code_suffix': 'D',
            'required_fields': ['title', 'code'],
            'export_fields': ['title', 'code'],
            'import_fields': ['title', 'code'],
            'validation_rules': {
                'code': lambda x: x.endswith('D'),
                'title': lambda x: len(x) >= 2
            }
        }
    
    def validate_code(self):
        if not self.code.endswith('D'):
            raise ValueError("Department code must end with 'D'")

class UserRole:
    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    USER = 'user'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default=UserRole.USER)

    def is_superadmin(self):
        return self.role == UserRole.SUPERADMIN

    def is_admin(self):
        return self.role in [UserRole.SUPERADMIN, UserRole.ADMIN]

    def is_user(self):
        return self.role == UserRole.USER

    @classmethod
    def find_by_username_or_email(cls, login):
        return cls.query.filter((cls.username == login) | (cls.email == login)).first()

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256))

# Set up event listeners for each model
event.listen(AssetType.code, 'set', AssetType._uppercase_code, retval=True)
event.listen(Building.code, 'set', Building._uppercase_code, retval=True)
event.listen(Department.code, 'set', Department._uppercase_code, retval=True)

class PermissionType(Enum):
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    MANAGE = 'manage'

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'settings', 'users', 'database_ops'
    description = db.Column(db.String(200))

class PermissionGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    permissions = db.relationship('Permission', secondary='group_permissions')
    users = db.relationship('User', secondary='user_groups')

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    permission_type = db.Column(db.Enum(PermissionType), nullable=False)
    
    resource = db.relationship('Resource')

    def __repr__(self):
        return f'<Permission {self.resource.name}:{self.permission_type.value}>'

class RolePermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # References UserRole
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)

class UserPermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)
    granted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

class PermissionAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User affected
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User making the change
    action = db.Column(db.String(50), nullable=False)  # 'grant', 'revoke', 'modify'
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('permission_group.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)  # JSON string with additional details

# Association tables
group_permissions = db.Table('group_permissions',
    db.Column('group_id', db.Integer, db.ForeignKey('permission_group.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
)

user_groups = db.Table('user_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('permission_group.id'))
)

# Add these to your existing User model
class User(UserMixin, db.Model):
    # ... (existing fields)
    
    permissions = db.relationship('Permission', secondary='user_permission')
    groups = db.relationship('PermissionGroup', secondary='user_groups')
    
    def has_permission(self, resource_name, permission_type):
        """Check if user has specific permission"""
        # Check direct user permissions
        for perm in self.permissions:
            if perm.resource.name == resource_name and perm.permission_type == permission_type:
                return True
                
        # Check group permissions
        for group in self.groups:
            for perm in group.permissions:
                if perm.resource.name == resource_name and perm.permission_type == permission_type:
                    return True
                    
        # Check role-based permissions
        role_perms = RolePermission.query.filter_by(role=self.role).all()
        for role_perm in role_perms:
            perm = role_perm.permission
            if perm.resource.name == resource_name and perm.permission_type == permission_type:
                return True
                
        return False

    def can_manage_user(self, target_user):
        """Check if user can manage another user"""
        if self.is_superadmin():
            return True
        if self.is_admin():
            return not target_user.is_admin() and not target_user.is_superadmin()
        return False
