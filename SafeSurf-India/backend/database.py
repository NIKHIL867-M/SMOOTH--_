import sqlite3
import logging
import config
from neo4j import GraphDatabase

# --- SQLite DB connection for backend storage ---
def get_sqlite_connection():
    try:
        conn = sqlite3.connect(
            config.SQLITE_DB_PATH,
            timeout=getattr(config, "SQLITE_TIMEOUT", 20),
            check_same_thread=getattr(config, "SQLITE_CHECK_SAME_THREAD", False)
        )
        return conn
    except Exception as e:
        logging.error(f"SQLite connection error: {e}")
        raise

def init_sqlite_db():
    try:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                label TEXT,
                reason TEXT,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reputation INTEGER DEFAULT 0,
                user_reports INTEGER DEFAULT 0,
                visits INTEGER DEFAULT 0
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file TEXT,
                site_url TEXT,
                risk INTEGER,
                reason TEXT,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS site_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        conn.commit()
        conn.close()
        logging.info("DB initialized and tables created.")
    except Exception as e:
        logging.error(f"DB init failed: {e}")

# --- Record download scan ---
def log_download(file_name, site_url, risk, reason):
    try:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO downloads(file, site_url, risk, reason) VALUES (?, ?, ?, ?)",
            (file_name, site_url, risk, reason)
        )
        conn.commit()
        conn.close()
        logging.info(f"Download logged: {file_name} from {site_url} risk={risk}")
    except Exception as e:
        logging.warning(f"Download log error: {e}")

# --- Record site action (report, override, etc) ---
def log_site_action(url, action, details=""):
    try:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO site_actions(url, action, details) VALUES (?, ?, ?)",
            (url, action, details)
        )
        conn.commit()
        conn.close()
        logging.info(f"Site action logged: {url}, action={action}")
    except Exception as e:
        logging.warning(f"Site action log error: {e}")

# --- Neo4j connector for threat graph ---
def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(
            config.NEO4J_URL,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
            max_connection_lifetime=getattr(config, "NEO4J_MAX_CONNECTION_LIFETIME", 3600),
            encrypted=getattr(config, "NEO4J_ENCRYPTED", False)
        )
        return driver
    except Exception as e:
        logging.error(f"Neo4j driver error: {e}")
        raise

