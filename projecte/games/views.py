from django.http import JsonResponse
from django.shortcuts import render
from .models import SteamGame

from django.contrib.auth.forms import UserCreationForm  # Django's built-in signup form
from django.urls import reverse_lazy                     # like reverse(), but delays evaluation
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

def lista_juegos(request):
    juegos = SteamGame.objects.all()
    return render(request, 'games/lista.html', {'juegos': juegos})

def home(request):
    juegos = SteamGame.objects.all()[:20]
    return render(request, "home.html", {"juegos": juegos})

def search_juegos(request):
    query = request.GET.get('q', '')
    games = SteamGame.objects.filter(name__icontains=query)[:5]
    results = list(games.values('steam_id', 'name'))
    return JsonResponse(results, safe=False)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm                  # the form to show (username + password + confirm)
    template_name = 'registration/signup.html'     # the HTML template to render
    success_url = reverse_lazy('login')            # after signup, redirect to the login page