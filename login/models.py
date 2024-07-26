from django.db import models
from django.contrib.auth.models import User


class RegisteredUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reg_user_profile_pic = models.TextField(null=True)
    reg_user_about = models.CharField(max_length=200, null=True)
    reg_user_preferences = models.JSONField(default=dict())
    reg_user_status = models.JSONField(default=dict([("is_suspended", False), ("suspension_end", None)]))
    reg_user_warning_count = models.IntegerField(default=0)
