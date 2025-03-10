from django.test import TestCase
from restaurant.models import Menu

# Create your tests here.


class TestLemonAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.item = Menu.objects.create(title="Boeuf", price=80, inventory=50)

    def test_menu_item(self):
        self.assertEqual(
            self.item.title
            + " "
            + str(self.item.price)
            + " "
            + str(self.item.inventory),
            "Boeuf 80 50",
        )
