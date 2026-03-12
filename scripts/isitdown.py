#!/usr/bin/env python3
import http.client
import socket
import ssl
import sys
import time

BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"

if len(sys.argv) < 2:
    print(f"{RED}Usage: python3 isitdown.py <hostname[:port]>{RESET}")
    sys.exit(1)

target = sys.argv[1]
cleaned = target.replace("http://", "").replace("https://", "").split("/")[0]

custom_port = None
if ":" in cleaned:
    parts = cleaned.rsplit(":", 1)
    hostname = parts[0]
    try:
        custom_port = int(parts[1])
    except ValueError:
        hostname = cleaned
else:
    hostname = cleaned

use_ssl = target.startswith("https://")

print(f"\n{BOLD}{CYAN}Website Status Checker{RESET}")
print(f"{BOLD}{'='*50}{RESET}")
print(f"{BOLD}Target:{RESET} {cleaned}")
print(f"{BOLD}Time:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

try:
    ip = socket.gethostbyname(hostname)
    print(f"{BOLD}IP Address:{RESET} {ip}")
except socket.gaierror:
    print(f"{RED}{BOLD}[DOWN]{RESET} Cannot resolve hostname: {hostname}")
    sys.exit(0)

if custom_port:
    if use_ssl:
        schemes = [("https", custom_port)]
    else:
        schemes = [("http", custom_port)]
else:
    schemes = [("https", 443), ("http", 80)]

for scheme, port in schemes:
    try:
        start = time.time()
        if scheme == "https":
            conn = http.client.HTTPSConnection(hostname, port, timeout=10,
                                                context=ssl._create_unverified_context())
        else:
            conn = http.client.HTTPConnection(hostname, port, timeout=10)
        conn.request("GET", "/", headers={"User-Agent": "Mozilla/5.0 IsItDown/1.0"})
        resp = conn.getresponse()
        elapsed = time.time() - start
        status = resp.status
        reason = resp.reason
        conn.close()

        print(f"{BOLD}Protocol:{RESET} {scheme.upper()}")
        print(f"{BOLD}Port:{RESET} {port}")
        print(f"{BOLD}Status:{RESET} {status} {reason}")
        print(f"{BOLD}Response Time:{RESET} {elapsed*1000:.0f}ms")

        if status < 400:
            print(f"\n{GREEN}{BOLD}[UP] ✓ Website is UP and responding{RESET}")
        elif status < 500:
            print(f"\n{YELLOW}{BOLD}[UP] ⚠ Website responds but returned {status}{RESET}")
        else:
            print(f"\n{RED}{BOLD}[DOWN] ✗ Server error: {status} {reason}{RESET}")
        print()
        sys.exit(0)

    except Exception as e:
        if scheme == schemes[-1][0] and port == schemes[-1][1]:
            print(f"\n{RED}{BOLD}[DOWN] ✗ Website is DOWN or unreachable{RESET}")
            print(f"{RED}Error: {e}{RESET}\n")
        continue

print(f"\n{RED}{BOLD}[DOWN] ✗ Website is DOWN or unreachable{RESET}\n")
