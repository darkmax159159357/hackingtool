#!/usr/bin/env python3
import argparse
import socket
import ssl
import time
import sys
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

def tag_pass(msg):
    return f"{GREEN}{BOLD}[PASS]{RESET} {msg}"

def tag_warn(msg):
    return f"{YELLOW}{BOLD}[WARN]{RESET} {msg}"

def tag_fail(msg):
    return f"{RED}{BOLD}[FAIL]{RESET} {msg}"

def tag_info(msg):
    return f"{CYAN}{BOLD}[INFO]{RESET} {msg}"

def section(title):
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

def recommendation(text):
    print(f"  {DIM}→ Recommendation: {text}{RESET}")

def parse_target(target_str):
    if not re.match(r'^https?://', target_str):
        target_str = f"http://{target_str}"
    parsed = urlparse(target_str)
    hostname = parsed.hostname or ""
    scheme = parsed.scheme or "http"
    return hostname, scheme

def get_base_response(hostname, port, use_ssl):
    try:
        if use_ssl:
            conn = http.client.HTTPSConnection(hostname, port, timeout=10,
                                                context=ssl._create_unverified_context())
        else:
            conn = http.client.HTTPConnection(hostname, port, timeout=10)
        conn.request("GET", "/", headers={"User-Agent": "Mozilla/5.0 SlowlorisAnalyzer/1.0"})
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        status = resp.status
        conn.close()
        return status, headers
    except Exception as e:
        return None, {"_error": str(e)}


def check_header_timeout(hostname, port, use_ssl):
    section("1. HTTP Header Timeout Analysis")
    print(tag_info(f"Sending incomplete HTTP request to {hostname}:{port}..."))
    print(tag_info("Measuring how long the server keeps the connection open..."))

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(120)
        sock.connect((hostname, port))

        if use_ssl:
            ctx = ssl._create_unverified_context()
            sock = ctx.wrap_socket(sock, server_hostname=hostname)

        partial_request = f"GET / HTTP/1.1\r\nHost: {hostname}\r\n"
        sock.send(partial_request.encode())

        start = time.time()
        try:
            while True:
                data = sock.recv(1)
                if not data:
                    break
        except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError):
            pass
        elapsed = time.time() - start
        sock.close()

        if elapsed >= 90:
            print(tag_fail(f"Server kept incomplete connection open for {elapsed:.1f}s (very high)"))
            print(tag_fail("Highly vulnerable to Slowloris — server waits too long for complete headers"))
            recommendation("Set header timeout to 10-30 seconds. Apache: RequestReadTimeout header=20-40. Nginx: client_header_timeout 10s;")
            return "FAIL"
        elif elapsed >= 30:
            print(tag_warn(f"Server kept incomplete connection open for {elapsed:.1f}s (moderate)"))
            print(tag_warn("Moderately vulnerable — timeout is longer than recommended"))
            recommendation("Reduce header timeout to under 30 seconds. Consider: RequestReadTimeout header=10-20 (Apache) or client_header_timeout 10s (Nginx)")
            return "WARN"
        else:
            print(tag_pass(f"Server closed incomplete connection after {elapsed:.1f}s (good)"))
            print(tag_pass("Short timeout reduces Slowloris effectiveness"))
            return "PASS"

    except socket.timeout:
        print(tag_fail("Connection timed out after 120s — server never closed the incomplete request"))
        recommendation("Configure aggressive header timeouts. This server is highly vulnerable.")
        return "FAIL"
    except Exception as e:
        print(tag_warn(f"Could not complete timeout test: {e}"))
        return "UNKNOWN"


def check_connection_limits(hostname, port, use_ssl):
    section("2. Connection Limits Per IP")
    print(tag_info(f"Opening multiple concurrent connections to {hostname}:{port}..."))

    max_conns = 100
    successful = 0
    sockets = []

    for i in range(max_conns):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((hostname, port))
            if use_ssl:
                ctx = ssl._create_unverified_context()
                s = ctx.wrap_socket(s, server_hostname=hostname)
            partial = f"GET / HTTP/1.1\r\nHost: {hostname}\r\n"
            s.send(partial.encode())
            sockets.append(s)
            successful += 1
        except Exception:
            break

    for s in sockets:
        try:
            s.close()
        except Exception:
            pass

    if successful >= 90:
        print(tag_fail(f"Server accepted {successful}/{max_conns} concurrent connections from same IP"))
        print(tag_fail("No effective per-IP connection limit detected"))
        recommendation("Configure per-IP connection limits. Nginx: limit_conn_zone $binary_remote_addr zone=addr:10m; limit_conn addr 10; Apache: mod_limitipconn or iptables -A INPUT -p tcp --dport 80 -m connlimit --connlimit-above 20 -j DROP")
        return "FAIL"
    elif successful >= 30:
        print(tag_warn(f"Server accepted {successful}/{max_conns} connections before refusing"))
        print(tag_warn("Connection limit exists but may be too high"))
        recommendation("Consider lowering per-IP connection limit to 10-20 concurrent connections")
        return "WARN"
    else:
        print(tag_pass(f"Server limited connections to {successful} per IP (good)"))
        print(tag_pass("Effective connection throttling is in place"))
        return "PASS"


