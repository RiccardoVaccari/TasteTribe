from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Field, Fieldset
from django import forms
from login.models import RegisteredUser


class SearchForm(forms.Form):
    SEARCH_TYPE_PARAM = [
        ("recipe_title", "Titolo"),
        ("author_name", "Autore"),
        ("tag_name", "Tag"),
        ("ingredient_name", "Ingrediente")
    ]
    search_string = forms.CharField(label="Chiave di ricerca", max_length=50, min_length=3, required=True)
    search_param = forms.ChoiceField(label="Cerca per", choices=SEARCH_TYPE_PARAM, required=False)
    from_homepage = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        user_suspended = kwargs.pop("user_suspended", False)
        from_homepage = kwargs.pop("from_homepage", True)
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Fieldset(
                "Cerca ricette:",
                Div(
                    Div("search_string", css_class="col-md-6"),
                    FieldWithButtons(
                        "search_param",
                        Submit("submit", "Cerca", css_class="btn btn-submit", css_id="search-btn"),
                        css_class="col-md-2"
                    ),
                    css_class="row align-items-center mb-2",
                )
            )
        )
        if not (user and user.is_authenticated and not user_suspended and from_homepage):
            # The following two lines of code are needed in order to set a default for search_param
            self.fields["search_param"].initial = "recipe_title"
            self.fields["search_param"].widget = forms.HiddenInput()
        self.fields["from_homepage"].initial = from_homepage
        self.fields["from_homepage"].widget = forms.HiddenInput()
