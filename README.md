# Minigotchi Dashboard

A sleek, interactive dashboard for the Pwnagotchi project, optimized for Raspberry Pi and repurposed Chromebooks.  
Built with Flask and Socket.IO, it provides real-time WiFi scanning, attack controls, detailed analytics, and a custom animated Pwnagotchi face UI.

---

## Features

- Real-time WiFi network scanning with signal strength, encryption, channel info  
- Deauthentication attack controls with target selection  
- Interactive dashboard with tabs: Networks, Attacks, Analytics, Settings  
- Custom animated Pwnagotchi face with expressions based on status  
- Modular, production-ready Flask backend with WebSocket communication  
- Compatible with Raspberry Pi and Linux laptops  

---

## Prerequisites

- Linux system (Raspberry Pi OS, Debian, Ubuntu, etc.)  
- WiFi adapter capable of monitor mode (e.g., Alfa AWUS036NHA)  
- Python 3.10+  
- `iwlist` and `aireplay-ng` tools installed (usually via `wireless-tools` and `aircrack-ng` packages)  
- Root or sudo privileges to perform WiFi monitoring and attacks  

---

## Installation

1. Clone this repository and navigate to the project directory:

   ```bash
   git clone https://github.com/yourusername/minigotchi-dashboard.git
   cd minigotchi-dashboard