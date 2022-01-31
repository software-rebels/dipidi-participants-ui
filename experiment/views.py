import json

from django.contrib.auth import login
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.views import View
from .models import Participant, TimeLog, ParticipantTask, Response
from .forms import TypeAForm, TypeBForm
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
        url = reverse('tasks', kwargs={'order': 1})
        return HttpResponseRedirect(url)


class MarkAsReadyView(LoginRequiredMixin, View):
    def post(self, request, order):
        participant = self.request.user.participant
        task = ParticipantTask.objects.get(participant=participant, order=order)
        task.is_ready = True
        task.save()
        TimeLog.createAction(f"MarkAsReady-{order}", participant)
        url = reverse('tasks', kwargs={'order': order})
        return HttpResponseRedirect(url)


class TasksView(LoginRequiredMixin, View):
    def get(self, request, order):
        participant = self.request.user.participant
        if order > 3:
            url = reverse('post_experiment')
            return HttpResponseRedirect(url)

        task = ParticipantTask.objects.get(participant=participant, order=order)
        if task.is_done:
            url = reverse('tasks', kwargs={'order': order + 1})
            return HttpResponseRedirect(url)
        TimeLog.createAction(f"LoadTask-{order}", participant)
        if task.task.task_type == 'A':
            TaskFormSet = formset_factory(TypeAForm, extra=task.task.extra['number_of_targets'])
            formset = TaskFormSet()
        elif task.task.task_type == 'B':
            TaskFormSet = formset_factory(TypeBForm, extra=0)
            formset = TaskFormSet(initial=[
                {"commit_id": commit} for commit in task.task.extra['commits']
            ])
        elif task.task.task_type == 'C':
            pass
        else:
            url = reverse('welcome')
            return HttpResponseRedirect(url)
        context = {
            **task.task.extra,
            "forms": formset,
            "tooling_level": participant.tooling_level,
            "ready": task.is_ready
        }
        return render(request, f'task_{task.task.task_type.lower()}.html', context)

    def post(self, request, order):
        participant = self.request.user.participant
        task = ParticipantTask.objects.get(participant=participant, order=order)
        if task.task.task_type == 'A':
            TaskFormSet = formset_factory(TypeAForm)
            formset = TaskFormSet(request.POST)
        elif task.task.task_type == 'B':
            TaskFormSet = formset_factory(TypeBForm)
            formset = TaskFormSet(request.POST, initial=[
                {"commit_id": commit} for commit in task.task.extra['commits']
            ])
        else:
            return HttpResponse("Shouldn't happen! Please send us an email.")

        if formset.is_valid():
            for form in formset:
                Response.objects.create(participant_task=task, response=json.dumps(form.cleaned_data))
            TimeLog.createAction(f"FinishTask-{order}", participant)
            task.is_done = True
            task.save()
            url = reverse('tasks', kwargs={'order': order+1})
            return HttpResponseRedirect(url)
        else:
            print(formset.non_form_errors())
            print("error")
            return HttpResponse("Input is not valid!")
