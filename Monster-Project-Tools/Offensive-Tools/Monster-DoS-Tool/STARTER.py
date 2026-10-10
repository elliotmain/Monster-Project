try:
    import platform
    import time
    import subprocess
    import sys
except ImportError:
    print("Run the installer(s) and try again later.")
    sys.exit(1)

system = platform.system()
if system == "Windows":
    print("Warning: The windows support is bad, sorry for it.")
    print("Requires WSL with ubuntu installed, if you do not have it, errors will occur. (The installer might have installed this), Here is some help: on WSL with Ubuntu, you will need to install hping3, python3, python3-pip, and the Python3 libraries via pip. The commands are: `sudo apt update; sudo apt install hping3 python3 python3-pip; pip install rich asyncio readline --break-system-packages`. If any dependencies are missing, look for them in the open-source code.")
    time.sleep(1)
    subprocess.run("wsl python3 main.py", check=True)
elif system in ["Linux", "Darwin"]:
    import main
else:
    print("Manually execute main.py and resolve any errors for your system.")
