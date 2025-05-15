<!-- File: run.py -->
```python
from flask import current_app
from flask_socketio import SocketIO
from minigotchi.gui import create_app

# Initialize Flask app and SocketIO
app = create_app('config.py')
socketio = SocketIO(app)

# Example: listen for deauth plugin logs and relay to clients
@socketio.on('plugin_event')
def handle_plugin_event(data):
    # Emitted by Pwnagotchi agent via RPC notifications
    method = data.get('method')
    payload = data.get('payload')
    if method == 'plugin.deauth.log':
        emit('deauth_log', payload, broadcast=True)
    elif method == 'plugin.swordfish.log':
        emit('brute_log', payload, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)