from django.urls import path
from quiz.views import *

urlpatterns = [
    path("quiz/", QuizListView.as_view(), name="quiz_home"),
    path("quiz/create/", QuizCreationView.as_view(), name="quiz_creation"),
    path("quiz/play/<uuid:quiz_guid>/", play_quiz, name="quiz_game"),
]