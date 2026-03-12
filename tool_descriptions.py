TOOL_INFO = {
    "anon:Anonymously Surf": {
        "desc_en": "Routes all traffic through Tor network to anonymize your internet connection and hide your IP address.",
        "desc_ar": "يوجه كل حركة المرور عبر شبكة Tor لإخفاء هويتك على الإنترنت وإخفاء عنوان IP الخاص بك.",
        "usage": "Start: anonsurf start | Stop: anonsurf stop | Status: anonsurf status",
    },
    "anon:Multitor": {
        "desc_en": "Creates multiple Tor instances with different exit nodes for load balancing and enhanced anonymity.",
        "desc_ar": "ينشئ عدة نسخ من Tor بعقد خروج مختلفة لتوزيع الحمل وتعزيز إخفاء الهوية.",
        "usage": "Run: multitor --init 5 (creates 5 Tor instances)",
    },
    "info:Network Map (nmap)": {
        "desc_en": "Powerful network scanner for discovering hosts, services, OS detection, and vulnerability scanning on networks.",
        "desc_ar": "أداة فحص شبكات قوية لاكتشاف الأجهزة والخدمات ونظام التشغيل والثغرات على الشبكات.",
        "usage": "Scan: nmap -sV target_ip | OS detect: nmap -O target | Full: nmap -A target",
    },
    "info:Dracnmap": {
        "desc_en": "Provides a menu-driven interface for Nmap with pre-built scan profiles for easier network reconnaissance.",
        "desc_ar": "يوفر واجهة سهلة لـ Nmap مع ملفات فحص جاهزة لتسهيل استطلاع الشبكات.",
        "usage": "Run: python3 dracnmap.py then follow the menu",
    },
    "info:Port scanning": {
        "desc_en": "Scans target hosts for open ports and running services to map the network attack surface.",
        "desc_ar": "يفحص الأجهزة المستهدفة للبحث عن المنافذ المفتوحة والخدمات لرسم خريطة سطح الهجوم.",
        "usage": "nmap -sS target_ip (SYN scan) | nmap -p 1-65535 target (all ports)",
    },
    "info:Host to IP": {
        "desc_en": "Resolves domain names to their IP addresses using DNS lookup for reconnaissance.",
        "desc_ar": "يحول أسماء النطاقات إلى عناوين IP باستخدام استعلام DNS للاستطلاع.",
        "usage": "Enter a domain name and get its IP address",
    },
    "info:Xerosploit": {
        "desc_en": "Performs man-in-the-middle attacks for network analysis including packet sniffing and injection.",
        "desc_ar": "ينفذ هجمات الرجل في المنتصف لتحليل الشبكة بما في ذلك التقاط وحقن الحزم.",
        "usage": "Run: python3 xerosploit.py then select attack module",
    },
    "info:RED HAWK (All In One Scanning)": {
        "desc_en": "All-in-one tool for information gathering, vulnerability scanning, and crawling websites.",
        "desc_ar": "أداة شاملة لجمع المعلومات وفحص الثغرات وزحف المواقع.",
        "usage": "Run: php rhawk.php then enter target URL",
    },
    "info:ReconSpider(For All Scanning)": {
        "desc_en": "OSINT framework for scanning IP addresses, emails, websites, and organizations for public information.",
        "desc_ar": "إطار استخبارات مفتوحة المصدر لفحص عناوين IP والبريد والمواقع والمنظمات.",
        "usage": "Run: python3 reconspider.py then choose scan type",
    },
    "info:IsItDown (Check Website Down/Up)": {
        "desc_en": "Checks if a website is currently up or down by sending HTTP requests and analyzing responses.",
        "desc_ar": "يتحقق مما إذا كان موقع ما يعمل أو متوقف عن طريق إرسال طلبات HTTP وتحليل الردود.",
        "usage": "Enter website URL to check its status",
    },
    "info:Infoga - Email OSINT": {
        "desc_en": "Gathers email account information from different public sources for OSINT investigations.",
        "desc_ar": "يجمع معلومات حسابات البريد الإلكتروني من مصادر عامة مختلفة للتحقيقات الاستخباراتية.",
        "usage": "Run: python3 infoga.py --domain target.com --source all",
    },
    "info:ReconDog": {
        "desc_en": "Reconnaissance tool that performs various OSINT lookups including Censys, NS lookup, and port scanning.",
        "desc_ar": "أداة استطلاع تقوم بعمليات بحث مختلفة بما في ذلك Censys و NS وفحص المنافذ.",
        "usage": "Run: python3 dog.py then choose scan type from menu",
    },
    "info:Striker": {
        "desc_en": "Offensive information and vulnerability scanner that checks for common web vulnerabilities.",
        "desc_ar": "ماسح ثغرات هجومي يفحص الثغرات الشائعة في تطبيقات الويب.",
        "usage": "Run: python3 striker.py target_url",
    },
    "info:SecretFinder (like API & etc)": {
        "desc_en": "Discovers sensitive data like API keys, tokens, and credentials in JavaScript files.",
        "desc_ar": "يكتشف البيانات الحساسة مثل مفاتيح API والتوكنات وبيانات الاعتماد في ملفات JavaScript.",
        "usage": "Run: python3 SecretFinder.py -i target_url -e",
    },
    "info:Find Info Using Shodan": {
        "desc_en": "Uses Shodan search engine to find internet-connected devices, servers, and their vulnerabilities.",
        "desc_ar": "يستخدم محرك بحث Shodan للعثور على الأجهزة المتصلة بالإنترنت والخوادم وثغراتها.",
        "usage": "Run: shodan search apache | shodan host target_ip",
    },
    "info:Port Scanner - rang3r": {
        "desc_en": "Fast multi-threaded port scanner that can scan multiple hosts simultaneously.",
        "desc_ar": "ماسح منافذ سريع متعدد الخيوط يمكنه فحص عدة أجهزة في وقت واحد.",
        "usage": "Run: python3 rang3r.py --ip target_ip",
    },
    "info:Breacher": {
        "desc_en": "Finds admin login pages on websites by testing common admin panel paths.",
        "desc_ar": "يبحث عن صفحات تسجيل دخول المدير في المواقع عن طريق اختبار المسارات الشائعة.",
        "usage": "Run: python3 breacher.py -u target_url --type php",
    },
    "wordlist:Cupp": {
        "desc_en": "Generates custom password wordlists based on target's personal information (birthday, pet name, etc).",
        "desc_ar": "ينشئ قوائم كلمات مرور مخصصة بناءً على المعلومات الشخصية للهدف (تاريخ الميلاد، اسم الحيوان الأليف، إلخ).",
        "usage": "Run: python3 cupp.py -i (interactive mode to create wordlist)",
    },
    "wordlist:WordlistCreator": {
        "desc_en": "Creates targeted wordlists from website content by crawling and extracting potential passwords.",
        "desc_ar": "ينشئ قوائم كلمات مستهدفة من محتوى الموقع عن طريق الزحف واستخراج كلمات المرور المحتملة.",
        "usage": "Run: python3 wordlistcreator.py then enter target URL",
    },
    "wordlist:Goblin WordGenerator": {
        "desc_en": "Generates smart wordlists using various techniques like permutations and character substitution.",
        "desc_ar": "ينشئ قوائم كلمات ذكية باستخدام تقنيات مختلفة مثل التبديلات واستبدال الأحرف.",
        "usage": "Run: python3 goblin.py -h for options",
    },
    "wordlist:Password list (1.4 Billion Clear Text Password)": {
        "desc_en": "Downloads massive password database containing 1.4 billion clear text passwords for offline attacks.",
        "desc_ar": "يحمل قاعدة بيانات ضخمة تحتوي على 1.4 مليار كلمة مرور نصية للهجمات بدون اتصال.",
        "usage": "Download and use with tools like Hydra or John the Ripper",
    },
    "wireless:Bluetooth Honeypot GUI Framework": {
        "desc_en": "Creates fake Bluetooth devices to monitor and log connection attempts for security analysis.",
        "desc_ar": "ينشئ أجهزة Bluetooth وهمية لمراقبة وتسجيل محاولات الاتصال لتحليل الأمان.",
        "usage": "Requires Bluetooth hardware. Run the GUI application.",
    },
    "wireless:WiFi-Pumpkin": {
        "desc_en": "Creates rogue access points for man-in-the-middle attacks and wireless network auditing.",
        "desc_ar": "ينشئ نقاط وصول مزيفة لهجمات الرجل في المنتصف ومراجعة الشبكات اللاسلكية.",
        "usage": "Run: wifipumpkin3 then configure AP settings",
    },
    "wireless:pixiewps": {
        "desc_en": "Exploits WPS (Wi-Fi Protected Setup) offline brute force vulnerability to crack WiFi passwords.",
        "desc_ar": "يستغل ثغرة WPS في شبكات WiFi لكسر كلمات المرور بدون اتصال.",
        "usage": "Run: pixiewps -e PKE -r PKR -s EHASH1 -z EHASH2 -a AUTHKEY",
    },
    "wireless:Fluxion": {
        "desc_en": "Creates evil twin access points for capturing WPA/WPA2 passwords through social engineering.",
        "desc_ar": "ينشئ نقاط وصول توأم شريرة لالتقاط كلمات مرور WPA/WPA2 عبر الهندسة الاجتماعية.",
        "usage": "Run: bash fluxion.sh then follow wizard",
    },
    "wireless:Wifiphisher": {
        "desc_en": "Automates phishing attacks against WiFi networks to capture credentials.",
        "desc_ar": "يؤتمت هجمات التصيد ضد شبكات WiFi لالتقاط بيانات الاعتماد.",
        "usage": "Run: wifiphisher --essid 'Target' -p firmware-upgrade",
    },
    "wireless:Wifite": {
        "desc_en": "Automated wireless network auditor that attacks WEP, WPA, and WPS encrypted networks.",
        "desc_ar": "مدقق شبكات لاسلكية آلي يهاجم شبكات WEP و WPA و WPS المشفرة.",
        "usage": "Run: wifite then select target network",
    },
    "wireless:EvilTwin": {
        "desc_en": "Creates fake access points with captive portals to capture credentials.",
        "desc_ar": "ينشئ نقاط وصول مزيفة مع بوابات أسيرة لالتقاط بيانات الاعتماد.",
        "usage": "Run: bash eviltwin.sh then configure settings",
    },
    "wireless:Howmanypeople": {
        "desc_en": "Counts the number of people around you by monitoring WiFi probe requests.",
        "desc_ar": "يحسب عدد الأشخاص من حولك عن طريق مراقبة طلبات WiFi probe.",
        "usage": "Run: python3 howmanypeople.py -i wlan0mon",
    },
    "wireless:Fastssh": {
        "desc_en": "Fast SSH brute force tool for testing SSH server security.",
        "desc_ar": "أداة سريعة لاختبار قوة كلمات مرور خوادم SSH.",
        "usage": "Run: python3 fastssh.py -t target -u user -w wordlist",
    },
    "sql:Sqlmap tool": {
        "desc_en": "Automatic SQL injection detection and exploitation tool. The most powerful SQL injection tool available.",
        "desc_ar": "أداة كشف واستغلال حقن SQL تلقائياً. أقوى أداة حقن SQL متاحة.",
        "usage": "sqlmap -u 'url?id=1' --dbs (find databases) | sqlmap -u 'url?id=1' -D db --tables",
    },
    "sql:NoSqlMap": {
        "desc_en": "Exploits NoSQL database injection vulnerabilities in MongoDB, CouchDB, and Redis.",
        "desc_ar": "يستغل ثغرات حقن قواعد بيانات NoSQL في MongoDB و CouchDB و Redis.",
        "usage": "Run: python3 nosqlmap.py then enter target URL",
    },
    "sql:Damn Small SQLi Scanner": {
        "desc_en": "Lightweight SQL injection vulnerability scanner written in Python.",
        "desc_ar": "ماسح ثغرات حقن SQL خفيف الوزن مكتوب بلغة Python.",
        "usage": "Run: python3 dsss.py -u 'target_url?param=value'",
    },
    "sql:Explo": {
        "desc_en": "Human and machine readable web vulnerability testing format and execution tool.",
        "desc_ar": "أداة اختبار ثغرات الويب بتنسيق قابل للقراءة من الإنسان والآلة.",
        "usage": "Run: explo test_file.yaml (define tests in YAML format)",
    },
    "sql:Blisqy - Exploit Time-based blind-SQL injection": {
        "desc_en": "Exploits time-based blind SQL injection in HTTP headers for data extraction.",
        "desc_ar": "يستغل حقن SQL الأعمى المبني على الوقت في رؤوس HTTP لاستخراج البيانات.",
        "usage": "Run: python3 blisqy.py --server target --port 80 --header 'X-Forwarded-For'",
    },
    "sql:Leviathan - Wide Range Mass Audit Toolkit": {
        "desc_en": "Mass audit toolkit including SQL injection scanning and brute forcing capabilities.",
        "desc_ar": "مجموعة أدوات تدقيق جماعي تشمل فحص حقن SQL وقدرات التخمين.",
        "usage": "Run: python3 leviathan.py then choose audit type",
    },
    "sql:SQLScan": {
        "desc_en": "Automated SQL injection scanner that finds and exploits SQL injection flaws.",
        "desc_ar": "ماسح حقن SQL آلي يكتشف ويستغل عيوب حقن SQL.",
        "usage": "Run: python3 sqlscan.py target_url",
    },
    "phishing:Setoolkit": {
        "desc_en": "Social Engineering Toolkit - the standard framework for social engineering penetration tests.",
        "desc_ar": "مجموعة أدوات الهندسة الاجتماعية - الإطار المعياري لاختبارات اختراق الهندسة الاجتماعية.",
        "usage": "Run: setoolkit then choose attack vector from menu",
    },
    "phishing:SocialFish": {
        "desc_en": "Creates phishing pages for popular sites like Facebook, Google, LinkedIn for credential harvesting.",
        "desc_ar": "ينشئ صفحات تصيد لمواقع شهيرة مثل Facebook و Google و LinkedIn لجمع بيانات الاعتماد.",
        "usage": "Run: python3 SocialFish.py then select template and start server",
    },
    "phishing:HiddenEye": {
        "desc_en": "Advanced phishing tool with 38+ templates and keylogger, IP tracker, and webcam capture.",
        "desc_ar": "أداة تصيد متقدمة مع 38+ قالب ومسجل مفاتيح وتتبع IP والتقاط كاميرا الويب.",
        "usage": "Run: python3 HiddenEye.py then select phishing template",
    },
    "phishing:Evilginx2": {
        "desc_en": "Man-in-the-middle attack framework that bypasses 2FA by proxying login sessions.",
        "desc_ar": "إطار هجوم الرجل في المنتصف الذي يتجاوز المصادقة الثنائية عن طريق توكيل جلسات تسجيل الدخول.",
        "usage": "Run: evilginx2 then configure phishlets and lures",
    },
    "phishing:I-See_You": {
        "desc_en": "Tracks target's real-time location using social engineering and browser geolocation API.",
        "desc_ar": "يتتبع موقع الهدف في الوقت الفعلي باستخدام الهندسة الاجتماعية وواجهة تحديد الموقع.",
        "usage": "Run: bash ISeeYou.sh then share the generated link",
    },
    "phishing:SayCheese": {
        "desc_en": "Captures target's webcam photos through a phishing link using browser camera permissions.",
        "desc_ar": "يلتقط صور كاميرا الهدف عبر رابط تصيد باستخدام أذونات كاميرا المتصفح.",
        "usage": "Run: bash saycheese.sh then share the link with target",
    },
    "phishing:QR Code Jacking": {
        "desc_en": "Creates malicious QR codes that redirect to phishing pages when scanned.",
        "desc_ar": "ينشئ رموز QR خبيثة تعيد التوجيه إلى صفحات تصيد عند مسحها.",
        "usage": "Run: python3 qrjacker.py then configure QR code attack",
    },
    "phishing:ShellPhish": {
        "desc_en": "Phishing tool that generates fake login pages for 18 social media platforms.",
        "desc_ar": "أداة تصيد تنشئ صفحات تسجيل دخول مزيفة لـ 18 منصة تواصل اجتماعي.",
        "usage": "Run: bash shellphish.sh then select platform template",
    },
    "phishing:Pyphisher": {
        "desc_en": "Advanced phishing tool with multiple templates and tunneling options (Ngrok, Serveo).",
        "desc_ar": "أداة تصيد متقدمة مع قوالب متعددة وخيارات أنفاق (Ngrok, Serveo).",
        "usage": "Run: python3 pyphisher.py then select phishing template",
    },
    "phishing:BlackPhish": {
        "desc_en": "Phishing tool with custom templates and email delivery capabilities.",
        "desc_ar": "أداة تصيد مع قوالب مخصصة وقدرات إرسال بريد إلكتروني.",
        "usage": "Run: python3 blackphish.py then configure attack",
    },
    "web:Web2Attack": {
        "desc_en": "Web application attack and auditing framework with SQL injection, XSS, and command injection modules.",
        "desc_ar": "إطار هجوم ومراجعة تطبيقات الويب مع وحدات حقن SQL و XSS وحقن الأوامر.",
        "usage": "Run: python3 w2aconsole then select attack module",
    },
    "web:Skipfish": {
        "desc_en": "Active web application security scanner that creates a sitemap and identifies vulnerabilities.",
        "desc_ar": "ماسح أمان تطبيقات ويب نشط ينشئ خريطة موقع ويحدد الثغرات.",
        "usage": "Run: skipfish -o output_dir target_url",
    },
    "web:SubDomain Finder": {
        "desc_en": "Discovers subdomains of a target domain using various enumeration techniques.",
        "desc_ar": "يكتشف النطاقات الفرعية لنطاق مستهدف باستخدام تقنيات تعداد مختلفة.",
        "usage": "Run: python3 sublist3r.py -d target.com -o output.txt",
    },
    "web:CheckURL": {
        "desc_en": "Scans URLs for potential security threats and malicious content.",
        "desc_ar": "يفحص عناوين URL للتهديدات الأمنية المحتملة والمحتوى الضار.",
        "usage": "Run: python3 checkurl.py target_url",
    },
    "web:Blazy(Also Find ClickJacking)": {
        "desc_en": "Tests login page security by performing brute force attacks on web login forms.",
        "desc_ar": "يختبر أمان صفحة تسجيل الدخول عن طريق تنفيذ هجمات التخمين على نماذج تسجيل الدخول.",
        "usage": "Run: python3 blazy.py then enter target login URL",
    },
    "web:Sub-Domain TakeOver": {
        "desc_en": "Identifies subdomains vulnerable to takeover attacks where DNS points to unclaimed resources.",
        "desc_ar": "يحدد النطاقات الفرعية المعرضة لهجمات الاستيلاء حيث يشير DNS إلى موارد غير مطالب بها.",
        "usage": "Run: python3 takeover.py -d target.com -w subdomains.txt",
    },
    "web:Dirb": {
        "desc_en": "Web content scanner that discovers hidden directories and files on web servers.",
        "desc_ar": "ماسح محتوى ويب يكتشف الأدلة والملفات المخفية على خوادم الويب.",
        "usage": "Run: dirb target_url /usr/share/wordlists/dirb/common.txt",
    },
    "post:Vegile - Ghost In The Shell": {
        "desc_en": "Post-exploitation framework for maintaining persistent access and hiding processes.",
        "desc_ar": "إطار ما بعد الاستغلال للحفاظ على الوصول المستمر وإخفاء العمليات.",
        "usage": "Run: bash vegile.sh then choose persistence method",
    },
    "post:Chrome Keylogger": {
        "desc_en": "Extracts saved passwords and browsing data from Chrome browser for post-exploitation.",
        "desc_ar": "يستخرج كلمات المرور المحفوظة وبيانات التصفح من متصفح Chrome لما بعد الاستغلال.",
        "usage": "Run: python3 keylogger.py (on target machine)",
    },
    "forensic:Autopsy": {
        "desc_en": "Digital forensics platform for analyzing hard drives, smartphones, and media storage.",
        "desc_ar": "منصة تحليل جنائي رقمي لتحليل الأقراص الصلبة والهواتف ووسائط التخزين.",
        "usage": "Run: autopsy then open browser to localhost:9999",
    },
    "forensic:Wireshark": {
        "desc_en": "Network protocol analyzer that captures and inspects network traffic in real-time.",
        "desc_ar": "محلل بروتوكولات الشبكة يلتقط ويفحص حركة مرور الشبكة في الوقت الفعلي.",
        "usage": "Run: wireshark (GUI) or tshark -i eth0 (CLI)",
    },
    "forensic:Bulk extractor": {
        "desc_en": "Extracts useful information like emails, URLs, credit card numbers from disk images.",
        "desc_ar": "يستخرج معلومات مفيدة مثل البريد والعناوين وأرقام البطاقات من صور الأقراص.",
        "usage": "Run: bulk_extractor -o output_dir disk_image.dd",
    },
    "forensic:Disk Clone and ISO Image Acquire": {
        "desc_en": "Creates forensic disk clones and ISO images for evidence preservation.",
        "desc_ar": "ينشئ نسخ أقراص جنائية وصور ISO للحفاظ على الأدلة.",
        "usage": "Run: dd if=/dev/sda of=image.dd bs=4M status=progress",
    },
    "forensic:Toolsley": {
        "desc_en": "Online forensic tools for file identification, hash calculation, and binary analysis.",
        "desc_ar": "أدوات جنائية عبر الإنترنت لتحديد الملفات وحساب التجزئة والتحليل الثنائي.",
        "usage": "Visit: toolsley.com for online forensic analysis tools",
    },
    "payload:The FatRat": {
        "desc_en": "Generates undetectable backdoor payloads for Windows, Linux, Mac, and Android.",
        "desc_ar": "ينشئ حمولات أبواب خلفية غير قابلة للكشف لـ Windows و Linux و Mac و Android.",
        "usage": "Run: fatrat then choose payload type from menu",
    },
    "payload:Brutal": {
        "desc_en": "Creates various payloads for Teensy-like hardware attacks (USB rubber ducky).",
        "desc_ar": "ينشئ حمولات متنوعة لهجمات الأجهزة مثل USB rubber ducky.",
        "usage": "Run: python3 brutal.py then select payload type",
    },
    "payload:Stitch": {
        "desc_en": "Cross-platform remote administration tool (RAT) with multi-OS support.",
        "desc_ar": "أداة إدارة عن بعد عبر المنصات مع دعم أنظمة تشغيل متعددة.",
        "usage": "Run: python3 main.py then configure listener/payload",
    },
    "payload:MSFvenom Payload Creator": {
        "desc_en": "Simplifies MSFvenom payload generation with an easy-to-use interface.",
        "desc_ar": "يبسط إنشاء حمولات MSFvenom بواجهة سهلة الاستخدام.",
        "usage": "Run: bash msfpc.sh windows (generates Windows payload)",
    },
    "payload:Venom Shellcode Generator": {
        "desc_en": "Generates shellcode and payloads that bypass antivirus detection.",
        "desc_ar": "ينشئ كود shell وحمولات تتجاوز الكشف من برامج مكافحة الفيروسات.",
        "usage": "Run: bash venom.sh then choose payload format",
    },
    "payload:Spycam": {
        "desc_en": "Captures webcam streams remotely through generated payloads.",
        "desc_ar": "يلتقط بث كاميرا الويب عن بعد من خلال الحمولات المولدة.",
        "usage": "Run: python3 spycam.py then generate webcam payload",
    },
    "payload:Mob-Droid": {
        "desc_en": "Generates Android payloads for remote device administration and monitoring.",
        "desc_ar": "ينشئ حمولات Android للإدارة عن بعد والمراقبة.",
        "usage": "Run: bash Mob-Droid.sh then configure Android payload",
    },
    "payload:Enigma": {
        "desc_en": "Multi-platform payload dropper with AV bypass capabilities.",
        "desc_ar": "أداة إسقاط حمولات متعددة المنصات مع قدرات تجاوز مكافحة الفيروسات.",
        "usage": "Run: python3 enigma.py then select target platform",
    },
    "exploit:RouterSploit": {
        "desc_en": "Exploitation framework for embedded devices and routers with scanner modules.",
        "desc_ar": "إطار استغلال للأجهزة المدمجة والراوترات مع وحدات فحص.",
        "usage": "Run: rsf > use scanners/autopwn > set target IP > run",
    },
    "exploit:WebSploit": {
        "desc_en": "Advanced MITM framework with network attack modules and social engineering.",
        "desc_ar": "إطار هجوم الرجل في المنتصف المتقدم مع وحدات هجوم الشبكة والهندسة الاجتماعية.",
        "usage": "Run: websploit then use module > set target > run",
    },
    "exploit:Commix": {
        "desc_en": "Automated command injection exploitation tool for web applications.",
        "desc_ar": "أداة استغلال حقن الأوامر الآلية لتطبيقات الويب.",
        "usage": "Run: python3 commix.py -u 'target_url?param=value'",
    },
    "exploit:Android Debug Bridge": {
        "desc_en": "Command-line tool for communicating with and controlling Android devices.",
        "desc_ar": "أداة سطر أوامر للتواصل مع أجهزة Android والتحكم بها.",
        "usage": "Run: adb devices | adb shell | adb install app.apk",
    },
    "reverse:Androguard": {
        "desc_en": "Reverse engineering and analysis tool for Android APK files.",
        "desc_ar": "أداة هندسة عكسية وتحليل لملفات APK الخاصة بـ Android.",
        "usage": "Run: androguard analyze app.apk (Python library for APK analysis)",
    },
    "reverse:Apk2Gold": {
        "desc_en": "Decompiles Android APK files to readable Java source code.",
        "desc_ar": "يفكك ملفات APK الخاصة بـ Android إلى كود مصدر Java قابل للقراءة.",
        "usage": "Run: apk2gold app.apk (decompiles to Java source)",
    },
    "reverse:JadX": {
        "desc_en": "Produces Java source code from Android DEX and APK files with a GUI.",
        "desc_ar": "ينتج كود مصدر Java من ملفات DEX و APK الخاصة بـ Android مع واجهة رسومية.",
        "usage": "Run: jadx-gui app.apk (opens GUI decompiler)",
    },
    "ddos:SlowLoris": {
        "desc_en": "Low-bandwidth DoS attack that keeps many connections open to the target web server.",
        "desc_ar": "هجوم حجب خدمة منخفض النطاق الترددي يبقي العديد من الاتصالات مفتوحة للخادم المستهدف.",
        "usage": "Run: slowloris target_ip -p 80 -s 200 (200 sockets on port 80)",
    },
    "ddos:Asyncrone | Multifunction SYN Flood DDoS Weapon": {
        "desc_en": "Multi-function SYN flood DDoS tool that sends intense SYN packets to disable target systems.",
        "desc_ar": "أداة DDoS متعددة الوظائف ترسل حزم SYN مكثفة لتعطيل الأنظمة المستهدفة.",
        "usage": "Run: ./aSYNcrone target_ip target_port source_port",
    },
    "ddos:UFOnet": {
        "desc_en": "DDoS toolkit that uses open redirect vulnerabilities on third-party sites to attack targets.",
        "desc_ar": "مجموعة أدوات DDoS تستخدم ثغرات إعادة التوجيه المفتوحة في مواقع طرف ثالث لمهاجمة الأهداف.",
        "usage": "Run: python3 ufonet.py --attack target_url",
    },
    "ddos:GoldenEye": {
        "desc_en": "HTTP DoS attack tool that uses KeepAlive, Cache-Control, and unique requests to exhaust servers.",
        "desc_ar": "أداة هجوم حجب خدمة HTTP تستخدم KeepAlive و Cache-Control وطلبات فريدة لإنهاك الخوادم.",
        "usage": "Run: python3 goldeneye.py target_url -w 50 -s 10",
    },
    "ddos:SaphyraDDoS": {
        "desc_en": "Multi-threaded DDoS tool for stress testing web servers.",
        "desc_ar": "أداة DDoS متعددة الخيوط لاختبار ضغط خوادم الويب.",
        "usage": "Run: python3 saphyra.py target_url",
    },
    "ddos:Slowloris Vulnerability Analyzer": {
        "desc_en": "Analyzes a web server for vulnerability to Slowloris-style HTTP slow request attacks. Performs 8 non-destructive security checks: HTTP header timeout, per-IP connection limits, rate limiting, WAF detection, server architecture analysis, reverse proxy detection, CDN/traffic filtering, and keep-alive configuration. Provides color-coded results (PASS/WARN/FAIL) and specific remediation recommendations.",
        "desc_ar": "يحلل خادم الويب للكشف عن الثغرات الأمنية ضد هجمات Slowloris البطيئة. يجري 8 فحوصات أمنية غير مدمرة: مهلة رؤوس HTTP، حدود الاتصال لكل عنوان IP، تحديد معدل الطلبات، كشف جدار حماية التطبيقات، تحليل بنية الخادم، كشف الوكيل العكسي، كشف شبكة CDN، وإعدادات الاتصال المستمر. يقدم نتائج ملونة (نجاح/تحذير/فشل) وتوصيات إصلاح محددة.",
        "usage": "Run: python3 scripts/slowloris_analyzer.py --target example.com --port 80",
    },
    "rat:Stitch": {
        "desc_en": "Cross-platform python RAT for Windows, Mac, and Linux with file management, keylogging, and screenshots.",
        "desc_ar": "أداة تحكم عن بعد عبر المنصات لـ Windows و Mac و Linux مع إدارة الملفات وتسجيل المفاتيح ولقطات الشاشة.",
        "usage": "Run: python3 main.py then set up listener and generate payload",
    },
    "xss:DalFox (Finder of XSS)": {
        "desc_en": "Fast parameter analysis and XSS scanning tool written in Go with smart payload generation.",
        "desc_ar": "أداة تحليل معلمات سريعة وفحص XSS مكتوبة بـ Go مع توليد حمولات ذكية.",
        "usage": "Run: dalfox url target_url -b your_server",
    },
    "xss:XSS Payload Generator": {
        "desc_en": "Generates various XSS payloads for bypassing filters and WAFs.",
        "desc_ar": "ينشئ حمولات XSS متنوعة لتجاوز الفلاتر وجدران الحماية.",
        "usage": "Run: python3 xss_payload_generator.py then select payload type",
    },
    "xss:XSpear": {
        "desc_en": "Powerful XSS scanning and parameter analysis tool with pattern matching.",
        "desc_ar": "أداة فحص XSS وتحليل معلمات قوية مع مطابقة الأنماط.",
        "usage": "Run: xspear -u 'target_url?param=value' -v 1",
    },
    "xss:RVuln": {
        "desc_en": "Multi-threaded web vulnerability scanner for XSS, SQL injection, and open redirects.",
        "desc_ar": "ماسح ثغرات ويب متعدد الخيوط لـ XSS وحقن SQL وإعادة التوجيه المفتوحة.",
        "usage": "Run: python3 rvuln.py -u target_url",
    },
    "xss:XSS-Freak": {
        "desc_en": "XSS scanner with a collection of handcrafted payloads for thorough testing.",
        "desc_ar": "ماسح XSS مع مجموعة من الحمولات المصنوعة يدوياً للاختبار الشامل.",
        "usage": "Run: python3 xss-freak.py -u 'target_url'",
    },
    "xss:XSSCon": {
        "desc_en": "Simple and powerful XSS scanner that crawls websites and tests for reflected XSS.",
        "desc_ar": "ماسح XSS بسيط وقوي يزحف على المواقع ويختبر XSS المنعكس.",
        "usage": "Run: python3 xsscon.py -u target_url",
    },
    "xss:XanXSS": {
        "desc_en": "WAF bypass XSS tool that uses various encoding techniques to evade security filters.",
        "desc_ar": "أداة XSS لتجاوز WAF تستخدم تقنيات ترميز مختلفة للتهرب من فلاتر الأمان.",
        "usage": "Run: python3 xanxss.py -u 'target_url'",
    },
    "xss:Advanced XSS Detection Suite": {
        "desc_en": "Comprehensive XSS testing framework with automated scanning and reporting.",
        "desc_ar": "إطار اختبار XSS شامل مع فحص آلي وتقارير.",
        "usage": "Run: python3 xss_scanner.py -u target_url",
    },
    "xss:Extended XSS Searcher and Finder": {
        "desc_en": "Searches for XSS vulnerabilities using various techniques including DOM-based and reflected XSS.",
        "desc_ar": "يبحث عن ثغرات XSS باستخدام تقنيات مختلفة بما في ذلك XSS المبني على DOM والمنعكس.",
        "usage": "Run: python3 xss_finder.py -u target_url",
    },
    "stego:StegoCracker": {
        "desc_en": "Cracks steganography passwords by brute forcing with wordlists.",
        "desc_ar": "يكسر كلمات مرور إخفاء المعلومات عن طريق التخمين باستخدام قوائم الكلمات.",
        "usage": "Run: stegocracker image.jpg wordlist.txt",
    },
    "stego:SteganoHide": {
        "desc_en": "Hides and extracts data within images, audio, and video files using steganography.",
        "desc_ar": "يخفي ويستخرج البيانات داخل ملفات الصور والصوت والفيديو باستخدام إخفاء المعلومات.",
        "usage": "Hide: steghide embed -cf cover.jpg -ef secret.txt | Extract: steghide extract -sf cover.jpg",
    },
    "stego:StegnoCracker": {
        "desc_en": "Brute force tool for cracking steganography passwords hidden in files.",
        "desc_ar": "أداة قوة غاشمة لكسر كلمات مرور إخفاء المعلومات المخفية في الملفات.",
        "usage": "Run: stegcracker image.jpg wordlist.txt",
    },
    "stego:Whitespace": {
        "desc_en": "Hides messages in whitespace characters (spaces and tabs) within text files.",
        "desc_ar": "يخفي الرسائل في أحرف المسافات البيضاء (المسافات وعلامات التبويب) داخل الملفات النصية.",
        "usage": "Run: snow -C -m 'secret message' -p password input.txt output.txt",
    },
    "other:SocialMedia Bruteforce": {
        "desc_en": "Collection of brute force tools for testing social media account security.",
        "desc_ar": "مجموعة أدوات تخمين كلمات المرور لاختبار أمان حسابات التواصل الاجتماعي.",
        "usage": "Select a sub-tool: Instagram, Facebook, or AllInOne attack",
    },
    "other:Instagram Attack": {
        "desc_en": "Tests Instagram account security through brute force login attempts.",
        "desc_ar": "يختبر أمان حساب Instagram من خلال محاولات تسجيل دخول بالتخمين.",
        "usage": "Run: python3 instagram.py -u username -w wordlist.txt",
    },
    "other:Facebook Attack": {
        "desc_en": "Tests Facebook account security through automated login testing.",
        "desc_ar": "يختبر أمان حساب Facebook من خلال اختبار تسجيل الدخول الآلي.",
        "usage": "Run: python3 facebook.py -u username -w wordlist.txt",
    },
    "other:AllinOne SocialMedia Attack": {
        "desc_en": "Multi-platform social media brute force tool supporting multiple platforms.",
        "desc_ar": "أداة تخمين متعددة المنصات تدعم عدة منصات تواصل اجتماعي.",
        "usage": "Run: python3 allinone.py then select platform",
    },
    "other:Application Checker": {
        "desc_en": "Checks installed applications for known vulnerabilities and outdated versions.",
        "desc_ar": "يتحقق من التطبيقات المثبتة بحثاً عن ثغرات معروفة وإصدارات قديمة.",
        "usage": "Run: python3 checker.py then enter application path",
    },
    "other:Android Hacking tools": {
        "desc_en": "Collection of tools for Android security testing and exploitation.",
        "desc_ar": "مجموعة أدوات لاختبار أمان Android واستغلال الثغرات.",
        "usage": "Select a sub-tool: Keydroid, MySMS, Lockphish, DroidCam, or EvilApp",
    },
    "other:Keydroid": {
        "desc_en": "Android keylogger that records all keystrokes on the target device.",
        "desc_ar": "مسجل مفاتيح Android يسجل جميع ضغطات المفاتيح على الجهاز المستهدف.",
        "usage": "Run: python3 keydroid.py then install APK on target",
    },
    "other:MySMS": {
        "desc_en": "Reads and manages SMS messages from Android devices remotely.",
        "desc_ar": "يقرأ ويدير رسائل SMS من أجهزة Android عن بعد.",
        "usage": "Run: python3 mysms.py with target device connected via ADB",
    },
    "other:Lockphish (Grab target LOCK PIN)": {
        "desc_en": "Captures target's phone lock screen PIN through a phishing page.",
        "desc_ar": "يلتقط رمز PIN لشاشة قفل هاتف الهدف من خلال صفحة تصيد.",
        "usage": "Run: bash lockphish.sh then share link with target",
    },
    "other:DroidCam (Capture Image)": {
        "desc_en": "Captures images from Android device camera remotely.",
        "desc_ar": "يلتقط صور من كاميرا جهاز Android عن بعد.",
        "usage": "Run: python3 droidcam.py with target device",
    },
    "other:EvilApp (Hijack Session)": {
        "desc_en": "Creates malicious Android apps that can hijack user sessions.",
        "desc_ar": "ينشئ تطبيقات Android خبيثة يمكنها خطف جلسات المستخدم.",
        "usage": "Run: python3 evilapp.py then generate malicious APK",
    },
    "other:HatCloud(Bypass CloudFlare for IP)": {
        "desc_en": "Discovers the real IP address of websites behind CloudFlare protection.",
        "desc_ar": "يكتشف عنوان IP الحقيقي للمواقع المحمية بـ CloudFlare.",
        "usage": "Run: ruby hatcloud.rb -b target.com",
    },
    "other:IDN Homograph Attack": {
        "desc_en": "Creates IDN homograph phishing domains that look identical to legitimate ones.",
        "desc_ar": "ينشئ نطاقات تصيد متجانسة IDN تبدو مطابقة للنطاقات الشرعية.",
        "usage": "Select EvilURL sub-tool to generate homograph URLs",
    },
    "other:EvilURL": {
        "desc_en": "Generates Unicode domain names that look identical to legitimate URLs for phishing.",
        "desc_ar": "ينشئ أسماء نطاقات Unicode تبدو مطابقة لعناوين URL الشرعية للتصيد.",
        "usage": "Run: python3 evilurl.py then enter target domain",
    },
    "other:Email Verify tools": {
        "desc_en": "Verifies if email addresses are valid and exist on mail servers.",
        "desc_ar": "يتحقق مما إذا كانت عناوين البريد الإلكتروني صالحة وموجودة على خوادم البريد.",
        "usage": "Select Knockmail sub-tool to verify emails",
    },
    "other:Knockmail": {
        "desc_en": "Verifies email addresses by connecting to SMTP servers without sending emails.",
        "desc_ar": "يتحقق من عناوين البريد عن طريق الاتصال بخوادم SMTP بدون إرسال رسائل.",
        "usage": "Run: python3 knockmail.py -e target@email.com",
    },
    "other:Hash cracking tools": {
        "desc_en": "Tools for cracking various hash types (MD5, SHA, NTLM, etc).",
        "desc_ar": "أدوات لكسر أنواع مختلفة من التجزئة (MD5, SHA, NTLM, إلخ).",
        "usage": "Select Hash Buster sub-tool to crack hashes",
    },
    "other:Hash Buster": {
        "desc_en": "Cracks password hashes using online hash databases without brute force.",
        "desc_ar": "يكسر تجزئات كلمات المرور باستخدام قواعد بيانات التجزئة عبر الإنترنت بدون تخمين.",
        "usage": "Run: python3 hash.py -s hash_value (auto-detects hash type)",
    },
    "other:Wifi Deauthenticate": {
        "desc_en": "Disconnects devices from WiFi networks by sending deauthentication frames.",
        "desc_ar": "يقطع اتصال الأجهزة من شبكات WiFi عن طريق إرسال إطارات إلغاء المصادقة.",
        "usage": "Select WifiJammer-NG or KawaiiDeauther sub-tool",
    },
    "other:WifiJammer-NG": {
        "desc_en": "Continuously jams all WiFi clients and access points within range.",
        "desc_ar": "يشوش باستمرار على جميع عملاء WiFi ونقاط الوصول في النطاق.",
        "usage": "Run: python3 wifijammer.py -i wlan0mon",
    },
    "other:KawaiiDeauther": {
        "desc_en": "User-friendly WiFi deauthentication tool with a simple interface.",
        "desc_ar": "أداة إلغاء مصادقة WiFi سهلة الاستخدام بواجهة بسيطة.",
        "usage": "Run: python3 kawaii-deauther.py then select target",
    },
    "other:SocialMedia Finder": {
        "desc_en": "Collection of tools to find social media accounts by username, email, or photo.",
        "desc_ar": "مجموعة أدوات للعثور على حسابات التواصل الاجتماعي حسب اسم المستخدم أو البريد أو الصورة.",
        "usage": "Select a sub-tool: Sherlock, SocialScan, or Facial Recognition",
    },
    "other:Sherlock": {
        "desc_en": "Finds social media accounts by username across 300+ platforms worldwide.",
        "desc_ar": "يبحث عن حسابات التواصل الاجتماعي حسب اسم المستخدم عبر 300+ منصة حول العالم.",
        "usage": "Run: python3 -m sherlock username (searches all platforms)",
    },
    "other:SocialScan | Username or Email": {
        "desc_en": "Checks username and email availability across social media platforms.",
        "desc_ar": "يتحقق من توفر اسم المستخدم والبريد الإلكتروني عبر منصات التواصل الاجتماعي.",
        "usage": "Run: socialscan username email@test.com",
    },
    "other:Find SocialMedia By Facial Recognation System": {
        "desc_en": "Uses facial recognition to find social media profiles matching a person's photo.",
        "desc_ar": "يستخدم التعرف على الوجه للعثور على ملفات التواصل الاجتماعي المطابقة لصورة شخص.",
        "usage": "Run: python3 social_mapper.py -f imagefolder -i 'name' -m fast",
    },
    "other:Find SocialMedia By UserName": {
        "desc_en": "Searches for social media profiles using a specific username across platforms.",
        "desc_ar": "يبحث عن ملفات التواصل الاجتماعي باستخدام اسم مستخدم محدد عبر المنصات.",
        "usage": "Run: python3 finduser.py username",
    },
    "other:Payload Injector": {
        "desc_en": "Injects payloads into files for security testing purposes.",
        "desc_ar": "يحقن حمولات في الملفات لأغراض اختبار الأمان.",
        "usage": "Select Debinject or Pixload sub-tool",
    },
    "other:Debinject": {
        "desc_en": "Injects payloads into Debian packages (.deb files) for trojan creation.",
        "desc_ar": "يحقن حمولات في حزم Debian (ملفات .deb) لإنشاء أحصنة طروادة.",
        "usage": "Run: python3 debinject.py -a payload.deb",
    },
    "other:Pixload": {
        "desc_en": "Creates image files with embedded payloads for XSS and other web attacks.",
        "desc_ar": "ينشئ ملفات صور مع حمولات مدمجة لهجمات XSS وهجمات ويب أخرى.",
        "usage": "Run: python3 pixload.py -p payload -o output.png",
    },
    "other:Web crawling": {
        "desc_en": "Tools for crawling and mapping website structures.",
        "desc_ar": "أدوات للزحف على المواقع ورسم خريطة هياكلها.",
        "usage": "Select Gospider sub-tool for web crawling",
    },
    "other:Gospider": {
        "desc_en": "Fast web crawling tool written in Go for discovering URLs and endpoints.",
        "desc_ar": "أداة زحف ويب سريعة مكتوبة بـ Go لاكتشاف عناوين URL ونقاط النهاية.",
        "usage": "Run: gospider -s target_url -d 3 (depth 3 crawl)",
    },
    "other:Mix tools": {
        "desc_en": "Miscellaneous utility tools for various tasks.",
        "desc_ar": "أدوات مساعدة متنوعة لمهام مختلفة.",
        "usage": "Select a sub-tool from the list",
    },
    "other:Terminal Multiplexer": {
        "desc_en": "Manages multiple terminal sessions in one window (tmux/screen).",
        "desc_ar": "يدير عدة جلسات طرفية في نافذة واحدة (tmux/screen).",
        "usage": "Run: tmux new -s session_name | tmux attach -t session_name",
    },
    "other:Crivo": {
        "desc_en": "URL parameter filtering and organization tool for pentesters.",
        "desc_ar": "أداة تصفية وتنظيم معلمات URL لمختبري الاختراق.",
        "usage": "Run: python3 crivo.py -u url_list.txt -o output.txt",
    },
    "manager:Update Tool or System": {
        "desc_en": "Updates all installed hacking tools to their latest versions.",
        "desc_ar": "يحدث جميع أدوات الاختراق المثبتة إلى أحدث إصداراتها.",
        "usage": "Click Run to update all tools",
    },
    "manager:Uninstall HackingTool": {
        "desc_en": "Removes HackingTool and all installed tools from the system.",
        "desc_ar": "يزيل HackingTool وجميع الأدوات المثبتة من النظام.",
        "usage": "Click Run to uninstall (WARNING: removes everything)",
    },
    "exploit:Web2Attack": {
        "desc_en": "Web application attack and auditing framework with SQL injection, XSS, and command injection modules.",
        "desc_ar": "إطار هجوم ومراجعة تطبيقات الويب مع وحدات حقن SQL و XSS وحقن الأوامر.",
        "usage": "Run: python3 w2aconsole then select attack module",
    },
    "phishing:AdvPhishing": {
        "desc_en": "Advanced phishing tool with modern templates and multiple tunneling options.",
        "desc_ar": "أداة تصيد متقدمة مع قوالب حديثة وخيارات أنفاق متعددة.",
        "usage": "Run: bash advphishing.sh then select phishing template",
    },
    "phishing:Autophisher RK": {
        "desc_en": "Automated phishing tool that generates login pages for credential harvesting.",
        "desc_ar": "أداة تصيد آلية تنشئ صفحات تسجيل دخول لجمع بيانات الاعتماد.",
        "usage": "Run: python3 autophisher.py then select target platform",
    },
    "phishing:BlackEye": {
        "desc_en": "Phishing tool with 38 website templates for creating convincing phishing pages.",
        "desc_ar": "أداة تصيد مع 38 قالب موقع لإنشاء صفحات تصيد مقنعة.",
        "usage": "Run: bash blackeye.sh then select template",
    },
    "phishing:Thanos": {
        "desc_en": "Multi-platform phishing tool with social engineering attack vectors.",
        "desc_ar": "أداة تصيد متعددة المنصات مع متجهات هجوم الهندسة الاجتماعية.",
        "usage": "Run: python3 thanos.py then configure attack",
    },
    "phishing:QRLJacking": {
        "desc_en": "Exploits QR code login systems to hijack user sessions via social engineering.",
        "desc_ar": "يستغل أنظمة تسجيل الدخول بـ QR لاختطاف جلسات المستخدم عبر الهندسة الاجتماعية.",
        "usage": "Run: python3 qrljacker.py then share QR code with target",
    },
    "phishing:Miskphish": {
        "desc_en": "Simple phishing tool for creating customizable phishing pages.",
        "desc_ar": "أداة تصيد بسيطة لإنشاء صفحات تصيد قابلة للتخصيص.",
        "usage": "Run: bash miskphish.sh then select template",
    },
    "rat:Pyshell": {
        "desc_en": "Python-based reverse shell handler for remote command execution.",
        "desc_ar": "معالج shell عكسي مبني على Python لتنفيذ الأوامر عن بعد.",
        "usage": "Run: python3 pyshell.py --lhost your_ip --lport port",
    },
}

