from django.contrib import admin
from .models import Participant, Task, TimeLog, ParticipantTask, Response


# Register your models here.

@admin.action(description="Create tasks for participant")
def make_tasks(modeladmin, request, queryset):
    for participant in queryset:
        ParticipantTask.initializeTasks(participant)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'link', 'tooling_level', 'logged_in', 'finished_experiment']
    actions = [make_tasks]


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Task)
admin.site.register(TimeLog)
admin.site.register(ParticipantTask)
admin.site.register(Response)
