import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from urllib.parse import urlparse

from .models import ShortURL
from .utils import generate_short_code
from .abuse_detector import detect_abuse


#  HOME API
def home(request):
    return HttpResponse("<h1>URL Shortener is Running 🚀</h1>")


#  HELPER: Validate URL
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


#  HELPER: Get client IP (production-safe)
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


#  CREATE SHORT URL
@csrf_exempt
def create_short_url(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    original_url = None

    # 🔥 Parse JSON body
    if request.body:
        try:
            data = json.loads(request.body.decode("utf-8"))
            original_url = data.get("url")
        except:
            pass

    # 🔥 Fallback form-data
    if not original_url:
        original_url = request.POST.get("url")

    # 🔴 Validate input
    if not original_url:
        return JsonResponse({"error": "url is required"}, status=400)

    if not is_valid_url(original_url):
        return JsonResponse({"error": "Invalid URL format"}, status=400)

    # 🔥 ABUSE DETECTION
    ip = get_client_ip(request)

    if detect_abuse(ip, original_url):
        return JsonResponse(
            {"error": "Abusive behavior detected"},
            status=403
        )

    # 🔥 Generate unique short code
    while True:
        short_code = generate_short_code()
        if not ShortURL.objects.filter(short_code=short_code).exists():
            break

    # 🔥 Save to DB
    ShortURL.objects.create(
        original_url=original_url,
        short_code=short_code
    )

    return JsonResponse({
        "short-url": f"http://127.0.0.1:8000/r/{short_code}"
    })


#  REDIRECT URL
def redirect_url(request, short_code):

    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)

    try:
        # 🔥 Atomic increment (no race condition)
        url = ShortURL.objects.get(short_code=short_code)
        ShortURL.objects.filter(id=url.id).update(clicks=F('clicks') + 1)

        return redirect(url.original_url)

    except ShortURL.DoesNotExist:
        return JsonResponse({"error": "URL not found"}, status=404)