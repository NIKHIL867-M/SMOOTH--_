document.addEventListener("DOMContentLoaded", () => {
    fetchHotspots();
    fetchGraph();

    document.getElementById("checkEmailBtn").onclick = checkEmailForPhishing;
    document.getElementById("clearEmailBtn")?.addEventListener("click", clearEmailResult);
    document.getElementById("refreshDataBtn")?.addEventListener("click", handleDataRefresh);
});

// --- Fetch and Fill Top Risk Table ---
function fetchHotspots() {
    fetch("http://localhost:8000/community_hotspots?top=10")
        .then(resp => resp.json())
        .then(fillRiskTable)
        .catch(err => showGlobalError("Error fetching hotspots: " + err));
}

function fillRiskTable(data) {
    const tableBody = document.querySelector("#riskTable tbody");
    tableBody.innerHTML = "";
    data.forEach(item => {
        const color = item.label === "risky" ? "#ff4083"
                    : item.label === "unknown" ? "#f1c40f"
                    : "#23bb73";

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.url}</td>
            <td class="risk-rank" style="color:${color};font-weight:bold">${item.label || "-"}</td>
            <td>${item.user_reports ?? 0}</td>
            <td>${item.visits ?? 0}</td>
            <td style="min-width:124px">
                <button class="action-btn view-btn" title="View Details">View</button>
                <button class="action-btn report-btn" title="Mark as risky">Report</button>
                <button class="action-btn trust-btn" title="Mark as trusted">Trust</button>
            </td>
        `;

        // Ripple feedback on click for all actions
        row.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener("click", ev => {
                ev.stopPropagation();
                if(btn.classList.contains('view-btn')) {
                    window.open(`https://${item.url}`, '_blank');
                }
                if(btn.classList.contains('report-btn')) {
                    handleSiteAction(item.url, "report");
                }
                if(btn.classList.contains('trust-btn')) {
                    handleSiteAction(item.url, "trust");
                }
            });
        });

        // Hover highlight for row
        row.addEventListener("mouseenter", () => row.style.backgroundColor = "#f0e9fd");
        row.addEventListener("mouseleave", () => row.style.backgroundColor = "");

        tableBody.appendChild(row);
    });
}

// --- Report/Trust Site Actions (calls backend) ---
function handleSiteAction(url, action) {
    if(action === "report") {
        fetch("http://localhost:8000/report_site", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        }).then(resp => resp.json())
          .then(data => showGlobalError(`Reported ${url} as risky.`));
    }
    if(action === "trust") {
        fetch("http://localhost:8000/override_warning", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        }).then(resp => resp.json())
          .then(data => showGlobalError(`Marked ${url} as trusted.`));
    }
}

// --- Cytoscape Animated Threat Graph ---
function fetchGraph() {
    fetch("http://localhost:8000/actor_relations")
        .then(resp => resp.json())
        .then(drawGraph)
        .catch(err => showGlobalError("Error fetching graph: " + err));
}

function drawGraph(data) {
    if (typeof cytoscape === "undefined") {
        showGlobalError("Visualization library not loaded.");
        return;
    }
    const nodes = {}, edges = [];
    data.forEach(rel => {
        nodes[rel.actor] = { data: { id: rel.actor, label: rel.actor, type: "actor" }};
        nodes[rel.url] = { data: { id: rel.url, label: rel.url, type: "site" }};
        edges.push({ data: { source: rel.actor, target: rel.url, label: rel.relation }});
    });
    const cy = cytoscape({
        container: document.getElementById("cy-graph"),
        elements: [...Object.values(nodes), ...edges],
        style: [
            {
                selector: 'node[type="actor"]', style: {
                    'background-color': '#673ab7', 'shape': 'rectangle', 'width': 34,
                    'height': 34, 'label': 'data(label)', 'font-size': 15, 'color': '#fff',
                    'text-valign':'center','text-halign':'center','border-width':4,'border-color':'#b0e0ff','overlay-opacity':0
                }
            },
            {
                selector: 'node[type="site"]', style: {
                    'background-color': '#ff4083', 'shape': 'ellipse', 'width': 26,
                    'height': 26, 'label': 'data(label)', 'font-size': 12, 'color': '#fff',
                    'border-width': 2, 'border-color': '#f4e7ff','overlay-opacity':0
                }
            },
            {
                selector: 'edge', style: {
                    'curve-style': 'bezier', 'target-arrow-shape': 'triangle',
                    'width': 4, 'line-color': '#baffff', 'target-arrow-color': '#6de9fc',
                    'label':'data(label)', 'font-size': 10, 'text-background-color': '#fff',
                    'text-background-opacity': 0.8, 'text-background-padding': 2
                }
            }
        ],
        layout: { name: 'cose', animate: true, animationDuration: 2200, randomize: true, fit: true }
    });
    setInterval(() => cy.layout({ name: 'cose', animate: true, animationDuration: 1800 }).run(), 12000);

    // Tooltip (pure HTML, no dependencies)
    cy.nodes().forEach(node => {
        node.on("mouseover", (e) => {
            const tip = document.createElement("div");
            tip.className = "cy-tip";
            tip.innerHTML = `<strong style="color:#ff4083">${node.data('label')}</strong><br>Type: <b>${node.data('type')}</b>`;
            tip.style.position = "fixed";
            tip.style.left = (e.renderedPosition.x + 50) + "px";
            tip.style.top = (e.renderedPosition.y + 40) + "px";
            tip.style.background = "#fff8";
            tip.style.border = "1.5px solid #7a4bde";
            tip.style.padding = "8px 16px";
            tip.style.borderRadius = "10px";
            tip.style.boxShadow = "0 4px 16px #aaccff17";
            tip.style.zIndex = "999999";
            tip.style.transition = "opacity 0.18s";
            tip.style.pointerEvents = "none";
            tip.id = "graph-tip";
            document.body.appendChild(tip);
        });
        node.on("mouseout", () => {
            document.getElementById("graph-tip")?.remove();
        });
    });
}

