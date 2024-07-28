import uuid
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from .forms import *
from .models import *


# Create your views here.
class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quiz_home.html"


class QuizCreationView(LoginRequiredMixin, CreateView):
    model = Quiz
    template_name = "quiz_creation.html"
    form_class = QuizCreationForm
    success_url = reverse_lazy("quiz_home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        # Saving the Quiz entity
        quiz: Quiz = form.instance
        quiz.quiz_guid = uuid.uuid4()
        quiz.quiz_author = self.request.user
        quiz.quiz_creation_date = date.today()
        quiz.save()
        question_sequential = 1
        quiz_questions_list = form.cleaned_data.get("quiz_questions_list", [])
        for quiz_question in quiz_questions_list:
            quiz_question_instance = QuizQuestion(
                question_sequential=question_sequential,
                question_quiz_guid=quiz,
                question_text=quiz_question.get("question_text"),
                question_possible_answers=quiz_question.get("question_possible_answers"),
                question_correct_answer=quiz_question.get("question_correct_answer")
            )
            quiz_question_instance.save()
            question_sequential += 1
        return super().form_valid(form)


@login_required
def play_quiz(request):
    pass
