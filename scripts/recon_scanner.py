#!/usr/bin/env python3
import argparse
import socket
import ssl
import sys
import time
import re
import http.client
from urllib.parse import urlparse

BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
DIM = "\033[2m"

def section(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def info(msg):
    print(f"{CYAN}{BOLD}[INFO]{RESET} {msg}")

def good(msg):
    print(f"{GREEN}{BOLD}[+]{RESET} {msg}")

def warn(msg):
    print(f"{YELLOW}{BOLD}[!]{RESET} {msg}")

def fail(msg):
    print(f"{RED}{BOLD}[-]{RESET} {msg}")

def fetch_url(url, timeout=10):
    try:
        parsed = urlparse(url)
        if parsed.scheme == "https":
            conn = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=timeout,
                                                context=ssl._create_unverified_context())
        else:
            conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=timeout)
        conn.request("GET", parsed.path or "/", headers={
            "User-Agent": "Mozilla/5.0 ReconScanner/1.0",
            "Accept": "text/html,application/xhtml+xml"
        })
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        body = resp.read(50000).decode("utf-8", errors="ignore")
        status = resp.status
        conn.close()
        return status, headers, body
    except Exception as e:
        return None, {}, str(e)

def dns_lookup(hostname):
    section("1. DNS & IP Resolution")
    try:
        ip = socket.gethostbyname(hostname)
        good(f"IP Address: {ip}")
    except socket.gaierror:
        fail(f"Could not resolve hostname: {hostname}")
        return

    try:
        reverse = socket.gethostbyaddr(ip)
        good(f"Reverse DNS: {reverse[0]}")
        if reverse[1]:
            good(f"Aliases: {', '.join(reverse[1])}")
    except Exception:
        warn("Reverse DNS lookup failed")

    try:
        addrs = socket.getaddrinfo(hostname, None)
        unique_ips = list(set(addr[4][0] for addr in addrs))
        if len(unique_ips) > 1:
            good(f"All IPs: {', '.join(unique_ips)}")
        for addr in addrs:
            if addr[0] == socket.AF_INET6:
                good(f"IPv6: {addr[4][0]}")
                break
    except Exception:
        pass

def whois_info(hostname):
    section("2. WHOIS Information")
    try:
        import subprocess
        import shutil
        if shutil.which("whois"):
            result = subprocess.run(["whois", hostname], capture_output=True, text=True, timeout=15)
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                important_fields = ["Domain Name", "Registrar", "Creation Date", "Updated Date",
                                     "Registry Expiry", "Name Server", "Registrant Organization",
                                     "Registrant Country", "DNSSEC"]
                for line in lines:
                    for field in important_fields:
                        if field.lower() in line.lower() and ":" in line:
                            good(line.strip())
                            break
            else:
                warn("WHOIS query returned no results")
        else:
            warn("whois command not available — skipping")
    except Exception as e:
        warn(f"WHOIS lookup error: {e}")

def http_headers_analysis(url, headers, status):
    section("3. HTTP Headers & Server Info")
    info(f"HTTP Status: {status}")

    server = headers.get("Server", headers.get("server", ""))
    if server:
        good(f"Server: {server}")
    else:
        warn("Server header hidden")

    powered = headers.get("X-Powered-By", headers.get("x-powered-by", ""))
    if powered:
        good(f"X-Powered-By: {powered}")

    security_headers = {
        "Strict-Transport-Security": "HSTS",
        "Content-Security-Policy": "CSP",
        "X-Frame-Options": "Clickjacking Protection",
        "X-Content-Type-Options": "MIME Sniffing Protection",
        "X-XSS-Protection": "XSS Filter",
        "Referrer-Policy": "Referrer Policy",
        "Permissions-Policy": "Permissions Policy",
    }

    print(f"\n{BOLD}  Security Headers:{RESET}")
    for header, desc in security_headers.items():
        val = headers.get(header, headers.get(header.lower(), ""))
        if val:
            good(f"  {desc}: {val[:80]}")
        else:
            fail(f"  {desc}: MISSING")

