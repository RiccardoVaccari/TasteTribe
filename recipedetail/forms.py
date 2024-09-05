import json
from typing import Any
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Div, HTML
from crispy_forms.bootstrap import StrictButton, InlineRadios, FieldWithButtons
from homepage.models import Recipe, TagXRecipe
from .models import Allergen, IngredientXRecipe, RecipeStep, Review

CATEGORIES = [
    ("Antipasto", "Antipasto"),
    ("Primo piatto", "Primo piatto"),
    ("Secondo piatto", "Secondo piatto"),
    ("Contorno", "Contorno"),
    ("Dessert", "Dessert"),
]


class RecipeForm(forms.ModelForm):
    recipe_cover = forms.ImageField(label="Immagine di copertina", required=False)
    recipe_category = forms.ChoiceField(
        choices=CATEGORIES,
        label="Seleziona il tipo di portata",
        widget=forms.RadioSelect,
        initial="Primo piatto",
    )
    hours = forms.IntegerField(label="Ore", min_value=0, initial=0)
    minutes = forms.IntegerField(label="Minuti", min_value=0, initial=0)

    # INGREDIENTS
    ingredient = forms.CharField(label="Ingrediente", max_length=50, required=False)
    ingredients_list = forms.CharField(widget=forms.HiddenInput(), required=False)
    dosage_per_person = forms.CharField(max_length=50, required=False, label="Dose per persona")
    allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Allergeni"
    )

    # STEPS
    step_description = forms.CharField(label="Descrizione", min_length=30, widget=forms.Textarea, required=False)
    step_required_hours = forms.IntegerField(label="Ore per step", min_value=0, initial=0, required=False)
    step_required_minutes = forms.IntegerField(label="Minuti per step", min_value=0, initial=0, required=False)
    steps_list = forms.CharField(widget=forms.HiddenInput(), required=False)

    # TAGS
    tag = forms.CharField(max_length=100, required=False)
    tags_list = forms.CharField(widget=forms.HiddenInput(), required=False)

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
        starting_recipe = kwargs.pop("starting_recipe", None)
        super().__init__(*args, **kwargs)
        self.fields["recipe_name"].label = "Titolo ricetta"
        self.fields["recipe_notes"].label = "Note sulla ricetta"
        self.fields["recipe_description"].label = "Descrizione ricetta"
        self.fields["recipe_is_private"].label = "Ricetta privata"
        self.fields["recipe_is_vegetarian"].label = "Ricetta vegetariana"
        self.fields["recipe_is_vegan"].label = "Ricetta vegana"
        self.fields["recipe_gluten_free"].label = "Senza glutine"
        if (self.instance and self.instance.pk) or (starting_recipe):
            recipe = self.instance
            if starting_recipe:
                recipe = starting_recipe
                self.fields['recipe_name'].initial = recipe.recipe_name
                self.fields['recipe_cover'].initial = recipe.recipe_cover
                self.fields['recipe_notes'].initial = recipe.recipe_notes
                self.fields['recipe_description'].initial = recipe.recipe_description
                self.fields['recipe_category'].initial = recipe.recipe_category
                self.fields['recipe_is_private'].initial = recipe.recipe_is_private
                self.fields['recipe_is_vegetarian'].initial = recipe.recipe_is_vegetarian
                self.fields['recipe_gluten_free'].initial = recipe.recipe_gluten_free
                self.fields['recipe_is_vegan'].initial = recipe.recipe_is_vegan
            prep_time = recipe.recipe_prep_time
            self.fields["hours"].initial = prep_time.seconds // 3600
            self.fields["minutes"].initial = (prep_time.seconds // 60) % 60
            # Populate existing ingredients, tags and steps
            ingredients = IngredientXRecipe.objects.filter(ixr_recipe_guid=recipe).select_related("ixr_ingredient_guid")
            self.fields["ingredients_list"].initial = json.dumps([
                {
                    "name": ingredient_x_recipe.ixr_ingredient_guid.ingredient_name,
                    "dosage": ingredient_x_recipe.ixr_dosage_per_person,
                    "allergens": ingredient_x_recipe.ixr_ingredient_guid.ingredient_allergens,
                } for ingredient_x_recipe in ingredients
            ])
            self.fields["steps_list"].initial = json.dumps([
                {
                    "description": step.step_description,
                    "hours": step.step_required_time.seconds // 3600,
                    "minutes": (step.step_required_time.seconds // 60) % 60,
                } for step in RecipeStep.objects.filter(step_recipe_guid=recipe)
            ])
            tags = TagXRecipe.objects.filter(txr_recipe_guid=recipe).select_related("txr_tag_guid")
            self.fields["tags_list"].initial = json.dumps([
                tag_x_recipe.txr_tag_guid.tag_name for tag_x_recipe in tags if tag_x_recipe.txr_tag_guid.tag_field not in ("Ingredient", "Course")
            ])
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
                "Categoria",
                Div(
                    InlineRadios("recipe_category"),
                    css_class="form-check-inline radio-input"
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
                    FieldWithButtons("dosage_per_person", StrictButton("Aggiungi", css_class="btn btn-info", css_id="add-ingredient-btn"), css_class="col-md-4"),
                    Field("ingredients_list", css_class="d-none"),
                    css_class="row align-items-center mb-2",
                ),
                Div(css_id="ingredients-list"),
                css_class="p-2 my-2"
            ),
            Fieldset(
                "Crea step di preparazione",
                Div(
                    Field("step_description"),
                    Div(
                        Div("step_required_hours", css_class="col-md-3",),
                        Div("step_required_minutes", css_class="col-md-3",),
                        StrictButton("Aggiungi step", css_class="col-md-2 btn btn-info", css_id="add-step-btn"),
                        css_class="row",
                    ),
                ),
                Field("steps_list", css_class="d-none"),
                Div(css_id="steps-list"),
                css_class="p-2 my-2"
            ),
            Fieldset(
                "Aggiungi tags",
                FieldWithButtons("tag", StrictButton("Aggiungi tag", css_class="btn btn-info", css_id="add-tag-btn"),),
                Field("tags_list", css_class="d-none"),
                Div(css_id="tags-list"),
                css_class="p-2 my-2"
            )
        )

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
            self.add_error(field="ingredient", error="La ricetta deve avere almeno un ingrediente")
        if not len(cleaned_data.get("steps_list")):
            self.add_error(field="step_description", error="La ricetta deve avere almeno un passo di preparazione")
        if not len(cleaned_data.get("tags_list")):
            self.add_error(field="tag", error="La ricetta deve avere almeno un custom tag")
        if cleaned_data.get("hours") == 0 and cleaned_data.get("minutes") == 0:
            self.add_error(field=None, error="Il tempo di preparazione non può essere 0 ore e 0 minuti")
        return cleaned_data


class CreateRecipeForm(RecipeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append(
            Div(
                HTML('<button type="submit" name="submit" id="create-recipe-btn" class="btn btn-primary"><i class="fa-solid fa-plus"></i> Crea ricetta</button>'),
                css_class="form-group text-center"
            )
        )


class EditRecipeForm(RecipeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append(
            Div(
                HTML('<button type="submit" name="submit" id="edit-recipe-btn" class="btn btn-primary"><i class="fa-solid fa-pen"></i> Modifica ricetta</button>'),
                css_class="form-group text-center"
            )
        )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["review_grade", "review_notes"]
