// content.js

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (!msg || !msg.action) return;

    // Remove existing overlays (avoid duplicates)
    const oldOverlay = document.getElementById("safesurf-overlay");
    if (oldOverlay) oldOverlay.remove();

    // Create overlay
    const overlay = document.createElement("div");
    overlay.id = "safesurf-overlay";
    overlay.style.position = "fixed";
    overlay.style.top = "-120px"; // start hidden for slide down
    overlay.style.left = "50%";
    overlay.style.transform = "translateX(-50%)";
    overlay.style.width = "92%";
    overlay.style.maxWidth = "620px";
    overlay.style.padding = "1em 1.5em";
    overlay.style.borderRadius = "10px";
    overlay.style.color = "#fff";
    overlay.style.fontSize = "1.12em";
    overlay.style.fontFamily = "Segoe UI, Arial, sans-serif";
    overlay.style.boxShadow = "0 6px 28px rgba(52,90,180,0.17)";
    overlay.style.zIndex = "999999";
    overlay.style.transition = "top 0.6s cubic-bezier(0.56,0.01,0.54,1), opacity 0.5s";
    overlay.style.opacity = "0.97";

    // Set background color based on risk
    let bgColor = "#3498db"; // info
    if (msg.risk === 2) bgColor = "linear-gradient(90deg,#e74c3c 60%,#f77 100%)";
    else if (msg.risk === 1) bgColor = "linear-gradient(90deg,#f39c12 63%,#fff5c8 100%)";
    overlay.style.background = bgColor;

    // Content (title, reason, url, buttons)
    overlay.innerHTML = `
        <strong style="font-size:1.2em;">⚠️ SafeSurf Alert</strong>
        <div style="margin:7px 0 2px 0;">${msg.reason}</div>
        <small style="word-break:break-all;">${msg.url}</small>
        <div style="margin-top:13px;display:flex;gap:10px;">
            <button id="overrideBtn" style="flex:1;padding:7px 0;border:none;border-radius:6px;cursor:pointer;background:#2ecc71;color:#fff;font-weight:bold;">Override</button>
            <button id="reportBtn" style="flex:1;padding:7px 0;border:none;border-radius:6px;cursor:pointer;background:#c0392b;color:#fff;font-weight:bold;">Report</button>
        </div>
        <div id="safesurf-result" style="margin-top:7px;"></div>
    `;

    document.body.appendChild(overlay);

    // Slide-down animation
    setTimeout(() => overlay.style.top = "24px", 90);

    // Remove overlay after 21 seconds
    setTimeout(() => {
        overlay.style.top = "-150px";
        overlay.style.opacity = "0";
        setTimeout(() => overlay.remove(), 750);
    }, 21000);

    // Button handlers with robust error/catch
    overlay.querySelector("#overrideBtn").addEventListener("click", () => {
        fetch("http://localhost:8000/override_warning", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: msg.url })
        })
        .then(() => showResult("Override sent. Refresh to clear warning.", "#59fd79"))
        .catch(()=>showResult("Error sending override!", "#e74c3c"));
    });

    overlay.querySelector("#reportBtn").addEventListener("click", () => {
        fetch("http://localhost:8000/report_site", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: msg.url })
        })
        .then(() => showResult("Site reported. Thank you!", "#ff5968"))
        .catch(()=>showResult("Error reporting site!", "#e74c3c"));
    });

    function showResult(text, color) {
        const res = overlay.querySelector("#safesurf-result");
        res.innerText = text;
        res.style.color = color;
        setTimeout(() => { res.innerText = ""; }, 3800);
    }
});
