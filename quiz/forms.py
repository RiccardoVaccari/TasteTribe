import json
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, BaseInput, Fieldset, Div, Row
from crispy_forms.bootstrap import StrictButton, InlineRadios
from django.forms import inlineformset_factory
from .models import Quiz, QuizQuestion


class QuizCreationForm(forms.ModelForm):

    quiz_difficulty = forms.ChoiceField(
        choices=[
            ("easy", "Facile"),
            ("medium", "Medio"),
            ("hard", "Difficile"),
        ],
        label="Seleziona la difficoltà",
        widget=forms.RadioSelect,
        initial="easy",
    )

    quiz_title = forms.CharField(required=True, label="Titolo del quiz")
    quiz_question_text = forms.CharField(required=False, label="Testo della domanda")
    quiz_question_answer1 = forms.CharField(required=False, label="Risposta 1:")
    quiz_question_answer2 = forms.CharField(required=False, label="Risposta 2:")
    quiz_question_answer3 = forms.CharField(required=False, label="Risposta 3:")
    quiz_question_answer4 = forms.CharField(required=False, label="Risposta 4:")
    quiz_question_correct_answer = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[(i, f"{i}") for i in range(1, 5)],
        required=False,
        label="Seleziona la risposta corretta"
    )
    quiz_questions_list = forms.CharField(
        widget=forms.HiddenInput(), required=False)

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
                Div(
                    InlineRadios("quiz_difficulty"),
                    css_class="form-check-inline radio-input"
                )
            ),
            Div(
                Fieldset(
                    "Aggiungi domande al quiz",
                    Field("quiz_question_text"),
                    Div(
                        Div(
                            Field("quiz_question_answer1"),
                            Field("quiz_question_answer2"),
                            Field("quiz_question_answer3"),
                            Field("quiz_question_answer4"),
                            css_class="col-md-10"
                        ),
                        Div(
                            InlineRadios("quiz_question_correct_answer",
                                         css_class="correct-answer-radio", wrapper_class="d-flex align-items-center"),
                            css_class="col-md-2"
                        ),
                        css_class="row align-items-center"
                    ),
                    Div(
                        StrictButton(
                            "Aggiungi domanda", css_class="btn btn-success", css_id="add-question-btn"),
                        css_class="mb-2"
                    ), Field("quiz_questions_list", css_class="d-none"),
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


class QuizGameForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions")
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        layout = []
        for question in questions:
            field_name = f"question_{question.question_sequential}"
            self.fields[field_name] = forms.ChoiceField(
                label=f"{question.question_sequential}) {question.question_text}",
                choices=[(question.question_possible_answers.index(answer), answer)
                         for answer in question.question_possible_answers],
                widget=forms.RadioSelect()
            )
            layout.append(Div(field_name, css_class="border-bottom border-start mb-3 p-4 border-black rounded-start"))
        layout.append(ButtonHolder(Submit("submit", "Rispondi al quiz!", css_class="btn-success mb-3")))
        self.helper.layout = Layout(*layout)
