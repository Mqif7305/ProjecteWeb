from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from src.GetInfoApi import get_info, insert_data, get_info_games
from .models import SteamGame, Wishlist, Comment

from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CommentForm

def lista_juegos(request):
    juegos = SteamGame.objects.all()
    return render(request, 'games/lista.html', {'juegos': juegos})


def home(request):
    millors = SteamGame.objects.filter(details__score__isnull=False).order_by('-details__score')[:6]

    aleatoris = SteamGame.objects.order_by('?')[:30]

    return render(request, "home.html", {
        "millors_valorats": millors,
        "aleatoris": aleatoris
    })

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

    comments = game.comments.all()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.game = game
            comment.save()
            return redirect('game_detail', id=id)

    else:
        form = CommentForm()

    context = {
        "game": game,
        "offers": offers,
        "in_wishlist": in_wishlist,
        "comments": comments,
        "form": form,
    }
    return render(request, "games/details.html", context)

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
def profile_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request,"profile.html", {"games": wishlist.games.all()})

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.user != request.user:
        return redirect('game_detail', id=comment.game.steam_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('game_detail', id=comment.game.steam_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, "games/edit_comment.html", {
        "form": form,
        "comment": comment
    })


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.user == request.user:
        game_id = comment.game.steam_id
        comment.delete()
        return redirect('game_detail', id=game_id)

    return redirect('game_detail', id=comment.game.steam_id)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm            # the form to show (username + password + confirm)
    template_name = 'registration/signup.html'     # the HTML template to render
    success_url = reverse_lazy('login')            # after signup, redirect to the login page
