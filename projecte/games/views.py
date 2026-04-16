from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import SteamGame

from django.urls import reverse_lazy
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

def game_detail(request, id):
    game = get_object_or_404(SteamGame, steam_id=id)
    offers = []
    if hasattr(game, 'storegame'):
        offers = game.storegame.offers.all().order_by('price')
    return render(request, "games/details.html", {"game": game, "offers": offers})

class SignUpView(CreateView):
    form_class = CustomUserCreationForm            # the form to show (username + password + confirm)
    template_name = 'registration/signup.html'     # the HTML template to render
    success_url = reverse_lazy('login')            # after signup, redirect to the login page