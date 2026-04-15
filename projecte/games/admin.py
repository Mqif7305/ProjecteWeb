from django.contrib import admin
from .models import SteamGame, GameDetails, StoreGame


@admin.register(SteamGame)
class SteamGameAdmin(admin.ModelAdmin):
    list_display = ('name', 'steam_id', 'price')

@admin.register(GameDetails)
class GameDetailsAdmin(admin.ModelAdmin):
    list_display = ('game', 'score')

@admin.register(StoreGame)
class StoreGameAdmin(admin.ModelAdmin):
    list_display = ('game', 'price')