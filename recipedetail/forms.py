from typing import Any
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Div
from crispy_forms.bootstrap import StrictButton, InlineRadios

from homepage.models import Recipe

CATEGORIES = [
    ("antipasto", "Antipasto"),
    ("primo-piatto", "Primo piatto"),
    ("secondo-piatto", "Secondo piatto"),
    ("contorno", "Contorno"),
    ("dessert", "Dessert"),
]


class CreateRecipeForm(forms.ModelForm):

    recipe_cover = forms.ImageField(required=False)
    recipe_category = forms.ChoiceField(
        choices=CATEGORIES,
        label="Seleziona il tipo di portata",
        widget=forms.RadioSelect,
        initial="primo-piatto",
    )

    hours = forms.IntegerField(min_value=0, initial=0)
    minutes = forms.IntegerField(min_value=0, initial=0)

    ingredient = forms.CharField(max_length=50, required=False)
    dosage_per_person = forms.CharField(
        max_length=50, required=True, label="Dose per persona")

    step_description = forms.CharField(min_length=30, widget=forms.Textarea)
    step_image = forms.ImageField(required=False)
    step_required_hours = forms.IntegerField(min_value=0, initial=0)
    step_required_minutes = forms.IntegerField(min_value=0, initial=0)

    class Meta:
        model = Recipe
        fields = [
            "recipe_name",
            "recipe_cover",
            "recipe_notes",
            "recipe_description",
            "recipe_category",
            "recipe_is_private",
            "recipe_is_vegetarian",
            "recipe_gluten_free",
            "recipe_is_vegan"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.layout = Layout(
            Fieldset(
                "Informazioni ricetta",
                Field("recipe_name"),
                Field("recipe_cover"),
                Field("recipe_notes"),
                Field("recipe_description"),
            ),
            Div(
                Div(Field("recipe_is_private"), css_class="col-md-3"),
                Div(Field("recipe_is_vegetarian"), css_class="col-md-3"),
                Div(Field("recipe_gluten_free"), css_class="col-md-3"),
                Div(Field("recipe_is_vegan"), css_class="col-md-3"),
                css_class="row align-items-center"
            ),
            Fieldset(
                'Categoria',
                Div(
                    InlineRadios('recipe_category'),
                    # css_class='form-check'
                )
            ),
            Fieldset(
                "Tempo di preparazione",
                Div(
                    Div("hours", css_class="col-md-2",),
                    Div("minutes", css_class="col-md-2",),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Aggiungi ingredienti",
                Div(
                    Div("ingredient", css_class="col-md-7",),
                    Div("dosage_per_person", css_class="col-md-3",),
                    StrictButton(
                        "Aggiungi", css_class="col-md-1 btn btn-info"),
                    css_class="row align-items-center",
                ),
                css_class="border p-2 my-2"
            ),
            Fieldset(
                "Crea passo di preparazione",
                Div(
                    Field('step_description'),
                    Field('step_image'),
                    Div(
                        Div("step_required_hours", css_class="col-md-3",),
                        Div("step_required_minutes", css_class="col-md-3",),
                        css_class="row",
                    ),
                ),
                StrictButton("Aggiungi passo", css_class="btn btn-info"),
                css_class="border p-2 my-2"
            )
        )
        self.helper.add_input(Submit("submit", "Crea ricetta"))

