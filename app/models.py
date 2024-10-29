from enum import Enum
from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event  # Add this import

class UserRoleType(str, Enum):
    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    USER = 'user'

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

class UserRole(db.Model):
    __tablename__ = 'user_role'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.relationship('RolePermission', backref='role', lazy=True)
    
    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    USER = 'user'
    
    def has_permission(self, permission):
        if isinstance(permission, Permission):
            permission = permission.value
        return any(p.permission == permission for p in self.permissions)

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

class Permission(Enum):
    # Page Access Permissions
    ACCESS_DASHBOARD = "access_dashboard"
    ACCESS_GENERATE_TAG = "access_generate_tag"
    ACCESS_ASSET_TYPES = "access_asset_types"
    ACCESS_BUILDINGS = "access_buildings"
    ACCESS_DEPARTMENTS = "access_departments"
    ACCESS_USER_MANAGEMENT = "access_user_management"
    ACCESS_DATABASE_OPS = "access_database_operations"
    ACCESS_SETTINGS = "access_settings"
    
    # Action Permissions
    CREATE_ASSET_TYPE = "create_asset_type"
    EDIT_ASSET_TYPE = "edit_asset_type"
    DELETE_ASSET_TYPE = "delete_asset_type"
    
    CREATE_BUILDING = "create_building"
    EDIT_BUILDING = "edit_building"
    DELETE_BUILDING = "delete_building"
    
    CREATE_DEPARTMENT = "create_department"
    EDIT_DEPARTMENT = "edit_department"
    DELETE_DEPARTMENT = "delete_department"
    
    CREATE_USER = "create_user"
    EDIT_USER = "edit_user"
    DELETE_USER = "delete_user"
    
    IMPORT_DATA = "import_data"
    EXPORT_DATA = "export_data"
    BACKUP_DATABASE = "backup_database"
    RESTORE_DATABASE = "restore_database"

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'), nullable=False)
    permission = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<RolePermission {self.role_id}:{self.permission}>'

# Set up event listeners for each model
event.listen(AssetType.code, 'set', AssetType._uppercase_code, retval=True)
event.listen(Building.code, 'set', Building._uppercase_code, retval=True)
event.listen(Department.code, 'set', Department._uppercase_code, retval=True)
