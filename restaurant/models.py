from django.db import models

# Create your models here.


class Menu(models.Model):
    title = models.CharField(max_length=225)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()

    def __str__(self):
        return self.title


class Booking(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
    tableno = models.CharField(max_length=225)
    no_of_guest = models.IntegerField()
    booking_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            str(self.id)
            + " "
            + self.menu.title
            + " "
            + str(self.tableno)
            + " "
            + str(self.no_of_guest)
        )
