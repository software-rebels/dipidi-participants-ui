import json

from django.contrib.auth import login, logout
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.views import View
from .models import Participant, TimeLog, ParticipantTask, Response
from .forms import TypeAForm, TypeBForm, TypeCForm, TypeC2Form, Questionnaire
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
        template = "welcome.html"
        rendered_tasks = []
        for idx, task in enumerate(participant.tasks.all().values_list('task_type', flat=True)):
            if task == 'A':
                rendered_tasks.append([f"{idx + 1}. Find Impacted Targets",
                                       "You are provided with the names of changed files and a set of build "
                                       "specifications. Your task is to list impacted deliverables. The experiment UI "
                                       "provides a text input field for you to list those deliverables."])
            if task == 'B':
                rendered_tasks.append([f"{idx + 1}. Rank the Commits",
                                       "You are given three commits and a "
                                       "set of build specifications. We ask you to rank the "
                                       "commits listed in the experiment UI based on (a) the number "
                                       "of impacted deliverables or (b) the number of impacted "
                                       "application variants (e.g., number of affected OS)."])

            if task == 'C':
                rendered_tasks.append([f"{idx + 1}. Identify the Commit",
                                       "You are presented "
                                       "with three commits and asked to identify those that (a) affect "
                                       "a specified set of deliverables or (b) affect a specific variant of "
                                       "the software or (c) identify the configuration settings under "
                                       "which the changes will affect any target."
                                       ])

        return render(request, template, {
            'tooling_level': participant.tooling_level,
            'tasks': rendered_tasks
        })


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


class SkipTaskView(LoginRequiredMixin, View):
    def get(self, request, order):
        participant = self.request.user.participant
        task = ParticipantTask.objects.get(participant=participant, order=order)
        task.is_done = True
        task.is_skipped = True
        task.save()
        TimeLog.createAction(f"Skip-{order}", participant)
        url = reverse('tasks', kwargs={'order': order + 1})
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
            if task.task.extra['type'] == 3:
                TaskFormSet = formset_factory(TypeC2Form, extra=0)
            else:
                TaskFormSet = formset_factory(TypeCForm, extra=0)
            formset = TaskFormSet(initial=[
                {"commit_id": commit} for commit in task.task.extra['commits']
            ])
        else:
            url = reverse('welcome')
            return HttpResponseRedirect(url)
        context = {
            **task.task.extra,
            "forms": formset,
            "tooling_level": participant.tooling_level,
            "ready": task.is_ready,
            "order": order
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
        elif task.task.task_type == 'C':
            if task.task.extra['type'] == 3:
                TaskFormSet = formset_factory(TypeC2Form, extra=0)
            else:
                TaskFormSet = formset_factory(TypeCForm, extra=0)
            formset = TaskFormSet(request.POST, initial=[
                {"commit_id": commit, 'affect': False} for commit in task.task.extra['commits']
            ])
        else:
            return HttpResponse("Shouldn't happen! Please send us an email.")

        if formset.is_valid():
            for form in formset:
                Response.objects.create(participant_task=task, response=json.dumps(form.cleaned_data))
            TimeLog.createAction(f"FinishTask-{order}", participant)
            task.is_done = True
            task.save()
            url = reverse('tasks', kwargs={'order': order + 1})
            return HttpResponseRedirect(url)
        else:
            print(formset.errors)
            print(formset.non_form_errors())
            print("error")
            return HttpResponse("Input is not valid!")


class PostExperimentView(LoginRequiredMixin, View):
    def get(self, request):
        participant = self.request.user.participant
        participant.finished_experiment = True
        participant.save()
        TimeLog.createAction(f"PostExperiment-Started", participant)
        form = Questionnaire()
        return render(request, 'questionnaire.html', {'form': form, 'tooling_level': participant.tooling_level})

    def post(self, request):
        participant = self.request.user.participant
        form = Questionnaire(request.POST)
        if form.is_valid():
            TimeLog.createAction(f"PostExperiment-Finished", participant)
            task = ParticipantTask.objects.get(participant=participant, order=4)
            Response.objects.create(participant_task=task, response=json.dumps(form.cleaned_data))
            task.is_done = True
            task.save()
            logout(request)
            return HttpResponse("Thank you :)")
        else:
            return HttpResponse("Something went wrong :(")
