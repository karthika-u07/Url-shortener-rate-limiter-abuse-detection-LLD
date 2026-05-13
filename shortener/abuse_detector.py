import time
from collections import defaultdict
from urllib.parse import urlparse

# Store behavior per IP
USER_BEHAVIOR = defaultdict(list)
ABUSE_THRESHOLD = 60
def detect_abuse(ip, url):
    score = 0
    now = time.time()
    # Keep only last 60 seconds activity
    USER_BEHAVIOR[ip] = [
        t for t in USER_BEHAVIOR[ip]
        if now - t < 60
    ]

    request_count = len(USER_BEHAVIOR[ip])

    # Rule 1: Too many requests
    if request_count > 5:
        score += 30

    # Rule 2: Very long URLs
    if len(url) > 200:
        score += 20

    # Rule 3: Suspicious domains
    domain = urlparse(url).netloc
    if domain.count(".") > 3:
        score += 20

    # Rule 4: Burst behavior
    if request_count > 3:
        score += 10

    USER_BEHAVIOR[ip].append(now)

    return score >= ABUSE_THRESHOLD
