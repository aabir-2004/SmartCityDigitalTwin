import os
from flask import Flask
from flask_socketio import SocketIO

# Global Socket.IO instance attached to the eventlet/werkzeug WSGI
socketio = SocketIO(cors_allowed_origins="*")

def create_app() -> Flask:
    """Factory method to construct the Flask application module."""
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=static_dir)
    
    from app.database import initialize_database
    try:
        initialize_database()
    except Exception as e:
        app.logger.warning(f"Deferred database provisioning: {e}")

    # Initialize SocketIO onto the application instance
    socketio.init_app(app)

    # Register modular REST components
    from app.api.endpoints import api_bp
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        return app.send_static_file(filename)

    # Start the continuous Time-Evolving Simulation Engine as a background task
    from app.engine import run_simulation_loop
    socketio.start_background_task(run_simulation_loop, socketio)

    return app
