import os
from pathlib import Path
from typing import Dict, List

# -----------------------------------------------------------------------------
# CORE APP METADATA
# -----------------------------------------------------------------------------
APP_NAME = "SafeSurf Security Analyzer"
APP_VERSION = "2.0.0"
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION
# -----------------------------------------------------------------------------
NEO4J_URL = os.environ.get("NEO4J_URL", "bolt://127.0.0.1:7687")    # <-- your active Neo4j bolt URI!
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "123456789")      # <-- your real Neo4j DB password!

NEO4J_MAX_CONNECTION_LIFETIME = int(os.environ.get("NEO4J_MAX_CONN", "3600"))
NEO4J_ENCRYPTED = os.environ.get("NEO4J_ENCRYPTED", "False").lower() == "true"

SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", str(Path(__file__).parent.parent / "data" / "security_analytics.db"))
SQLITE_TIMEOUT = int(os.environ.get("SQLITE_TIMEOUT", "30"))
SQLITE_CHECK_SAME_THREAD = os.environ.get("SQLITE_THREAD_CHECK", "False").lower() == "true"

# -----------------------------------------------------------------------------
# DIRECTORY PATHS
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
FEED_DIR = DATA_DIR / "feeds"
CACHE_DIR = DATA_DIR / "cache"
BACKUP_DIR = DATA_DIR / "backups"
REPORTS_DIR = DATA_DIR / "reports"

for d in [DATA_DIR, FEED_DIR, LOG_DIR, CACHE_DIR, BACKUP_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# THREAT FEED CONFIGURATION
# -----------------------------------------------------------------------------
THREAT_FEEDS = {
    "malware_ips": {
        "url": "https://feodotracker.abuse.ch/downloads/ipblocklist.txt",
        "type": "ip",
        "refresh_interval": 3600,
        "enabled": True
    },
    "phishing_domains": {
        "url": "https://openphish.com/feed.txt",
        "type": "domain",
        "refresh_interval": 1800,
        "enabled": True
    },
    "malware_domains": {
        "url": "https://mirror1.malwaredomains.com/files/justdomains",
        "type": "domain",
        "refresh_interval": 86400,
        "enabled": True
    },
    "suspicious_tlds": {
        "url": "",
        "type": "tld",
        "domains": [".tk", ".ml", ".ga", ".cf", ".xyz", ".top", ".gq"],
        "enabled": True
    }
}

# -----------------------------------------------------------------------------
# RISK & DETECTION SETTINGS
# -----------------------------------------------------------------------------
RISK_SCORING = {
    "high": 8,
    "medium": 5,
    "low": 3,
    "weights": {
        "malicious": 10,
        "suspicious_tld": 3,
        "phishing_keyword": 2,
        "urgency_tactic": 3,
        "url_pattern": 2
    }
}

PHISHING_PATTERNS = [
    {"name": "urgency_tactic", "pattern": r"\b(urgent|immediate|asap|emergency)\b.*\b(click|link|update|verify)\b", "weight": 3},
    {"name": "prize_scam", "pattern": r"\b(win|won|prize|reward|million|billion)\b.*\b(claim|collect|money)\b", "weight": 3},
    {"name": "account_threat", "pattern": r"\b(account|bank|paypal)\b.*\b(suspend|closed|terminate|verify)\b", "weight": 4},
    {"name": "credentials", "pattern": r"\b(login|password|credentials)\b.*\b(verify|update|confirm)\b", "weight": 4},
]

# -----------------------------------------------------------------------------
# ALERTING & UI SETTINGS
# -----------------------------------------------------------------------------
ALERT_CONFIG = {
    "extended_reasons": os.environ.get("SHOW_EXTENDED_REASONS", "True").lower() == "true",
    "desktop_alert": True,
    "browser_integration": True,
    "alert_sound": True
}

UI_CONFIG = {
    "risk_threshold": int(os.environ.get("RISK_THRESHOLD", "2")),
    "theme": os.environ.get("DASHBOARD_THEME", "#355c7d"),
    "dark_mode": True,
    "language": "en",
    "refresh_interval": 300
}

API_CONFIG = {
    "extension_key": os.environ.get("EXTENSION_KEY", "safesurf-prod-v2"),
    "frontend_url": os.environ.get("FRONTEND_API_URL", "http://localhost:8000"),
    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000", "chrome-extension://*"],
    "rate_limit": "100/minute",
    "api_version": "v2"
}

LOGGING_CONFIG = {
    "level": os.environ.get("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s %(levelname)s %(message)s",
    "file_path": str(LOG_DIR / "safesurf.log"),
    "max_file_size": 10485760,
    "backup_count": 5
}

PERFORMANCE_CONFIG = {
    "cache_ttl": 3600,
    "max_cache_size": 1000,
    "feed_download_timeout": 30,
    "db_timeout": 10,
    "compression": True
}

SECURITY_CONFIG = {
    "encrypt_local_data": True,
    "auto_clear_cache": True,
    "cache_clear_interval": 86400,
    "telemetry": False,
    "privacy_mode": False
}

# -----------------------------------------------------------------------------
# CONFIG VALIDATION
# -----------------------------------------------------------------------------
def validate_config() -> List[str]:
    issues = []
    if NEO4J_PASSWORD == "your_secure_password_here":
        issues.append("Neo4j password must be changed for production!")
    for feed, settings in THREAT_FEEDS.items():
        if settings.get("url") and not settings["url"].startswith(("http", "https")) and settings.get("enabled", True):
            issues.append(f"Feed URL for {feed} is not valid: {settings['url']}")
    try:
        test_file = DATA_DIR / ".write_test"
        test_file.touch()
        test_file.unlink()
    except Exception:
        issues.append(f"No write permission in data directory: {DATA_DIR}")
    return issues

CONFIG_ISSUES = validate_config()
if CONFIG_ISSUES and DEBUG:
    print("Config issues:")
    for issue in CONFIG_ISSUES:
        print("⚠️", issue)
