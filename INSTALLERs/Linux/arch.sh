#!/bin/bash
set -e
sudo pacman -Syu
sudo pacman -S --needed --noconfirm hping python python-pip nmap
pip install rich scapy --break-system-packages
echo "Monster-Project: Installed with SUCCESS!"
