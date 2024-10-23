from app import create_app, db
from app.models import User, UserRole

app = create_app()

with app.app_context():
    # Ensure only one superadmin exists
    superadmins = User.query.filter_by(role=UserRole.SUPERADMIN).all()
    if len(superadmins) > 1:
        # Keep the first superadmin, demote others to admin
        for superadmin in superadmins[1:]:
            superadmin.role = UserRole.ADMIN
        db.session.commit()
        print(f"Demoted {len(superadmins) - 1} extra superadmin(s) to admin.")
    elif len(superadmins) == 0:
        # If no superadmin exists, create one
        superadmin = User(username='superadmin', email='superadmin@example.com', role=UserRole.SUPERADMIN)
        superadmin.set_password('superadmin123')  # Make sure to change this password!
        db.session.add(superadmin)
        db.session.commit()
        print("Created a new superadmin user.")
    else:
        print("Superadmin check completed. No changes needed.")

    # Print all users
    users = User.query.all()
    for user in users:
        print(f"User: {user.username}, Role: {user.role}")
