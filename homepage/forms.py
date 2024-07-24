from django import forms


class SearchForm(forms.Form):
    # To be implemented in a future feature (the advanced search)
    # CHOICE_SECTORS = [("Title", "Ricerca per titolo"), ("Autore", "Ricerca per autore"), ("Tag", "Ricerca per tag"), ("Ingrediente", "Ricerca per ingrediente")]
    search_string = forms.CharField(help_text="Cerca una ricetta", max_length=50, min_length=3, required=True)
