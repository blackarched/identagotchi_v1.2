<!-- File: minigotchi/services.py -->
```python
import logging
import socket
import json
from pathlib import Path

# Helper to communicate with Pwnagotchi agent via its UNIX socket
def pwnagotchi_rpc(method: str, params: dict = None, socket_path: str = '/run/pwnagotchi.sock') -> dict:
    params = params or {}
    request = {'method': method, 'params': params}
    sock_path = Path(socket_path)
    if not sock_path.exists():
        raise FileNotFoundError(f"Pwnagotchi socket not found: {socket_path}")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(socket_path)
        s.sendall(json.dumps(request).encode('utf-8'))
        data = s.recv(65536)
    return json.loads(data.decode('utf-8'))

# Core services
from .wifi_scanner import scan_wifi
from .deauth_attack import send_deauth
from .password_brute import brute_force


def scan_service(data):
    try:
        response = pwnagotchi_rpc('scan_networks')
        return response.get('result', [])
    except Exception as e:
        logging.error('Scan error: %s', e)
        return []


def deauth_service(data):
    try:
        params = {
            'bssid': data['bssid'],
            'count': int(data.get('count', 100)),
            'interval': float(data.get('interval', 0.1))
        }
        return pwnagotchi_rpc('plugin.deauth.start', params)
    except Exception as e:
        logging.error('Deauth error: %s', e)
        return {'status': 'error', 'message': str(e)}


def brute_service(data):
    try:
        params = {
            'ssid': data['ssid'],
            'bssid': data['bssid'],
            'wordlist': data['wordlist'],
            'delay': float(data.get('delay', 1.0))
        }
        return pwnagotchi_rpc('plugin.swordfish.start', params)
    except Exception as e:
        logging.error('Brute error: %s', e)
        return {'status': 'error', 'message': str(e)}


def list_interfaces_service():
    try:
        response = pwnagotchi_rpc('list_interfaces')
        return response.get('result', [])
    except Exception as e:
        logging.error('Interfaces error: %s', e)
        return []


def status_service():
    try:
        response = pwnagotchi_rpc('status')
        return response.get('result', {})
    except Exception as e:
        logging.error('Status error: %s', e)
        return {}