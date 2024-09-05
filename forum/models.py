from django.db import models
from login.models import User


# Create your models here.
class ForumThread(models.Model):
    fthread_guid = models.UUIDField(primary_key=True)
    fthread_title = models.CharField(max_length=150)
    fthread_creator = models.ForeignKey(User, on_delete=models.PROTECT)
    fthread_creation_date = models.DateTimeField()


class ForumMessage(models.Model):
    fmessage_thread_guid = models.ForeignKey(ForumThread, on_delete=models.CASCADE)
    fmessage_creation_date = models.DateTimeField()
    fmessage_author = models.ForeignKey(User, on_delete=models.PROTECT)
    fmessage_up_votes = models.IntegerField(default=0)
    fmessage_down_votes = models.IntegerField(default=0)
    fmessage_content = models.TextField()

    class Meta:
        unique_together = [['fmessage_thread_guid', 'fmessage_creation_date', 'fmessage_author']]


class ForumMessageInteraction(models.Model):
    interaction_fmessage = models.ForeignKey(ForumMessage, on_delete=models.CASCADE)
    interaction_user = models.ForeignKey(User, on_delete=models.PROTECT)
    interaction_liked = models.IntegerField(null=True)  # This field will be 1 if the User liked the message, -1 if the user disliked the message

    class Meta:
        unique_together = ("interaction_fmessage", "interaction_user")
