import sys
def mcaller(host, port, type):
    print(f"[DEBUG] mcaller called with {host}, {port}, {type}")
    suffix = "W" if sys.platform.startswith("win") else ""
    try:
        if type in ["1", "http", "HTTP", "https", "HTTPS"]:
            mod = __import__(f"scripts.HTTP.main{suffix}", fromlist=["run"])
            mod.run(host, port, type)
        elif type in ["2", "tcp", "TCP", "syn", "SYN"]:
            mod = __import__(f"scripts.TCP.main{suffix}", fromlist=["run"])
            mod.run(host, port)
        elif type in ["udp", "UDP"]:
            mod = __import__(f"scripts.UDP.main{suffix}", fromlist=["run"])
            mod.run(host, port)
        elif type in ["icmp", "ICMP"]:
            mod = __import__(f"scripts.ICMP.main{suffix}", fromlist=["run"])
            mod.run(host)
        elif type in ["dns", "DNS"]:
            mod = __import__(f"scripts.DNS.main{suffix}", fromlist=["run"])
            mod.run(host)
        else:
            print(f"[DEBUG] Unknown type of attack: {type}")
    except ImportError as e:
        print(f"Runner error: ImportError - {e}")
    except Exception as e:
        print(f"Runner error: {e}")