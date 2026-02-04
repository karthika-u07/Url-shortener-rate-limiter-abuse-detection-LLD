from django.urls import path
from . import views

urlpatterns=[
    path('create/',views.create_short_url),
    path('<str:short_code>/',views.redirect_url),
]