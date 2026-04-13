from django.urls import path
from . import views

urlpatterns=[
    path('', views.home),
    path('create/',views.create_short_url),
    path('r/<str:short_code>/',views.redirect_url),
]