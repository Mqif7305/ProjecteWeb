from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from src.GetInfoApi import get_info, insert_data, get_info_games
from .models import SteamGame, Wishlist

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

    if not hasattr(game, 'details') or not game.details.description:
        get_info_games(id)
        game.refresh_from_db()

    offers = []
    if hasattr(game, 'storegame'):
        offers = game.storegame.offers.all().order_by('price')

    in_wishlist = False
    if request.user.is_authenticated:
        try:
            in_wishlist = request.user.wishlist.games.filter(steam_id=game.steam_id).exists()
        except (Wishlist.DoesNotExist, OperationalError, ProgrammingError):
            in_wishlist = False
    return render(request, "games/details.html", {"game": game, "offers": offers, "in_wishlist": in_wishlist})

@login_required
def toggle_wishlist(request, id):
    game = get_object_or_404(SteamGame, steam_id=id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    if game in wishlist.games.all():
        wishlist.games.remove(game)
    else:
        wishlist.games.add(game)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, "games/wishlist.html", {"games": wishlist.games.all()})

class SignUpView(CreateView):
    form_class = CustomUserCreationForm            # the form to show (username + password + confirm)
    template_name = 'registration/signup.html'     # the HTML template to render
    success_url = reverse_lazy('login')            # after signup, redirect to the login page
