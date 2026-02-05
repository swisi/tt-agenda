from flask import Flask, abort, request, session
from .config import Config
from .extensions import db
from .utils import get_activity_color, ACTIVITY_TYPE_DEFAULTS, get_activity_type_defs, get_activity_type_order, get_team_like_types
from .activity_colors import get_activity_color_map
from datetime import timedelta
from .routes import main, auth, admin
from .models import User, ActivityType
import json
from dotenv import load_dotenv
import logging
import secrets
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import sys
from pathlib import Path
from jinja2 import ChoiceLoader, FileSystemLoader

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
    
    # Create Flask app
    app = Flask(__name__)
    
    # Add shared templates using ChoiceLoader
    shared_path = Path(__file__).parent.parent / "shared"
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(str(Path(__file__).parent / "templates")),
        FileSystemLoader(str(shared_path / "templates"))
    ])
    
    # Register shared static folder as additional static folder
    @app.route('/shared/<path:filename>')
    def shared_static(filename):
        from flask import send_from_directory
        return send_from_directory(shared_path / "static", filename)
    
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
        activity_defs = get_activity_type_defs()
        return {
            'LIGHT_MODE_COLORS': get_activity_color_map('light'),
            'DARK_MODE_COLORS': get_activity_color_map('dark'),
            'get_activity_color': get_activity_color,
            'timedelta': timedelta,
            'ACTIVITY_TYPE_DEFS': activity_defs,
            'ACTIVITY_TYPE_ORDER': get_activity_type_order(),
            'TEAM_LIKE_TYPES': get_team_like_types(),
            'ACTIVITY_TYPE_BEHAVIORS': {key: value.get('behavior') for key, value in activity_defs.items()}
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

    def ensure_activity_types():
        if not ACTIVITY_TYPE_DEFAULTS:
            return
        defaults_by_key = {item['key']: item for item in ACTIVITY_TYPE_DEFAULTS}
        rows = ActivityType.query.all()
        existing_keys = {row.key for row in rows}
        missing = [item for item in ACTIVITY_TYPE_DEFAULTS if item['key'] not in existing_keys]
        if missing:
            for item in missing:
                db.session.add(ActivityType(**item))
            db.session.commit()
            rows = ActivityType.query.all()

        changed = False
        for row in rows:
            defaults = defaults_by_key.get(row.key)
            if not defaults:
                continue
            for field in ('label', 'behavior', 'badge_class', 'sort_order'):
                if getattr(row, field, None) in (None, ''):
                    setattr(row, field, defaults[field])
                    changed = True
            if row.light_color in (None, '', '#E8E8E8') and defaults.get('light_color'):
                row.light_color = defaults['light_color']
                changed = True
            if row.dark_color in (None, '', '#4A4A4A') and defaults.get('dark_color'):
                row.dark_color = defaults['dark_color']
                changed = True
        if changed:
            db.session.commit()

    with app.app_context():
        if app.config.get('AUTO_CREATE_DB'):
            try:
                db.create_all()
            except OperationalError as exc:
                if 'already exists' not in str(exc).lower():
                    raise
                app.logger.warning('DB init race condition detected; continuing.')
            if db.engine.dialect.name == 'sqlite':
                table_exists = db.session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name='activity_type'")
                ).fetchone()
                if table_exists:
                    result = db.session.execute(text("PRAGMA table_info(activity_type)")).fetchall()
                    existing_columns = {row[1] for row in result}
                    if 'light_color' not in existing_columns:
                        db.session.execute(text("ALTER TABLE activity_type ADD COLUMN light_color VARCHAR(7) NOT NULL DEFAULT '#E8E8E8'"))
                    if 'dark_color' not in existing_columns:
                        db.session.execute(text("ALTER TABLE activity_type ADD COLUMN dark_color VARCHAR(7) NOT NULL DEFAULT '#4A4A4A'"))

                result = db.session.execute(text("PRAGMA table_info(training)")).fetchall()
                existing_columns = {row[1] for row in result}
                if 'is_hidden' not in existing_columns:
                    db.session.execute(text("ALTER TABLE training ADD COLUMN is_hidden BOOLEAN NOT NULL DEFAULT 0"))
                    db.session.commit()
                else:
                    db.session.commit()
            ensure_activity_types()
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
