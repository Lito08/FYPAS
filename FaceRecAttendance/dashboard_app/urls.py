from django.urls import path
from .views import home

urlpatterns = [
    path("", home, name="home"),  # Sets homepage to base.html
]
