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
    import os, subprocess, sys
    main_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    subprocess.run([sys.executable, main_py], check=True)
else:
    print("Manually execute main.py and resolve any errors for your system.")
