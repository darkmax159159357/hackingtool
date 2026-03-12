#!/usr/bin/env python3
import argparse
import json
import sys
import os
import time
import re
import urllib.parse
from html.parser import HTMLParser

CHROMIUM_PATH = None
for p in [
    os.path.expanduser("~/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"),
    "/home/runner/workspace/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome",
]:
    if os.path.exists(p):
        CHROMIUM_PATH = p
        break


class FormExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current_form = None
        self.links = set()
        self.scripts = []
        self.meta = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "form":
            self.current_form = {"action": attrs_dict.get("action", ""), "method": attrs_dict.get("method", "GET").upper(), "inputs": []}
        elif tag == "input" and self.current_form is not None:
            self.current_form["inputs"].append(attrs_dict)
        elif tag == "a" and "href" in attrs_dict:
            self.links.add(attrs_dict["href"])
        elif tag == "script":
            src = attrs_dict.get("src", "")
            if src:
                self.scripts.append(src)
        elif tag == "meta":
            self.meta.append(attrs_dict)
        elif tag == "title":
            self._in_title = True
        elif tag == "textarea" and self.current_form is not None:
            self.current_form["inputs"].append({**attrs_dict, "type": "textarea"})

    def handle_endtag(self, tag):
        if tag == "form" and self.current_form is not None:
            self.forms.append(self.current_form)
            self.current_form = None
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def print_header():
    print("""
\033[1;35m╔══════════════════════════════════════════════════════════╗
║   CloudFlare Bypass Scanner v2.0                        ║
║   Powered by Playwright + Chromium                      ║
║   For authorized security testing only                  ║
╚══════════════════════════════════════════════════════════╝\033[0m""")


