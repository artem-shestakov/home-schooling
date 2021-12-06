from functools import cache
import json
from datetime import datetime
from django import template
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db.models.base import Model
from django.db.utils import IntegrityError
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest, QueryDict, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from .models import Day, Subject, Lesson
from .forms import ChangeDay, CreateSubject, LoginForm
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
    days = Day.objects.all().order_by('-date')
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
                return HttpResponseRedirect("/subject")
        else:
            form = CreateSubject()
        return render(request, "subject/create.html", {'form': form})
    else:
        return HttpResponse("Access forbidden")

def get_day(request, id):
    study_day = Day.objects.get(pk=id)
    lessons = study_day.lesson_set.all()
    subjects = Subject.objects.all()
    return render(request, 'day/day.html', 
        {
            "day": study_day,
            "lessons": lessons,
            "subjects": subjects
        })

def create_day(request):
    date = request.POST.get("date")
    try:
        date = datetime.utcfromtimestamp(int(date)).strftime("%Y-%m-%d")
    except ValueError:
        return JsonResponse({
            "error": True,
            "message": "Ошибка в предоставленной дате"
        }, status=400)
    day = Day(date=date)
    try:
        day.save()
    except ValidationError:
        return JsonResponse({
            "created": False,
            "message": "Ошибка в предоставленной дате"
        }, status=400)
    except IntegrityError:
        return JsonResponse({
            "created": False,
            "message": "Невозможно создать объект"
        }, status=500)
    return JsonResponse({
        "error": False,
        "day_id": day.id
        })

def update_day(request, day_id):
    if request.method == "PUT":
        date = QueryDict(request.body).get("date")
        day = get_object_or_404(Day, pk=day_id)
        day.date = datetime.strptime(date, "%Y-%m-%d")
        day.save()
        return JsonResponse({"error": False})
    else: 
        return HttpResponseNotAllowed(["PUT"])

def delete_day(request, day_id):
    if request.method == "DELETE":
        day = get_object_or_404(Day, pk=day_id)
        day.delete()
        return JsonResponse({"error": False})
    else:
        return HttpResponseNotAllowed(["DELETE"])

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

def get_lesson(request):
    lesson_id = request.GET.get("lesson_id")
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    data = {
        "lesson_id": lesson.id,
        "subject": lesson.subject.title,
        "description": lesson.description,
        "homework": lesson.home_work,
        "grade": lesson.grade,
        "day": lesson.day.id
    }
    return JsonResponse(data)

def update_lesson(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    lesson = get_object_or_404(Lesson, pk=int(body["lesson_id"]))
    subject = Subject.objects.get(title=body["subject"])
    lesson.subject = subject
    lesson.description = body["description"]
    lesson.home_work = body["home_work"]
    if body["grade"]:
        lesson.grade = int(body["grade"])
    else:
        lesson.grade = None
    lesson.save()
    return JsonResponse({
        "error": False,
        "lesson": lesson.id
    })

def delete_lesson(request):
    lesson_id = request.POST.get("lesson_id")
    Lesson.objects.get(pk=lesson_id).delete()

    return JsonResponse({"deleted": True})