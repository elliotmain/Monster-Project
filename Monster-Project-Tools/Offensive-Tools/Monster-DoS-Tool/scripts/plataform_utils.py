# scripts/platform_utils.py
import os
import shutil
import subprocess
import sys


def find_hping3():
    found = shutil.which("hping3")
    if found:
        return found

    candidates = [
        # Linux
        "/usr/sbin/hping3",
        "/usr/bin/hping3",
        "/sbin/hping3",
        "/usr/local/sbin/hping3",
        "/usr/local/bin/hping3",
        # macOS (Apple Silicon + Intel via Homebrew)
        "/opt/homebrew/sbin/hping3",
        "/opt/homebrew/bin/hping3",
        "/usr/local/sbin/hping3",
        "/usr/local/bin/hping3",
    ]
    for path in candidates:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path

    print("[!] hping3 not found.")
    print("[!] Install it with your package manager:")
    print("    Debian/Ubuntu : sudo apt install hping3")
    print("    Arch          : sudo pacman -S hping3")
    print("    Fedora/RHEL   : sudo dnf install hping3")
    print("    Gentoo        : sudo emerge --ask net-analyzer/hping")
    print("    Slackware     : build via SlackBuilds (SBo: hping3)")
    print("    macOS         : brew install hping3")
    sys.exit(1)


def apply_kernel_tunings():
    # Raise FD limit on the current Python process (portable: Linux + macOS).
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        target = min(65535, hard)
        if soft < target:
            resource.setrlimit(resource.RLIMIT_NOFILE, (target, hard))
    except Exception:
        pass

    # Per-OS sysctl tunings.
    if sys.platform.startswith("linux"):
        cmds = [
            "sysctl -w net.ipv4.ip_local_port_range='1024 65535'",
            "sysctl -w net.ipv4.tcp_tw_reuse=1",
        ]
    elif sys.platform == "darwin":
        cmds = [
            "sysctl -w net.inet.ip.portrange.first=1024",
            "sysctl -w net.inet.ip.portrange.last=65535",
        ]
    else:
        cmds = []

    for cmd in cmds:
        try:
            subprocess.run(
                cmd,
                shell=True, check=False,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass


def get_history_file():
    """Return a path inside the invoking user's home even when run with sudo."""
    base = None
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        try:
            import pwd
            base = pwd.getpwnam(sudo_user).pw_dir
        except Exception:
            base = None
    if not base:
        base = os.path.expanduser("~")
    return os.path.join(base, ".monster_dos_history")