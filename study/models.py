from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Day(models.Model):
    date = models.DateField(
        'Study day',
        default=datetime.date.today,
        unique=True
        )

    def __str__(self) -> str:
        return str(self.date)

class Subject(models.Model):
    title = models.CharField('Subject title', max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT)
    def __str__(self) -> str:
        return self.title

class Lesson(models.Model):
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.PROTECT,
        unique=True)
    description = models.TextField('Lesson description')
    home_work = models.TextField('Home work')
    grade = models.IntegerField('Studen\'s grade for lesson',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True)
    day = models.ForeignKey(Day, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{str(self.day)}_{str(self.subject)}"
