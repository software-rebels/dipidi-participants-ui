"""experiment_ui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from experiment import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/<uuid:uuid_link>', views.LoginByLinkView.as_view()),
    path('welcome', views.StartPageView.as_view(), name='welcome'),
    path('begin_experiment', views.BeginExperimentView.as_view(), name='begin_page'),
    path('tasks/<int:order>/', views.TasksView.as_view(), name='tasks'),
    path('tasks/<int:order>/ready', views.MarkAsReadyView.as_view(), name='mark_as_ready'),
    path('tasks/<int:order>/skip', views.SkipTaskView.as_view(), name='skip'),
    path('post_experiment', views.PostExperimentView.as_view(), name='post_experiment')
]
