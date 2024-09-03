import base64
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from common.utils import generate_avatar
from .models import *


class CollectionCreationForm(forms.ModelForm):
    collection_cover = forms.ImageField(required=False, widget=forms.FileInput(attrs={"accept": "image/jpeg, image/png, image/gif"}))

    class Meta:
        model = RecipesCollection
        fields = ["collection_name", "collection_cover", "collection_is_private"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.fields["collection_name"].label = "Nome della nuova raccolta"
        self.fields["collection_cover"].label = "Copertina della nuova raccolta"
        self.fields["collection_is_private"].label = "Raccolta privata"
        self.helper.add_input(Submit("submit", "Crea", css_class="btn-primary"))

    def clean_collection_cover(self):
        image = self.cleaned_data.get("collection_cover")
        if image:
            image_data = image.read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            return image_base64
        return generate_avatar("", 800, 350)
