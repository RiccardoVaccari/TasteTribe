from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    reg_user_profile_pic = forms.ImageField(required=False)
    reg_user_preferences = forms.JSONField(required=False)

    class Meta:
        model = RegisteredUser
        fields = ["reg_user_profile_pic", "reg_user_about", "reg_user_preferences"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("first_name"),
            Field("last_name"),
            Field("email"),
            Field("reg_user_about"),
            Field("reg_user_profile_pic"),
            Field("reg_user_preferences"),
            Submit("submit", "Salva")
        )
