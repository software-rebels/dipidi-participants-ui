# Generated by Django 4.0.1 on 2022-01-31 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0004_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='participanttask',
            name='is_ready',
            field=models.BooleanField(default=False),
        ),
    ]
