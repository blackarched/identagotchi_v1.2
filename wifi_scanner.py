# File: minigotchi/wifi_scanner.py
import argparse
import logging
import subprocess
import sys
import time

from typing import List, Set


def scan_wifi(interface: str, timeout: int = 5) -> List[dict]:
    """
    Perform a WiFi scan on the given interface.

    :param interface: Network interface to scan (e.g., wlan0).
    :param timeout: Scan duration in seconds.
    :return: List of unique access points with SSID, BSSID, and signal strength.
    """
    try:
        result = subprocess.run(
            ["sudo", "iwlist", interface, "scan"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout + 2,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logging.error("WiFi scan failed: %s", e.stderr.strip())
        return []
    except subprocess.TimeoutExpired:
        logging.warning("WiFi scan on %s timed out after %ds", interface, timeout)
        return []

    return _parse_scan_output(result.stdout)


def _parse_scan_output(output: str) -> List[dict]:
    """Parse `iwlist scan` output into structured data, removing duplicates."""
    seen: Set[str] = set()
    aps: List[dict] = []

    for line in output.splitlines():
        if "ESSID:" in line:
            ssid = line.split(':', 1)[1].strip().strip('"')
        elif "Address:" in line:
            bssid = line.split()[1]
        elif "Signal level=" in line:
            level = int(line.split('=')[2].split(' ')[0])
            if bssid not in seen:
                seen.add(bssid)
                aps.append({"ssid": ssid, "bssid": bssid, "signal": level})
    return aps


def main():
    parser = argparse.ArgumentParser(description="WiFi Scanner for Minigotchi")
    parser.add_argument("-i", "--interface", default="wlan0", help="Wireless interface to scan")
    parser.add_argument(
        "-t", "--timeout", type=int, default=5, help="Scan timeout in seconds"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.info("Starting WiFi scan on interface %s", args.interface)
    while True:
        aps = scan_wifi(args.interface, args.timeout)
        if aps:
            for ap in aps:
                logging.info(
                    "Found AP: SSID=%s, BSSID=%s, Signal=%ddBm",
                    ap["ssid"], ap["bssid"], ap["signal"],
                )
        time.sleep(args.timeout)


if __name__ == "__main__":
    main()