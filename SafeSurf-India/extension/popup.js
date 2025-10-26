// popup.js

document.addEventListener("DOMContentLoaded", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
        const url = tabs[0]?.url || "";
        document.getElementById("siteStatus").innerText = "Checking: " + url;
        checkUrl(url);
    });

    document.getElementById("forceAllowBtn").onclick = () => {
        alert("Override requested (demo only)");
    };
});

function checkUrl(url) {
    fetch("http://localhost:8000/check_url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    }).then(resp => resp.json())
      .then(data => {
        let color = data.risk == 2 ? "#e74c3c" : (data.risk == 1 ? "#f39c12" : "#2ecc71");
        document.getElementById("siteStatus").style.color = color;
        document.getElementById("siteStatus").innerText =
            "Status: " + ["Trusted", "Unknown", "Risky"][data.risk] +
            "\nReason: " + data.reason;
      }).catch(() =>
        document.getElementById("siteStatus").innerText = "Unable to check risk"
      );
}
