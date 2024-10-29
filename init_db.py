from app import db, create_app
from app.models import User, UserRole
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create superadmin if it doesn't exist
        if not User.query.filter_by(username='superadmin').first():
            user = User(
                username='superadmin',
                email='superadmin@example.com',
                password_hash=generate_password_hash('superadmin'),
                role=UserRole.SUPERADMIN
            )
            db.session.add(user)
            db.session.commit()
            print("Superadmin user created successfully")
        else:
            print("Superadmin user already exists")

if __name__ == '__main__':
    init_db()
