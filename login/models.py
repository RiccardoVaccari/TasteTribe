from django.db import models


# Create your models here.

class RegisteredUser(models.Model):
    reg_user_guid = models.UUIDField(primary_key=True)
    reg_user_name = models.CharField(max_length=50)
    reg_user_surname = models.CharField(max_length=50)
    reg_user_username = models.CharField(max_length=50, unique=True)
    reg_user_password = models.TextField()
    reg_user_email = models.EmailField()
    reg_user_profile_pic = models.TextField()
    reg_user_about = models.CharField(max_length=200)
    reg_user_preferences = models.JSONField()
    reg_user_status = models.JSONField()
    reg_user_warning_count = models.IntegerField()
