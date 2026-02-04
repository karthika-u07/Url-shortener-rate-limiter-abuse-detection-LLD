import json
from django.http import JsonResponse
from .models import ShortURL
from .utils import generate_short_code
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from .abuse_detector import detect_abuse


# Create your views here.
@csrf_exempt
def create_short_url(request):
    if request.method!="POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    original_url = None
    #  Try JSON body
    if request.body:
        try:
            data=json.loads(request.body.decode("utf-8"))
            original_url=data.get("url")

        except Exception:
            pass

        #  Fallback to form-data
        if not original_url:
            original_url = request.POST.get("url")

        #  Final validation
        if not original_url:
            return JsonResponse({"error":"url is required"},status=400)

        # ABUSE DETECTION (ADD THIS BLOCK)
        ip = request.META.get("REMOTE_ADDR")

        if detect_abuse(ip, original_url):
            return JsonResponse(
                {"error": "Abusive behavior detected"},
                    status=403
                )
        #  Prevent short-code collision
        while True:
            short_code=generate_short_code()
            if not ShortURL.objects.filter(short_code=short_code).exists():
                break

        ShortURL.objects.create(original_url=original_url,
            short_code=short_code)

        return JsonResponse({
            "short-url":f"http://127.0.0.1:8000/{short_code}"})
    return JsonResponse({"error":"POST request required"})

def redirect_url(request,short_code):
    try:
        url=ShortURL.objects.get(short_code=short_code)
        url.clicks+=1
        url.save()
        return redirect(url.original_url)

    except ShortURL.DoesNotExist:
        return JsonResponse({"error":"URL not found"})


