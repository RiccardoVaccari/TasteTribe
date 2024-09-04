import random
import uuid
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from login.models import RegisteredUser
from homepage.models import Recipe, Tag, TagXRecipe
from .models import RecipesCollection, RecipeXCollection
from .views import generate_tag_set


# Create your tests here.
class GenerateTagSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.reg_user = RegisteredUser.objects.create(user=self.user)
        self.collections = []
        # Create a couple of test collections
        for c in range(2):
            self.collections.append(RecipesCollection.objects.create(
                collection_guid=uuid.uuid4(),
                collection_name=f"Raccolta #{c}",
                collection_cover="",
                collection_author=self.user,
                collection_creation_date=timezone.now().date(),
                collection_is_private=False
            ))
        # Create a list of test tags
        self.tags = []
        for t in range(5):
            self.tags.append(Tag.objects.create(
                tag_guid=uuid.uuid4(),
                tag_name=f"Tag {t}",
                tag_field="Test tag",
                tag_relevance=10
            ))
        # Create a few test recipes
        for r in range(8):
            collection_index = random.randint(0, 1)
            recipe = Recipe.objects.create(
                recipe_guid=uuid.uuid4(),
                recipe_name=f"Ricetta di prova #{r}",
                recipe_prep_time=timezone.timedelta(minutes=30),
                recipe_cover=None,
                recipe_notes="Note della ricetta",
                recipe_description="Descrizione di prova",
                recipe_category="Categoria di prova",
                recipe_is_private=False,
                recipe_is_vegetarian=True,
                recipe_gluten_free=False,
                recipe_is_vegan=False,
                recipe_creation_date=timezone.now().date(),
                recipe_author=self.user
            )
            # insert the test recipe in one of the two collections
            RecipeXCollection.objects.create(rxc_recipe_guid=recipe, rxc_collection_guid=self.collections[collection_index])
            # Bind tags to recipes randomly
            tag_to_bind = random.randint(0, 5)
            for tag_index in range(tag_to_bind):
                TagXRecipe.objects.create(txr_recipe_guid=recipe, txr_tag_guid=self.tags[tag_index])

    def test_generate_tag_set(self):
        tag_set = generate_tag_set(self.collections)
        # Check if the tags added are among the ones actually defined in the test environment
        for tag in tag_set:
            self.assertIn(tag, self.tags)
        # Check the tag_set length (which shouldn't exceed the self.tags list length)
        self.assertLessEqual(len(tag_set), len(self.tags))


class DeleteRecipeFromCollectionTests(TestCase):
    pass
