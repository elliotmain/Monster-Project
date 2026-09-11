  ###########
 # IMPORTS #
###########
try:
    import socket
    import time
    import subprocess
    import readline
    import sys
    from rich.console import Console
except ImportError:
    print("Error in imports, use the installer and try again.")

  ############
 # PRE-DEFS #
############
console = Console()

  #################
 # CLI and SHELL #
#################
try:
    console.print(r"""[bold purple]
   _____            ________  ________          _________
  /     \           \______ \ \______ \   ____ /   _____/
 /  \ /  \   ______  |    |  \ |    |  \ /  _ \\_____  \ 
/    Y    \ /_____/  |    `   \|    `   (  <_> )        \
\____|__  /         /_______  /_______  /\____/_______  /
        \/                  \/        \/              \/
    [/bold purple]""")
    host = console.input("[purple] Enter the IP: [/purple]")
    console.print("[yellow] Testing...[/yellow]")
    try:
        subprocess.run(f"ping {host}"
        console.print("[green] Test completed successfully.[/green]")
    port = console.input("[purple] Enter the PORT(53 for ICMP): [/purple]")
    console.print("""Supported Protocols:
 1-TCP (SYN)
 2-UDP
 3-ICMP
 4-DNS
    """)
    type = console.input("[purple]Enter your option: [/purple]").strip().lower()
    if type in ["1", "tcp"]:
        type = "tcp"
    elif type in ["2", "udp"]:
        type = "udp"
    elif type in ["3", "icmp"]:
        type = "icmp"
    elif type in ["4", "dns"]:
        type = "dns"
    else:
        console.print("[red] Unidentified protocol.[/red]")
        sys.exit(1)



