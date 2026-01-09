from flask import Flask, abort, request, session
from .config import Config
from .extensions import db
from .utils import get_activity_color, LIGHT_MODE_COLORS, DARK_MODE_COLORS, ACTIVITY_TYPE_DEFS, ACTIVITY_TYPE_ORDER, TEAM_LIKE_TYPES
from datetime import timedelta
from .routes import main, auth, admin
from .models import User
import json
from dotenv import load_dotenv
import logging
import secrets
from sqlalchemy import text

def create_app(config_class=Config):
    load_dotenv()  # Load .env file
    
    # Configure logging based on config
    log_level = getattr(logging, config_class.LOG_LEVEL, logging.INFO)
    formatter = logging.Formatter('[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    root_logger.setLevel(log_level)
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        if app.debug or app.testing:
            app.logger.warning('SECRET_KEY is not set; running in insecure development mode.')
        else:
            raise RuntimeError('SECRET_KEY must be set in production.')
    
    # Log the configured log level
    app.logger.info(f"Application started with LOG_LEVEL: {config_class.LOG_LEVEL}")

    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)

    # Context processors and filters
    @app.context_processor
    def inject_colors():
        return {
            'LIGHT_MODE_COLORS': LIGHT_MODE_COLORS,
            'DARK_MODE_COLORS': DARK_MODE_COLORS,
            'get_activity_color': get_activity_color,
            'timedelta': timedelta,
            'ACTIVITY_TYPE_DEFS': ACTIVITY_TYPE_DEFS,
            'ACTIVITY_TYPE_ORDER': ACTIVITY_TYPE_ORDER,
            'TEAM_LIKE_TYPES': TEAM_LIKE_TYPES
        }

    def generate_csrf_token():
        token = session.get('_csrf_token')
        if not token:
            token = secrets.token_urlsafe(32)
            session['_csrf_token'] = token
        return token

    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': generate_csrf_token}

    @app.before_request
    def csrf_protect():
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            token = session.get('_csrf_token')
            if request.is_json:
                payload = request.get_json(silent=True) or {}
                request_token = request.headers.get('X-CSRFToken') or payload.get('csrf_token')
            else:
                request_token = request.form.get('csrf_token')
            if not token or not request_token or token != request_token:
                abort(400)

    @app.template_filter('parse_groups')
    def parse_groups(groups_json):
        try:
            return json.loads(groups_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @app.template_filter('from_json')
    def from_json(json_string):
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            return {}

    @app.template_filter('get_activity_color')
    def get_activity_color_filter(activity_type):
        return get_activity_color(activity_type)

    @app.template_filter('build_group_cells')
    def build_group_cells_filter(activity):
        from .utils import build_group_cells
        return build_group_cells(activity)

    with app.app_context():
        if app.config.get('AUTO_CREATE_DB'):
            db.create_all()
            if db.engine.dialect.name == 'sqlite':
                result = db.session.execute(text("PRAGMA table_info(training)")).fetchall()
                existing_columns = {row[1] for row in result}
                if 'is_hidden' not in existing_columns:
                    db.session.execute(text("ALTER TABLE training ADD COLUMN is_hidden BOOLEAN NOT NULL DEFAULT 0"))
                    db.session.commit()
        if app.config.get('CREATE_DEFAULT_USERS') and User.query.count() == 0:
            # Create default users if not exist
            try:
                admin_user = User(
                    username=app.config.get('DEFAULT_ADMIN_USERNAME', 'admin'),
                    role='admin'
                )
                admin_user.set_password(app.config.get('DEFAULT_ADMIN_PASSWORD', 'admin'))
                user = User(
                    username=app.config.get('DEFAULT_USER_USERNAME', 'user'),
                    role='user'
                )
                user.set_password(app.config.get('DEFAULT_USER_PASSWORD', 'user'))
                db.session.add(admin_user)
                db.session.add(user)
                db.session.commit()
                app.logger.info('Default users created from configuration.')
            except Exception as e:
                app.logger.error(f"Error creating default users: {e}")

    return app
