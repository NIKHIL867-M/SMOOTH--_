from flask import Flask, request, jsonify
from flask_cors import CORS
import feeds
import classify
import graph
import database
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Flask app setup ---
app = Flask(__name__)
CORS(app)

# --- Logging ---
logging.basicConfig(filename='error.log', level=logging.INFO)

# --- Rate Limiter: Compatible with both Flask-Limiter v2 and v3 ---
try:
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["120 per minute"]
    )
except TypeError:
    limiter = Limiter(app, key_func=get_remote_address, default_limits=["120 per minute"])

# --- Error handler ---
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Error: {e}", exc_info=True)
    return jsonify({"error": str(e)}), 500

# --- Health check ---
@app.route("/ping")
def ping():
    return jsonify({"status": "SafeSurf API Active"})

# --- Update threat feeds ---
@app.route("/update_feeds", methods=["POST"])
def update_feeds():
    try:
        feeds.update_local_feeds()
        return jsonify({"status": "feeds updated"})
    except Exception as e:
        logging.error(f"Feed update failed: {e}")
        return jsonify({"error": str(e)}), 500

# --- URL classification ---
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.json
    url = data.get("url", "")
    score, reason = classify.classify_url(url)
    return jsonify({
        "url": url,
        "risk": score,
        "reason": reason
    })

# --- File classification ---
@app.route("/check_file", methods=["POST"])
def check_file():
    data = request.json
    fname = data.get("file", "")
    site_url = data.get("site_url", "")
    score, reason = classify.classify_file(fname, site_url)
    return jsonify({
        "file": fname,
        "risk": score,
        "reason": reason
    })

# --- Community hotspots (for dashboard) ---
@app.route("/community_hotspots")
def get_hotspots():
    try:
        top = int(request.args.get("top", 10))
        result = graph.community_hotspots(top_n=top)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Hotspot error: {e}")
        return jsonify([])

# --- Predict link risk ---
@app.route("/predict_link_risk", methods=["POST"])
def link_risk():
    data = request.json
    url = data.get("url", "")
    risky, reason, _ = graph.predict_link_risk(url)
    return jsonify({
        "url": url,
        "likely_risky": risky,
        "reason": reason
    })

# --- Report a site (user reports through extension/popup) ---
@app.route("/report_site", methods=["POST"])
def report_site():
    url = request.json.get("url", "")
    try:
        from database import get_sqlite_connection
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("UPDATE sites SET user_reports = user_reports + 1 WHERE url=?;", (url,))
        conn.commit()
        conn.close()
        return jsonify({"status": "reported", "url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- User override of warnings (extension/popup) ---
@app.route("/override_warning", methods=["POST"])
def override_warning():
    url = request.json.get("url", "")
    try:
        from database import get_sqlite_connection
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("UPDATE sites SET reputation = reputation + 2 WHERE url=?;", (url,))
        conn.commit()
        conn.close()
        return jsonify({"status": "override", "url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Threat actor relations (dashboard graph) ---
@app.route("/actor_relations")
def actor_relations():
    try:
        from graph import get_all_relations
        rels = get_all_relations()
        return jsonify(rels)
    except Exception as e:
        logging.error(f"Actor relation error: {e}")
        return jsonify([])

# --- Email phishing check (dashboard) ---
@app.route("/check_email", methods=["POST"])
def check_email():
    text = request.json.get("text", "")
    from email_detector import is_email_phishing
    phishing, reason, confidence = is_email_phishing(text)
    return jsonify({
        "phishing": phishing,
        "reason": reason,
        "confidence": confidence
    })

if __name__ == "__main__":
    # On first run, init DB structure if not present
    database.init_sqlite_db()
    app.run(debug=True, port=8000)
