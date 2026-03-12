#!/usr/bin/env python3
import socket
import sys

BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RED = "\033[91m"

if len(sys.argv) < 2:
    print(f"{RED}Usage: python3 host_to_ip.py <hostname>{RESET}")
    sys.exit(1)

hostname = sys.argv[1].replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]

print(f"\n{BOLD}{CYAN}Host to IP Resolution{RESET}")
print(f"{BOLD}{'='*40}{RESET}")
print(f"{BOLD}Hostname:{RESET} {hostname}")

try:
    ip = socket.gethostbyname(hostname)
    print(f"{GREEN}{BOLD}IP Address:{RESET} {ip}")
except socket.gaierror:
    print(f"{RED}{BOLD}Error:{RESET} Could not resolve hostname")
    sys.exit(1)

try:
    addrs = socket.getaddrinfo(hostname, None)
    unique_ips = list(set(addr[4][0] for addr in addrs))
    if len(unique_ips) > 1:
        print(f"{BOLD}All IPs:{RESET}")
        for a in unique_ips:
            print(f"  {GREEN}{a}{RESET}")
    for addr in addrs:
        if addr[0] == socket.AF_INET6:
            print(f"{BOLD}IPv6:{RESET} {GREEN}{addr[4][0]}{RESET}")
            break
except Exception:
    pass

try:
    reverse = socket.gethostbyaddr(ip)
    print(f"{BOLD}Reverse DNS:{RESET} {GREEN}{reverse[0]}{RESET}")
except Exception:
    pass

print()
