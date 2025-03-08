from django.db import models

# Create your models here.


class Booking(models.Model):
    name = models.CharField(max_length=225)
    no_of_guest = models.IntegerField()
    booking_date = models.DateTimeField(auto_now=True)


class Menu(models.Model):
    title = models.CharField(max_length=225)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
