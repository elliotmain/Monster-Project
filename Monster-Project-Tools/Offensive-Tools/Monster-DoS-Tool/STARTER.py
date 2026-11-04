import os
import sys
import subprocess
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(base_dir, "main.py")

    if not os.path.isfile(main_py):
        print(f"[!] main.py not found at: {main_py}")
        print("[!] Run the installer(s) and try again later.")
        return 1
    try:
        result = subprocess.run([sys.executable, main_py])
        return result.returncode
    except KeyboardInterrupt:
        print("\n[!] Canceled by user.")
        return 0
    except FileNotFoundError:
        print(f"[!] Python executable not found: {sys.executable}")
        return 1
    except Exception as e:
        print(f"[!] Failed to launch main.py: {e}")
        return 1
if __name__ == "__main__":
    sys.exit(main())