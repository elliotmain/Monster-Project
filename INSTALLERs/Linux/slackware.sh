#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Run with ROOT: su -c './slackware.sh'"
    exit 1
fi

set -e
su -
cd /tmp
wget https://www.sbopkg.org/downloads/sbopkg-0.38.3-noarch-1_wsr.tgz
installpkg sbopkg-0.38.3-noarch-1_wsr.tgz
sbopkg -r
slackpkg update
slackpkg install python3 python-pip nmap -y
sbopkg -i hping3
pip install rich scapy --break-system-packages
echo "Monster-Project: Installed with SUCCESS!"
