import feeds
import logging

def classify_url(url):
    """
    Classifies the given URL.
    Returns: (score, reason)
    score: 0 = trusted, 1 = unknown, 2 = risky
    """
    url = url.lower()
    risky_reasons = []
    domain_list = feeds.load_cached_domains()
    ip_list = feeds.load_cached_ips()

    # Domain check
    for domain in domain_list:
        if domain in url:
            risky_reasons.append(f"Domain listed in phishing/malware feed ({domain})")

    # IP check in url
    for ip in ip_list:
        if ip in url:
            risky_reasons.append(f"IP listed in malware feed ({ip})")

    if risky_reasons:
        score = 2  # Risky
        reason = "; ".join(risky_reasons)
        update_site_history(url, score, reason)
        logging.info(f"URL classified as risky: {url} - {reason}")
        return score, reason

    # Heuristic: risky downloads or long links
    if any(e in url for e in [".exe", ".zip", ".apk"]) or len(url) > 60:
        score = 1
        reason = "Unknown site, suspicious download or link pattern"
        update_site_history(url, score, reason)
        logging.info(f"URL classified as unknown: {url} - {reason}")
        return score, reason

    score = 0
    reason = "Site is not flagged in any threat feeds"
    update_site_history(url, score, reason)
    logging.info(f"URL classified as trusted: {url}")
    return score, reason

def classify_file(file_name, site_url=""):
    """
    Classifies the downloaded file, logs to downloads table.
    Returns: (score, reason)
    """
    file_name = file_name.lower()
    risky_files = [".exe", ".apk", ".scr", ".bat", ".js", ".wsf"]  # risky filetypes

    for ext in risky_files:
        if file_name.endswith(ext):
            score = 2
            reason = f"File type flagged as risky ({ext})"
            if site_url:
                update_site_history(site_url, score, reason)
            log_download(file_name, site_url, score, reason)
            logging.info(f"File classified as risky: {file_name} from {site_url}")
            return score, reason

    if any(ext in file_name for ext in [".zip", ".rar"]):
        score = 1
        reason = "Archive file, treat with caution"
        if site_url:
            update_site_history(site_url, score, reason)
        log_download(file_name, site_url, score, reason)
        logging.info(f"File classified as unknown: {file_name} from {site_url}")
        return score, reason

    score = 0
    reason = "No obvious risk detected"
    if site_url:
        update_site_history(site_url, score, reason)
    log_download(file_name, site_url, score, reason)
    logging.info(f"File classified as trusted: {file_name} from {site_url}")
    return score, reason

def update_site_history(url, risk, reason):
    from database import get_sqlite_connection
    label = ["trusted", "unknown", "risky"][risk]
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO sites(url, label, reason, visits) VALUES (?, ?, ?, 0);",
        (url, label, reason)
    )
    cur.execute(
        "UPDATE sites SET visits = visits + 1, label=?, reason=?, last_checked=CURRENT_TIMESTAMP WHERE url=?;",
        (label, reason, url)
    )
    conn.commit()
    conn.close()

def log_download(file_name, site_url, risk, reason):
    from database import get_sqlite_connection
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO downloads(file, site_url, risk, reason) VALUES (?, ?, ?, ?);",
        (file_name, site_url, risk, reason)
    )
    conn.commit()
    conn.close()
