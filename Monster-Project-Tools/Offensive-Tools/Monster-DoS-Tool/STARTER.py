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
    subprocess.run("wsl -u root python3 main.py")
elif system in ["Linux", "Darwin"]:
    import main
else:
    print("Manually execute main.py and resolve any errors for your system.")
