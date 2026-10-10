def mcaller(host, port, type):
    print(f"[DEBUG] mcaller called with {host}, {port}, {type}")
    try:
        # HTTP / HTTPS
        if type in ["1", "http", "HTTP", "https", "HTTPS"]:
            from scripts.HTTP.main import run as http_run
            http_run(host, port, type)
        # TCP / SYN
        elif type in ["2", "tcp", "TCP", "syn", "SYN"]:
            from scripts.TCP.main import run as tcp_run
            tcp_run(host, port)    
        # UDP
        elif type in ["udp", "UDP"]:
            from scripts.UDP.main import run as udp_run
            udp_run(host, port)
        # ICMP
        elif type in ["icmp", "ICMP"]:
            from scripts.ICMP.main import run as icmp_run
            icmp_run(host)
        # DNS
        elif type in ["dns", "DNS"]:
            from scripts.DNS.main import run as dns_run
            dns_run(host)
        else:
            print(f"[DEBUG] Unknow type of attack: {type}")
    except ImportError as e:
        print(f"Runner error: ImportError - {e}")
    except Exception as e:
        print(f"Runner error: {e}")