def check_rate_limiting(hostname, port, use_ssl):
    section("3. Request Rate Limiting")
    print(tag_info(f"Sending rapid sequential requests to detect rate limiting..."))

    rate_limited = False
    total_requests = 30
    blocked_at = None
    status_codes = []

    conn_errors = 0
    for i in range(total_requests):
        try:
            if use_ssl:
                conn = http.client.HTTPSConnection(hostname, port, timeout=5,
                                                    context=ssl._create_unverified_context())
            else:
                conn = http.client.HTTPConnection(hostname, port, timeout=5)
            conn.request("GET", "/", headers={"User-Agent": "Mozilla/5.0 SlowlorisAnalyzer/1.0"})
            resp = conn.getresponse()
            status_codes.append(resp.status)
            if resp.status == 429 or resp.status == 503:
                rate_limited = True
                blocked_at = i + 1
                conn.close()
                break
            conn.close()
        except Exception:
            conn_errors += 1
            blocked_at = i + 1
            if conn_errors >= 3:
                break

    if rate_limited:
        print(tag_pass(f"Rate limiting detected after {blocked_at} requests (HTTP {status_codes[-1]})"))
        if blocked_at and blocked_at <= 10:
            print(tag_pass("Aggressive rate limiting — good protection against Slowloris"))
        else:
            print(tag_warn("Rate limiting exists but threshold may be too high"))
            recommendation("Consider lowering rate limit threshold for better protection")
        return "PASS"
    elif conn_errors >= 3:
        print(tag_warn(f"Connection errors occurred after {blocked_at} requests"))
        print(tag_warn("Server may be blocking connections, but could also be a network issue"))
        recommendation("Verify if this is intentional rate limiting or a connectivity problem. Check server logs.")
        return "WARN"
    else:
        print(tag_fail(f"No rate limiting detected after {total_requests} rapid requests"))
        print(tag_fail("All responses returned status codes: {0}".format(list(set(status_codes)))))
        recommendation("Enable rate limiting. Nginx: limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s; limit_req zone=one burst=20; Apache: mod_ratelimit or mod_qos; Or use iptables: -A INPUT -p tcp --dport 80 -m state --state NEW -m limit --limit 50/minute --limit-burst 200 -j ACCEPT")
        return "FAIL"


def check_waf_detection(headers):
    section("4. Web Application Firewall (WAF) Detection")
    print(tag_info("Inspecting response headers for WAF signatures..."))

    waf_signatures = {
        "cloudflare": {"headers": ["cf-ray", "cf-cache-status", "cf-request-id"], "server": ["cloudflare"]},
        "aws_waf": {"headers": ["x-amzn-requestid", "x-amz-cf-id"], "server": ["awselb", "amazons3"]},
        "modsecurity": {"headers": ["x-mod-security", "mod_security"], "server": ["mod_security"]},
        "akamai": {"headers": ["x-akamai-transformed", "akamai-origin-hop"], "server": ["akamaighost"]},
        "sucuri": {"headers": ["x-sucuri-id", "x-sucuri-cache"], "server": ["sucuri"]},
        "imperva": {"headers": ["x-iinfo", "x-cdn"], "server": ["imperva", "incapsula"]},
        "f5_big_ip": {"headers": ["x-wa-info", "x-cnection"], "server": ["big-ip", "bigip"]},
        "barracuda": {"headers": ["barra_counter_session"], "server": ["barracuda"]},
        "fortiweb": {"headers": ["fortiwafsid"], "server": ["fortiweb"]},
        "citrix_netscaler": {"headers": ["cneonction", "nncoection"], "server": ["netscaler"]},
    }

    headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
    detected_wafs = []

    for waf_name, sigs in waf_signatures.items():
        for hdr in sigs["headers"]:
            if hdr.lower() in headers_lower:
                detected_wafs.append(waf_name)
                break
        server_val = headers_lower.get("server", "")
        for srv_sig in sigs["server"]:
            if srv_sig in server_val:
                if waf_name not in detected_wafs:
                    detected_wafs.append(waf_name)

    if detected_wafs:
        print(tag_pass(f"WAF detected: {', '.join(detected_wafs)}"))
        print(tag_pass("Web Application Firewall provides protection against Slowloris"))
        return "PASS"
    else:
        print(tag_fail("No WAF signatures detected in response headers"))
        print(tag_fail("Server appears to lack WAF protection"))
        recommendation("Deploy a WAF solution. Options: ModSecurity (open source), Cloudflare WAF, AWS WAF, Imperva, or Sucuri. ModSecurity with OWASP CRS provides Slowloris-specific rules (rule 900020).")
        return "FAIL"


