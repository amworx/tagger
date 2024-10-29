from flask import Flask, request, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_assets import Environment, Bundle
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
assets = Environment()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set default config values first
    app.config.setdefault('APP_NAME', 'Tagger')
    app.config.setdefault('INTERFACE_THEME', 'theme-light')
    app.config.setdefault('APP_FONT', 'Inter')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    assets.init_app(app)

    with app.app_context():
        # Import models here to avoid circular imports
        from app.models import Setting, User
        
        # Create all tables
        db.create_all()
        
        # Now try to load settings
        try:
            settings = Setting.query.all()
            for setting in settings:
                app.config[setting.key] = setting.value
        except Exception as e:
            app.logger.warning(f"Could not load settings: {str(e)}")

    # Define asset bundles
    css = Bundle('css/style.css', output='gen/packed.css')
    js = Bundle('js/theme.js', output='gen/packed.js')
    assets.register('css_all', css)
    assets.register('js_all', js)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.permissions import bp as permissions_bp
    app.register_blueprint(permissions_bp, url_prefix='/permissions')

    @app.before_request
    def require_login():
        if not current_user.is_authenticated and request.endpoint and request.endpoint != 'static' and request.endpoint[:4] != 'auth':
            return redirect(url_for('auth.login'))

    @app.context_processor
    def inject_settings():
        return dict(
            app_name=app.config.get('APP_NAME', 'Tagger'),
            app_font=app.config.get('APP_FONT', 'Inter'),
            interface_theme=app.config.get('INTERFACE_THEME', 'theme-light'),
            current_app=app
        )

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
