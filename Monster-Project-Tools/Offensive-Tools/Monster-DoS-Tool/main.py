# Minimum import
import sys

   ###########
  # Imports #
 ###########
try:
    import os
    import socket
    import subprocess
    import time
    import ctypes
    import atexit
    from rich.console import Console
except ImportError as e:
    print(f"[-] Error, start the installer and after start again! Error: {e}")
    sys.exit(1)

# readline is optional (native on Linux/macOS, pyreadline3 on Windows)
try:
    import readline
except ImportError:
    try:
        import pyreadline3 as readline
    except ImportError:
        readline = None

   ##########################################
  # Check if it is running with privileges #
 ##########################################
def is_admin():
    if sys.platform.startswith("win"):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False

if not is_admin():
    print("[!] This tool requires Administrator/root privileges to use raw sockets.")
    print("[!] On Linux/macOS: sudo python STARTER.sh")
    print("[!] On Windows: right-click the terminal and select 'Run as administrator'.")
    sys.exit(1)

   ######################################
  # Pre-definitions and Configurations #
 ######################################
console = Console()
whatmodenext = None
host = None
port = None
type = None
timeout = 2

# Color palette (purple / violet / dark violet / red / green)
C_PRIMARY = "bright_magenta"
C_ACCENT  = "violet"
C_DARK    = "dark_violet"
C_ERROR   = "bright_red"
C_SUCCESS = "bright_green"
C_INFO    = "bright_yellow"

LOGO = r"""[bold bright_magenta]
   _____            ________          _________
  /     \           \______ \   ____ /   _____/
 /  \ /  \   ______  |    |  \ /  _ \\_____  \
/    Y    \ /_____/  |    `   (  <_> )        \
\____|__  /         /_______  /\____/_______  /
        \/                  \/              \/
[/bold bright_magenta]"""

   ###############
  # Help Result #
 ###############
HELP_RESULT = f"""[{C_PRIMARY}]
The help command says:
 Commands:
  clear    - Clears the screen;
  help     - Shows the available commands and subcommands;
  set      - Define attack definitions (Contains subcommands);
  start    - Start the attack (alias: play);
  exit     - Exit the tool (alias: quit).

 Subcommands of 'set':
  host!<ip>     - Target IP (IPv4 only);              (CRITICAL!)
  port!<port>   - Port the server is running on;      (CRITICAL!)
  type!<proto>  - Define the attack protocol.

 Types of protocols:
  http, https, tcp, syn, udp, icmp, dns
[/{C_PRIMARY}]"""

   ##################
  # Readline setup #
 ##################