def check_server_architecture(headers):
    section("5. Server Architecture Analysis")
    print(tag_info("Analyzing server software for thread-per-connection vulnerability..."))

    server = headers.get("Server", headers.get("server", ""))
    powered_by = headers.get("X-Powered-By", headers.get("x-powered-by", ""))

    vulnerable_servers = {
        "apache": "Apache HTTP Server uses thread/process-per-connection (prefork/worker MPM)",
        "iis": "Microsoft IIS uses thread-per-connection architecture",
        "tomcat": "Apache Tomcat uses thread-per-connection by default",
        "weblogic": "Oracle WebLogic uses thread-per-connection",
        "websphere": "IBM WebSphere uses thread-per-connection",
    }

    resilient_servers = {
        "nginx": "Nginx uses event-driven, non-blocking architecture",
        "openresty": "OpenResty (Nginx-based) uses event-driven architecture",
        "lighttpd": "Lighttpd uses event-driven architecture",
        "litespeed": "LiteSpeed uses event-driven architecture",
        "caddy": "Caddy uses Go's goroutine-based concurrency",
        "node": "Node.js uses event-driven, non-blocking I/O",
        "envoy": "Envoy proxy uses event-driven architecture",
        "haproxy": "HAProxy uses event-driven architecture",
        "gunicorn": "Gunicorn with async workers is event-driven",
        "uvicorn": "Uvicorn uses asyncio event loop",
    }

    server_lower = (server + " " + powered_by).lower()
    detected_type = None

    for name, desc in vulnerable_servers.items():
        if name in server_lower:
            detected_type = "vulnerable"
            print(tag_fail(f"Server: {server}"))
            print(tag_fail(f"{desc}"))
            print(tag_fail("Thread-per-connection servers are highly vulnerable to Slowloris"))
            recommendation(f"Place a reverse proxy (Nginx or HAProxy) in front of {server.split('/')[0]}. Alternatively, switch to an event-driven server. For Apache: use event MPM instead of prefork: LoadModule mpm_event_module modules/mod_mpm_event.so")
            return "FAIL"

    for name, desc in resilient_servers.items():
        if name in server_lower:
            detected_type = "resilient"
            print(tag_pass(f"Server: {server}"))
            print(tag_pass(f"{desc}"))
            print(tag_pass("Event-driven servers are naturally resistant to Slowloris"))
            return "PASS"

    if not detected_type:
        if server:
            print(tag_warn(f"Server: {server} — architecture unknown"))
            print(tag_warn("Could not determine if server uses thread-per-connection"))
            recommendation("Verify server architecture. If thread-based, deploy Nginx/HAProxy as reverse proxy.")
        else:
            print(tag_warn("Server header is hidden or empty"))
            print(tag_info("Cannot determine server architecture from headers alone"))
            recommendation("Hidden server headers are good for security, but verify your architecture independently")
        return "WARN"