def bypass_and_scan(target_url, crawl_depth=2, timeout=30):
    from playwright.sync_api import sync_playwright

    print_header()
    print(f"\n\033[1;36m[TARGET]\033[0m {target_url}")
    print(f"\033[1;36m[INFO]\033[0m Crawl depth: {crawl_depth}")
    print(f"\033[1;36m[INFO]\033[0m Initializing Chromium browser with CloudFlare bypass...\n")
    sys.stdout.flush()

    with sync_playwright() as p:
        launch_args = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                     "--disable-blink-features=AutomationControlled",
                     "--window-size=1920,1080"],
        }
        if CHROMIUM_PATH:
            launch_args["executable_path"] = CHROMIUM_PATH

        browser = p.chromium.launch(**launch_args)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
        )
        page = context.new_page()

        try:
            print("=" * 60)
            print("  \033[1;33m1. CloudFlare Bypass & Initial Access\033[0m")
            print("=" * 60)
            sys.stdout.flush()

            page.goto(target_url, wait_until="domcontentloaded", timeout=timeout * 1000)
            time.sleep(3)

            cf_bypassed = False
            for attempt in range(5):
                title = page.title() or ""
                html = page.content() or ""
                if "just a moment" in title.lower() or "checking your browser" in html.lower() or "cf-browser-verification" in html.lower():
                    print(f"  \033[1;33m[INFO]\033[0m CloudFlare challenge detected (attempt {attempt+1}/5), waiting...")
                    sys.stdout.flush()
                    time.sleep(5)
                    page.reload(wait_until="domcontentloaded")
                    time.sleep(3)
                else:
                    cf_bypassed = True
                    break

            if cf_bypassed:
                print("  \033[1;32m[PASS]\033[0m CloudFlare bypass successful!")
                print(f"  \033[1;36m[INFO]\033[0m Page title: {page.title()}")
            else:
                print("  \033[1;33m[WARN]\033[0m CloudFlare challenge may still be active")
                print(f"  \033[1;36m[INFO]\033[0m Page title: {page.title()}")

            cookies = context.cookies()
            cf_cookies = [c for c in cookies if "cf" in c.get("name", "").lower() or "cloudflare" in c.get("name", "").lower()]
            if cf_cookies:
                print(f"  \033[1;32m[+]\033[0m CloudFlare cookies captured: {[c['name'] for c in cf_cookies]}")

            print(f"  \033[1;36m[INFO]\033[0m Total cookies: {len(cookies)}")
            print(f"  \033[1;36m[INFO]\033[0m Response URL: {page.url}")
            sys.stdout.flush()

            headers_info = page.evaluate("""() => ({
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                cookieEnabled: navigator.cookieEnabled,
                webdriver: navigator.webdriver
            })""")
            if headers_info:
                wd = headers_info.get("webdriver", "N/A")
                color = "\033[1;32m" if not wd else "\033[1;31m"
                print(f"  {color}[INFO]\033[0m WebDriver detected: {wd}")

            html_content = page.content()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m2. Page Analysis & Technology Detection\033[0m")
            print(f"{'='*60}")
            sys.stdout.flush()

            extractor = FormExtractor()
            try:
                extractor.feed(html_content)
            except:
                pass

            print(f"  \033[1;36m[INFO]\033[0m Page title: {extractor.title.strip()}")
            print(f"  \033[1;36m[INFO]\033[0m HTML size: {len(html_content):,} bytes")

            tech_signatures = {
                "React": ["react", "_reactRoot", "__NEXT_DATA__", "reactRoot"],
                "Next.js": ["__NEXT_DATA__", "_next/static", "next/dist"],
                "Vue.js": ["vue.js", "__vue__", "v-if=", "v-for="],
                "Angular": ["ng-version", "angular.js", "ng-app"],
                "jQuery": ["jquery", "jQuery"],
                "Bootstrap": ["bootstrap"],
                "Tailwind CSS": ["tailwindcss", "tailwind"],
                "WordPress": ["wp-content", "wp-includes"],
                "Laravel": ["laravel_session"],
                "Django": ["csrfmiddlewaretoken"],
                "PHP": [".php", "PHPSESSID"],
                "Magento": ["magento", "mage-", "Magento_"],
                "Shopify": ["shopify", "myshopify"],
                "Cloudflare": ["cloudflare", "cf-ray"],
            }

            detected_tech = []
            html_lower = html_content.lower()
            for tech, sigs in tech_signatures.items():
                for sig in sigs:
                    if sig.lower() in html_lower:
                        detected_tech.append(tech)
                        break

            if detected_tech:
                print(f"  \033[1;32m[+]\033[0m Technologies detected: \033[1;36m{', '.join(detected_tech)}\033[0m")

            js_libs = page.evaluate("""() => {
                var libs = [];
                if (window.jQuery) libs.push('jQuery ' + jQuery.fn.jquery);
                if (window.React) libs.push('React');
                if (window.__NEXT_DATA__) libs.push('Next.js');
                if (window.Vue) libs.push('Vue.js');
                if (window.angular) libs.push('Angular');
                if (window._ && window._.VERSION) libs.push('Lodash ' + _.VERSION);
                return libs;
            }""")
            if js_libs:
                print(f"  \033[1;32m[+]\033[0m JS libraries (runtime): \033[1;36m{', '.join(js_libs)}\033[0m")

            version_patterns = [
                (r'jquery[.-v]?([\d.]+)', 'jQuery'),
                (r'bootstrap[/.-v]?([\d.]+)', 'Bootstrap'),
            ]
            for pattern, lib_name in version_patterns:
                match = re.search(pattern, html_lower)
                if match:
                    print(f"  \033[1;32m[+]\033[0m {lib_name} version: \033[1;31m{match.group(1)}\033[0m")

            sys.stdout.flush()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m3. Security Headers Analysis\033[0m")
            print(f"{'='*60}")

            security_meta = {}
            for meta in extractor.meta:
                equiv = meta.get("http-equiv", "").lower()
                content = meta.get("content", "")
                if equiv:
                    security_meta[equiv] = content

            csp = page.evaluate("() => document.querySelector('meta[http-equiv=\"Content-Security-Policy\"]')?.content || ''")
            if csp:
                print(f"  \033[1;32m[+]\033[0m CSP (meta): {csp[:100]}...")
                security_meta["content-security-policy"] = csp

            important_headers = [
                ("X-Frame-Options", "Clickjacking protection"),
                ("X-Content-Type-Options", "MIME sniffing protection"),
                ("X-XSS-Protection", "XSS filter"),
                ("Strict-Transport-Security", "HSTS"),
                ("Content-Security-Policy", "CSP"),
                ("Referrer-Policy", "Referrer control"),
                ("Permissions-Policy", "Feature restrictions"),
            ]

            missing_headers = []
            for header, desc in important_headers:
                found = header.lower() in [k.lower() for k in security_meta]
                if found:
                    print(f"  \033[1;32m[PASS]\033[0m {header}: Present ({desc})")
                else:
                    print(f"  \033[1;31m[FAIL]\033[0m {header}: \033[1;31mMissing\033[0m ({desc})")
                    missing_headers.append(header)
            sys.stdout.flush()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m4. Form & Input Analysis\033[0m")
            print(f"{'='*60}")

            forms = extractor.forms
            if forms:
                print(f"  \033[1;32m[+]\033[0m Found {len(forms)} form(s)")
                for i, form in enumerate(forms):
                    action = form["action"] or "(same page)"
                    method = form["method"]
                    print(f"\n  \033[1;36mForm #{i+1}:\033[0m action={action}, method={method}")
                    for inp in form["inputs"]:
                        itype = inp.get("type", "text")
                        iname = inp.get("name", "(unnamed)")
                        ival = inp.get("value", "")
                        print(f"    → Input: name={iname}, type={itype}{f', value={ival}' if ival else ''}")
                        if itype == "hidden":
                            print(f"      \033[1;33m[!]\033[0m Hidden field: {iname}={ival[:50]}")
                        if itype == "password" and method == "GET":
                            print(f"      \033[1;31m[VULN]\033[0m Password sent via GET method!")

                csrf_found = any(
                    any("csrf" in inp.get("name", "").lower() or "token" in inp.get("name", "").lower()
                        for inp in form["inputs"])
                    for form in forms
                )
                if csrf_found:
                    print(f"\n  \033[1;32m[PASS]\033[0m CSRF tokens detected in forms")
                else:
                    print(f"\n  \033[1;31m[FAIL]\033[0m No CSRF tokens found - \033[1;31mpotential CSRF vulnerability!\033[0m")
            else:
                print("  \033[1;36m[INFO]\033[0m No forms found on this page")
            sys.stdout.flush()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m5. Link Discovery & Crawling\033[0m")
            print(f"{'='*60}")

            parsed = urllib.parse.urlparse(target_url)
            base_domain = parsed.netloc

            internal_links = set()
            external_links = set()
            param_links = set()

            all_links = set(extractor.links)
            try:
                elements = page.query_selector_all("a[href]")
                for el in elements:
                    href = el.get_attribute("href")
                    if href:
                        all_links.add(href)
            except:
                pass

            for link in all_links:
                if not link or link.startswith("#") or link.startswith("javascript:") or link.startswith("mailto:"):
                    continue
                full_url = urllib.parse.urljoin(target_url, link)
                parsed_link = urllib.parse.urlparse(full_url)
                if parsed_link.netloc == base_domain or not parsed_link.netloc:
                    internal_links.add(full_url)
                    if parsed_link.query:
                        param_links.add(full_url)
                else:
                    external_links.add(full_url)

            print(f"  \033[1;32m[+]\033[0m Internal links: {len(internal_links)}")
            print(f"  \033[1;32m[+]\033[0m External links: {len(external_links)}")
            print(f"  \033[1;32m[+]\033[0m Links with parameters: {len(param_links)}")

            if param_links:
                print(f"\n  \033[1;33m[!]\033[0m Parameterized URLs (potential injection points):")
                for pl in sorted(param_links)[:20]:
                    print(f"    \033[1;31m→\033[0m {pl}")
            sys.stdout.flush()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m6. JavaScript & API Endpoint Discovery\033[0m")
            print(f"{'='*60}")

            script_srcs = list(extractor.scripts)
            api_found = set()

            api_patterns = re.findall(r'["\'](/api/[^"\']+)["\']', html_content)
            api_patterns += re.findall(r'["\'](https?://[^"\']*api[^"\']*)["\']', html_content)
            fetch_patterns = re.findall(r'fetch\(["\']([^"\']+)["\']', html_content)

            api_found.update(api_patterns)
            api_found.update(fetch_patterns)

            internal_scripts = [s for s in script_srcs if base_domain in urllib.parse.urljoin(target_url, s)]
            print(f"  \033[1;36m[INFO]\033[0m Internal scripts: {len(internal_scripts)}")
            for s in internal_scripts[:10]:
                print(f"    → {urllib.parse.urljoin(target_url, s)[:120]}")

            if api_found:
                print(f"\n  \033[1;32m[+]\033[0m API/Fetch endpoints discovered:")
                for ep in sorted(api_found)[:15]:
                    print(f"    \033[1;31m→\033[0m {ep}")
            sys.stdout.flush()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m7. Deep Crawl (Depth {crawl_depth})\033[0m")
            print(f"{'='*60}")

            visited = {target_url, target_url.rstrip("/"), target_url.rstrip("/") + "/"}
            to_visit = sorted(internal_links - visited)[:30]
            all_forms_found = list(forms)
            all_params_found = set(param_links)

            for depth in range(1, crawl_depth + 1):
                if not to_visit:
                    break
                print(f"\n  \033[1;36m[Depth {depth}]\033[0m Visiting {len(to_visit)} pages...")
                sys.stdout.flush()
                next_level = set()

                for url in to_visit[:15]:
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=10000)
                        time.sleep(1)

                        title = page.title() or ""
                        if "just a moment" in title.lower():
                            time.sleep(5)

                        page_html = page.content() or ""
                        print(f"    → {url[:80]} [{len(page_html):,} bytes]")
                        sys.stdout.flush()

                        try:
                            sub_extractor = FormExtractor()
                            sub_extractor.feed(page_html)

                            if sub_extractor.forms:
                                for f in sub_extractor.forms:
                                    f["page_url"] = url
                                    all_forms_found.append(f)
                                print(f"      \033[1;32m[+]\033[0m {len(sub_extractor.forms)} form(s) found")

                            for link in sub_extractor.links:
                                if not link or link.startswith("#"):
                                    continue
                                full = urllib.parse.urljoin(url, link)
                                lp = urllib.parse.urlparse(full)
                                if lp.netloc == base_domain and full not in visited:
                                    next_level.add(full)
                                    if lp.query:
                                        all_params_found.add(full)
                        except:
                            pass

                        visited.add(url)
                    except Exception as e:
                        print(f"    \033[1;31m[ERR]\033[0m {url[:60]}: {str(e)[:50]}")
                        visited.add(url)

                to_visit = sorted(next_level - visited)[:20]

            print(f"\n  \033[1;36m[INFO]\033[0m Total pages crawled: {len(visited)}")
            print(f"  \033[1;36m[INFO]\033[0m Total forms found: {len(all_forms_found)}")
            print(f"  \033[1;36m[INFO]\033[0m Total parameterized URLs: {len(all_params_found)}")
            sys.stdout.flush()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m8. XSS Quick Test on Parameters\033[0m")
            print(f"{'='*60}")

            xss_payloads = [
                '<script>alert(1)</script>',
                '"><img src=x onerror=alert(1)>',
                "'-alert(1)-'",
                '<svg onload=alert(1)>',
            ]

            xss_tested = 0
            xss_found = []

            for param_url in sorted(all_params_found)[:10]:
                parsed_p = urllib.parse.urlparse(param_url)
                params = urllib.parse.parse_qs(parsed_p.query)

                for param_name in params:
                    for payload in xss_payloads[:2]:
                        test_params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}
                        test_params[param_name] = payload
                        test_url = f"{parsed_p.scheme}://{parsed_p.netloc}{parsed_p.path}?{urllib.parse.urlencode(test_params)}"

                        try:
                            page.goto(test_url, wait_until="domcontentloaded", timeout=8000)
                            time.sleep(1)
                            resp_html = page.content() or ""

                            if payload in resp_html:
                                xss_found.append({"url": param_url, "param": param_name, "payload": payload})
                                print(f"  \033[1;31m[VULN] XSS REFLECTED:\033[0m {param_name} at {param_url[:60]}")
                                print(f"         Payload: {payload}")
                            xss_tested += 1
                        except:
                            pass

                        if xss_tested > 20:
                            break
                    if xss_tested > 20:
                        break
                if xss_tested > 20:
                    break

            if not xss_found:
                print(f"  \033[1;36m[INFO]\033[0m Tested {xss_tested} parameter/payload combinations")
                print(f"  \033[1;32m[PASS]\033[0m No reflected XSS found in quick test")
            else:
                print(f"\n  \033[1;31m[!!] {len(xss_found)} XSS vulnerabilities confirmed!\033[0m")
            sys.stdout.flush()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m9. Cookie Security Analysis\033[0m")
            print(f"{'='*60}")

            cookies = context.cookies()
            for cookie in cookies:
                name = cookie.get("name", "")
                secure = cookie.get("secure", False)
                httponly = cookie.get("httpOnly", False)
                samesite = cookie.get("sameSite", "None")

                issues = []
                if not secure:
                    issues.append("Missing Secure flag")
                if not httponly and ("session" in name.lower() or "token" in name.lower() or "auth" in name.lower()):
                    issues.append("Missing HttpOnly (sensitive cookie!)")
                if samesite == "None":
                    issues.append("SameSite=None (CSRF risk)")

                if issues:
                    print(f"  \033[1;33m[WARN]\033[0m Cookie '{name}': {', '.join(issues)}")
                else:
                    print(f"  \033[1;32m[PASS]\033[0m Cookie '{name}': Properly secured")
            sys.stdout.flush()

            print(f"\n{'='*60}")
            print(f"  \033[1;33m10. Information Disclosure & Path Probing\033[0m")
            print(f"{'='*60}")

            disclosure_paths = [
                "/.env", "/robots.txt", "/sitemap.xml", "/.git/config",
                "/wp-config.php.bak", "/server-status", "/server-info",
                "/crossdomain.xml", "/phpinfo.php",
                "/api/v1", "/api/v2", "/graphql", "/.well-known/security.txt",
                "/admin", "/login", "/register", "/debug", "/wp-admin",
                "/api", "/swagger", "/docs", "/.htpasswd",
            ]

            accessible_paths = []
            for path in disclosure_paths:
                try:
                    test_url = f"{parsed.scheme}://{parsed.netloc}{path}"
                    resp = page.goto(test_url, wait_until="domcontentloaded", timeout=8000)
                    resp_html = page.content() or ""
                    title = page.title() or ""
                    status = resp.status if resp else 0

                    if status == 200 and len(resp_html) > 200 and "not found" not in title.lower() and "404" not in title:
                        accessible_paths.append({"path": path, "size": len(resp_html), "title": title.strip()[:50], "status": status})
                        print(f"  \033[1;32m[FOUND]\033[0m {path} ({len(resp_html):,} bytes, HTTP {status}) - {title.strip()[:50]}")
                    elif status in [301, 302, 403]:
                        print(f"  \033[1;36m[{status}]\033[0m {path}")
                except:
                    pass
                sys.stdout.flush()

            if not accessible_paths:
                print("  \033[1;32m[PASS]\033[0m No sensitive paths directly accessible")

            print(f"\n{'='*60}")
            print(f"  \033[1;35m  VULNERABILITY ASSESSMENT SUMMARY\033[0m")
            print(f"{'='*60}")

            vuln_count = 0
            high_vulns = []
            medium_vulns = []
            low_vulns = []

            if not cf_bypassed:
                print(f"  \033[1;33m[INFO]\033[0m CloudFlare challenge was NOT bypassed - results may be limited")
            else:
                print(f"  \033[1;32m[PASS]\033[0m CloudFlare successfully bypassed")

            if xss_found:
                vuln_count += len(xss_found)
                for v in xss_found:
                    high_vulns.append(f"XSS in '{v['param']}' at {v['url'][:60]}")

            forms_without_csrf = [f for f in all_forms_found if not any("csrf" in i.get("name", "").lower() or "token" in i.get("name", "").lower() for i in f["inputs"])]
            if forms_without_csrf:
                vuln_count += 1
                high_vulns.append(f"CSRF: {len(forms_without_csrf)} form(s) without CSRF tokens")

            if missing_headers:
                vuln_count += 1
                medium_vulns.append(f"Missing security headers: {', '.join(missing_headers)}")

            cookie_issues_list = [c for c in cookies if not c.get("secure") or (not c.get("httpOnly") and any(k in c.get("name", "").lower() for k in ["session", "token", "auth"]))]
            if cookie_issues_list:
                vuln_count += 1
                medium_vulns.append(f"{len(cookie_issues_list)} cookie(s) with security issues")

            sensitive_paths = [p for p in accessible_paths if p["path"] in ["/.env", "/.git/config", "/wp-config.php.bak", "/phpinfo.php", "/debug", "/.htpasswd"]]
            if sensitive_paths:
                vuln_count += len(sensitive_paths)
                for s in sensitive_paths:
                    high_vulns.append(f"Sensitive file accessible: {s['path']}")

            if high_vulns:
                print(f"\n  \033[1;31m[CRITICAL/HIGH] Vulnerabilities:\033[0m")
                for v in high_vulns:
                    print(f"    \033[1;31m•\033[0m {v}")

            if medium_vulns:
                print(f"\n  \033[1;33m[MEDIUM] Issues:\033[0m")
                for v in medium_vulns:
                    print(f"    \033[1;33m•\033[0m {v}")

            if all_params_found:
                low_vulns.append(f"{len(all_params_found)} parameterized URLs (manual testing recommended)")
            if low_vulns:
                print(f"\n  \033[1;36m[LOW/INFO]:\033[0m")
                for v in low_vulns:
                    print(f"    \033[1;36m•\033[0m {v}")

            print(f"\n  \033[1;36mStats:\033[0m {len(visited)} pages crawled, {len(all_forms_found)} forms, {len(all_params_found)} params, {xss_tested} XSS tests")
            print(f"  \033[1;36mVulnerability categories:\033[0m {vuln_count}")

            if vuln_count == 0:
                print(f"  \033[1;32mOverall: No critical vulnerabilities detected\033[0m")
            elif len(high_vulns) > 0:
                print(f"  \033[1;31mOverall: HIGH RISK - Critical issues found, immediate remediation needed\033[0m")
            elif len(medium_vulns) > 0:
                print(f"  \033[1;33mOverall: MEDIUM RISK - Security improvements recommended\033[0m")
            else:
                print(f"  \033[1;32mOverall: LOW RISK - Minor improvements recommended\033[0m")

            print(f"\n{'='*60}")
            sys.stdout.flush()

        except Exception as e:
            print(f"\n\033[1;31m[ERROR]\033[0m {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="CloudFlare Bypass Scanner using Playwright + Chromium")
    parser.add_argument("--target", "-t", required=True, help="Target URL")
    parser.add_argument("--depth", "-d", type=int, default=2, help="Crawl depth (default: 2)")
    parser.add_argument("--timeout", type=int, default=30, help="Page load timeout in seconds (default: 30)")
    args = parser.parse_args()

    target = args.target
    if not target.startswith("http"):
        target = f"https://{target}"

    bypass_and_scan(target, crawl_depth=args.depth, timeout=args.timeout)


if __name__ == "__main__":
    main()
