from django.db import models
from login.models import RegisteredUser, User


# Create your models here.
class Quiz(models.Model):

    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('medium', 'Media'),
        ('hard', 'Difficile'),
    ]

    quiz_guid = models.UUIDField(primary_key=True)
    quiz_title = models.CharField(max_length=50)
    quiz_difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    quiz_author = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz_creation_date = models.DateField(null=True)


class QuizQuestion(models.Model):
    question_quiz_guid = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_sequential = models.IntegerField()
    question_text = models.TextField()
    question_correct_answer = models.IntegerField()
    question_possible_answers = models.JSONField()

    class Meta:
        unique_together = [["question_quiz_guid", "question_sequential"]]