// --- Phishing Email Detector ---
function checkEmailForPhishing() {
    const textArea = document.getElementById("emailText");
    const res = document.getElementById("phishingResult");
    const text = textArea.value.trim();
    if (!text) return showPhishingMsg("Please enter email text to check.", false, "");
    fetch("http://localhost:8000/check_email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    })
    .then(resp => resp.json())
    .then(data => {
        showPhishingMsg(
            data.phishing 
                ? `⚠️ Phishing Detected: ${data.reason}` 
                : `✅ No phishing detected: ${data.reason}`,
            data.phishing,
            data.confidence || ""
        );
    })
    .catch(err => showPhishingMsg("Error checking phishing email: " + err, false, ""));
}

function showPhishingMsg(text, isRisk, confidence) {
    const res = document.getElementById("phishingResult");
    res.innerHTML = `${text}<br>${confidence ? `<em>Confidence: <b>${confidence}</b></em>` : ""}`;
    res.style.color = isRisk ? "#e74c3c" : "#14ad40";
    res.style.border = isRisk ? "2px solid #e74c3c" : "2px solid #70ea8c";
    res.style.opacity = 0;
    setTimeout(() => { res.style.opacity = 1; res.style.transition = "opacity 0.6s"; }, 50);
}

function clearEmailResult() {
    document.getElementById("emailText").value = "";
    showPhishingMsg("", false, "");
}

// --- Refresh handler (reloads data+feeds) ---
function handleDataRefresh() {
    showGlobalError("Refreshing data and threat feeds...");
    fetch("http://localhost:8000/update_feeds", { method: "POST" })
        .then(r => r.json()).then(() => {
            fetchHotspots();
            fetchGraph();
            showGlobalError("Feeds updated and table/graph refreshed!");
        });
}

// --- Utility: Show global error / info
function showGlobalError(msg) {
    let el = document.getElementById("global-error-banner");
    if (!el) {
        el = document.createElement("div");
        el.id = "global-error-banner";
        el.style.position = "fixed";
        el.style.top = "0";
        el.style.left = "0";
        el.style.width = "100vw";
        el.style.background = "#ff4083";
        el.style.color = "#fff";
        el.style.fontWeight = "bold";
        el.style.textAlign = "center";
        el.style.padding = "10px";
        el.style.zIndex = "999999";
        document.body.appendChild(el);
    }
    el.textContent = msg;
    setTimeout(() => el.remove(), 4200);
}

// Nice ripple animation for any .action-btn
(function() {
    const style = document.createElement('style');
    style.innerHTML = `
    @keyframes ripple-expand {
        from { transform: scale(0.4); opacity: 0.5; }
        to { transform: scale(2.8); opacity: 0; }
    }
    .action-btn:active {
        filter: brightness(0.95);
    }
    .ripple {
        animation: ripple-expand 0.6s linear;
        pointer-events: none;
        position: absolute;
    }
    .action-btn {
        margin: 0 2px;
        padding: 3.5px 12px;
        border-radius: 7px;
        background: linear-gradient(80deg, #ff4083 50%, #355c7d 100%);
        border: none;
        color: #fff;
        font-weight: 600;
        font-size: 0.97em;
        cursor: pointer;
        box-shadow: 0 1px 4px #994fff20;
        transition: background 0.13s;
    }
    .action-btn.view-btn { background: linear-gradient(80deg, #5fdeff, #355c7d 100%);}
    .action-btn.trust-btn { background: linear-gradient(80deg, #1ceb9a, #ffdeaf 100%);}
    .action-btn.report-btn { background: linear-gradient(80deg, #ff4083 60%, #f2994a 120%);}
    .action-btn:hover { filter: brightness(1.13);}
    `;
    document.head.appendChild(style);
})();
