from django.shortcuts import render
from .models import SteamGame

def lista_juegos(request):
    juegos = SteamGame.objects.all()
    return render(request, 'games/lista.html', {'juegos': juegos})

def home(request):
    juegos = SteamGame.objects.all()[:20]
    return render(request, "home.html", {"juegos": juegos})