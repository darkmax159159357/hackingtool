import os
import sys
import json
import subprocess
import threading
import uuid
import time
import re
from flask import Flask, render_template, jsonify, request, Response

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)

TOOLS_DIR = os.path.join(os.path.dirname(__file__), "installed_tools")
os.makedirs(TOOLS_DIR, exist_ok=True)

from tools.anonsurf import AnonSurfTools
from tools.information_gathering_tools import InformationGatheringTools
from tools.wordlist_generator import WordlistGeneratorTools
from tools.wireless_attack_tools import WirelessAttackTools
from tools.sql_tools import SqlInjectionTools
from tools.phising_attack import PhishingAttackTools
from tools.webattack import WebAttackTools
from tools.post_exploitation import PostExploitationTools
from tools.forensic_tools import ForensicTools
from tools.payload_creator import PayloadCreatorTools
from tools.exploit_frameworks import ExploitFrameworkTools
from tools.reverse_engineering import ReverseEngineeringTools
from tools.ddos import DDOSTools
from tools.remote_administration import RemoteAdministrationTools
from tools.xss_attack import XSSAttackTools
from tools.steganography import SteganographyTools
from tools.other_tools import OtherTools
from tools.tool_manager import ToolManager
from tool_descriptions import TOOL_INFO, EXTRA_FALLBACK_RUN

installed_status = {}
INSTALL_STATUS_FILE = os.path.join(TOOLS_DIR, ".install_status.json")