def check_reverse_proxy(headers):
    section("6. Reverse Proxy Detection")
    print(tag_info("Checking for reverse proxy / load balancer signatures..."))

    proxy_indicators = {
        "via": "Via header indicates a proxy is in the request chain",
        "x-forwarded-for": "X-Forwarded-For header suggests a reverse proxy",
        "x-forwarded-proto": "X-Forwarded-Proto indicates proxy protocol handling",
        "x-real-ip": "X-Real-IP header set by reverse proxy",
        "x-cache": "X-Cache header indicates caching proxy",
        "x-cache-hits": "X-Cache-Hits shows caching layer",
        "x-served-by": "X-Served-By reveals proxy/CDN node",
        "x-timer": "X-Timer header from Varnish or similar proxy",
        "x-varnish": "Varnish caching proxy detected",
        "x-proxy-cache": "Proxy cache header detected",
        "x-forwarded-host": "Forwarded host indicates proxy routing",
        "x-forwarded-server": "Forwarded server header detected",
    }

    headers_lower = {k.lower(): v for k, v in headers.items()}
    found_indicators = []

    for indicator, description in proxy_indicators.items():
        if indicator in headers_lower:
            found_indicators.append((indicator, headers_lower[indicator], description))

    if found_indicators:
        print(tag_pass("Reverse proxy / load balancer detected:"))
        for hdr, val, desc in found_indicators:
            print(f"  {GREEN}•{RESET} {hdr}: {val} — {desc}")
        print(tag_pass("Reverse proxy provides connection buffering and filtering"))
        recommendation("Ensure your proxy has Slowloris-specific settings: proxy_read_timeout, proxy_connect_timeout (Nginx) or timeout settings (HAProxy)")
        return "PASS"
    else:
        print(tag_fail("No reverse proxy indicators found in response headers"))
        print(tag_fail("Direct server exposure increases Slowloris vulnerability"))
        recommendation("Deploy Nginx or HAProxy as a reverse proxy. Config: proxy_pass http://backend; proxy_connect_timeout 5s; proxy_read_timeout 10s; proxy_send_timeout 10s; This buffers connections and protects the backend.")
        return "FAIL"


