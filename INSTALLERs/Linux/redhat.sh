#!/bin/bash
set -e
sudo dnf upgrade --refresh -y
sudo dnf install hping python3 python3-pip nmap -y
pip install rich --break-system-packages
echo "Monster-Project: Installed with SUCCESS!"
