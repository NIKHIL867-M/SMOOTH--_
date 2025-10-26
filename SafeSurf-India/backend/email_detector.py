import re

def is_email_phishing(email_text):
    """
    Check if an email contains phishing indicators.
    Returns: (is_phishing: bool, reason: str, confidence: str)
    """
    patterns = [
        # Urgency and action demands
        {
            'pattern': r'\b(urgent|immediate|asap|emergency)\b.*\b(click|link|update|verify|confirm)\b',
            'reason': 'Creates false urgency with action demand',
            'weight': 'high'
        },
        # Prize and reward scams
        {
            'pattern': r'\b(win|won|prize|reward|million|billion)\b.*\b(claim|collect|money|cash)\b',
            'reason': 'Too-good-to-be-true offer',
            'weight': 'high'
        },
        # Account suspension threats
        {
            'pattern': r'\b(account|bank|paypal|amazon)\b.*\b(suspend|closed|terminate|verify)\b',
            'reason': 'Threatens account suspension',
            'weight': 'high'
        },
        # Login/credential requests
        {
            'pattern': r'\b(login|sign.in|password|credentials)\b.*\b(verify|update|confirm)\b',
            'reason': 'Requests credential verification',
            'weight': 'medium'
        },
        # Suspicious sender domains
        {
            'pattern': r'@(?!.*\.(com|org|net|edu|gov))[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'reason': 'Suspicious sender domain',
            'weight': 'medium'
        },
        # Generic greetings
        {
            'pattern': r'^\s*(dear customer|dear user|valued customer|dear account holder)',
            'reason': 'Generic greeting instead of personal name',
            'weight': 'low'
        },
        # Poor grammar, excessive punctuation
        {
            'pattern': r'!!+|\?\?+|[A-Z][a-z]*[A-Z][a-z]*[A-Z]',
            'reason': 'Poor grammar or excessive punctuation',
            'weight': 'low'
        }
    ]

    def check_suspicious_urls(text):
        url_pattern = r'https?://([a-zA-Z0-9.-]+)'
        suspicious_domains = [
            r'.*security-?verify.*',
            r'.*login-?update.*',
            r'.*account-?confirm.*',
            r'.*\.(tk|ml|ga|cf)$'
        ]
        urls = re.findall(url_pattern, text)
        for url in urls:
            for domain_pattern in suspicious_domains:
                if re.match(domain_pattern, url, re.IGNORECASE):
                    return True
        return False

    score = 0
    detected_reasons = []

    for pattern_data in patterns:
        if re.search(pattern_data['pattern'], email_text, re.IGNORECASE):
            detected_reasons.append(pattern_data['reason'])
            if pattern_data['weight'] == 'high':
                score += 3
            elif pattern_data['weight'] == 'medium':
                score += 2
            else:
                score += 1

    if check_suspicious_urls(email_text):
        score += 2
        detected_reasons.append('Suspicious URL detected')

    if score >= 5:
        return True, " | ".join(detected_reasons), "High confidence"
    elif score >= 3:
        return True, " | ".join(detected_reasons), "Medium confidence"
    elif score >= 2:
        return False, " | ".join(detected_reasons), "Low suspicion - review recommended"
    else:
        return False, "No clear phishing indicators detected", "Safe"

# Test block (remove for production)
if __name__ == "__main__":
    test_emails = [
        "URGENT: Your account will be suspended! Click here to verify: http://security-verify-bank.com",
        "Congratulations! You won $1,000,000! Claim your prize now!",
        "Hi John, just checking in about our meeting tomorrow.",
        "Dear Customer, please update your login credentials immediately at http://login-update-site.tk"
    ]
    for i, email in enumerate(test_emails, 1):
        result, reason, confidence = is_email_phishing(email)
        print(f"Email {i}: {'PHISHING' if result else 'SAFE'}")
        print(f"Reason: {reason}")
        print(f"Confidence: {confidence}")
        print("-" * 50)
