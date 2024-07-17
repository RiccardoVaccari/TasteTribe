from django.db import models
from login.models import RegisteredUser


# Create your models here.

class ForumThread(models.Model):
    fthread_guid = models.UUIDField(primary_key=True)
    fthread_title = models.CharField(max_length=150)
    fthread_creator = models.ForeignKey(RegisteredUser, on_delete=models.PROTECT)
    fthread_creation_date = models.DateField()


class ForumMessage(models.Model):
    fmessage_thread_guid = models.ForeignKey(ForumThread, on_delete=models.CASCADE)
    fmessage_creation_date = models.DateField()
    fmessage_author = models.ForeignKey(RegisteredUser, on_delete=models.PROTECT)
    fmessage_up_votes = models.IntegerField()
    fmessage_down_votes = models.IntegerField()

    class Meta:
        unique_together = [['fmessage_thread_guid', 'fmessage_creation_date', 'fmessage_author']]
