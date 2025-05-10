from django.views.generic.base import RedirectView
from django.views.generic import ListView, DetailView
from django.urls import path
# from . import views

from main_page.models import Articles
from main_page.models import Projects


urlpatterns = [
    path('', ListView.as_view(queryset=Projects.objects.all().order_by("-date")[:20], template_name="unfold/index.html")),

    # ссылки на социальные сети
    path('iam', RedirectView.as_view(url="https://t.me/Egor_Deev")),
    path('vk', RedirectView.as_view(url="https://vk.com/this_egor")),
    path('inst', RedirectView.as_view(url="https://www.instagram.com/egor.dev")),
    path('x', RedirectView.as_view(url="https://twitter.com/this_egor")),

    path('telegram', RedirectView.as_view(url="https://t.me/programium")),
    path('discord', RedirectView.as_view(url="https://discordapp.com/users/480433544380809226/")),
    path('github', RedirectView.as_view(url="https://github.com/IGlek")),
]
