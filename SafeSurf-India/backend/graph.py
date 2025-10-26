from neo4j import GraphDatabase
import logging
from typing import List, Dict, Tuple
from datetime import datetime

try:
    from config import NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD, RISK_SCORING
except ImportError:
    NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD = "bolt://localhost:7687", "neo4j", "password"
    RISK_SCORING = {"medium": 5, "high": 8, "low": 3}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SafeSurfGraph")

def get_driver():
    try:
        driver = GraphDatabase.driver(
            NEO4J_URL,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            max_connection_lifetime=3600
        )
        # Test connection
        with driver.session() as session:
            session.run("RETURN 1 AS ok")
        logger.info("Connected to Neo4j successfully!")
        return driver
    except Exception as e:
        logger.error(f"Neo4j connection error: {e}")
        raise

def add_website(driver, url: str, label: str = "unknown", risk_score: int = 0, metadata=None):
    try:
        with driver.session() as session:
            query = """
            MERGE (w:Website {url: $url})
            SET w.label = $label,
                w.risk_score = $risk_score,
                w.last_updated = $timestamp
            """
            params = {
                "url": url,
                "label": label,
                "risk_score": risk_score,
                "timestamp": datetime.now().isoformat()
            }
            if metadata:
                for k, v in metadata.items():
                    query += f", w.{k} = ${k}"
                    params[k] = v
            session.run(query, **params)
    except Exception as e:
        logger.warning(f"Add website failed ({url}): {e}")

def clear_graph():
    driver = get_driver()
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.warning("Entire graph cleared.")
    finally:
        driver.close()

def build_basic_graph_from_feeds():
    try:
        from feeds import load_cached_domains
        driver = get_driver()
        for domain in load_cached_domains():
            add_website(driver, domain, label="risky", risk_score=7,
                        metadata={"source": "threat_feed", "first_seen": datetime.now().isoformat()})
        logger.info("Graph built from feeds.")
    except Exception as e:
        logger.error(f"Graph build failed: {e}")

def community_hotspots(top_n=10) -> List[Dict]:
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (w:Website)
                WHERE w.label IN ['suspicious', 'risky', 'malicious']
                RETURN w.url as url, w.label as label, w.risk_score as risk_score,
                       1 as user_reports, 1 as visits
                ORDER BY w.risk_score DESC
                LIMIT $n
            """, n=top_n)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Failed to get community hotspots: {e}")
        return []
    finally:
        driver.close()

def get_all_relations() -> List[Dict]:
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (w:Website)
                WHERE w.label IN ['suspicious', 'risky', 'malicious']
                RETURN 'SafeSurfAI' as actor, w.url as url, 'flagged' as relation
                LIMIT 20
            """)
            return [{"actor": rec["actor"], "url": rec["url"], "relation": rec["relation"]} for rec in result]
    except Exception as e:
        logger.error(f"Get all relations error: {e}")
        return []
    finally:
        driver.close()

# For risk scoring and other analytic features, keep your functions as they are (predict_link_risk, etc.)

if __name__ == "__main__":
    build_basic_graph_from_feeds()
    # Uncomment for demo: clear_graph()
