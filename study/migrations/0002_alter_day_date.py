# Generated by Django 3.2.9 on 2021-12-02 09:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='date',
            field=models.DateField(default=datetime.date.today, unique_for_date=True, verbose_name='Study day'),
        ),
    ]
