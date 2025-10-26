# **SafeSurf India - Complete Setup & Demo Guide**

---

## **1. What We Built**
A **full-stack web security threat analytics platform** with:
- **Backend API** (Flask) for threat feeds, risk scoring, phishing detection, and graph analytics
- **Neo4j graph database** for threat actor relationships and community hotspot detection
- **SQLite database** for site history, downloads, and reports
- **Modern web dashboard** (HTML/CSS/JS) with real-time threat visualization, animated graph, and phishing email scanner
- **Chrome extension** (optional, for browser-based site risk alerts)

***

## **2. Required Software & Installation**

### **A. Python 3.12**
- Already installed on your system.

### **B. Neo4j Desktop**
- Already installed and running.
- **Instance Name:** `build`
- **Password:** `123456789`
- **Connection URI:** `bolt://127.0.0.1:7687`

### **C. Python Dependencies**
Install all required packages:
```bash
pip install flask flask-cors flask-limiter neo4j requests
```

***

## **3. Project Structure**
```
SafeSurf-India/
├── backend/
│   ├── app.py              # Main Flask API server
│   ├── config.py           # Configuration (DB credentials, feeds, etc.)
│   ├── feeds.py            # Threat feed downloader
│   ├── classify.py         # URL/file risk classifier
│   ├── graph.py            # Neo4j graph analytics
│   ├── database.py         # SQLite DB operations
│   └── email_detector.py   # Phishing email detection
├── dashboard/
│   ├── app.py              # Frontend Flask server
│   ├── templates/
│   │   └── dashboard.html  # Main dashboard UI
│   └── static/
│       ├── dashboard.css   # Modern UI styling
│       └── dashboard.js    # Frontend logic
├── data/
│   ├── feeds/              # Downloaded threat feeds (auto-generated)
│   ├── logs/               # Application logs
│   └── security_analytics.db  # SQLite database
└── extension/              # Chrome extension (optional)
```

***

## **4. How to Run (Step-by-Step)**

### **Step 1: Start Neo4j**
- Open **Neo4j Desktop**
- Make sure your `build` instance is **RUNNING** (green status)

### **Step 2: Import Threat Feeds**
```bash
cd SafeSurf-India/backend
python feeds.py
```
**Output:** `Feeds updated: X IPs, 300 phishing domains, Y malware domains.`

### **Step 3: Build Threat Graph**
```bash
python graph.py
```
**Output:** `Connected to Neo4j successfully!` and `Graph built from feeds.`

### **Step 4: Start Backend API**
```bash
python app.py
```
**Output:** `Running on http://127.0.0.1:8000`  
**Keep this terminal open and running!**

### **Step 5: Start Dashboard (Frontend)**
Open a **new terminal** and run:
```bash
cd SafeSurf-India/dashboard
python app.py
```
**Output:** `Running on http://127.0.0.1:8050`

### **Step 6: Open Dashboard in Browser**
- Go to: **http://127.0.0.1:8050**
- You should see:
  - **Top Risk Domains** table with real phishing sites
  - **Threat Network** animated graph with nodes and connections
  - **Phishing Email Detector** ready to test

***

## **5. What Each Component Does**

### **Backend API Endpoints**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ping` | GET | Health check |
| `/check_url` | POST | Check if URL is risky |
| `/check_file` | POST | Check if file download is risky |
| `/community_hotspots` | GET | Get top risky domains |
| `/actor_relations` | GET | Get threat network graph data |
| `/check_email` | POST | Check if email is phishing |
| `/update_feeds` | POST | Refresh threat feeds |
| `/report_site` | POST | User report risky site |
| `/override_warning` | POST | Mark site as trusted |

### **Dashboard Features**
1. **Top Risk Domains**: Shows risky sites from threat feeds with action buttons (View, Report, Trust)
2. **Threat Network**: Animated graph visualization of threat actors and flagged domains
3. **Phishing Email Detector**: Paste email text to check for phishing indicators

***

## **6. Demo Workflow**

### **For Judges/Reviewers:**
1. **Show the dashboard** - Point out the modern UI, real-time data, and animated graph
2. **Explain threat feeds** - "We pull from OpenPhish and abuse.ch in real-time"
3. **Test phishing detector** - Paste a sample phishing email and show detection
4. **Show action buttons** - Click View/Report/Trust on a risky domain
5. **Explain the tech stack**:
   - Backend: Flask + Neo4j + SQLite
   - Frontend: Modern HTML5/CSS3/JS
   - Data: Real threat intelligence feeds

### **Sample Phishing Email for Demo:**
```
URGENT: Your account will be suspended!
Click here to verify: http://security-verify-bank.com
Act now to claim your $1,000,000 prize!
```

***

## **7. Troubleshooting**

### **If dashboard shows blank panels:**
- Check Neo4j is running (green status in Neo4j Desktop)
- Check backend logs for errors
- Run `python graph.py` again to rebuild

### **If you get connection errors:**
- Verify `config.py` has correct Neo4j password (`123456789`)
- Verify Neo4j is on port `7687`
- Restart backend: `python app.py`

***

## **8. Key Features Implemented**
✅ Real-time threat feed integration (OpenPhish, abuse.ch)  
✅ Graph-based threat intelligence with Neo4j  
✅ ML-powered phishing email detection  
✅ Modern, responsive UI with glassmorphism design  
✅ Community-driven risk scoring  
✅ RESTful API for extensibility  
✅ Browser extension architecture (if time permits)

***

## **9. Technologies Used**
- **Backend:** Python 3.12, Flask, Neo4j Driver
- **Database:** Neo4j (graph), SQLite (relational)
- **Frontend:** HTML5, CSS3 (Glassmorphism), Vanilla JavaScript
- **Visualization:** Cytoscape.js for graph rendering
- **Security:** Rate limiting, CORS protection, input validation

***