TOOL_INPUTS = {
    "info:Network Map (nmap)": {
        "fields": [
            {"name": "target", "label": "Target IP / Hostname", "label_ar": "عنوان IP أو اسم المضيف", "placeholder": "192.168.1.1 or example.com", "type": "text", "required": True, "validate": "hostname"},
            {"name": "scan_type", "label": "Scan Type", "label_ar": "نوع الفحص", "type": "select", "options": ["Quick Scan", "Version Detection", "OS Detection", "Full Scan"], "required": False, "validate": "enum:Quick Scan,Version Detection,OS Detection,Full Scan"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "port_scanner.py"), inputs["target"]]
                   + (["--ports", "all"] if inputs.get("scan_type") in ("Full Scan", "OS Detection") else []),
            "cwd": None,
        },
    },
    "info:Port scanning": {
        "fields": [
            {"name": "target", "label": "Target IP / Hostname", "label_ar": "عنوان IP أو اسم المضيف", "placeholder": "192.168.1.1", "type": "text", "required": True, "validate": "hostname"},
            {"name": "ports", "label": "Ports (e.g. 80,443 or 1-100)", "label_ar": "المنافذ (مثال: 80,443 أو 1-100)", "placeholder": "top", "type": "text", "required": False},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "port_scanner.py"), inputs["target"]]
                   + (["-p", inputs["ports"]] if inputs.get("ports") else []),
            "cwd": None,
        },
    },
    "info:Host to IP": {
        "fields": [
            {"name": "hostname", "label": "Hostname", "label_ar": "اسم المضيف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "host_to_ip.py"), inputs["hostname"]],
            "cwd": None,
        },
    },
    "info:RED HAWK (All In One Scanning)": {
        "fields": [
            {"name": "target", "label": "Target Domain", "label_ar": "النطاق المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "recon_scanner.py"), inputs["target"]],
            "cwd": None,
        },
    },
    "info:ReconSpider(For All Scanning)": {
        "fields": [
            {"name": "target", "label": "Target Domain / IP", "label_ar": "النطاق أو عنوان IP المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "recon_scanner.py"), inputs["target"]],
            "cwd": None,
        },
    },
    "info:IsItDown (Check Website Down/Up)": {
        "fields": [
            {"name": "target", "label": "Website URL", "label_ar": "رابط الموقع", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "isitdown.py"), inputs["target"]],
            "cwd": None,
        },
    },
    "info:Infoga - Email OSINT": {
        "fields": [
            {"name": "target", "label": "Target Domain", "label_ar": "النطاق المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "infoga.py", "--domain", inputs["target"], "--source", "all"],
            "cwd": "Infoga",
        },
    },
    "info:ReconDog": {
        "fields": [
            {"name": "target", "label": "Target Domain / IP", "label_ar": "النطاق أو عنوان IP المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "recon_scanner.py"), inputs["target"], "--no-subdomains"],
            "cwd": None,
        },
    },
    "info:Striker": {
        "fields": [
            {"name": "target", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "striker.py", inputs["target"]],
            "cwd": "Striker",
        },
    },
    "info:SecretFinder (like API & etc)": {
        "fields": [
            {"name": "target", "label": "Target URL (JS file or page)", "label_ar": "الرابط المستهدف (ملف JS أو صفحة)", "placeholder": "https://example.com/app.js", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "SecretFinder.py", "-i", inputs["target"], "-o", "cli"],
            "cwd": "SecretFinder",
        },
    },
    "info:Find Info Using Shodan": {
        "fields": [
            {"name": "query", "label": "Search Query", "label_ar": "عبارة البحث", "placeholder": "apache country:US", "type": "text", "required": True},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "-c", f"import shodan; print('Shodan Search Query: {inputs['query']}'); print('Note: Requires API key. Set SHODAN_API_KEY env variable.')"],
            "cwd": None,
        },
    },
    "info:Port Scanner - rang3r": {
        "fields": [
            {"name": "target", "label": "Target IP / Hostname", "label_ar": "عنوان IP أو اسم المضيف", "placeholder": "192.168.1.1", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "port_scanner.py"), inputs["target"]],
            "cwd": None,
        },
    },
    "info:Breacher": {
        "fields": [
            {"name": "target", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "breacher.py", "-u", inputs["target"]],
            "cwd": "Breacher",
        },
    },
    "sql:Sqlmap tool": {
        "fields": [
            {"name": "target_url", "label": "Target URL (with parameter)", "label_ar": "الرابط المستهدف (مع بارامتر)", "placeholder": "http://example.com/page?id=1", "type": "text", "required": True, "validate": "url"},
            {"name": "level", "label": "Test Level (1-5)", "label_ar": "مستوى الاختبار (1-5)", "placeholder": "1", "type": "select", "options": ["1", "2", "3", "4", "5"], "required": False, "validate": "enum:1,2,3,4,5"},
            {"name": "risk", "label": "Risk Level (1-3)", "label_ar": "مستوى المخاطرة (1-3)", "placeholder": "1", "type": "select", "options": ["1", "2", "3"], "required": False, "validate": "enum:1,2,3"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "sqlmap.py", "-u", inputs["target_url"], "--batch"]
                   + (["--level", inputs["level"]] if inputs.get("level") else [])
                   + (["--risk", inputs["risk"]] if inputs.get("risk") else []),
            "cwd": "sqlmap",
        },
    },
    "sql:NoSqlMap": {
        "fields": [
            {"name": "target", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "nosqlmap.py", "-u", inputs["target"]],
            "cwd": "NoSQLMap",
        },
    },
    "sql:Damn Small SQLi Scanner": {
        "fields": [
            {"name": "target_url", "label": "Target URL (with parameter)", "label_ar": "الرابط المستهدف (مع بارامتر)", "placeholder": "http://example.com/page?id=1", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "dsss.py", "-u", inputs["target_url"]],
            "cwd": "dsss",
        },
    },
    "sql:Explo": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "-m", "explo", inputs["target_url"]],
            "cwd": "explo",
        },
    },
    "sql:Blisqy - Exploit Time-based blind-SQL injection": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com/page", "type": "text", "required": True, "validate": "url"},
            {"name": "header", "label": "Injectable Header", "label_ar": "الهيدر القابل للحقن", "placeholder": "X-Forwarded-For", "type": "text", "required": False},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "blisqy.py", "--server", inputs["target_url"]]
                   + (["--header", inputs["header"]] if inputs.get("header") else []),
            "cwd": "Blisqy",
        },
    },
    "web:Skipfish": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "web_scanner.py"), inputs["target_url"]],
            "cwd": None,
        },
    },
    "web:Dirb": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
            {"name": "scan_type", "label": "Scan Type", "label_ar": "نوع الفحص", "type": "select", "options": ["All", "Directories Only", "Files Only"], "required": False, "validate": "enum:All,Directories Only,Files Only"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "web_scanner.py"), inputs["target_url"]]
                   + (["--dirs-only"] if inputs.get("scan_type") == "Directories Only" else [])
                   + (["--files-only"] if inputs.get("scan_type") == "Files Only" else []),
            "cwd": None,
        },
    },
    "web:SubDomain Finder": {
        "fields": [
            {"name": "domain", "label": "Target Domain", "label_ar": "النطاق المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "sublist3r.py", "-d", inputs["domain"]],
            "cwd": "Sublist3r",
        },
    },
    "web:CheckURL": {
        "fields": [
            {"name": "target_url", "label": "URL to Check", "label_ar": "الرابط للفحص", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "checkURL.py", "--url", inputs["target_url"], "--check-url"],
            "cwd": "checkURL",
        },
    },
    "web:Blazy(Also Find ClickJacking)": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "main.py", "-i", inputs["target_url"]],
            "cwd": "Blazy",
        },
    },
    "web:Sub-Domain TakeOver": {
        "fields": [
            {"name": "domain", "label": "Target Domain", "label_ar": "النطاق المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "takeover.py", "-d", inputs["domain"]],
            "cwd": "subdomain-takeover",
        },
    },
    "exploit:Commix": {
        "fields": [
            {"name": "target_url", "label": "Target URL (with parameter)", "label_ar": "الرابط المستهدف (مع بارامتر)", "placeholder": "http://example.com/page?cmd=test", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "commix.py", "--url", inputs["target_url"], "--batch"],
            "cwd": "commix",
        },
    },
    "exploit:RouterSploit": {
        "fields": [
            {"name": "target_ip", "label": "Target IP Address", "label_ar": "عنوان IP المستهدف", "placeholder": "192.168.1.1", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "rsf.py"],
            "cwd": "routersploit",
        },
    },
    "xss:DalFox (Finder of XSS)": {
        "fields": [
            {"name": "target_url", "label": "Target URL (with parameter)", "label_ar": "الرابط المستهدف (مع بارامتر)", "placeholder": "http://example.com/page?q=test", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "xsstrike.py", "-u", inputs["target_url"], "--crawl"],
            "cwd": "XSStrike",
        },
    },
    "xss:Extended XSS Searcher and Finder": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "xss_finder.py", "-u", inputs["target_url"]],
            "cwd": "xss-finder",
        },
    },
    "xss:XSS-Freak": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "XSS-Freak.py", "-u", inputs["target_url"]],
            "cwd": "XSS-Freak",
        },
    },
    "xss:XSSCon": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "xsscon.py", "-u", inputs["target_url"]],
            "cwd": "XSSCon",
        },
    },
    "xss:XanXSS": {
        "fields": [
            {"name": "target_url", "label": "Target URL (with parameter)", "label_ar": "الرابط المستهدف (مع بارامتر)", "placeholder": "http://example.com/page?q=test", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "xanxss.py", "-u", inputs["target_url"]],
            "cwd": "XanXSS",
        },
    },
    "xss:Advanced XSS Detection Suite": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "xss_scanner.py", "-u", inputs["target_url"]],
            "cwd": "xss-detection-suite",
        },
    },
    "other:Sherlock": {
        "fields": [
            {"name": "username", "label": "Username to Search", "label_ar": "اسم المستخدم للبحث", "placeholder": "johndoe", "type": "text", "required": True},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "-m", "sherlock_project", inputs["username"]],
            "cwd": "sherlock",
        },
    },
    "other:SocialScan | Username or Email": {
        "fields": [
            {"name": "query", "label": "Username or Email", "label_ar": "اسم المستخدم أو البريد الإلكتروني", "placeholder": "johndoe or user@example.com", "type": "text", "required": True},
        ],
        "build_args": lambda inputs: {
            "cmd": ["socialscan", inputs["query"]],
            "cwd": None,
        },
    },
    "other:Knockmail": {
        "fields": [
            {"name": "email", "label": "Email Address", "label_ar": "عنوان البريد الإلكتروني", "placeholder": "user@example.com", "type": "text", "required": True},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "knockmail.py", "-e", inputs["email"]],
            "cwd": "KnockMail",
        },
    },
    "other:Hash Buster": {
        "fields": [
            {"name": "hash_value", "label": "Hash to Crack", "label_ar": "الهاش للكسر", "placeholder": "5d41402abc4b2a76b9719d911017c592", "type": "text", "required": True},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "hash.py", "-s", inputs["hash_value"]],
            "cwd": "Hash-Buster",
        },
    },
    "other:HatCloud(Bypass CloudFlare for IP)": {
        "fields": [
            {"name": "domain", "label": "Target Domain", "label_ar": "النطاق المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["ruby", "hatcloud.rb", "-b", inputs["domain"]],
            "cwd": "HatCloud",
        },
    },
    "other:CloudFlare Bypass Scanner (DrissionPage)": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "https://example.com", "type": "text", "required": True, "validate": "url"},
            {"name": "depth", "label": "Crawl Depth (default 2)", "label_ar": "عمق الزحف (افتراضي 2)", "placeholder": "2", "type": "number", "required": False, "validate": "int"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "cloudflare_bypass.py"),
                    "--target", inputs["target_url"]]
                   + (["--depth", inputs["depth"]] if inputs.get("depth") else []),
            "cwd": None,
            "timeout": 300,
        },
    },
    "other:Gospider": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
            {"name": "depth", "label": "Crawl Depth (default 3)", "label_ar": "عمق الزحف (افتراضي 3)", "placeholder": "3", "type": "number", "required": False, "validate": "int"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["gospider", "-s", inputs["target_url"]]
                   + (["-d", inputs["depth"]] if inputs.get("depth") else ["-d", "3"]),
            "cwd": None,
        },
    },
    "other:Crivo": {
        "fields": [
            {"name": "target", "label": "Target Domain / IP", "label_ar": "النطاق أو عنوان IP المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "crivo.py", "-t", inputs["target"]],
            "cwd": "crivo",
        },
    },
    "other:Pixload": {
        "fields": [
            {"name": "payload", "label": "Payload Type", "label_ar": "نوع الحمولة", "type": "select", "options": ["gif", "bmp", "png", "jpg", "webp"], "required": True, "validate": "enum:gif,bmp,png,jpg,webp"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "pixload.py", "--" + inputs["payload"]],
            "cwd": "pixload",
        },
    },
    "stego:SteganoHide": {
        "fields": [
            {"name": "action", "label": "Action", "label_ar": "الإجراء", "type": "select", "options": ["embed", "extract", "info"], "required": True, "validate": "enum:embed,extract,info"},
            {"name": "cover_file", "label": "Cover File Path", "label_ar": "مسار ملف الغطاء", "placeholder": "/path/to/image.jpg", "type": "text", "required": True},
        ],
        "build_args": lambda inputs: {
            "cmd": ["steghide", inputs["action"], "-cf", inputs["cover_file"]],
            "cwd": None,
        },
    },
    "stego:StegnoCracker": {
        "fields": [
            {"name": "file_path", "label": "Encrypted File Path", "label_ar": "مسار الملف المشفر", "placeholder": "/path/to/image.jpg", "type": "text", "required": True},
            {"name": "wordlist", "label": "Wordlist Path (optional)", "label_ar": "مسار قائمة الكلمات (اختياري)", "placeholder": "/path/to/wordlist.txt", "type": "text", "required": False},
        ],
        "build_args": lambda inputs: {
            "cmd": ["stegcracker", inputs["file_path"]]
                   + ([inputs["wordlist"]] if inputs.get("wordlist") else []),
            "cwd": None,
        },
    },
    "ddos:SlowLoris": {
        "fields": [
            {"name": "target_site", "label": "Target Site URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "example.com", "type": "text", "required": True, "validate": "hostname"},
            {"name": "port", "label": "Port (default 80)", "label_ar": "المنفذ (افتراضي 80)", "placeholder": "80", "type": "number", "required": False, "validate": "port"},
            {"name": "sockets", "label": "Number of Sockets (default 150)", "label_ar": "عدد الاتصالات (افتراضي 150)", "placeholder": "150", "type": "number", "required": False, "validate": "int"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["slowloris", inputs["target_site"]]
                   + (["-p", inputs["port"]] if inputs.get("port") else [])
                   + (["-s", inputs["sockets"]] if inputs.get("sockets") else []),
            "cwd": None,
        },
    },
    "ddos:Asyncrone | Multifunction SYN Flood DDoS Weapon": {
        "fields": [
            {"name": "source_port", "label": "Source Port", "label_ar": "منفذ المصدر", "placeholder": "4444", "type": "number", "required": True, "validate": "port"},
            {"name": "target_ip", "label": "Target IP Address", "label_ar": "عنوان IP المستهدف", "placeholder": "192.168.1.1", "type": "text", "required": True, "validate": "ip"},
            {"name": "target_port", "label": "Target Port", "label_ar": "منفذ الهدف", "placeholder": "80", "type": "number", "required": True, "validate": "port"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["./aSYNcrone", inputs["source_port"], inputs["target_ip"], inputs["target_port"], "1000"],
            "cwd": "aSYNcrone",
        },
    },
    "ddos:UFOnet": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
            {"name": "rounds", "label": "Number of Rounds (default 1)", "label_ar": "عدد الجولات (افتراضي 1)", "placeholder": "1", "type": "number", "required": False, "validate": "int"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "ufonet", "-a", inputs["target_url"]]
                   + (["-r", inputs["rounds"]] if inputs.get("rounds") else []),
            "cwd": "ufonet",
        },
    },
    "ddos:GoldenEye": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
            {"name": "workers", "label": "Number of Workers (default 10)", "label_ar": "عدد العمال (افتراضي 10)", "placeholder": "10", "type": "number", "required": False, "validate": "int"},
            {"name": "sockets", "label": "Sockets per Worker (default 500)", "label_ar": "اتصالات لكل عامل (افتراضي 500)", "placeholder": "500", "type": "number", "required": False, "validate": "int"},
            {"name": "method", "label": "HTTP Method", "label_ar": "طريقة HTTP", "placeholder": "get", "type": "select", "options": ["get", "post", "random"], "required": False, "validate": "enum:get,post,random"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "goldeneye.py", inputs["target_url"]]
                   + (["-w", inputs["workers"]] if inputs.get("workers") else [])
                   + (["-s", inputs["sockets"]] if inputs.get("sockets") else [])
                   + (["-m", inputs["method"]] if inputs.get("method") else []),
            "cwd": "GoldenEye",
        },
    },
    "ddos:SaphyraDDoS": {
        "fields": [
            {"name": "target_url", "label": "Target URL", "label_ar": "عنوان الموقع المستهدف", "placeholder": "http://example.com", "type": "text", "required": True, "validate": "url"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", "saphyra.py", inputs["target_url"]],
            "cwd": "Saphyra-DDoS",
        },
    },
    "ddos:Slowloris Vulnerability Analyzer": {
        "fields": [
            {"name": "target", "label": "Target (hostname or URL)", "label_ar": "الهدف (اسم المضيف أو الرابط)", "placeholder": "example.com or http://example.com", "type": "text", "required": True, "validate": "hostname"},
            {"name": "port", "label": "Port (default 80)", "label_ar": "المنفذ (افتراضي 80)", "placeholder": "80", "type": "number", "required": False, "validate": "port"},
        ],
        "build_args": lambda inputs: {
            "cmd": ["python3", os.path.join(os.path.dirname(__file__), "scripts", "slowloris_analyzer.py"),
                    "--target", inputs["target"]]
                   + (["--port", inputs["port"]] if inputs.get("port") else []),
            "cwd": None,
        },
    },
}

