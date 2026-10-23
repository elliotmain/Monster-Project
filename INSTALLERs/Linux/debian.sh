#!/bin/bash
set -e
sudo apt install hping python python-pip nmap -y
pip install rich scapy --break-system-packages
echo "Monster-Project: Installed with SUCCESS!"
