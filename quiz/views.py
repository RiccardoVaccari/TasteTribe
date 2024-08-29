import random
from typing import Any
import uuid
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from django.db.models import Count
from .forms import *
from .models import *
from homepage.views import check_user_suspension


# Create your views here.
class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz

    def dispatch(self, request, *args, **kwargs):
        self.template_name = get_template_based_on_user_status(self.request.user.id, "home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        all_quizzes = Quiz.objects.annotate(num_questions=Count('quizquestion'))
        quizzes_by_difficulty = {
            "Facile": [quiz for quiz in all_quizzes if quiz.quiz_difficulty == "easy"],
            "Media": [quiz for quiz in all_quizzes if quiz.quiz_difficulty == "medium"],
            "Difficile": [quiz for quiz in all_quizzes if quiz.quiz_difficulty == "hard"]
        }

        for difficulty in quizzes_by_difficulty:
            random.shuffle(quizzes_by_difficulty[difficulty])
        context['quizzes_by_difficulty'] = quizzes_by_difficulty

        return context



class QuizCreationView(LoginRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizCreationForm
    success_url = reverse_lazy("quiz_home")

    def dispatch(self, request, *args, **kwargs):
        self.template_name = get_template_based_on_user_status(self.request.user.id, "creation")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        reg_user = None
        if self.request.user.is_authenticated:
            reg_user = RegisteredUser.objects.get(user=self.request.user.id)
        context["reg_user"] = reg_user
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
def play_quiz(request, quiz_guid):
    quiz = get_object_or_404(Quiz, quiz_guid=quiz_guid)
    questions = QuizQuestion.objects.filter(question_quiz_guid=quiz).order_by("question_sequential")
    # Check if the logged user is suspended and therefore has no access to this page
    try:
        reg_user = RegisteredUser.objects.get(user=request.user.id)
        if check_user_suspension(reg_user):
            return render(request, "quiz_not_allowed.html", {"user": request.user, "reg_user": reg_user})
    except RegisteredUser.DoesNotExist:
        return render(request, "quiz_not_allowed.html", {"user": request.user, "reg_user": None})
    # Handle quiz creation form
    if request.method == "POST":
        form = QuizGameForm(request.POST, questions=questions)
        if form.is_valid():
            results = {}
            for question in questions:
                given_answer = int(form.cleaned_data[f"question_{question.question_sequential}"])
                if given_answer + 1 == question.question_correct_answer:
                    question_result = "correct"
                else:
                    question_result = "wrong"
                results[question.question_sequential] = {
                    "given_answer": given_answer,
                    "correct_answer": question.question_correct_answer - 1,  # To avoid discrepancies between indexes
                    "possible_answers": question.question_possible_answers,
                    "question_text": question.question_text,
                    "question_result": question_result
                }
            return render(request, "quiz_result.html", {"quiz": quiz, "results": results, "user": request.user, "reg_user": reg_user})
    else:
        form = QuizGameForm(questions=questions)
    return render(request, "quiz_play.html", {"quiz": quiz, "form": form, "user": request.user, "reg_user": reg_user})


def get_template_based_on_user_status(user_id, landing_page):
    # Check if the user is suspended
    try:
        reg_user = RegisteredUser.objects.get(user=user_id)
        if not check_user_suspension(reg_user):
            if landing_page == "home":
                template_name = "quiz_home.html"
            else:
                template_name = "quiz_creation.html"
        else:
            template_name = "quiz_not_allowed.html"
    except RegisteredUser.DoesNotExist:
        template_name = "quiz_not_allowed.html"
    return template_name
