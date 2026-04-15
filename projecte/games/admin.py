from django.contrib import admin
from .models import SteamGame, GameDetails, StoreGame, StoreOffer


@admin.register(SteamGame)
class SteamGameAdmin(admin.ModelAdmin):
    list_display = ('name', 'steam_id', 'price')

@admin.register(GameDetails)
class GameDetailsAdmin(admin.ModelAdmin):
    list_display = ('game', 'score')

@admin.register(StoreOffer)
class StoreOfferAdmin(admin.ModelAdmin):
    list_display = ('store_game','store_name', 'price')