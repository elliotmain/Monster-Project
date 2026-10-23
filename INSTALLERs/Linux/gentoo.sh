#!/bin/bash
set -e
sudo emerge --sync dev-lang/python dev-python/pip net-analyzer/nmap net-analyzer/hping
pip install rich scapy --break-system-packages
echo "Monster-Project: Installed with SUCCESS!"
