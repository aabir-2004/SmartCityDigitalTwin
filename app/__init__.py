import os
from flask import Flask

def create_app() -> Flask:
    """Factory method to construct the Flask application module."""
    # Configure the frontend path relative to this module
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=static_dir)
    
    from app.database import initialize_database
    try:
        initialize_database()
    except Exception as e:
        app.logger.warning(f"Deferred database provisioning: {e}")

    # Register modular components
    from app.api.endpoints import api_bp
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        return app.send_static_file(filename)

    return app
