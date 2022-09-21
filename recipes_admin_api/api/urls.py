from django.contrib import admin
from django.urls import path, include

from .views import get_user, add_user


urlpatterns = [
    path('users/<int:telegram_id>', get_user),
    path('users/add/', add_user)
]