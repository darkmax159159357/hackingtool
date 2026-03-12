#!/usr/bin/env python3
import argparse
import socket
import ssl
import sys
import time
import re
import http.client
import concurrent.futures
from urllib.parse import urlparse, urljoin

BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
DIM = "\033[2m"

COMMON_DIRS = [
    "/admin", "/login", "/dashboard", "/api", "/wp-admin", "/wp-login.php",
    "/administrator", "/phpmyadmin", "/cpanel", "/webmail",
    "/console", "/manager", "/portal", "/config", "/setup",
    "/install", "/backup", "/test", "/dev", "/staging",
    "/old", "/new", "/tmp", "/temp", "/uploads", "/upload",
    "/images", "/img", "/css", "/js", "/static", "/assets",
    "/media", "/files", "/docs", "/documentation", "/doc",
    "/help", "/support", "/status", "/health", "/info",
    "/server-status", "/server-info", "/.env", "/.git",
    "/.git/HEAD", "/.gitignore", "/.htaccess", "/.htpasswd",
    "/robots.txt", "/sitemap.xml", "/crossdomain.xml",
    "/favicon.ico", "/humans.txt", "/security.txt",
    "/.well-known/security.txt", "/wp-content", "/wp-includes",
    "/xmlrpc.php", "/wp-json", "/feed", "/rss",
    "/cgi-bin", "/bin", "/scripts", "/include", "/includes",
    "/lib", "/library", "/vendor", "/node_modules",
    "/app", "/application", "/src", "/source",
    "/database", "/db", "/sql", "/data",
    "/log", "/logs", "/error", "/errors",
    "/debug", "/trace", "/monitoring",
    "/api/v1", "/api/v2", "/rest", "/graphql",
    "/swagger", "/api-docs", "/openapi",
    "/user", "/users", "/account", "/accounts", "/profile",
    "/register", "/signup", "/signin", "/logout",
    "/reset", "/forgot", "/password",
    "/search", "/query", "/find",
    "/download", "/export", "/import",
    "/panel", "/control", "/manage",
    "/secret", "/private", "/internal", "/hidden",
]

COMMON_FILES = [
    "/index.html", "/index.php", "/index.asp", "/default.html",
    "/web.config", "/config.php", "/config.yml", "/config.json",
    "/package.json", "/composer.json", "/Gemfile",
    "/requirements.txt", "/Dockerfile", "/docker-compose.yml",
    "/.env.example", "/.env.backup", "/.env.old",
    "/backup.sql", "/dump.sql", "/database.sql",
    "/error_log", "/access_log", "/debug.log",
    "/readme.html", "/readme.txt", "/README.md",
    "/license.txt", "/changelog.txt",
    "/phpinfo.php", "/info.php", "/test.php",
    "/adminer.php", "/.DS_Store", "/Thumbs.db",
]

def fetch(host, port, path, use_ssl, timeout=5):
    try:
        if use_ssl:
            conn = http.client.HTTPSConnection(host, port, timeout=timeout,
                                                context=ssl._create_unverified_context())
        else:
            conn = http.client.HTTPConnection(host, port, timeout=timeout)
        conn.request("GET", path, headers={
            "User-Agent": "Mozilla/5.0 WebScanner/1.0",
            "Accept": "*/*",
        })
        resp = conn.getresponse()
        resp.read()
        status = resp.status
        headers = dict(resp.getheaders())
        conn.close()
        return path, status, headers
    except Exception:
        return path, None, {}