def detect_technologies(body, headers):
    section("4. Technology Detection")

    cms_signatures = {
        "WordPress": ["/wp-content/", "/wp-includes/", "wp-json", "wordpress"],
        "Joomla": ["/components/com_", "/media/jui/", "joomla"],
        "Drupal": ["drupal.js", "/sites/default/", "drupal"],
        "Magento": ["mage/", "/static/frontend/Magento", "magento"],
        "Shopify": ["cdn.shopify.com", "shopify"],
        "Wix": ["wixsite.com", "static.wixstatic.com"],
        "Squarespace": ["squarespace.com", "sqsp.com"],
        "Ghost": ["ghost.org", "ghost-"],
        "PrestaShop": ["prestashop", "/modules/ps_"],
    }

    frameworks = {
        "React": ["react", "_react", "reactDOM"],
        "Angular": ["ng-version", "angular"],
        "Vue.js": ["vue.js", "vue.min.js", "__vue__"],
        "jQuery": ["jquery", "jQuery"],
        "Bootstrap": ["bootstrap.min", "bootstrap.css"],
        "Tailwind CSS": ["tailwindcss", "tailwind"],
        "Next.js": ["__next", "_next/"],
        "Nuxt.js": ["__nuxt", "_nuxt/"],
        "Laravel": ["laravel", "csrf-token"],
        "Django": ["csrfmiddlewaretoken", "django"],
        "Flask": ["flask", "werkzeug"],
        "Express": ["express"],
        "ASP.NET": ["__VIEWSTATE", "asp.net", "aspnet"],
    }

    body_lower = body.lower()
    server = (headers.get("Server", "") + " " + headers.get("X-Powered-By", "")).lower()

    detected_cms = []
    for cms, sigs in cms_signatures.items():
        for sig in sigs:
            if sig.lower() in body_lower or sig.lower() in server:
                detected_cms.append(cms)
                break

    detected_fw = []
    for fw, sigs in frameworks.items():
        for sig in sigs:
            if sig.lower() in body_lower or sig.lower() in server:
                detected_fw.append(fw)
                break

    if detected_cms:
        for cms in detected_cms:
            good(f"CMS: {cms}")
    else:
        warn("No CMS detected")

    if detected_fw:
        for fw in detected_fw:
            good(f"Framework/Library: {fw}")
    else:
        warn("No frontend frameworks detected")

def check_robots_sitemap(base_url):
    section("5. Robots.txt & Sitemap")

    robots_url = base_url.rstrip("/") + "/robots.txt"
    status, _, body = fetch_url(robots_url)
    if status == 200 and ("user-agent" in body.lower() or "disallow" in body.lower()):
        good("robots.txt found:")
        lines = body.strip().split("\n")
        for line in lines[:20]:
            print(f"  {DIM}{line.strip()}{RESET}")
        if len(lines) > 20:
            info(f"  ... and {len(lines) - 20} more lines")
    else:
        warn("robots.txt not found or empty")

    sitemap_url = base_url.rstrip("/") + "/sitemap.xml"
    status, _, body = fetch_url(sitemap_url)
    if status == 200 and "url" in body.lower():
        url_count = body.lower().count("<url>") or body.lower().count("<loc>")
        good(f"sitemap.xml found ({url_count} URLs)")
    else:
        warn("sitemap.xml not found")

def check_common_files(base_url):
    section("6. Common Files & Paths")

    paths = [
        "/.git/HEAD", "/.env", "/.htaccess", "/wp-login.php",
        "/admin", "/login", "/administrator", "/phpmyadmin",
        "/.well-known/security.txt", "/crossdomain.xml",
        "/humans.txt", "/security.txt", "/.DS_Store",
        "/server-status", "/server-info",
    ]

    for path in paths:
        url = base_url.rstrip("/") + path
        try:
            status, _, _ = fetch_url(url, timeout=5)
            if status and status < 400:
                warn(f"Accessible ({status}): {path}")
            elif status == 403:
                info(f"Forbidden (403): {path}")
        except Exception:
            pass

def subdomain_check(hostname):
    section("7. Common Subdomain Check")

    common_subs = [
        "www", "mail", "ftp", "admin", "webmail", "smtp", "pop",
        "ns1", "ns2", "blog", "dev", "staging", "api", "cdn",
        "test", "portal", "vpn", "remote", "m", "mobile",
        "shop", "store", "app", "dashboard",
    ]

    base_domain = hostname
    parts = hostname.split(".")
    if len(parts) > 2:
        base_domain = ".".join(parts[-2:])

    found = []
    for sub in common_subs:
        fqdn = f"{sub}.{base_domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            found.append((fqdn, ip))
            good(f"{fqdn} → {ip}")
        except socket.gaierror:
            pass

    if not found:
        warn("No common subdomains resolved")
    else:
        info(f"Found {len(found)} subdomains")

def main():
    parser = argparse.ArgumentParser(description="Python Reconnaissance Scanner (RED HAWK alternative)")
    parser.add_argument("target", help="Target hostname (e.g., example.com)")
    parser.add_argument("--no-whois", action="store_true", help="Skip WHOIS lookup")
    parser.add_argument("--no-subdomains", action="store_true", help="Skip subdomain check")
    args = parser.parse_args()

    target = args.target.strip()
    if target.startswith("http://") or target.startswith("https://"):
        parsed = urlparse(target)
        hostname = parsed.hostname
        base_url = target.rstrip("/")
    else:
        hostname = target
        base_url = f"http://{target}"

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║         Python Recon Scanner v1.0                       ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}")
    print(f"\n{BOLD}Target:{RESET} {hostname}")
    print(f"{BOLD}URL:{RESET} {base_url}")
    print(f"{BOLD}Scan started:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}")

    dns_lookup(hostname)

    if not args.no_whois:
        whois_info(hostname)

    status, headers, body = fetch_url(base_url)
    if status:
        http_headers_analysis(base_url, headers, status)
        detect_technologies(body, headers)
    else:
        fail(f"Could not connect to {base_url}")

    check_robots_sitemap(base_url)
    check_common_files(base_url)

    if not args.no_subdomains:
        subdomain_check(hostname)

    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  Reconnaissance Complete{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}Scan finished:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()
