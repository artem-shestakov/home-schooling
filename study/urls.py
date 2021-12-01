from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.user_login, name="login"),
    path("logout", views.user_logout, name="logout"),
    path("day/<int:year>/<int:month>/<int:day>", views.get_day, name="day"),
    path("day/<int:day_id>/lesson/add", views.add_lesson, name="add_lesson"),
    path("day/create", views.create_day, name="create_day"),
    path("lesson/delete", views.delete_lesson, name="delete_lesson"),
    path("subject", views.all_subjects, name="subjects"),
    path("subject/<int:subject_id>", views.subject, name="subject"),
    path("subject/create", views.create_subject, name="create_subject")
    
]