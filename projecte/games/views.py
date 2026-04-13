from django.http import JsonResponse
from django.shortcuts import render
from .models import SteamGame

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