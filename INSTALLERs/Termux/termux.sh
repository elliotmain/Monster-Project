pkg update
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu
alias sudo=""
apt update
apt install hping3 python3 python3-pip nmap -y
pip install rich --break-system-packages