def setup_readline():
    """Enable tab completion + persistent history (if readline is available)."""
    if readline is None:
        return

    from scripts.platform_utils import get_history_file

    commands = ["clear", "help", "set", "start", "play", "exit", "quit"]
    subcommands = ["host!", "port!", "type!"]

    def completer(text, state):
        buf = readline.get_line_buffer()
        if " " in buf:
            parts = buf.split()
            if parts and parts[0] == "set":
                options = [s for s in subcommands if s.startswith(text)]
            else:
                options = []
        else:
            options = [c for c in commands if c.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    try:
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
        histfile = get_history_file()
        try:
            readline.read_history_file(histfile)
        except (FileNotFoundError, OSError):
            pass
        atexit.register(readline.write_history_file, histfile)
    except Exception:
        pass

   ################
  # Helper funcs #
 ################
def clear_screen():
    console.clear()

def validate_target(h, t, p):
    """Return (host, port) or (None, None) on error."""
    if not h:
        console.print(f"[{C_ERROR}]Error: host must be set![/{C_ERROR}]")
        return None, None
    if not t:
        console.print(f"[{C_ERROR}]Error: type must be set![/{C_ERROR}]")
        return None, None
    t = t.lower()
    if t == "dns":
        try:
            p = int(p) if p else 53
        except (ValueError, TypeError):
            p = 53
    else:
        if not p:
            console.print(f"[{C_ERROR}]Error: port must be set for {t}![/{C_ERROR}]")
            return None, None
        try:
            p = int(p)
        except (ValueError, TypeError):
            console.print(f"[{C_ERROR}]Error: invalid port![/{C_ERROR}]")
            return None, None
    return h, p

def check_connectivity(h, p, t):
    """TCP pre-check only for TCP-based attacks. Warns but proceeds on failure."""
    if t.lower() not in ("http", "https", "tcp", "syn"):
        console.print(f"[{C_INFO}][*] Skipping TCP check for {t.upper()} attack.[/{C_INFO}]")
        return
    console.print(f"[{C_INFO}][*] Checking TCP connectivity to {h}:{p}...[/{C_INFO}]")
    for attempt in range(1, 4):
        try:
            with socket.create_connection((h, p), timeout=timeout):
                console.print(f"[{C_SUCCESS}][+] Connected![/{C_SUCCESS}]")
                return
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            console.print(f"[{C_ERROR}]Attempt {attempt} failed: {e}[/{C_ERROR}]")
            if attempt < 3:
                time.sleep(1)
    console.print(f"[{C_INFO}][!] Target not responding. Proceeding anyway.[/{C_INFO}]")

def run_attack(h, p, t):
    try:
        from scripts.Mcaller import mcaller
        mcaller(h, p, t)
    except Exception as e:
        console.print(f"[{C_ERROR}]Error starting attack: {e}[/{C_ERROR}]")

   ##########################
  # Cli Mode or Shell Mode #
 ##########################
def cli_mode():
    console.print(LOGO)
    h = console.input(f"[{C_PRIMARY}]Enter an IP here: [/{C_PRIMARY}]").strip().lower()
    t = console.input(f"[{C_PRIMARY}]Enter Protocol here (HTTP, HTTPS, TCP, UDP, ICMP, DNS): [/{C_PRIMARY}]").strip().lower()
    p = None if t != "dns" else 53
    if t != "dns":
        p = console.input(f"[{C_PRIMARY}]Enter a Port here: [/{C_PRIMARY}]").strip()
    h, p = validate_target(h, t, p)
    if h is None:
        sys.exit(1)
    check_connectivity(h, p, t)
    run_attack(h, p, t)

def shell_mode():
    global host, port, type
    console.print(LOGO)
    while True:
        try:
            cmd = console.input(f"[bold {C_PRIMARY}]root@Monster-DoS-Tool/>[/bold {C_PRIMARY}] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print(f"[{C_ERROR}]Going out as requested.[/{C_ERROR}]")
            sys.exit(2)

        if not cmd:
            continue

        if cmd in ("clear", "c"):
            clear_screen()

        elif cmd == "help":
            console.print(HELP_RESULT)

        elif cmd in ("exit", "quit"):
            console.print(f"[{C_ACCENT}]Bye![/{C_ACCENT}]")
            sys.exit(0)

        elif cmd.startswith("set"):
            parts = cmd.split()[1:]
            if not parts:
                console.print(f"[{C_ERROR}]Usage: set host!<ip> port!<port> type!<type>[/{C_ERROR}]")
                continue
            for sc in parts:
                if "!" not in sc:
                    console.print(f"[{C_ERROR}]Invalid option: {sc}[/{C_ERROR}]")
                    continue
                value, option = sc.split("!", 1)
                if option == "host":
                    host = value
                    console.print(f"[{C_SUCCESS}]Host set: {host}[/{C_SUCCESS}]")
                elif option == "port":
                    try:
                        port = int(value)
                        console.print(f"[{C_SUCCESS}]Port set: {port}[/{C_SUCCESS}]")
                    except ValueError:
                        console.print(f"[{C_ERROR}]Invalid port: {value}[/{C_ERROR}]")
                elif option == "type":
                    type = value.lower()
                    console.print(f"[{C_SUCCESS}]Type set: {type}[/{C_SUCCESS}]")
                else:
                    console.print(f"[{C_ERROR}]Subcommand not found: {option}[/{C_ERROR}]")

        elif cmd in ("start", "play"):
            h, p = validate_target(host, type, port)
            if h is None:
                continue
            host, port = h, p
            check_connectivity(host, port, type)
            run_attack(host, port, type)

        else:
            console.print(f"[{C_ERROR}]Command not found! Type 'help' for commands.[/{C_ERROR}]")

if __name__ == "__main__":
    setup_readline()
    try:
        whatmodenext = console.input(
            f"[bold {C_PRIMARY}]You want a CLI Mode(c) or Shell Mode(s) of this tool:[/bold {C_PRIMARY}] "
        ).strip().lower()
        if whatmodenext in ("c", "cli"):
            cli_mode()
        elif whatmodenext in ("s", "shell"):
            shell_mode()
        else:
            console.print(f"[{C_ERROR}]Mode not available![/{C_ERROR}]")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print(f"[{C_ERROR}]Going out as requested.[/{C_ERROR}]")
        sys.exit(2)
    except Exception as e:
        console.print(f"[{C_ERROR}]Error: {e}[/{C_ERROR}]")
        sys.exit(1)