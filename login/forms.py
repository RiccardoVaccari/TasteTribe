import base64
from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    reg_user_about = forms.CharField(widget=forms.Textarea, required=False)
    reg_user_profile_pic = forms.ImageField(required=False)


    class Meta:
        model = RegisteredUser
        fields = ["reg_user_profile_pic", "reg_user_about"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
            self.fields["username"].initial = user.username

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            try:
                user = self.instance.user
                if User.objects.exclude(id=user.id).filter(username=username).exists():
                    raise ValidationError("Questo username è già in uso. Scegline un altro.")
            except User.DoesNotExist:
                pass
        return username


    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            try:
                user = self.instance.user
                if User.objects.exclude(id=user.id).filter(email=email).exists():
                    raise ValidationError("Questa email è già in uso. Scegline un'altra.")
            except User.DoesNotExist:
                pass
        return email

    def clean(self):
        data = super().clean()
        if isinstance(data["reg_user_profile_pic"], InMemoryUploadedFile):
            data["reg_user_profile_pic"] = base64.b64encode(data["reg_user_profile_pic"].read()).decode('utf-8')
        return data
    