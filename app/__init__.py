from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_assets import Environment, Bundle
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
assets = Environment()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    assets.init_app(app)

    with app.app_context():
        db.create_all()  # This will create all tables, including the Setting table
        from app.models import Setting
        app_name_setting = Setting.query.filter_by(key='APP_NAME').first()
        if not app_name_setting:
            default_app_name = Setting(key='APP_NAME', value='Tagger')
            db.session.add(default_app_name)
            db.session.commit()
        app.config['APP_NAME'] = app_name_setting.value if app_name_setting else 'Tagger'

    # Define asset bundles
    css = Bundle('css/style.css', output='gen/packed.css')
    js = Bundle('js/theme.js', output='gen/packed.js')
    assets.register('css_all', css)
    assets.register('js_all', js)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app import routes
    app.register_blueprint(routes.bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    @app.before_request
    def require_login():
        if not current_user.is_authenticated and request.endpoint and request.endpoint != 'static' and request.endpoint[:4] != 'auth':
            return redirect(url_for('auth.login'))

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
