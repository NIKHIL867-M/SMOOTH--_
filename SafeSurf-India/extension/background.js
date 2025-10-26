// background.js

// Throttle logic to prevent too many API calls per tab
const throttleMap = new Map();
const THROTTLE_TIME = 2000; // milliseconds

chrome.webNavigation.onCompleted.addListener(details => {
    if (!details.url.startsWith("http")) return; // Ignore non-web URLs

    const lastCall = throttleMap.get(details.tabId) || 0;
    if (Date.now() - lastCall < THROTTLE_TIME) return;
    throttleMap.set(details.tabId, Date.now());

    checkUrl(details.url)
        .then(flagged => {
            console.log(`[SafeSurf] Checked: ${details.url}`, flagged);

            if (flagged.risk === 2) {
                // RISKY site → send warning + desktop notification
                sendTabMessage(details.tabId, "showWarning", flagged);
                showNotification("⚠️ Risky Site Detected!", details.url, flagged.reason);
            } else if (flagged.risk === 1) {
                // UNKNOWN site → info notification
                sendTabMessage(details.tabId, "showInfo", flagged);
                showNotification("ℹ️ Site May Be Risky", details.url, flagged.reason);
            } else {
                // TRUSTED site → optional log
                console.log(`[SafeSurf] Trusted: ${details.url}`);
            }
        })
        .catch(err => {
            console.error(`[SafeSurf] Error checking ${details.url}:`, err);
        });
}, { url: [{ schemes: ["http", "https"] }] });

// Send info to content/popup scripts
function sendTabMessage(tabId, action, flagged) {
    chrome.tabs.sendMessage(tabId, {
        action: action,
        url: flagged.url,
        reason: flagged.reason,
        risk: flagged.risk
    });
}

// Modern Chrome notification API
function showNotification(title, url, reason) {
    chrome.notifications.create({
        type: "basic",
        iconUrl: chrome.runtime.getURL("icons/icon128.png"),
        title: title,
        message: `${url}\nReason: ${reason}`
    });
}

// Check URL with backend API, with auto-retry on failure
async function checkUrl(url, retries = 2) {
    try {
        const response = await fetch("http://localhost:8000/check_url", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (err) {
        console.warn(`[SafeSurf] Fetch error on ${url}:`, err);
        if (retries > 0) {
            setTimeout(() => { checkUrl(url, retries - 1); }, 400); // Wait before retry
        }
        return { url, risk: 0, reason: "Error checking site" };
    }
}

// Optional: handle download events for risky files (for future feature!)
// chrome.downloads.onCreated.addListener(downloadItem => {
//     // Check file (call backend API if needed)
// });
