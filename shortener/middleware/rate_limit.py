import time
from django.http import JsonResponse
from collections import defaultdict

# In-memory store: {ip: [timestamps]}
REQUEST_LOG = defaultdict(list)

# Rate limits (per endpoint)
LIMITS = {
    "/create/": 10,   # strict limit for creation
    "/r/": 100        # higher limit for redirects
}

DEFAULT_LIMIT = 60
TIME_WINDOW = 60  # seconds


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        path = request.path
        ip = self.get_client_ip(request)
        current_time = time.time()

        # 🔥 Apply rate limiting ONLY to selected endpoints
        if not (path.startswith("/create/") or path.startswith("/r/")):
            return self.get_response(request)

        # 🔥 Get limit based on endpoint
        limit = self.get_limit(path)

        # 🔥 Sliding Window Logic
        REQUEST_LOG[ip] = [
            t for t in REQUEST_LOG[ip]
            if current_time - t < TIME_WINDOW
        ]

        # 🔴 Check limit
        if len(REQUEST_LOG[ip]) >= limit:
            return JsonResponse(
                {"error": "Rate limit exceeded. Try again later."},
                status=429
            )

        # ✅ Log request
        REQUEST_LOG[ip].append(current_time)

        return self.get_response(request)

    def get_client_ip(self, request):
        """
        Extract client IP address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    def get_limit(self, path):
        """
        Return rate limit based on endpoint
        """
        for endpoint in LIMITS:
            if path.startswith(endpoint):
                return LIMITS[endpoint]
        return DEFAULT_LIMIT