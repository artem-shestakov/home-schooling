import json
from datetime import datetime
from django import template
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.base import Model
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from .models import Day, Subject, Lesson
from .forms import CreateDay, CreateSubject, LoginForm
from django.views.decorators.csrf import csrf_protect

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
    subjects = Subject.objects.all()
    return render(request, 'day/day.html', 
        {
            "day": study_day,
            "lessons": lessons,
            "subjects": subjects
        })

def create_day(request):
    if request.method =="POST":
        form = CreateDay(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/")
    else:
        form = CreateDay()
    return render(request, "day/create.html", {"form": form})

def add_lesson(request, day_id):
    subject = request.POST.get("subject")
    description = request.POST.get("description")
    homework = request.POST.get("homework")
    grade = request.POST.get("grade")
    print(grade)
    if grade == "":
        grade = None
    
    day = Day.objects.get(id=day_id)
    subject = Subject.objects.get(title=subject)
    if day.lesson_set.filter(subject=subject.id).exists():
        return HttpResponseBadRequest("Object already exists")
    new_lesson = Lesson.objects.create(
        subject=subject,
        description=description,
        home_work=homework,
        grade=grade,
        day_id=day_id
    )

    lesson = {
        "id": new_lesson.id,
        "subject": new_lesson.subject.title,
        "description": new_lesson.description,
        "home_work": new_lesson.home_work,
        "grade": new_lesson.grade
    }

    return JsonResponse({"lesson": lesson})

def delete_lesson(request):
    lesson_id = request.POST.get("lesson_id")
    Lesson.objects.get(pk=lesson_id).delete()

    return JsonResponse({"deleted": True})