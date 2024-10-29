from app import create_app, db, bcrypt
from app.models import User, AssetType, Building, Department, UserRole, Setting
from sqlalchemy import inspect
from flask_migrate import Migrate, upgrade

app = create_app()
migrate = Migrate(app, db)

with app.app_context():
    inspector = inspect(db.engine)
    
    if not inspector.has_table("user") or not inspector.has_table("setting"):
        db.create_all()
        print("Database tables created.")
    else:
        print("Database schema is up to date.")

    # Create superadmin user if not exists
    superadmin = User.query.filter_by(role=UserRole.SUPERADMIN).first()
    if not superadmin:
        hashed_password = bcrypt.generate_password_hash('superadmin123').decode('utf-8')
        superadmin = User(username='superadmin', email='superadmin@example.com', password_hash=hashed_password, role=UserRole.SUPERADMIN)
        try:
            db.session.add(superadmin)
            db.session.commit()
            print("Superadmin user created.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating superadmin user: {str(e)}")
    else:
        print("Superadmin user already exists.")

    # Create or update APP_NAME setting
    update_setting('APP_NAME', 'Tagger')

    # Create or update INTERFACE_THEME setting
    update_setting('INTERFACE_THEME', 'theme-light')

    # Create or update APP_FONT setting
    update_setting('APP_FONT', 'Inter')

    print("Database initialization completed.")

    # Print all users
    users = User.query.all()
    for user in users:
        print(f"User: {user.username}, Role: {user.role}")

def update_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        new_setting = Setting(key=key, value=value)
        db.session.add(new_setting)
    db.session.commit()
    print(f"{key} setting created or updated.")
