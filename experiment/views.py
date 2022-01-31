import json

from django.contrib.auth import login
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.views import View
from .models import Participant, TimeLog, ParticipantTask, Response
from .forms import TypeAForm
from django.forms import formset_factory


# Create your views here.
class LoginByLinkView(View):
    def get(self, request, uuid_link):
        try:
            participant = Participant.objects.get(link=uuid_link)
        except Participant.DoesNotExist:
            return HttpResponse("Participant does not exist! Please contact mehran.meidani@uwaterloo.ca")
        if participant.finished_experiment:
            return HttpResponse("You already participated! Thank you!")
        participant.logged_in = True
        participant.save()
        TimeLog.createAction("Login", participant)

        user = participant.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        url = reverse('welcome')
        return HttpResponseRedirect(url)


class StartPageView(LoginRequiredMixin, View):
    login_url = None
    permission_denied_message = 'Access Denied'

    def get(self, request):
        participant = self.request.user.participant
        if participant.tooling_level == '1':
            template = "welcome_notool.html"
        elif participant.tooling_level == '2':
            template = "welcome_existingtool.html"
        elif participant.tooling_level == '3':
            template = "welcome_dipiditool.html"
        else:
            raise
        return render(request, template)


class BeginExperimentView(LoginRequiredMixin, View):
    def get(self, request):
        participant = self.request.user.participant
        TimeLog.createAction("BeginExperiment", participant)
        return HttpResponseRedirect('tasks/1')


class TasksView(LoginRequiredMixin, View):
    def get(self, request, order):
        participant = self.request.user.participant
        task = ParticipantTask.objects.get(participant=participant, order=order)
        TimeLog.createAction(f"LoadTask-{order}", participant)
        if task.is_done:
            return HttpResponse("You already completed this task!")
        TaskFormSet = formset_factory(TypeAForm, extra=3)
        return render(request, f'task_{task.task.task_type.lower()}.html', {**task.task.extra, "forms": TaskFormSet()})

    def post(self, request, order):
        participant = self.request.user.participant
        task = ParticipantTask.objects.get(participant=participant, order=order)
        TaskFormSet = formset_factory(TypeAForm, extra=3)
        formset = TaskFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                Response.objects.create(participant_task=task, response=json.dumps(form.cleaned_data))
        TimeLog.createAction(f"FinishTask-{order}", participant)
        return HttpResponseRedirect(f'tasks/{order+1}')
