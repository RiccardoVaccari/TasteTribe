from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import RegisteredUser
from .views import get_template_based_on_user_status
import uuid

class GetTemplateBasedOnUserStatusTest(TestCase):
    def setUp(self):
        # Get the user model (custom model extending AbstractUser)
        self.User = get_user_model()

        # Create a user
        self.user = self.User.objects.create_user(username='testuser', password='12345')
        
        # Create a registered user associated with the user
        self.reg_user = RegisteredUser.objects.create(
            user=self.user,
            reg_user_profile_pic='profile_pic.png',
            reg_user_about='About me',
            reg_user_search_history={},
            reg_user_status={
                "is_suspended": False,
                "suspension_end": None,
                "notifications": []
            },
            reg_user_warning_count=0
        )

    def test_user_not_suspended_home_template(self):
        # Test when the user is not suspended and the landing page is "home"
        template_name = get_template_based_on_user_status(self.user.id, "home")
        self.assertEqual(template_name, "quiz_home.html")

    def test_user_not_suspended_creation_template(self):
        # Test when the user is not suspended and the landing page is "creation"
        template_name = get_template_based_on_user_status(self.user.id, "creation")
        self.assertEqual(template_name, "quiz_creation.html")

    def test_user_suspended(self):
        # Mark the user as suspended
        self.reg_user.reg_user_status["is_suspended"] = True
        self.reg_user.save()

        # Test when the user is suspended
        template_name = get_template_based_on_user_status(self.user.id, "home")
        self.assertEqual(template_name, "quiz_not_allowed.html")

    def test_user_does_not_exist(self):
        # Test when the RegisteredUser does not exist
        self.reg_user.delete()
        template_name = get_template_based_on_user_status(self.user.id, "home")
        self.assertEqual(template_name, "quiz_not_allowed.html")