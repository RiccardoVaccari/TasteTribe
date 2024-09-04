from django.test import TestCase
from django.urls import reverse
from .models import Ingredient
import uuid

class CheckIngredientViewTest(TestCase):
    def setUp(self):
        self.ingredient1 = Ingredient.objects.create(
            ingredient_guid=uuid.uuid4(),
            ingredient_name="Sale",
            ingredient_image="",
            ingredient_allergens={}
        )
        self.ingredient2 = Ingredient.objects.create(
            ingredient_guid=uuid.uuid4(),
            ingredient_name="Zucchero",
            ingredient_image="",
            ingredient_allergens={}
        )

    def test_ingredient_exists(self):
        response = self.client.get(reverse('check_ingredient'), {'ingredient': 'sale'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'exists': True})

    def test_ingredient_does_not_exist(self):
        response = self.client.get(reverse('check_ingredient'), {'ingredient': 'pepe'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'exists': False})

    def test_empty_ingredient_query(self):
        response = self.client.get(reverse('check_ingredient'), {'ingredient': ''})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'exists': False})

    def test_no_ingredient_query(self):
        response = self.client.get(reverse('check_ingredient'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'exists': False})