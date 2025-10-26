import requests
import config
import os
import time
import logging
from pathlib import Path

FEED_DIR = config.FEED_DIR if hasattr(config, "FEED_DIR") else Path(__file__).parent.parent / "data" / "feeds"

def safe_download(url, retries=3, timeout=10):
    for i in range(retries):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                return resp.text
            time.sleep(1)
        except Exception as e:
            logging.warning(f"Feed download failed for {url}: {e}")
            time.sleep(2)
    return ""

def fetch_abusech_ips():
    raw = safe_download(config.THREAT_FEEDS["malware_ips"]["url"])
    ips = [line.strip() for line in raw.splitlines() if line and not line.startswith("#")]
    return [ip for ip in ips if ip.count('.') == 3]

def fetch_openphish_domains():
    raw = safe_download(config.THREAT_FEEDS["phishing_domains"]["url"])
    domains = set()
    for line in raw.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "." in line:
            domains.add(line)
    return sorted(domains)

def fetch_malware_domains():
    raw = safe_download(config.THREAT_FEEDS["malware_domains"]["url"])
    domains = set()
    for line in raw.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "." in line:
            domains.add(line)
    return sorted(domains)

def update_local_feeds():
    FEED_DIR.mkdir(parents=True, exist_ok=True)
    # grab feeds
    ips = fetch_abusech_ips()
    phish = fetch_openphish_domains()
    malware_domains = fetch_malware_domains()
    # save
    with open(FEED_DIR / "abusech_ips.txt", "w") as f:
        f.write("\n".join(ips) + "\n")
    with open(FEED_DIR / "openphish.txt", "w") as f:
        f.write("\n".join(phish) + "\n")
    with open(FEED_DIR / "malware_domains.txt", "w") as f:
        f.write("\n".join(malware_domains) + "\n")
    print(f"Feeds updated: {len(ips)} IPs, {len(phish)} phishing domains, {len(malware_domains)} malware domains.")

def load_cached_ips():
    fn = FEED_DIR / "abusech_ips.txt"
    if not fn.exists(): return []
    with open(fn, "r") as f:
        return [line.strip() for line in f if line.strip()]

def load_cached_domains():
    # For compatibility, union all known domains
    domains = set()
    for fname in ["openphish.txt", "malware_domains.txt"]:
        path = FEED_DIR / fname
        if path.exists():
            with open(path, "r") as f:
                domains.update(line.strip() for line in f if line.strip())
    return sorted(domains)

if __name__ == "__main__":
    update_local_feeds()
