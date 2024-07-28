import json
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, BaseInput, Fieldset, Div, Row
from crispy_forms.bootstrap import StrictButton
from django.forms import inlineformset_factory
from .models import Quiz, QuizQuestion


class QuizCreationForm(forms.ModelForm):

    quiz_difficulty = forms.IntegerField(min_value=1, max_value=5)

    quiz_question_text = forms.CharField(required=True)
    quiz_question_answer1 = forms.CharField(required=True)
    quiz_question_answer2 = forms.CharField(required=True)
    quiz_question_answer3 = forms.CharField(required=True)
    quiz_question_answer4 = forms.CharField(required=True)
    quiz_question_correct_answer = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[(i, "") for i in range(1, 5)],
    )
    quiz_questions_list = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Quiz
        fields = ["quiz_title", "quiz_difficulty"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = []
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.layout = Layout(
            Fieldset(
                "Dettagli sul quiz",
                Field("quiz_title"),
                Field("quiz_difficulty")
            ),
            Div(
                "Aggiungi domande al quiz",
                Div(
                    Field("quiz_question_text"),
                    Row(
                        Field("quiz_question_answer1"),
                        Field("quiz_question_answer2"),
                        Field("quiz_question_answer3"),
                        Field("quiz_question_answer4"),
                        Field("quiz_question_correct_answer", css_class="correct-answer-radio")
                    ),
                    StrictButton("Aggiungi domanda", css_class="col-md-1 btn btn-info", css_id="add-question-btn"),
                    Field("quiz_questions_list", css_class="d-none"),
                    css_class="row align-items-center"
                )
            )
        )
        self.helper.add_input(Submit("submit", "Crea Quiz!"))

    def clean_quiz_questions_list(self):
        quiz_questions_list = self.cleaned_data.get("quiz_questions_list")
        if quiz_questions_list:
            return json.loads(quiz_questions_list)
        return []

    def clean(self):
        cleaned_data = super().clean()
        quiz_questions_list = cleaned_data.get("quiz_questions_list", [])
        if not len(quiz_questions_list):
            self.add_error(None, "Il quiz deve avere almeno una domanda!")
        return cleaned_data