EXTRA_FALLBACK_RUN = {
    "info:Network Map (nmap)": ["nmap --help"],
    "info:SecretFinder (like API & etc)": ["cd SecretFinder && python3 SecretFinder.py -h"],
    "info:Find Info Using Shodan": ["python3 -c \"import shodan; print('Shodan module ready. Use: shodan search <query>')\""],
    "sql:Damn Small SQLi Scanner": ["cd dsss && python3 dsss.py -h"],
    "sql:Explo": ["cd explo && python3 -m explo -h"],
    "sql:Blisqy - Exploit Time-based blind-SQL injection": ["cd Blisqy && python3 blisqy.py -h"],
    "web:Sub-Domain TakeOver": ["cd subdomain-takeover && python3 takeover.py -h"],
    "forensic:Autopsy": ["echo 'Autopsy - Digital Forensics Platform. Requires GUI. Visit: https://www.autopsy.com'"],
    "forensic:Wireshark": ["echo 'Wireshark - Network Protocol Analyzer. Run: tshark -i any -c 10 (CLI mode)'"],
    "forensic:Bulk extractor": ["echo 'Bulk Extractor - Forensic data extraction. Run: bulk_extractor -h'"],
    "forensic:Toolsley": ["echo 'Toolsley - Online forensic tools. Visit: https://www.toolsley.com'"],
    "reverse:Androguard": ["python3 -c \"import androguard; print('Androguard ready. Use: androguard analyze app.apk')\""],
    "reverse:JadX": ["echo 'JadX - Android APK Decompiler. Run: jadx-gui app.apk'"],
    "xss:Advanced XSS Detection Suite": ["cd xss-detection-suite && python3 xss_scanner.py -h"],
    "other:Pixload": ["cd pixload && python3 pixload.py -h"],
    "other:Gospider": ["echo 'Gospider - Web crawler (Go). Run: gospider -s url -d 3'"],
    "other:Terminal Multiplexer": ["echo 'Terminal Multiplexer: Use tmux or screen'"],
    "other:Crivo": ["cd crivo && python3 crivo.py -h"],
    "manager:Update Tool or System": ["echo 'Update system: pip install --upgrade pip && cd installed_tools && for d in */; do (cd $d && git pull 2>/dev/null); done'"],
    "manager:Uninstall HackingTool": ["echo 'To uninstall, delete the installed_tools directory'"],
}
