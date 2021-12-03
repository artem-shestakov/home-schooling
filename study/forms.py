from django import forms
from django.contrib.auth import models
from django.forms import ModelForm, Textarea
from .models import Day, Subject
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class CreateSubject(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateSubject, self).__init__(*args, **kwargs)
        self.fields['teacher']=forms.ModelChoiceField(queryset=User.objects.filter(groups__name="teachers"))

    class Meta:
        model = Subject
        fields = ["title", "teacher"]
        labels = {
            'title': 'Название предмета',
        }

class ChangeDay(ModelForm):
    
    class Meta:
        model = Day
        fields = ["date"]
        labels = {
            "date": "Дата",
        }
        