VALIDATION_ERRORS = {
    "hostname": {
        "en": "Invalid hostname, IP, or URL",
        "ar": "اسم المضيف أو عنوان IP أو الرابط غير صالح",
    },
    "ip": {
        "en": "Invalid IP address (each octet must be 0-255)",
        "ar": "عنوان IP غير صالح (كل جزء يجب أن يكون بين 0 و 255)",
    },
    "port": {
        "en": "Invalid port number (must be 1-65535)",
        "ar": "رقم المنفذ غير صالح (يجب أن يكون بين 1 و 65535)",
    },
    "int": {
        "en": "Invalid number (must be a positive integer)",
        "ar": "رقم غير صالح (يجب أن يكون عدد صحيح موجب)",
    },
    "url": {
        "en": "Invalid URL or hostname",
        "ar": "رابط أو اسم مضيف غير صالح",
    },
    "enum": {
        "en": "Invalid selection",
        "ar": "اختيار غير صالح",
    },
    "required": {
        "en": "This field is required",
        "ar": "هذا الحقل مطلوب",
    },
}

def _is_valid_hostname(value):
    return bool(re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$', value))

def _is_valid_ip(value):
    m = re.match(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', value)
    if not m:
        return False
    return all(0 <= int(m.group(i)) <= 255 for i in range(1, 5))

def validate_input(value, validate_type):
    if not validate_type:
        return True
    if validate_type == "hostname":
        if re.match(r'^https?://', value):
            stripped = re.sub(r'^https?://', '', value).split('/')[0].split(':')[0]
            return _is_valid_hostname(stripped) or _is_valid_ip(stripped)
        host_part = value.split(':')[0].split('/')[0]
        return _is_valid_hostname(host_part) or _is_valid_ip(host_part)
    if validate_type == "ip":
        return _is_valid_ip(value)
    if validate_type == "port":
        try:
            p = int(value)
            return 1 <= p <= 65535
        except (ValueError, TypeError):
            return False
    if validate_type == "int":
        try:
            n = int(value)
            return n >= 1
        except (ValueError, TypeError):
            return False
    if validate_type == "url":
        if re.match(r'^https?://', value):
            stripped = re.sub(r'^https?://', '', value).split('/')[0].split(':')[0]
            return _is_valid_hostname(stripped) or _is_valid_ip(stripped)
        return _is_valid_hostname(value) or _is_valid_ip(value)
    if validate_type.startswith("enum:"):
        allowed = validate_type.split(":", 1)[1].split(",")
        return value in allowed
    return True

def get_validation_error(field, value):
    v_type = field.get("validate", "")
    base_type = v_type.split(":")[0] if ":" in v_type else v_type
    msgs = VALIDATION_ERRORS.get(base_type, VALIDATION_ERRORS.get("required"))
    label_en = field.get("label", "Field")
    label_ar = field.get("label_ar", label_en)
    return f"{label_en}: {msgs['en']} | {label_ar}: {msgs['ar']}"

def load_install_status():
    global installed_status
    if os.path.exists(INSTALL_STATUS_FILE):
        with open(INSTALL_STATUS_FILE) as f:
            installed_status = json.load(f)

def save_install_status():
    with open(INSTALL_STATUS_FILE, "w") as f:
        json.dump(installed_status, f)

load_install_status()

def get_attr(obj, *names, default=""):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default

def sanitize_command(cmd):
    cmd = re.sub(r'\bsudo\s+', '', cmd)
    return cmd

CATEGORIES = [
    {"id": "anon", "name": "Anonymously Hiding Tools", "icon": "shield-half", "collection": AnonSurfTools()},
    {"id": "info", "name": "Information Gathering", "icon": "search", "collection": InformationGatheringTools()},
    {"id": "wordlist", "name": "Wordlist Generator", "icon": "book", "collection": WordlistGeneratorTools()},
    {"id": "wireless", "name": "Wireless Attack Tools", "icon": "wifi", "collection": WirelessAttackTools()},
    {"id": "sql", "name": "SQL Injection Tools", "icon": "database", "collection": SqlInjectionTools()},
    {"id": "phishing", "name": "Phishing Attack Tools", "icon": "envelope-open-text", "collection": PhishingAttackTools()},
    {"id": "web", "name": "Web Attack Tools", "icon": "globe", "collection": WebAttackTools()},
    {"id": "post", "name": "Post Exploitation Tools", "icon": "wrench", "collection": PostExploitationTools()},
    {"id": "forensic", "name": "Forensic Tools", "icon": "fingerprint", "collection": ForensicTools()},
    {"id": "payload", "name": "Payload Creation Tools", "icon": "box", "collection": PayloadCreatorTools()},
    {"id": "exploit", "name": "Exploit Framework", "icon": "tools", "collection": ExploitFrameworkTools()},
    {"id": "reverse", "name": "Reverse Engineering", "icon": "recycle", "collection": ReverseEngineeringTools()},
    {"id": "ddos", "name": "DDOS Attack Tools", "icon": "bolt", "collection": DDOSTools()},
    {"id": "rat", "name": "Remote Admin Tools (RAT)", "icon": "desktop", "collection": RemoteAdministrationTools()},
    {"id": "xss", "name": "XSS Attack Tools", "icon": "code", "collection": XSSAttackTools()},
    {"id": "stego", "name": "Steganography Tools", "icon": "image", "collection": SteganographyTools()},
    {"id": "other", "name": "Other Tools", "icon": "ellipsis-h", "collection": OtherTools()},
    {"id": "manager", "name": "Update / Uninstall", "icon": "sync-alt", "collection": ToolManager()},
]

_tool_registry = {}

FALLBACK_RUN_COMMANDS = {
    "ddos:SlowLoris": ["slowloris --help"],
    "ddos:GoldenEye": ["cd GoldenEye && python3 goldeneye.py"],
    "ddos:SaphyraDDoS": ["cd saphyra && python3 saphyra.py --help"],
    "ddos:Asyncrone | Multifunction SYN Flood DDoS Weapon": ["cd aSYNcrone && ./aSYNcrone --help"],
    "ddos:ddos": ["echo 'DDoS collection - select a specific tool'"],
    "info:Port scanning": ["nmap --help"],
    "info:Host to IP": ["python3 -c \"import socket; print('Host to IP tool ready')\""],
    "info:IsItDown (Check Website Down/Up)": ["python3 -c \"print('IsItDown checker ready')\""],
    "info:Breacher": ["cd Breacher && python3 breacher.py --help"],
    "info:Striker": ["cd Striker && python3 striker.py --help"],
    "info:Port Scanner - rang3r": ["cd rang3r && python3 rang3r.py --help"],
    "web:Skipfish": ["skipfish -h"],
    "web:Dirb": ["dirb"],
    "xss:XSSCon": ["cd XSSCon && python3 xsscon.py --help"],
    "xss:XanXSS": ["cd XanXSS && python3 xanxss.py -h"],
    "xss:Extended XSS Searcher and Finder": ["cd xss-finder && python3 xss_finder.py --help"],
    "stego:SteganoHide": ["steghide --help"],
    "stego:StegnoCracker": ["stegcracker --help"],
    "reverse:Apk2Gold": ["apk2gold --help"],
    "wireless:pixiewps": ["pixiewps --help"],
    "other:HatCloud(Bypass CloudFlare for IP)": ["cd HatCloud && ruby hatcloud.rb --help"],
    "other:Sherlock": ["cd sherlock && python3 -m sherlock --help"],
    "other:SocialScan | Username or Email": ["socialscan --help"],
    "other:Find SocialMedia By Facial Recognation System": ["cd social_mapper && python3 social_mapper.py --help"],
    "other:Facebook Attack": ["echo 'Facebook Attack tool - select sub-tool'"],
    "other:Instagram Attack": ["echo 'Instagram Attack tool - select sub-tool'"],
}
FALLBACK_RUN_COMMANDS.update(EXTRA_FALLBACK_RUN)

def extract_tools(collection, category_id=""):
    tools_list = []
    items = getattr(collection, "TOOLS", [])
    for i, tool in enumerate(items):
        title = get_attr(tool, "TITLE", "Title", "title", default=tool.__class__.__name__)
        desc = get_attr(tool, "DESCRIPTION", "Description", "description", default="")
        url = get_attr(tool, "PROJECT_URL", "PROJECT_URL", "project_url", "projectUrl", default="")
        install_cmds = get_attr(tool, "INSTALL_COMMANDS", "Install_commands", default=[])
        run_cmds = get_attr(tool, "RUN_COMMANDS", "Run_commands", default=[])
        uninstall_cmds = get_attr(tool, "UNINSTALL_COMMANDS", default=[])

        has_sub = hasattr(tool, "TOOLS") and len(getattr(tool, "TOOLS", [])) > 0
        sub_tools = []
        if has_sub:
            sub_tools = extract_tools(tool, category_id)

        installable = bool(install_cmds)
        tool_key = f"{category_id}:{str(title).strip()}"

        if not run_cmds and tool_key in FALLBACK_RUN_COMMANDS:
            run_cmds = FALLBACK_RUN_COMMANDS[tool_key]

        runnable = bool(run_cmds)

        safe_install = [sanitize_command(c) for c in (list(install_cmds) if isinstance(install_cmds, (list, tuple)) else [])]
        safe_run = [sanitize_command(c) for c in (list(run_cmds) if isinstance(run_cmds, (list, tuple)) else [])]
        safe_uninstall = [sanitize_command(c) for c in (list(uninstall_cmds) if isinstance(uninstall_cmds, (list, tuple)) else [])]

        _tool_registry[tool_key] = {
            "install_commands": safe_install,
            "run_commands": safe_run,
            "uninstall_commands": safe_uninstall,
        }

        title_str = str(title).strip()
        if not title_str and not has_sub:
            continue

        info = TOOL_INFO.get(tool_key, {})
        desc_en = info.get("desc_en", "")
        desc_ar = info.get("desc_ar", "")
        usage = info.get("usage", "")

        tool_inputs = None
        if tool_key in TOOL_INPUTS:
            tool_inputs = [
                {k: v for k, v in f.items() if k != "validate"}
                for f in TOOL_INPUTS[tool_key]["fields"]
            ]

        tools_list.append({
            "index": i,
            "title": title_str,
            "tool_key": tool_key,
            "description": str(desc).replace("\n", " ").strip() if desc else "",
            "desc_en": desc_en,
            "desc_ar": desc_ar,
            "usage": usage,
            "project_url": str(url).strip() if url else "",
            "installable": installable,
            "runnable": runnable,
            "has_inputs": tool_inputs is not None,
            "input_fields": tool_inputs,
            "install_commands": list(install_cmds) if isinstance(install_cmds, (list, tuple)) else [],
            "run_commands": list(run_cmds) if isinstance(run_cmds, (list, tuple)) else [],
            "uninstall_commands": list(uninstall_cmds) if isinstance(uninstall_cmds, (list, tuple)) else [],
            "has_sub_tools": has_sub,
            "sub_tools": sub_tools,
            "installed": installed_status.get(tool_key, False),
        })
    return tools_list

for cat in CATEGORIES:
    extract_tools(cat["collection"], cat["id"])

VIRTUAL_TOOLS = {
    "other:CloudFlare Bypass Scanner (DrissionPage)": {
        "title": "CloudFlare Bypass Scanner (DrissionPage)",
        "description": "Bypass CloudFlare protection using DrissionPage + Chromium browser. Deep crawls target, detects technologies, tests XSS, analyzes security headers, cookies, forms, and discovers API endpoints.",
        "desc_en": "Advanced CloudFlare bypass scanner powered by DrissionPage and headless Chromium. Bypasses Cloudflare challenges, crawls the site deeply, detects technologies (React, Next.js, jQuery, WordPress, etc.), analyzes security headers, discovers forms and API endpoints, tests for XSS and CSRF, checks cookie security, and probes for information disclosure.",
        "desc_ar": "ماسح متقدم لتجاوز حماية كلاود فلير باستخدام DrissionPage ومتصفح Chromium. يتجاوز تحديات Cloudflare، يزحف للموقع بعمق، يكشف التقنيات المستخدمة، يحلل رؤوس الأمان، يكتشف النماذج ونقاط API، يختبر ثغرات XSS و CSRF، يفحص أمان الكوكيز، ويبحث عن تسريب المعلومات.",
        "category_id": "other",
    },
}
for vt_key, vt_info in VIRTUAL_TOOLS.items():
    _tool_registry[vt_key] = {
        "install_commands": [],
        "run_commands": ["echo 'Use interactive mode'"],
        "uninstall_commands": [],
    }

processes = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/xss-poc")
def xss_poc():
    return render_template("xss_poc.html")

@app.route("/api/categories")
def api_categories():
    cats = []
    for cat in CATEGORIES:
        tools = extract_tools(cat["collection"], cat["id"])
        cats.append({
            "id": cat["id"],
            "name": cat["name"],
            "icon": cat["icon"],
            "tool_count": len(tools),
        })
    return jsonify(cats)

@app.route("/api/category/<cat_id>")
def api_category(cat_id):
    for cat in CATEGORIES:
        if cat["id"] == cat_id:
            tools = extract_tools(cat["collection"], cat["id"])
            for vt_key, vt_info in VIRTUAL_TOOLS.items():
                if vt_info["category_id"] == cat_id:
                    tool_inputs = None
                    if vt_key in TOOL_INPUTS:
                        tool_inputs = [
                            {k: v for k, v in f.items() if k != "validate"}
                            for f in TOOL_INPUTS[vt_key]["fields"]
                        ]
                    tools.append({
                        "index": 999,
                        "title": vt_info["title"],
                        "tool_key": vt_key,
                        "description": vt_info["description"],
                        "desc_en": vt_info.get("desc_en", ""),
                        "desc_ar": vt_info.get("desc_ar", ""),
                        "usage": "",
                        "project_url": "",
                        "installable": False,
                        "runnable": True,
                        "has_inputs": tool_inputs is not None,
                        "input_fields": tool_inputs,
                        "install_commands": [],
                        "run_commands": [],
                        "uninstall_commands": [],
                        "has_sub_tools": False,
                        "sub_tools": [],
                        "installed": True,
                    })
            return jsonify({
                "id": cat["id"],
                "name": cat["name"],
                "icon": cat["icon"],
                "tools": tools,
            })
    return jsonify({"error": "Category not found"}), 404

@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.json
    tool_key = data.get("tool_key", "")
    action = data.get("action", "run")
    user_inputs = data.get("inputs", {})

    if not tool_key or tool_key not in _tool_registry:
        return jsonify({"error": "Invalid tool"}), 400

    if action == "run" and tool_key in TOOL_INPUTS:
        tool_input_cfg = TOOL_INPUTS[tool_key]
        for field in tool_input_cfg["fields"]:
            if field["required"] and not user_inputs.get(field["name"]):
                label_en = field.get("label", "Field")
                label_ar = field.get("label_ar", label_en)
                msgs = VALIDATION_ERRORS["required"]
                return jsonify({"error": f"{label_en}: {msgs['en']} | {label_ar}: {msgs['ar']}"}), 400
        clean_inputs = {}
        for field in tool_input_cfg["fields"]:
            val = str(user_inputs.get(field["name"], "")).strip()
            if val:
                v_type = field.get("validate")
                if v_type and not validate_input(val, v_type):
                    return jsonify({"error": get_validation_error(field, val)}), 400
                clean_inputs[field["name"]] = val
        try:
            args_info = tool_input_cfg["build_args"](clean_inputs)
            cmd_args = args_info["cmd"]
            tool_cwd = args_info.get("cwd")
        except Exception as e:
            return jsonify({"error": f"Failed to build command: {str(e)}"}), 400

        exec_cwd = TOOLS_DIR
        if tool_cwd:
            exec_cwd = os.path.join(TOOLS_DIR, tool_cwd)

        task_id = str(uuid.uuid4())[:8]

        def run_process():
            try:
                proc = subprocess.Popen(
                    cmd_args,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=exec_cwd,
                    env={**os.environ, "HOME": os.path.expanduser("~")},
                )
                processes[task_id]["process"] = proc
                output_lines = []
                for line in proc.stdout:
                    output_lines.append(line)
                    processes[task_id]["output"] = output_lines
                proc.wait()
                processes[task_id]["status"] = "completed"
                processes[task_id]["exit_code"] = proc.returncode
            except Exception as e:
                processes[task_id]["status"] = "error"
                processes[task_id]["output"].append(f"Error: {str(e)}\n")

        processes[task_id] = {
            "status": "running",
            "output": [],
            "process": None,
            "exit_code": None,
        }
        t = threading.Thread(target=run_process, daemon=True)
        t.start()
        return jsonify({"task_id": task_id})

    registered = _tool_registry[tool_key]
    if action == "install":
        commands = registered["install_commands"]
    elif action == "uninstall":
        commands = registered["uninstall_commands"]
    elif action == "run":
        commands = registered["run_commands"]
    else:
        return jsonify({"error": "Invalid action"}), 400

    if not commands:
        return jsonify({"error": f"No {action} commands for this tool"}), 400

    task_id = str(uuid.uuid4())[:8]
    combined = " && ".join(commands)

    def run_process():
        try:
            proc = subprocess.Popen(
                combined,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=TOOLS_DIR,
                env={**os.environ, "HOME": os.path.expanduser("~")},
            )
            processes[task_id]["process"] = proc
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line)
                processes[task_id]["output"] = output_lines
            proc.wait()
            processes[task_id]["status"] = "completed"
            processes[task_id]["exit_code"] = proc.returncode

            if action == "install" and proc.returncode == 0:
                installed_status[tool_key] = True
                save_install_status()
            elif action == "uninstall" and proc.returncode == 0:
                installed_status[tool_key] = False
                save_install_status()

        except Exception as e:
            processes[task_id]["status"] = "error"
            processes[task_id]["output"].append(f"Error: {str(e)}\n")

    processes[task_id] = {
        "status": "running",
        "output": [],
        "process": None,
        "exit_code": None,
    }
    t = threading.Thread(target=run_process, daemon=True)
    t.start()

    return jsonify({"task_id": task_id})

@app.route("/api/task/<task_id>")
def api_task(task_id):
    if task_id not in processes:
        return jsonify({"error": "Task not found"}), 404
    task = processes[task_id]
    return jsonify({
        "status": task["status"],
        "output": "".join(task["output"]),
        "exit_code": task["exit_code"],
    })

@app.route("/api/task/<task_id>/stop", methods=["POST"])
def api_task_stop(task_id):
    if task_id not in processes:
        return jsonify({"error": "Task not found"}), 404
    proc = processes[task_id].get("process")
    if proc and proc.poll() is None:
        proc.terminate()
        processes[task_id]["status"] = "stopped"
    return jsonify({"status": "stopped"})

@app.route("/api/stream/<task_id>")
def api_stream(task_id):
    if task_id not in processes:
        return jsonify({"error": "Task not found"}), 404

    def generate():
        last_len = 0
        while True:
            task = processes.get(task_id)
            if not task:
                break
            output = task["output"]
            current_len = len(output)
            if current_len > last_len:
                for line in output[last_len:current_len]:
                    yield f"data: {json.dumps({'line': line})}\n\n"
                last_len = current_len
            if task["status"] in ("completed", "error", "stopped"):
                yield f"data: {json.dumps({'done': True, 'status': task['status'], 'exit_code': task['exit_code']})}\n\n"
                break
            time.sleep(0.2)

    return Response(generate(), mimetype="text/event-stream")

@app.route("/api/install-all", methods=["POST"])
def api_install_all():
    data = request.json
    cat_id = data.get("category_id", "")

    target_cats = CATEGORIES
    if cat_id:
        target_cats = [c for c in CATEGORIES if c["id"] == cat_id]

    tools_to_install = []
    for cat in target_cats:
        tools = extract_tools(cat["collection"], cat["id"])
        for tool in tools:
            if tool["installable"] and not tool.get("installed"):
                tools_to_install.append(tool)

    if not tools_to_install:
        return jsonify({"error": "No tools to install", "message": "All tools are already installed or have no install commands"}), 400

    task_id = str(uuid.uuid4())[:8]
    tool_names = [t["title"] for t in tools_to_install]

    def run_all():
        try:
            output_lines = []
            processes[task_id]["output"] = output_lines
            overall_fail = False

            for tool in tools_to_install:
                cmds = [sanitize_command(c) for c in tool["install_commands"]]
                combined = " && ".join(cmds)
                header = f"\n=== Installing: {tool['title']} ===\n"
                output_lines.append(header)

                proc = subprocess.Popen(
                    combined,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=TOOLS_DIR,
                    env={**os.environ, "HOME": os.path.expanduser("~")},
                )
                processes[task_id]["process"] = proc
                for line in proc.stdout:
                    output_lines.append(line)
                proc.wait()

                if proc.returncode == 0:
                    output_lines.append(f"SUCCESS: {tool['title']}\n")
                    installed_status[tool["tool_key"]] = True
                    save_install_status()
                else:
                    output_lines.append(f"FAILED: {tool['title']} (exit code: {proc.returncode})\n")
                    overall_fail = True

                if processes[task_id]["status"] == "stopped":
                    break

            processes[task_id]["status"] = "completed"
            processes[task_id]["exit_code"] = 1 if overall_fail else 0

        except Exception as e:
            processes[task_id]["status"] = "error"
            processes[task_id]["output"].append(f"Error: {str(e)}\n")

    processes[task_id] = {
        "status": "running",
        "output": [],
        "process": None,
        "exit_code": None,
    }
    t = threading.Thread(target=run_all, daemon=True)
    t.start()

    return jsonify({"task_id": task_id, "tool_count": len(tool_names), "tools": tool_names})

workflow_state = {}

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

WORKFLOW_PHASES = [
    {
        "id": "cf_bypass",
        "name": "CloudFlare Bypass & Deep Scan",
        "name_ar": "تجاوز كلاود فلير وفحص عميق",
        "tools": [
            {"name": "CloudFlare Bypass Scanner", "cmd": ["python3", os.path.join(SCRIPTS_DIR, "cloudflare_bypass.py"), "--target", "{target_url}", "--depth", "2"], "cwd": None, "timeout": 300},
        ],
    },
    {
        "id": "recon",
        "name": "Reconnaissance",
        "name_ar": "الاستطلاع",
        "tools": [
            {"name": "Port Scanner", "cmd": ["python3", os.path.join(SCRIPTS_DIR, "port_scanner.py"), "{target}", "-p", "top"], "cwd": None, "timeout": 120},
            {"name": "Recon Scanner", "cmd": ["python3", os.path.join(SCRIPTS_DIR, "recon_scanner.py"), "{target_url}", "--no-subdomains"], "cwd": None, "timeout": 120},
        ],
    },
    {
        "id": "web_scan",
        "name": "Web Scanning",
        "name_ar": "فحص الويب",
        "tools": [
            {"name": "Web Scanner", "cmd": ["python3", os.path.join(SCRIPTS_DIR, "web_scanner.py"), "{target_url}"], "cwd": None, "timeout": 120},
        ],
    },
    {
        "id": "sql",
        "name": "SQL Injection",
        "name_ar": "حقن SQL",
        "tools": [
            {"name": "Sqlmap", "cmd": ["python3", "sqlmap.py", "-u", "{target_url}", "--batch", "--crawl=1", "--random-agent", "--level=1", "--risk=1"], "cwd": "sqlmap", "timeout": 180},
        ],
    },
    {
        "id": "xss",
        "name": "XSS Testing",
        "name_ar": "اختبار XSS",
        "tools": [
            {"name": "XSStrike", "cmd": ["python3", "xsstrike.py", "-u", "{target_url}", "--crawl", "-l", "3"], "cwd": "XSStrike", "timeout": 180},
        ],
    },
    {
        "id": "ddos",
        "name": "DDoS Analysis",
        "name_ar": "تحليل DDoS",
        "tools": [
            {"name": "Slowloris Analyzer", "cmd": ["python3", os.path.join(SCRIPTS_DIR, "slowloris_analyzer.py"), "--target", "{target}", "--port", "{port}"], "cwd": None, "timeout": 120},
        ],
    },
    {
        "id": "cmdi",
        "name": "Command Injection",
        "name_ar": "حقن الأوامر",
        "tools": [
            {"name": "Commix", "cmd": ["python3", "commix.py", "--url", "{target_url}", "--batch", "--crawl=2"], "cwd": "commix", "timeout": 180},
        ],
    },
]

@app.route("/api/workflow/start", methods=["POST"])
def api_workflow_start():
    global workflow_state
    data = request.json or {}
    target = data.get("target", "").strip()
    port = data.get("port", "80").strip() or "80"

    if not target:
        return jsonify({"error": "Target is required | الهدف مطلوب"}), 400

    if not validate_input(target, "hostname"):
        return jsonify({"error": "Invalid target hostname/IP | اسم المضيف أو عنوان IP غير صالح"}), 400

    if port and not validate_input(port, "port"):
        return jsonify({"error": "Invalid port number | رقم المنفذ غير صالح"}), 400

    if workflow_state.get("status") == "running":
        return jsonify({"error": "A workflow is already running | يوجد سير عمل قيد التشغيل بالفعل"}), 400

    if target.startswith("http"):
        target_url = target
    elif port == "443" or port == "8443":
        target_url = f"https://{target}"
    elif port == "80":
        target_url = f"http://{target}"
    else:
        target_url = f"http://{target}:{port}"
    target_host = re.sub(r'^https?://', '', target).split('/')[0].split(':')[0]

    workflow_id = str(uuid.uuid4())[:8]
    workflow_state = {
        "id": workflow_id,
        "status": "running",
        "target": target,
        "target_url": target_url,
        "target_host": target_host,
        "port": port,
        "current_phase": 0,
        "phases": [],
        "skip_requested": False,
        "stop_requested": False,
    }

    for phase in WORKFLOW_PHASES:
        workflow_state["phases"].append({
            "id": phase["id"],
            "name": phase["name"],
            "name_ar": phase["name_ar"],
            "status": "pending",
            "output": [],
            "process": None,
        })

    def run_workflow():
        for i, phase_def in enumerate(WORKFLOW_PHASES):
            if workflow_state.get("stop_requested"):
                workflow_state["status"] = "stopped"
                for j in range(i, len(WORKFLOW_PHASES)):
                    if workflow_state["phases"][j]["status"] == "pending":
                        workflow_state["phases"][j]["status"] = "skipped"
                return

            workflow_state["current_phase"] = i
            phase_state = workflow_state["phases"][i]

            if workflow_state.get("skip_requested"):
                workflow_state["skip_requested"] = False
                phase_state["status"] = "skipped"
                phase_state["output"].append(f"Phase skipped by user.\n")
                continue

            phase_state["status"] = "running"
            phase_state["output"].append(f"=== Starting {phase_def['name']} phase ===\n")

            phase_failed = False
            for tool in phase_def["tools"]:
                if workflow_state.get("stop_requested"):
                    break
                if workflow_state.get("skip_requested"):
                    break

                tool_name = tool["name"]
                cmd = []
                for arg in tool["cmd"]:
                    cmd.append(
                        arg.replace("{target}", target_host)
                           .replace("{target_url}", target_url)
                           .replace("{port}", port)
                    )

                phase_state["output"].append(f"\n--- Running {tool_name} ---\n")
                phase_state["output"].append(f"$ {' '.join(cmd)}\n")

                exec_cwd = TOOLS_DIR
                if tool.get("cwd"):
                    exec_cwd = os.path.join(TOOLS_DIR, tool["cwd"])

                tool_timeout = tool.get("timeout", 300)
                try:
                    proc = subprocess.Popen(
                        cmd,
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        cwd=exec_cwd,
                        env={**os.environ, "HOME": os.path.expanduser("~")},
                    )
                    phase_state["process"] = proc
                    tool_start = time.time()

                    for line in proc.stdout:
                        phase_state["output"].append(line)
                        if workflow_state.get("stop_requested") or workflow_state.get("skip_requested"):
                            proc.terminate()
                            break
                        if time.time() - tool_start > tool_timeout:
                            phase_state["output"].append(f"\n⏰ {tool_name} timed out after {tool_timeout}s — terminating.\n")
                            proc.terminate()
                            try:
                                proc.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                proc.kill()
                            break

                    proc.wait(timeout=10)
                    if proc.returncode != 0 and not workflow_state.get("skip_requested"):
                        phase_state["output"].append(f"{tool_name} exited with code {proc.returncode}\n")
                        phase_failed = True
                except FileNotFoundError:
                    phase_state["output"].append(f"Error: {tool_name} not found. Make sure it is installed.\n")
                    phase_failed = True
                except Exception as e:
                    phase_state["output"].append(f"Error running {tool_name}: {str(e)}\n")
                    phase_failed = True
                finally:
                    phase_state["process"] = None

            if workflow_state.get("skip_requested"):
                workflow_state["skip_requested"] = False
                phase_state["status"] = "skipped"
                phase_state["output"].append(f"Phase skipped by user.\n")
            elif workflow_state.get("stop_requested"):
                phase_state["status"] = "stopped"
            elif phase_failed:
                phase_state["status"] = "failed"
                phase_state["output"].append(f"=== {phase_def['name']} phase completed with errors ===\n")
            else:
                phase_state["status"] = "completed"
                phase_state["output"].append(f"=== {phase_def['name']} phase completed ===\n")

        if not workflow_state.get("stop_requested"):
            workflow_state["status"] = "completed"
            workflow_state["current_phase"] = len(WORKFLOW_PHASES)

    t = threading.Thread(target=run_workflow, daemon=True)
    t.start()

    phases_info = [{"id": p["id"], "name": p["name"], "name_ar": p["name_ar"]} for p in WORKFLOW_PHASES]
    return jsonify({"workflow_id": workflow_id, "phases": phases_info})


@app.route("/api/workflow/status")
def api_workflow_status():
    if not workflow_state or not workflow_state.get("id"):
        return jsonify({"error": "No workflow active"}), 404

    phases = []
    for p in workflow_state["phases"]:
        phases.append({
            "id": p["id"],
            "name": p["name"],
            "name_ar": p["name_ar"],
            "status": p["status"],
        })

    return jsonify({
        "id": workflow_state["id"],
        "status": workflow_state["status"],
        "target": workflow_state["target"],
        "port": workflow_state["port"],
        "current_phase": workflow_state["current_phase"],
        "phases": phases,
        "total_phases": len(WORKFLOW_PHASES),
    })


@app.route("/api/workflow/stream/<phase_id>")
def api_workflow_stream(phase_id):
    if not workflow_state or not workflow_state.get("id"):
        return jsonify({"error": "No workflow active"}), 404

    phase = None
    for p in workflow_state["phases"]:
        if p["id"] == phase_id:
            phase = p
            break

    if not phase:
        return jsonify({"error": "Phase not found"}), 404

    def generate():
        last_len = 0
        while True:
            output = phase["output"]
            current_len = len(output)
            if current_len > last_len:
                for line in output[last_len:current_len]:
                    yield f"data: {json.dumps({'line': line})}\n\n"
                last_len = current_len
            if phase["status"] in ("completed", "failed", "skipped", "stopped"):
                yield f"data: {json.dumps({'done': True, 'status': phase['status']})}\n\n"
                break
            if workflow_state.get("status") in ("stopped", "completed"):
                yield f"data: {json.dumps({'done': True, 'status': phase['status']})}\n\n"
                break
            time.sleep(0.3)

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/workflow/skip", methods=["POST"])
def api_workflow_skip():
    if not workflow_state or workflow_state.get("status") != "running":
        return jsonify({"error": "No running workflow"}), 400

    workflow_state["skip_requested"] = True
    current = workflow_state.get("current_phase", 0)
    if current < len(workflow_state["phases"]):
        proc = workflow_state["phases"][current].get("process")
        if proc and proc.poll() is None:
            proc.terminate()

    return jsonify({"status": "skip_requested"})


@app.route("/api/workflow/stop", methods=["POST"])
def api_workflow_stop():
    if not workflow_state or workflow_state.get("status") != "running":
        return jsonify({"error": "No running workflow"}), 400

    workflow_state["stop_requested"] = True
    current = workflow_state.get("current_phase", 0)
    if current < len(workflow_state["phases"]):
        proc = workflow_state["phases"][current].get("process")
        if proc and proc.poll() is None:
            proc.terminate()

    workflow_state["status"] = "stopped"
    return jsonify({"status": "stopped"})


@app.route("/api/workflow/rerun/<phase_id>", methods=["POST"])
def api_workflow_rerun(phase_id):
    if not workflow_state or not workflow_state.get("id"):
        return jsonify({"error": "No workflow active"}), 404

    if workflow_state.get("status") == "running":
        return jsonify({"error": "Workflow is still running"}), 400

    phase_idx = None
    phase_def = None
    for i, p in enumerate(workflow_state["phases"]):
        if p["id"] == phase_id:
            phase_idx = i
            break
    for pd in WORKFLOW_PHASES:
        if pd["id"] == phase_id:
            phase_def = pd
            break

    if phase_idx is None or phase_def is None:
        return jsonify({"error": "Phase not found"}), 404

    target_host = workflow_state["target_host"]
    target_url = workflow_state["target_url"]
    port = workflow_state["port"]

    phase_state = workflow_state["phases"][phase_idx]
    phase_state["status"] = "running"
    phase_state["output"] = [f"=== Re-running {phase_def['name']} phase ===\n"]

    def run_phase():
        phase_failed = False
        for tool in phase_def["tools"]:
            tool_name = tool["name"]
            cmd = []
            for arg in tool["cmd"]:
                cmd.append(
                    arg.replace("{target}", target_host)
                       .replace("{target_url}", target_url)
                       .replace("{port}", port)
                )

            phase_state["output"].append(f"\n--- Running {tool_name} ---\n")
            phase_state["output"].append(f"$ {' '.join(cmd)}\n")

            exec_cwd = TOOLS_DIR
            if tool.get("cwd"):
                exec_cwd = os.path.join(TOOLS_DIR, tool["cwd"])

            try:
                proc = subprocess.Popen(
                    cmd, shell=False, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, bufsize=1,
                    cwd=exec_cwd,
                    env={**os.environ, "HOME": os.path.expanduser("~")},
                )
                phase_state["process"] = proc
                for line in proc.stdout:
                    phase_state["output"].append(line)
                proc.wait(timeout=5)
                if proc.returncode != 0:
                    phase_state["output"].append(f"{tool_name} exited with code {proc.returncode}\n")
                    phase_failed = True
            except FileNotFoundError:
                phase_state["output"].append(f"Error: {tool_name} not found. Make sure it is installed.\n")
                phase_failed = True
            except Exception as e:
                phase_state["output"].append(f"Error running {tool_name}: {str(e)}\n")
                phase_failed = True
            finally:
                phase_state["process"] = None

        phase_state["status"] = "failed" if phase_failed else "completed"
        phase_state["output"].append(f"=== {phase_def['name']} phase {'completed with errors' if phase_failed else 'completed'} ===\n")

    t = threading.Thread(target=run_phase, daemon=True)
    t.start()
    return jsonify({"status": "rerunning"})


@app.route("/api/installed")
def api_installed():
    dirs = []
    try:
        dirs = [d for d in os.listdir(TOOLS_DIR) if os.path.isdir(os.path.join(TOOLS_DIR, d))]
    except Exception:
        pass
    return jsonify({
        "installed_tools": dirs,
        "status": installed_status,
        "tools_dir": TOOLS_DIR,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