def main():
    parser = argparse.ArgumentParser(description="Python Web Scanner (Skipfish/Dirb alternative)")
    parser.add_argument("target_url", help="Target URL (e.g., http://example.com)")
    parser.add_argument("--threads", type=int, default=20, help="Number of threads")
    parser.add_argument("--timeout", type=float, default=5, help="Timeout per request")
    parser.add_argument("--dirs-only", action="store_true", help="Only scan directories")
    parser.add_argument("--files-only", action="store_true", help="Only scan files")
    args = parser.parse_args()

    parsed = urlparse(args.target_url)
    host = parsed.hostname
    port = parsed.port
    use_ssl = parsed.scheme == "https"
    if not port:
        port = 443 if use_ssl else 80

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║         Python Web Scanner v1.0                         ║{RESET}")
    print(f"{BOLD}{CYAN}║    Directory & File Discovery (Skipfish/Dirb alt)       ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}")
    print(f"\n{BOLD}Target:{RESET} {args.target_url}")
    print(f"{BOLD}Host:{RESET} {host}:{port}")
    print(f"{BOLD}SSL:{RESET} {'Yes' if use_ssl else 'No'}")
    print(f"{BOLD}Scan started:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}")

    paths = []
    if args.files_only:
        paths = COMMON_FILES
    elif args.dirs_only:
        paths = COMMON_DIRS
    else:
        paths = COMMON_DIRS + COMMON_FILES

    print(f"{BOLD}Paths to scan:{RESET} {len(paths)}")
    print(f"{BOLD}Threads:{RESET} {args.threads}\n")

    results = {"2xx": [], "3xx": [], "4xx_interesting": [], "5xx": []}
    scanned = 0
    total = len(paths)

    print(f"{BOLD}{'PATH':<45}{'STATUS':<10}{'NOTE'}{RESET}")
    print(f"{DIM}{'─'*75}{RESET}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(fetch, host, port, path, use_ssl, args.timeout): path for path in paths}
        for future in concurrent.futures.as_completed(futures):
            path, status, headers = future.result()
            scanned += 1

            if status is None:
                continue

            if 200 <= status < 300:
                note = ""
                content_type = headers.get("Content-Type", headers.get("content-type", ""))
                if content_type:
                    note = content_type.split(";")[0]
                results["2xx"].append((path, status, note))
                print(f"{GREEN}{path:<45}{status:<10}{DIM}{note}{RESET}")
            elif 300 <= status < 400:
                location = headers.get("Location", headers.get("location", ""))
                results["3xx"].append((path, status, location))
                print(f"{YELLOW}{path:<45}{status:<10}{DIM}→ {location}{RESET}")
            elif status == 403:
                results["4xx_interesting"].append((path, status, "Forbidden"))
                print(f"{RED}{path:<45}{status:<10}{DIM}Forbidden{RESET}")
            elif status >= 500:
                results["5xx"].append((path, status, "Server Error"))
                print(f"{RED}{BOLD}{path:<45}{status:<10}{DIM}Server Error{RESET}")

    print(f"\n{DIM}{'─'*75}{RESET}")

    print(f"\n{BOLD}{CYAN}═══ SCAN SUMMARY ═══{RESET}\n")
    print(f"  {BOLD}Total paths scanned:{RESET} {total}")
    print(f"  {GREEN}{BOLD}Accessible (2xx):{RESET}   {len(results['2xx'])}")
    print(f"  {YELLOW}{BOLD}Redirects (3xx):{RESET}    {len(results['3xx'])}")
    print(f"  {RED}{BOLD}Forbidden (403):{RESET}    {len(results['4xx_interesting'])}")
    print(f"  {RED}{BOLD}Server Errors:{RESET}      {len(results['5xx'])}")

    if results["2xx"]:
        print(f"\n{BOLD}{GREEN}Accessible Paths:{RESET}")
        for path, status, note in sorted(results["2xx"]):
            print(f"  {GREEN}✓{RESET} {path} ({status}) {DIM}{note}{RESET}")

    if results["4xx_interesting"]:
        print(f"\n{BOLD}{YELLOW}Forbidden but Existing:{RESET}")
        for path, status, note in sorted(results["4xx_interesting"]):
            print(f"  {YELLOW}⚠{RESET} {path} ({status})")

    if results["5xx"]:
        print(f"\n{BOLD}{RED}Server Errors:{RESET}")
        for path, status, note in sorted(results["5xx"]):
            print(f"  {RED}✗{RESET} {path} ({status})")

    print(f"\n{BOLD}Scan finished:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()
