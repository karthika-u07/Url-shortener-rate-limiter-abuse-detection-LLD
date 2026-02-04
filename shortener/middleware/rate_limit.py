import time
from django.http import JsonResponse
from collections import defaultdict

# In-memory store: {ip: [timestamps]}
REQUEST_LOG=defaultdict(list)

RATE_LIMIT=50
TIME_WINDOW=60

class RateLimitMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self, request):
        # Apply rate
        # limiting ONLY to /create/
        if request.path != "/create/":
            return self.get_response(request)

        ip=self.get_client_ip(request)
        current_time=time.time()

        # Remove old requests
        REQUEST_LOG[ip]=[t for t in REQUEST_LOG[ip]
                         if current_time-t<TIME_WINDOW ]

        #check limit
        if len(REQUEST_LOG[ip])>=RATE_LIMIT:
            return JsonResponse(
                {"error":"Rate Limit exceed .Try again later"},status=429)

        #log request
        REQUEST_LOG[ip].append(current_time)

        response=self.get_response(request)
        return response

    def get_client_ip(self,request):
        return request.META.get("REMOTE_ADDR")
