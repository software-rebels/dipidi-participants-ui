# Generated by Django 4.0.1 on 2022-01-31 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0005_participanttask_is_ready'),
    ]

    operations = [
        migrations.AddField(
            model_name='participanttask',
            name='is_skipped',
            field=models.BooleanField(default=False),
        ),
    ]
