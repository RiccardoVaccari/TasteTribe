from django.db import models
from login.models import RegisteredUser, User


# Create your models here.

class Quiz(models.Model):
    quiz_guid = models.UUIDField(primary_key=True)
    quiz_title = models.CharField(max_length=50)
    quiz_difficulty = models.IntegerField()
    quiz_author = models.ForeignKey(User, on_delete=models.PROTECT)


class QuizQuestion(models.Model):
    question_quiz_guid = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_sequential = models.IntegerField()
    question_correct_answer = models.IntegerField()
    question_possible_answers = models.JSONField()

    class Meta:
        unique_together = [["question_quiz_guid", "question_sequential"]]
