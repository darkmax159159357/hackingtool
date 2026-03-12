#!/usr/bin/env python3
"""
Session Monitor - Proof of Concept
Monitors a target site for exposed session data, cookies, and API endpoints.
Owner-authorized testing only.
"""
import argparse
import time
import json
import sys
import re

CHROME = "/home/runner/workspace/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"


def monitor_session(target_url, duration=120):
    from playwright.sync_api import sync_playwright

    print(f"""
\033[1;35m╔══════════════════════════════════════════════════════════╗
║   Session Monitor & Cookie Interceptor v1.0             ║
║   Proof of Concept - Owner Authorized Testing           ║
╚══════════════════════════════════════════════════════════╝\033[0m

\033[1;36m[TARGET]\033[0m {target_url}
\033[1;36m[MODE]\033[0m Passive monitoring - capturing all network requests & cookies
\033[1;36m[DURATION]\033[0m {duration} seconds
""")
    sys.stdout.flush()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        captured_data = {
            "cookies": [],
            "api_requests": [],
            "auth_tokens": [],
            "local_storage": {},
            "session_storage": {},
            "forms_data": [],
            "network_requests": [],
        }

        def on_request(request):
            url = request.url
            headers = request.headers
            method = request.method

            auth_header = headers.get("authorization", "")
            cookie_header = headers.get("cookie", "")

            if auth_header:
                captured_data["auth_tokens"].append({
                    "url": url[:100],
                    "token": auth_header[:80] + "..." if len(auth_header) > 80 else auth_header,
                    "method": method,
                })
                print(f"  \033[1;31m[AUTH TOKEN CAPTURED]\033[0m {method} {url[:80]}")
                print(f"    Authorization: {auth_header[:60]}...")
                sys.stdout.flush()

            if cookie_header and any(k in url for k in ["api", "login", "auth", "user", "account", "session", "payment", "subscribe"]):
                captured_data["api_requests"].append({
                    "url": url[:100],
                    "method": method,
                    "cookies": cookie_header[:100],
                })
                print(f"  \033[1;33m[API REQUEST]\033[0m {method} {url[:80]}")
                if cookie_header:
                    print(f"    Cookies: {cookie_header[:80]}...")
                sys.stdout.flush()

            if any(k in url.lower() for k in ["token", "auth", "session", "jwt", "bearer", "api_key"]):
                captured_data["network_requests"].append({
                    "url": url[:150],
                    "method": method,
                })
                print(f"  \033[1;31m[SENSITIVE URL]\033[0m {method} {url[:100]}")
                sys.stdout.flush()

        def on_response(response):
            url = response.url
            headers = response.headers

            set_cookie = headers.get("set-cookie", "")
            if set_cookie:
                print(f"  \033[1;33m[SET-COOKIE]\033[0m {url[:60]}")
                print(f"    {set_cookie[:100]}")
                sys.stdout.flush()

        page.on("request", on_request)
        page.on("response", on_response)

        print("=" * 60)
        print(f"  \033[1;33m1. Initial Page Load & Cookie Capture\033[0m")
        print("=" * 60)
        sys.stdout.flush()

        page.goto(target_url, wait_until="networkidle", timeout=30000)
        time.sleep(3)

        title = page.title()
        if "just a moment" in title.lower():
            print(f"  \033[1;33m[INFO]\033[0m CloudFlare challenge, waiting...")
            time.sleep(8)
            page.reload(wait_until="networkidle")
            time.sleep(3)

        print(f"  \033[1;32m[OK]\033[0m Page loaded: {page.title()}")
        sys.stdout.flush()

        cookies = context.cookies()
        print(f"\n  \033[1;36m[COOKIES]\033[0m {len(cookies)} cookies found:")
        for c in cookies:
            flags = []
            if c.get("secure"): flags.append("Secure")
            if c.get("httpOnly"): flags.append("HttpOnly")
            flags.append(f"SameSite={c.get('sameSite', 'N/A')}")
            print(f"    \033[1;32m•\033[0m {c['name']} = {c['value'][:40]}{'...' if len(c['value'])>40 else ''}")
            print(f"      Domain: {c.get('domain','')} | Flags: {', '.join(flags)}")
            captured_data["cookies"].append({
                "name": c["name"],
                "value": c["value"][:50],
                "domain": c.get("domain", ""),
                "httpOnly": c.get("httpOnly", False),
                "secure": c.get("secure", False),
                "sameSite": c.get("sameSite", ""),
            })
        sys.stdout.flush()

        print(f"\n{'='*60}")
        print(f"  \033[1;33m2. JavaScript Storage Extraction\033[0m")
        print(f"{'='*60}")

        try:
            local_storage = page.evaluate("""() => {
                let data = {};
                for (let i = 0; i < localStorage.length; i++) {
                    let key = localStorage.key(i);
                    data[key] = localStorage.getItem(key);
                }
                return data;
            }""")
            if local_storage:
                print(f"\n  \033[1;31m[localStorage]\033[0m {len(local_storage)} items found:")
                for key, val in local_storage.items():
                    val_str = str(val)[:80]
                    print(f"    \033[1;31m•\033[0m {key} = {val_str}{'...' if len(str(val))>80 else ''}")
                    if any(k in key.lower() for k in ["token", "auth", "session", "user", "jwt", "key"]):
                        print(f"      \033[1;31m>>> SENSITIVE DATA!\033[0m")
                captured_data["local_storage"] = {k: str(v)[:100] for k, v in local_storage.items()}
            else:
                print(f"  \033[1;36m[INFO]\033[0m localStorage is empty")
        except:
            print(f"  \033[1;36m[INFO]\033[0m Could not access localStorage")

        try:
            session_storage = page.evaluate("""() => {
                let data = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    let key = sessionStorage.key(i);
                    data[key] = sessionStorage.getItem(key);
                }
                return data;
            }""")
            if session_storage:
                print(f"\n  \033[1;31m[sessionStorage]\033[0m {len(session_storage)} items found:")
                for key, val in session_storage.items():
                    val_str = str(val)[:80]
                    print(f"    \033[1;31m•\033[0m {key} = {val_str}")
                captured_data["session_storage"] = {k: str(v)[:100] for k, v in session_storage.items()}
            else:
                print(f"  \033[1;36m[INFO]\033[0m sessionStorage is empty")
        except:
            print(f"  \033[1;36m[INFO]\033[0m Could not access sessionStorage")
        sys.stdout.flush()

        print(f"\n{'='*60}")
        print(f"  \033[1;33m3. Probing Authentication Endpoints\033[0m")
        print(f"{'='*60}")

        auth_endpoints = [
            "/api/auth/session",
            "/api/auth/me",
            "/api/user",
            "/api/user/profile",
            "/api/me",
            "/api/v1/user",
            "/api/account",
            "/api/auth/csrf",
            "/api/current-user",
            "/api/whoami",
            "/api/profile",
            "/user/settings",
            "/account",
            "/api/subscription",
            "/api/payments",
        ]

        from urllib.parse import urlparse
        parsed = urlparse(target_url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for endpoint in auth_endpoints:
            try:
                url = f"{base}{endpoint}"
                resp = page.goto(url, wait_until="domcontentloaded", timeout=8000)
                status = resp.status if resp else 0
                body = page.content()
                body_text = page.evaluate("() => document.body?.innerText || ''") or ""

                if status == 200 and len(body_text.strip()) > 5:
                    try:
                        data = json.loads(body_text.strip())
                        if data and isinstance(data, dict):
                            print(f"  \033[1;31m[FOUND API]\033[0m {endpoint} (HTTP {status})")
                            safe_keys = list(data.keys())[:10]
                            print(f"    Keys: {safe_keys}")
                            for k in ["email", "username", "name", "id", "role", "subscription", "plan"]:
                                if k in data:
                                    print(f"    \033[1;31m{k}: {str(data[k])[:60]}\033[0m")
                            sys.stdout.flush()
                    except:
                        if any(k in body_text.lower() for k in ["email", "username", "logged", "session", "token"]):
                            print(f"  \033[1;33m[INTERESTING]\033[0m {endpoint} (HTTP {status}, {len(body_text)} chars)")
                elif status == 401 or status == 403:
                    print(f"  \033[1;36m[{status}]\033[0m {endpoint} (auth required)")
                elif status == 200:
                    pass
            except:
                pass
        sys.stdout.flush()

        print(f"\n{'='*60}")
        print(f"  \033[1;33m4. Login/Register Form Analysis\033[0m")
        print(f"{'='*60}")

        for form_url in [f"{base}/login", f"{base}/register"]:
            try:
                page.goto(form_url, wait_until="domcontentloaded", timeout=10000)
                time.sleep(2)
                forms = page.query_selector_all("form")
                if forms:
                    print(f"\n  \033[1;36m[PAGE]\033[0m {form_url}")
                    for i, form in enumerate(forms):
                        action = form.get_attribute("action") or "(same page)"
                        method = form.get_attribute("method") or "POST"
                        print(f"    Form: action={action}, method={method}")
                        inputs = form.query_selector_all("input, select, textarea")
                        csrf = False
                        for inp in inputs:
                            name = inp.get_attribute("name") or ""
                            itype = inp.get_attribute("type") or "text"
                            if "csrf" in name.lower() or "token" in name.lower():
                                csrf = True
                            print(f"      → {itype}: {name}")
                        if not csrf:
                            print(f"    \033[1;31m[NO CSRF TOKEN]\033[0m This form can be forged!")
                        captured_data["forms_data"].append({
                            "url": form_url,
                            "action": action,
                            "method": method,
                            "has_csrf": csrf,
                        })
            except:
                pass
        sys.stdout.flush()

        print(f"\n{'='*60}")
        print(f"  \033[1;33m5. Next.js Data Exposure Check\033[0m")
        print(f"{'='*60}")

        page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
        time.sleep(3)

        next_data = page.evaluate("""() => {
            const el = document.getElementById('__NEXT_DATA__');
            if (el) return el.textContent;
            return null;
        }""")

        if next_data:
            try:
                nd = json.loads(next_data)
                print(f"  \033[1;31m[FOUND]\033[0m __NEXT_DATA__ exposed ({len(next_data):,} bytes)")

                def find_sensitive(obj, path="", depth=0):
                    if depth > 5:
                        return
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            current_path = f"{path}.{k}" if path else k
                            if any(s in k.lower() for s in ["token", "secret", "key", "password", "auth", "session", "email", "user", "api_key", "private"]):
                                val_str = str(v)[:80] if v else "null"
                                print(f"    \033[1;31m[SENSITIVE]\033[0m {current_path} = {val_str}")
                            find_sensitive(v, current_path, depth + 1)
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj[:3]):
                            find_sensitive(item, f"{path}[{i}]", depth + 1)

                find_sensitive(nd)

                props = nd.get("props", {}).get("pageProps", {})
                if props:
                    keys = list(props.keys())[:15]
                    print(f"    Page props keys: {keys}")

            except:
                print(f"  \033[1;33m[INFO]\033[0m __NEXT_DATA__ found but could not parse")
        else:
            print(f"  \033[1;36m[INFO]\033[0m No __NEXT_DATA__ found")
        sys.stdout.flush()

        print(f"\n{'='*60}")
        print(f"  \033[1;35mSUMMARY\033[0m")
        print(f"{'='*60}")

        print(f"  Cookies captured: {len(captured_data['cookies'])}")
        print(f"  Auth tokens intercepted: {len(captured_data['auth_tokens'])}")
        print(f"  API requests logged: {len(captured_data['api_requests'])}")
        print(f"  localStorage items: {len(captured_data['local_storage'])}")
        print(f"  sessionStorage items: {len(captured_data['session_storage'])}")
        print(f"  Forms without CSRF: {sum(1 for f in captured_data['forms_data'] if not f['has_csrf'])}")
        print(f"  Sensitive network requests: {len(captured_data['network_requests'])}")

        stealable = []
        for c in captured_data["cookies"]:
            if not c["httpOnly"]:
                stealable.append(c["name"])
        if stealable:
            print(f"\n  \033[1;31m[!] Cookies stealable via XSS: {stealable}\033[0m")

        if captured_data["auth_tokens"]:
            print(f"  \033[1;31m[!] Auth tokens captured - session hijacking possible!\033[0m")

        if captured_data["local_storage"]:
            sens = [k for k in captured_data["local_storage"] if any(s in k.lower() for s in ["token", "auth", "session", "user", "jwt"])]
            if sens:
                print(f"  \033[1;31m[!] Sensitive localStorage keys: {sens}\033[0m")

        print(f"\n{'='*60}")
        sys.stdout.flush()

        browser.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", "-t", required=True)
    parser.add_argument("--duration", "-d", type=int, default=120)
    args = parser.parse_args()

    target = args.target
    if not target.startswith("http"):
        target = f"https://{target}"

    monitor_session(target, args.duration)


if __name__ == "__main__":
    main()
