#!/usr/bin/env python3
import argparse
import socket
import sys
import concurrent.futures
import time

BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
DIM = "\033[2m"

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPCbind", 135: "MSRPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    8888: "HTTP-Alt2", 27017: "MongoDB",
}

TOP_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
    993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379,
    8080, 8443, 8888, 27017,
]

def scan_port(host, port, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        if result == 0:
            try:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                sock.settimeout(2)
                banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            except Exception:
                banner = ""
            sock.close()
            return port, True, banner
        sock.close()
        return port, False, ""
    except Exception:
        return port, False, ""

def resolve_host(target):
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return None

def main():
    parser = argparse.ArgumentParser(description="Python Port Scanner (nmap alternative)")
    parser.add_argument("target", help="Target hostname or IP")
    parser.add_argument("--ports", "-p", default="top", help="Port range: 'top' (default), 'all' (1-1024), or '80,443,8080' or '1-100'")
    parser.add_argument("--timeout", "-t", type=float, default=1.5, help="Timeout per port in seconds")
    parser.add_argument("--threads", type=int, default=50, help="Number of threads")
    args = parser.parse_args()

    target = args.target
    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║           Python Port Scanner v1.0                      ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}")
    print(f"\n{BOLD}Target:{RESET} {target}")

    ip = resolve_host(target)
    if not ip:
        print(f"{RED}{BOLD}[ERROR]{RESET} Could not resolve hostname: {target}")
        sys.exit(1)

    print(f"{BOLD}IP Address:{RESET} {ip}")
    print(f"{BOLD}Scan started:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if args.ports == "top":
        ports = TOP_PORTS
    elif args.ports == "all":
        ports = list(range(1, 1025))
    elif "-" in args.ports:
        start, end = args.ports.split("-")
        ports = list(range(int(start), int(end) + 1))
    else:
        ports = [int(p.strip()) for p in args.ports.split(",")]

    print(f"{BOLD}Scanning:{RESET} {len(ports)} ports with {args.threads} threads\n")

    open_ports = []
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(scan_port, ip, port, args.timeout): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            port, is_open, banner = future.result()
            if is_open:
                service = COMMON_PORTS.get(port, "unknown")
                banner_info = f" | {banner[:60]}" if banner else ""
                open_ports.append((port, service, banner_info))

    elapsed = time.time() - start_time
    open_ports.sort(key=lambda x: x[0])

    print(f"{BOLD}{'PORT':<10}{'STATE':<10}{'SERVICE':<20}{'BANNER'}{RESET}")
    print(f"{DIM}{'─'*70}{RESET}")

    if open_ports:
        for port, service, banner in open_ports:
            print(f"{GREEN}{port}/tcp{RESET}{'':>4}{'open':<10}{service:<20}{DIM}{banner}{RESET}")
    else:
        print(f"{YELLOW}No open ports found in the scanned range.{RESET}")

    print(f"\n{DIM}{'─'*70}{RESET}")
    print(f"{BOLD}Scan complete:{RESET} {len(open_ports)} open port(s) found in {elapsed:.2f}s")
    print(f"{BOLD}Scan finished:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()
