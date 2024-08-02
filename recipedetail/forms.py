import json
from typing import Any
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Div
from crispy_forms.bootstrap import StrictButton, InlineRadios, FieldWithButtons

from homepage.models import Recipe
from .models import Allergen

CATEGORIES = [
    ("Antipasto", "Antipasto"),
    ("Primo piatto", "Primo piatto"),
    ("Secondo piatto", "Secondo piatto"),
    ("Contorno", "Contorno"),
    ("Dessert", "Dessert"),
]


class RecipeForm(forms.ModelForm):

    recipe_cover = forms.ImageField(required=False)
    recipe_category = forms.ChoiceField(
        choices=CATEGORIES,
        label="Seleziona il tipo di portata",
        widget=forms.RadioSelect,
        initial="Primo piatto",
    )

    hours = forms.IntegerField(min_value=0, initial=0)
    minutes = forms.IntegerField(min_value=0, initial=0)

    # INGREDIENTS
    ingredient = forms.CharField(max_length=50, required=False)
    ingredients_list = forms.CharField(
        widget=forms.HiddenInput(), required=False)
    dosage_per_person = forms.CharField(
        max_length=50, required=False, label="Dose per persona")
    allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Allergeni"
    )

    # STEPS
    step_description = forms.CharField(
        min_length=30, widget=forms.Textarea, required=False)
    step_image = forms.ImageField(required=False)
    step_required_hours = forms.IntegerField(
        min_value=0, initial=0, required=False)
    step_required_minutes = forms.IntegerField(
        min_value=0, initial=0, required=False)
    steps_list = forms.CharField(
        widget=forms.HiddenInput(), required=False)

    # TAGS
    tag = forms.CharField(max_length=100, required=False)
    tags_list = forms.CharField(
        widget=forms.HiddenInput(), required=False)

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

        self.ingredients = []
        self.steps = []

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
                    FieldWithButtons("dosage_per_person", StrictButton(
                        "Aggiungi", css_class="btn btn-info", css_id="add-ingredient-btn"), css_class="col-md-4"),
                    Field("ingredients_list", css_class="d-none"),
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
                StrictButton("Aggiungi passo",
                             css_class="btn btn-info", css_id="add-step-btn"),
                Field("steps_list", css_class="d-none"),
                css_class="border p-2 my-2"
            ),
            Fieldset(
                "Aggiungi tags",
                FieldWithButtons("tag", StrictButton(
                    "Aggiungi tag", css_class="btn btn-info", css_id="add-tag-btn"),),
                Field("tags_list", css_class="d-none"),
                css_class="border p-2 my-2"
            )
        )

        self.helper.add_input(Submit("submit", "Crea ricetta"))

    def clean_ingredients_list(self):
        return self.json_clean(self.cleaned_data.get("ingredients_list"))

    def clean_steps_list(self):
        return self.json_clean(self.cleaned_data.get("steps_list"))

    def clean_tags_list(self):
        return self.json_clean(self.cleaned_data.get("tags_list"))
    
    def json_clean(self, data) -> list:
        if data:
            return json.loads(data)
        return [] 


    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        if not len(cleaned_data.get("ingredients_list")):
            self.add_error(field="ingredient",
                           error="La ricetta deve avere almeno un ingrediente")

        if not len(cleaned_data.get("steps_list")):
            self.add_error(field="step_description",
                           error="La ricetta deve avere almeno un passo di preparazione")

        if not len(cleaned_data.get("tags_list")):
            self.add_error(field="tag",
                           error="La ricetta deve avere almeno un custom tag")

        if cleaned_data.get("hours") == 0 and cleaned_data.get("minutes") == 0:
            self.add_error(
                field=None, error="Il tempo di preparazione non può essere 0 ore e 0 minuti")

        return cleaned_data
