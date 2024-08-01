from django import forms
from .models import ForumThread, ForumMessage


class ForumThreadCreationForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ["fthread_title"]


class ForumMessageCreationForm(forms.ModelForm):
    class Meta:
        model = ForumMessage
        fields = ["fmessage_content"]
