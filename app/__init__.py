from flask import Flask
from .config import Config
from .extensions import db
from .utils import get_activity_color, LIGHT_MODE_COLORS, DARK_MODE_COLORS
from datetime import timedelta
from .routes import main, auth, admin
from .models import User
import json

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

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
            'timedelta': timedelta
        }

    @app.template_filter('parse_groups')
    def parse_groups(groups_json):
        try:
            return json.loads(groups_json)
        except:
            return []

    @app.template_filter('from_json')
    def from_json(json_string):
        try:
            return json.loads(json_string)
        except:
            return {}

    @app.template_filter('get_activity_color')
    def get_activity_color_filter(activity_type):
        return get_activity_color(activity_type)

    @app.template_filter('build_group_cells')
    def build_group_cells_filter(activity):
        from .utils import build_group_cells
        return build_group_cells(activity)

    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            # Create default users if not exist
            try:
                admin_user = User(username='admin', role='admin')
                admin_user.set_password('admin')
                user = User(username='user', role='user')
                user.set_password('user')
                db.session.add(admin_user)
                db.session.add(user)
                db.session.commit()
                print('Default users created: admin/admin and user/user')
            except Exception as e:
                print(f"Error creating default users: {e}")

    return app
