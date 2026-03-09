"""Flask application factory."""
import os
from flask import Flask, send_from_directory

from app.config import config_by_name
from app.extensions import db, migrate, jwt, cors
from app.utils.errors import register_error_handlers


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    flask_app = Flask(__name__, static_folder=None)
    flask_app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    jwt.init_app(flask_app)
    cors.init_app(flask_app, resources={r"/api/*": {"origins": "*"}})

    # Register error handlers
    register_error_handlers(flask_app)

    # Register API blueprints
    from app.api.v1 import all_blueprints
    for bp in all_blueprints:
        flask_app.register_blueprint(bp)

    # Serve uploaded files in development
    upload_folder = flask_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    @flask_app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(upload_folder, filename)

    # Health check
    @flask_app.route('/api/v1/health')
    def health():
        return {'status': 'ok', 'version': '1.0.0'}

    # Create tables if using SQLite (for easy dev)
    with flask_app.app_context():
        from app import models  # noqa: F401 — ensure models are imported
        db.create_all()

    # ── Serve frontend static files ──────────────────────────
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    admin_dir = os.path.join(project_root, 'admin')
    frontend_dir = os.path.join(project_root, 'frontend')

    @flask_app.route('/admin/')
    @flask_app.route('/admin/<path:filename>')
    def serve_admin(filename='index.html'):
        return send_from_directory(admin_dir, filename)

    @flask_app.route('/')
    @flask_app.route('/<path:filename>')
    def serve_frontend(filename='index.html'):
        file_path = os.path.join(frontend_dir, filename)
        if os.path.isfile(file_path):
            return send_from_directory(frontend_dir, filename)
        # SPA catch-all: return index.html for unknown paths
        return send_from_directory(frontend_dir, 'index.html')

    return flask_app