def check_cdn_detection(hostname, headers):
    section("7. CDN / Traffic Filtering Detection")
    print(tag_info(f"Checking DNS and headers for CDN/traffic filtering services..."))

    cdn_signatures = {
        "cloudflare": {"headers": ["cf-ray", "cf-cache-status"], "cname": ["cloudflare"]},
        "akamai": {"headers": ["x-akamai-transformed"], "cname": ["akamai", "edgekey", "edgesuite"]},
        "fastly": {"headers": ["x-fastly-request-id", "fastly-restarts"], "cname": ["fastly"]},
        "cloudfront": {"headers": ["x-amz-cf-id", "x-amz-cf-pop"], "cname": ["cloudfront.net"]},
        "maxcdn": {"headers": ["x-cdn"], "cname": ["maxcdn", "stackpath"]},
        "incapsula": {"headers": ["x-iinfo"], "cname": ["incapdns"]},
        "sucuri": {"headers": ["x-sucuri-id"], "cname": ["sucuri"]},
        "azure_cdn": {"headers": ["x-ms-ref"], "cname": ["azureedge.net", "msecnd.net"]},
        "google_cdn": {"headers": ["x-goog-meta"], "cname": ["googlevideo", "googleusercontent"]},
        "keycdn": {"headers": ["x-pull"], "cname": ["kxcdn.com"]},
    }

    headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
    detected_cdns = []

    for cdn_name, sigs in cdn_signatures.items():
        for hdr in sigs.get("headers", []):
            if hdr.lower() in headers_lower:
                detected_cdns.append(cdn_name)
                break

    cname_records = []
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        try:
            reverse = socket.gethostbyaddr(addr_info[0][4][0])
            cname_records = [reverse[0]]
        except Exception:
            pass
    except Exception:
        pass

    try:
        import shutil
        if shutil.which("dig"):
            import subprocess
            result = subprocess.run(["dig", "+short", "CNAME", hostname], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    if line not in cname_records:
                        cname_records.append(line)
    except Exception:
        pass

    for cdn_name, sigs in cdn_signatures.items():
        for cname in cname_records:
            for pattern in sigs.get("cname", []):
                if pattern in cname.lower():
                    if cdn_name not in detected_cdns:
                        detected_cdns.append(cdn_name)

    if detected_cdns:
        print(tag_pass(f"CDN/traffic filtering detected: {', '.join(detected_cdns)}"))
        print(tag_pass("CDN provides DDoS mitigation and connection management"))
        if cname_records:
            print(tag_info(f"DNS CNAME records: {', '.join(cname_records)}"))
        return "PASS"
    else:
        print(tag_fail("No CDN or traffic filtering service detected"))
        print(tag_fail("Server appears to be directly exposed to the internet"))
        recommendation("Deploy a CDN or DDoS protection service. Options: Cloudflare (free tier available), AWS CloudFront + Shield, Akamai, Fastly, or Azure CDN. These services absorb Slowloris attacks at the edge before they reach your server.")
        return "FAIL"


def check_keepalive(headers):
    section("8. Keep-Alive Configuration")
    print(tag_info("Analyzing HTTP Keep-Alive settings..."))

    connection = headers.get("Connection", headers.get("connection", ""))
    keepalive = headers.get("Keep-Alive", headers.get("keep-alive", ""))

    if "close" in connection.lower():
        print(tag_pass("Connection: close — server closes connections after each request"))
        print(tag_pass("This limits Slowloris effectiveness but may impact performance"))
        return "PASS"

    if keepalive:
        print(tag_info(f"Keep-Alive header: {keepalive}"))
        timeout_match = re.search(r'timeout=(\d+)', keepalive)
        max_match = re.search(r'max=(\d+)', keepalive)

        timeout_val = int(timeout_match.group(1)) if timeout_match else None
        max_val = int(max_match.group(1)) if max_match else None

        if timeout_val and timeout_val > 120:
            print(tag_fail(f"Keep-Alive timeout: {timeout_val}s (excessive)"))
            print(tag_fail("Long keep-alive allows attackers to hold connections open"))
            recommendation(f"Reduce keep-alive timeout to 15-30 seconds. Current: {timeout_val}s. Apache: KeepAliveTimeout 15. Nginx: keepalive_timeout 15s;")
            return "FAIL"
        elif timeout_val and timeout_val > 30:
            print(tag_warn(f"Keep-Alive timeout: {timeout_val}s (could be lower)"))
            recommendation(f"Consider reducing keep-alive timeout to 15-30s. Current: {timeout_val}s")
            return "WARN"
        elif timeout_val:
            print(tag_pass(f"Keep-Alive timeout: {timeout_val}s (good)"))
        else:
            print(tag_warn("Keep-Alive timeout not explicitly set"))

        if max_val:
            if max_val > 1000:
                print(tag_warn(f"Keep-Alive max requests: {max_val} (very high)"))
                recommendation(f"Lower max requests per connection to 100-200. Current: {max_val}")
            else:
                print(tag_pass(f"Keep-Alive max requests: {max_val}"))

        if timeout_val and timeout_val <= 30:
            return "PASS"
        return "WARN"

    if "keep-alive" in connection.lower():
        print(tag_warn("Keep-Alive enabled but no timeout/max values specified"))
        print(tag_warn("Server uses default keep-alive settings which may be too permissive"))
        recommendation("Explicitly set keep-alive parameters. Apache: KeepAliveTimeout 15, MaxKeepAliveRequests 100. Nginx: keepalive_timeout 15s;")
        return "WARN"

    print(tag_warn("No explicit Keep-Alive configuration detected"))
    recommendation("Configure keep-alive explicitly with short timeouts (15-30s) and request limits (100-200)")
    return "WARN"


def print_summary(results):
    section("VULNERABILITY ASSESSMENT SUMMARY")

    total = len(results)
    passes = sum(1 for r in results.values() if r == "PASS")
    warns = sum(1 for r in results.values() if r == "WARN")
    fails = sum(1 for r in results.values() if r == "FAIL")
    unknowns = sum(1 for r in results.values() if r == "UNKNOWN")

    check_names = {
        "header_timeout": "HTTP Header Timeout",
        "connection_limits": "Connection Limits Per IP",
        "rate_limiting": "Request Rate Limiting",
        "waf": "Web Application Firewall",
        "architecture": "Server Architecture",
        "reverse_proxy": "Reverse Proxy Protection",
        "cdn": "CDN / Traffic Filtering",
        "keepalive": "Keep-Alive Configuration",
    }

    print(f"\n  {'Check':<30} {'Result':<10}")
    print(f"  {'-'*30} {'-'*10}")
    for key, name in check_names.items():
        result = results.get(key, "N/A")
        if result == "PASS":
            color = GREEN
        elif result == "WARN":
            color = YELLOW
        elif result == "FAIL":
            color = RED
        else:
            color = DIM
        print(f"  {name:<30} {color}{BOLD}{result}{RESET}")

    print(f"\n  {BOLD}Score: {passes} PASS / {warns} WARN / {fails} FAIL / {unknowns} UNKNOWN{RESET}")

    if fails == 0 and warns <= 2:
        print(f"\n  {GREEN}{BOLD}Overall: Server appears well-protected against Slowloris attacks{RESET}")
    elif fails <= 2:
        print(f"\n  {YELLOW}{BOLD}Overall: Server has some Slowloris vulnerabilities that should be addressed{RESET}")
    else:
        print(f"\n  {RED}{BOLD}Overall: Server is significantly vulnerable to Slowloris attacks{RESET}")
        print(f"  {RED}Immediate remediation is recommended{RESET}")

    print(f"\n{BOLD}Key Remediation Steps (prioritized):{RESET}")
    priority = 1
    if results.get("header_timeout") in ("FAIL", "WARN"):
        print(f"  {priority}. Set HTTP header timeout to 10-30 seconds")
        priority += 1
    if results.get("architecture") == "FAIL":
        print(f"  {priority}. Deploy event-driven reverse proxy (Nginx/HAProxy) in front of your server")
        priority += 1
    if results.get("connection_limits") in ("FAIL", "WARN"):
        print(f"  {priority}. Configure per-IP connection limits (10-20 max)")
        priority += 1
    if results.get("rate_limiting") == "FAIL":
        print(f"  {priority}. Enable request rate limiting (10-50 req/s per IP)")
        priority += 1
    if results.get("waf") == "FAIL":
        print(f"  {priority}. Deploy a Web Application Firewall (ModSecurity + OWASP CRS)")
        priority += 1
    if results.get("cdn") == "FAIL":
        print(f"  {priority}. Use a CDN/DDoS protection service (Cloudflare, AWS Shield)")
        priority += 1
    if results.get("keepalive") in ("FAIL", "WARN"):
        print(f"  {priority}. Tune keep-alive: timeout 15-30s, max 100-200 requests")
        priority += 1
    if results.get("reverse_proxy") == "FAIL" and results.get("architecture") != "FAIL":
        print(f"  {priority}. Add a reverse proxy for connection buffering and filtering")
        priority += 1

    if priority == 1:
        print(f"  {GREEN}No critical remediation needed — keep monitoring and updating configurations{RESET}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Slowloris Vulnerability Analyzer")
    parser.add_argument("--target", required=True, help="Target hostname or URL")
    parser.add_argument("--port", type=int, default=80, help="Target port (default: 80)")
    args = parser.parse_args()

    hostname, scheme = parse_target(args.target)
    port = args.port
    use_ssl = scheme == "https" or port == 443

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║    Slowloris Vulnerability Analyzer v1.0                 ║{RESET}")
    print(f"{BOLD}{CYAN}║    For authorized security testing only                  ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}")
    print(f"\n{BOLD}Target:{RESET} {hostname}:{port} (SSL: {'Yes' if use_ssl else 'No'})")

    try:
        ip = socket.gethostbyname(hostname)
        print(f"{BOLD}Resolved IP:{RESET} {ip}")
    except socket.gaierror:
        print(f"{RED}Error: Could not resolve hostname '{hostname}'{RESET}")
        sys.exit(1)

    print(tag_info("Fetching initial response from target..."))
    status, headers = get_base_response(hostname, port, use_ssl)

    if status is None:
        print(f"{RED}Error: Could not connect to {hostname}:{port} — {headers.get('_error', 'unknown error')}{RESET}")
        sys.exit(1)

    print(tag_info(f"Target responded with HTTP {status}"))
    server = headers.get("Server", headers.get("server", "not disclosed"))
    print(tag_info(f"Server: {server}"))

    sys.stdout.flush()
    results = {}

    results["header_timeout"] = check_header_timeout(hostname, port, use_ssl)
    sys.stdout.flush()

    results["connection_limits"] = check_connection_limits(hostname, port, use_ssl)
    sys.stdout.flush()

    results["rate_limiting"] = check_rate_limiting(hostname, port, use_ssl)
    sys.stdout.flush()

    results["waf"] = check_waf_detection(headers)
    sys.stdout.flush()

    results["architecture"] = check_server_architecture(headers)
    sys.stdout.flush()

    results["reverse_proxy"] = check_reverse_proxy(headers)
    sys.stdout.flush()

    results["cdn"] = check_cdn_detection(hostname, headers)
    sys.stdout.flush()

    results["keepalive"] = check_keepalive(headers)
    sys.stdout.flush()

    print_summary(results)


if __name__ == "__main__":
    main()
