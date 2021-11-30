from datetime import datetime
from django import template
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.base import Model
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .models import Day, Subject
from .forms import CreateSubject, LoginForm

register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    nxt = request.session['next']
                    if nxt is None:
                        return redirect("/")
                    else:
                        return redirect(nxt)
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
        request.session['next'] = request.GET.get('next', '/')
    return render(request, 'account/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect("/")

def index(request):
    days = Day.objects.all()
    return render(request, "subject/index.html", {"days": days})

def all_subjects(request):
    subjects = Subject.objects.order_by('title')
    context = {
        "subjects": subjects
    }
    return render(request, 'subject/subjects.html', context)

def subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    context = {
        "subject": subject,
    }
    return render(request, 'subject/subject.html', context)

@login_required(login_url='/login')
def create_subject(request):
    if request.user.is_superuser:
        if request.method == "POST":
            form = CreateSubject(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect("/subjects")
        else:
            form = CreateSubject()
        return render(request, "subject/create.html", {'form': form})
    else:
        return HttpResponse("Access forbidden")

def get_day(request, year, month, day):
    date = datetime(year, month, day)
    study_day = Day.objects.get(date=date)
    lessons = study_day.lesson_set.all()
    return render(request, 'day/day.html', 
        {
            "day": study_day,
            "lessons": lessons
        })