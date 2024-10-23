from app import db
from flask_login import UserMixin
from sqlalchemy import event
from app import login_manager

class AssetType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), nullable=False, unique=True)

    @staticmethod
    def _uppercase_code(target, value, oldvalue, initiator):
        if value is not None:
            return value.upper()

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), nullable=False, unique=True)

    @staticmethod
    def _uppercase_code(target, value, oldvalue, initiator):
        if value is not None:
            return value.upper()

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), nullable=False, unique=True)

    @staticmethod
    def _uppercase_code(target, value, oldvalue, initiator):
        if value is not None:
            return value.upper()

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
