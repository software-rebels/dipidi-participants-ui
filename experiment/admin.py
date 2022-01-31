from django.contrib import admin
from .models import Participant, Task, TimeLog, ParticipantTask, Response
# Register your models here.
admin.site.register(Participant)
admin.site.register(Task)
admin.site.register(TimeLog)
admin.site.register(ParticipantTask)
admin.site.register(Response)