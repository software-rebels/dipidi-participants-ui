import random

from django.contrib.auth.models import User
from django.db import models
import uuid


def getRandomToolingLevel():
    return random.choice([1,2,3])


# Create your models here.
class Participant(models.Model):
    TOOLING_CHOICES = [
        ('1', 'NO TOOL'),
        ('2', 'EXISTING TOOL'),
        ('3', 'DiPiDi')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='participant')
    link = models.UUIDField(default=uuid.uuid4, unique=True)
    tooling_level = models.CharField(max_length=1, choices=TOOLING_CHOICES, default=getRandomToolingLevel)
    logged_in = models.BooleanField(default=False)
    finished_experiment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email or self.user.username

    @classmethod
    def createParticipant(cls, email):
        user = User.objects.get_or_create(email=email,
                                          defaults=dict(
                                              username=email,
                                              password=uuid.uuid4()
                                          ))[0]
        return Participant.objects.get_or_create(user=user)[0]


class TimeLog(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.participant.user.username}-{self.action}-{self.created_at}'

    @classmethod
    def createAction(cls, action: str, participant: Participant):
        return cls.objects.create(
            participant=participant,
            action=action
        )


class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ('A', 'Type A'),
        ('B', 'Type B'),
        ('C', 'Type C'),
        ('Q', 'Questionnaire')
    ]
    task_type = models.CharField(max_length=1, choices=TASK_TYPE_CHOICES)
    project = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    extra = models.JSONField()  # Commits, RPC Server, etc
    participants = models.ManyToManyField(Participant, through='ParticipantTask', related_name='tasks')

    class Meta:
        ordering = ('task_type', 'project')

    def __str__(self):
        return f"{self.task_type}-{self.project}-{self.title}"


class ParticipantTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    order = models.IntegerField()
    is_ready = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.participant.user.username}-{self.order}-{self.task.task_type}"

    @classmethod
    def initializeTasks(cls, participant: Participant):
        # Shuffle the projects
        projects = ["ET", "UV", "BOX2D"]
        random.shuffle(projects)

        # Randomly select 1 Type A, 2 Type B, and 2 Type C task from different projects
        A = Task.objects.filter(task_type='A', project=projects[0])
        B = Task.objects.filter(task_type='B', project=projects[1])
        C = Task.objects.filter(task_type='C', project=projects[2])
        tasks = random.choices(A) + random.choices(B, k=2) + random.choices(C, k=2)
        random.shuffle(tasks)
        task_order = 1
        for idx, task in enumerate(tasks):
            ParticipantTask.objects.create(
                task=task,
                participant=participant,
                order=task_order,
                is_done=False
            )
            task_order += 1
        # Last task will be the questionnaire
        ParticipantTask.objects.create(
            task=Task.objects.get(task_type='Q'),
            participant=participant,
            order=task_order,
            is_done=False
        )


class Response(models.Model):
    participant_task = models.ForeignKey(ParticipantTask, on_delete=models.CASCADE)
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.participant_task.participant.user.username}-{self.participant_task.task.task_type} '

