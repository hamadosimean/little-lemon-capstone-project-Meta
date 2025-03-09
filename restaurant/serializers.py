from django.contrib.auth.models import User
from .models import Menu, Booking
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    menu_id = serializers.IntegerField(write_only=True)
    menu = MenuSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"
