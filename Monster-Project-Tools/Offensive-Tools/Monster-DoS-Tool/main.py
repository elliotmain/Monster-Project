try:
    from rich.console import Console
    import sys
    import os
    import socket
    import subprocess
    import readline
    import time
except ImportError:
    print("[-] Error, start the installer and after start again!")
    sys.exit(1)

   ##########################################
  # Check if it is running with privileges #
 ##########################################
if os.geteuid() != 0:
    print("[!] This tool requires root privileges to use raw sockets (hping3).")
    print("[!] Please run with: sudo python3 STARTER.py")
    print("Press ENTER to continue, else press CONTROL + C.")
    try:
        input()
    except:
        sys.exit(2)    

   ######################################
  # Pre-definitions and Configurations #
 ######################################
# Pre-definitions
console = Console()
whatmodenext = None
# Config's
host = None
port = None
type = None
timeout = 2 # Standard

   ###############
  # Help Result #
 ###############
helpresult = """[red]
The help command says:
 Commands:
  clear    - Clears the screen;
  help     - Shows the available commands and subcommands;
  set      - Define definições do ataque (Contains subcommands).

 Subcomands of 'set':
  127.0.0.1!host  (JUST ACCEPT IPv4!) - Target IP;                                  (CRITICAL!)
  443!port                            - Port on which the server/domain is running  (CRITICAL!)
  http!type / tcp!type and anothers   - Define the protocol of attack;

  Types of protocols (!type):
   HTTPS
   HTTP
   TCP
   UDP
   ICMP
   DNS
[/red]"""
   ##########################
  # Cli Mode or Shell Mode #
 ##########################
if __name__ == "__main__":
    try:
        try:
            whatmodenext = input("\033[33mYou want a CLI Mode(c) or Shell Mode(s) of this tool:\033[0m ")
        except KeyboardInterrupt:
            console.print("[red] Going out as requested.[/red]")
        except Exception as e:
            console.print(f"[red] Error: {e}[/red]")

        if whatmodenext == "c":
            console.print(r"""[bold purple]
   _____            ________          _________
  /     \           \______ \   ____ /   _____/
 /  \ /  \   ______  |    |  \ /  _ \\_____  \ 
/    Y    \ /_____/  |    `   (  <_> )        \
\____|__  /         /_______  /\____/_______  /
        \/                  \/              \/ 
            [/bold purple]""")

            host = console.input("[purple] Enter a IP here: [/purple]").strip().lower()
            type = console.input("[purple] Enter Protocol here(HTTP, HTTPS, TCP, UDP, ICMP, DNS): [/purple]").strip().lower()
            if type != "dns":
                port = console.input("[purple] Enter a Port here: [/purple]")
            else:
                pass
            if host is None or port is None:
                console.print("[red]Error: host and port must be set first![/red]")
                connected = False
                for attempt in range(1, 11):
                    try:
                        print(f" Attempt {attempt} of 10: connecting to {host}:{port}...")
                        with socket.create_connection((host, port), timeout=timeout):
                            print(" Connection successful! Proceeding...")
                            connected = True
                            break
                    except (socket.timeout, ConnectionRefusedError, OSError) as e:
                        print(f" Attempt {attempt} failed: {e}")
                        if attempt < 10:
                            print(" Waiting 1 second before trying again...")
                            time.sleep(1)
                if not connected:
                    print(" Failed after 10 attempts. The target is not responding. Canceling...")
                    sys.exit(1)
            else:
                print(f"[*] Skipping TCP connectivity check for {type} attack. Proceeding...")
            try:
                from scripts.Mcaller import mcaller
                mcaller(host, port, type)
            except Exception as e:
                console.print(f"[red]Error starting attack: {e}[/red]")
                sys.exit(1)
        # Shell Mode
        elif whatmodenext == "s":
            pass

        else:
            console.print("[red] Mode not available![/red]")
            sys.exit(1)

   #################
  # CMD and SHELL #
 #################
        try:
            console.print(r"""[bold purple]
   _____            ________          _________
  /     \           \______ \   ____ /   _____/
 /  \ /  \   ______  |    |  \ /  _ \\_____  \ 
/    Y    \ /_____/  |    `   (  <_> )        \
\____|__  /         /_______  /\____/_______  /
        \/                  \/              \/ 
            [/bold purple]""")
            while True:
                cmd = input("\033[35mroot@Monster-DoS-Tool/>\033[0m ")

                if cmd in ["clear", "c"]:
                    subprocess.run("clear", shell=True)

                elif cmd == "help":
                    console.print(helpresult)

                elif cmd.startswith("set"):
                    subcomandos = cmd.split()[1:]

                    for subcomando in subcomandos:
                        if "!" not in subcomando:
                            console.print(f"[red] Invalid option: {subcomandos}[/red]")
                            continue

                        value, option = subcomando.split("!", 1)
                        if option == "host":
                            host = value
                            console.print(f"[green] Host set: {host}[/green]")
                    
                        elif option == "port":
                            port = int(value) # Is a int!
                            console.print(f"[green] Port set: {port}[/green]")

                        elif option == "type":
                            type = value
                            console.print(f"[green] Type set: {type}[/green]")
    
                        else:
                            console.print("[red] Subcommand not founded![/red]")
                elif cmd in ["start", "play"]:
                    if host is None or port is None:
                        console.print("[red]Error: host and port must be set first![/red]")
                        connected = False
                        for attempt in range(1, 11):
                            try:
                                print(f" Attempt {attempt} of 10: connecting to {host}:{port}...")
                                with socket.create_connection((host, port), timeout=timeout):
                                    print(" Connection successful! Proceeding...")
                                    connected = True
                                    break
                            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                                print(f" Attempt {attempt} failed: {e}")
                                if attempt < 10:
                                    print(" Waiting 1 second before trying again...")
                                    time.sleep(1)
                        if not connected:
                            print(" Failed after 10 attempts. The target is not responding. Canceling...")
                            continue
                    else:
                        print(f"[*] Skipping TCP connectivity check for {type} attack. Proceeding...")
                try:
                    from scripts.Mcaller import mcaller
                    mcaller(host, port, type)
                except Exception as e:
                    console.print(f"[red]Error starting attack: {e}[/red]")
                    continue
            else:
                console.print("[red] Command Not Found![/red]")
        except KeyboardInterrupt:
            console.print("[red]\n Going out as requested.[/red]")
            sys.exit(2)
        except Exception as e:
            console.print(f"[red]\n Error: {e}[/red]")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("[red]\n Going out as requested.[/red]")
    except Exception as e:
        console.print(f"[red]\n Error: {e}[/red]")
        sys.exit(1)
