import os
from app import create_app, socketio

flask_app = create_app()

if __name__ == '__main__':
    port_config = int(os.environ.get('PORT', 8080))
    # Using SocketIO wrapper to support WebSocket lifecycle
    socketio.run(flask_app, host='127.0.0.1', port=port_config, debug=True, use_reloader=False)
