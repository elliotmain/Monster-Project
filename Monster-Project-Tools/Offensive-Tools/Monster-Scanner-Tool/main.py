try:
    import sys
    import os
    from rich.console import Console
    import platform
    import subprocess
    import time
except ImportError:
    print("Error, run the installer and try again later.")
    sys.exit(1)

   ###################
  # PATH-IN-WINDOWS #
 ###################
if platform.system() == "Windows":
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
            system_path, _ = winreg.QueryValueEx(key, "Path")
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            user_path, _ = winreg.QueryValueEx(key, "Path")
        os.environ["PATH"] = system_path + os.pathsep + user_path
    except Exception:
        os.environ["PATH"] += os.pathsep + r"C:\Program Files (x86)\Nmap"

   ############
  # PRE-DEFS #
 ############
console = Console()

   ###########
  # BANNERS #
 ###########
console.print(r"""[purple]
   _____              _________                                         
  /     \            /   _____/ ____ _____    ____   ____   ___________ 
 /  \ /  \   ______  \_____  \_/ ___\\__  \  /    \ /    \_/ __ \_  __ \
/    Y    \ /_____/  /        \  \___ / __ \|   |  \   |  \  ___/|  | \/
\____|__  /         /_______  /\___  >____  /___|  /___|  /\___  >__|   
        \/                  \/     \/     \/     \/     \/     \/       
[/purple]""")

   ##########
  # TARGET #
 ##########
# TRATAMENT WITH TRY (STARTING)
try:
    target = console.input("[purple]Enter a target:\n YOU/> [/purple]")

   ###############
  # SELECT TYPE #
 ###############
    console.print("""[purple]
Select a type of SCAN:
 1-Simple -  (Fast, but less efficient)
 2-Full   -  (It takes a while!)
    [/purple]""")
    
    try:
        scan_type = int(console.input("[purple] YOU/> [/purple]"))
    except ValueError:
        console.print("[red]Error: Invalid Value![/red]")
        sys.exit(1)

    # STARTING PRINT FOR WARNING
    console.print("[red]Starting...[/red]")
    
   ##############
  # PROCESSING #
 ##############
    if scan_type == 1:
        subprocess.run(["nmap", "-sT", target], check=True)
    elif scan_type == 2:
        subprocess.run(["nmap", "-p-", target], check=True)
    else:
        console.print("[red]Invalid option![/red]")

   #####################################
  # TRATAMENT WITH TRY (CONTINUATION) #
 #####################################
except KeyboardInterrupt:
    console.print("\n[red]KeyboardInterrupt detected, exiting...[/red]")
    sys.exit(2)
except Exception as e:
    console.print(f"[red]Error: {e}[/red]")
    sys.exit(2)
