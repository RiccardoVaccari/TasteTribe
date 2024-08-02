from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from login.models import RegisteredUser


class SearchForm(forms.Form):
    SEARCH_TYPE_PARAM = [
        ("recipe_title", "Titolo"),
        ("author_name", "Autore"),
        ("tag_name", "Tag"),
        ("ingredient_name", "Ingrediente")
    ]
    search_string = forms.CharField(label="Cerca ricette", max_length=50, min_length=3, required=True)
    search_param = forms.ChoiceField(label="Cerca per", choices=SEARCH_TYPE_PARAM, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        user_suspended = kwargs.pop("user_suspended", False)
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        if user and user.is_authenticated and not user_suspended:
            self.helper.layout = Layout(
                "search_string",
                Div("search_param", css_id="search_param_div"),
                Submit("submit", "Cerca")
            )
        else:
            self.helper.layout = Layout(
                "search_string",
                Submit("submit", "Cerca")
            )
            # The following two lines of code are needed in order to set a default for search_param
            self.fields["search_param"].initial = "recipe_title"
            self.fields["search_param"].widget = forms.HiddenInput()


