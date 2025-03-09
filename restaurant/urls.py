from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from . import views

urlpatterns = [
    path("", views.MenuItemView().as_view()),
    path("menu/<int:pk>", views.SingleMenuItemView().as_view()),
    path("booking/", views.BookingItemView().as_view()),
    path("obtain-token", ObtainAuthToken.as_view()),
]
