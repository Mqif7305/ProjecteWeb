from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class SteamGame(models.Model):
    steam_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=50)

    url = models.URLField()
    def __str__(self):
        return self.name

class GameDetails(models.Model):
    game = models.OneToOneField(SteamGame, on_delete=models.CASCADE, related_name='details')

    description = models.TextField(null=True, blank=True)
    description_brief = models.TextField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    header_image = models.URLField()

    developers = models.JSONField(null=True, blank=True)
    publishers = models.JSONField(null=True, blank=True)
    photos = models.JSONField(null=True, blank=True)
    release_date = models.CharField(max_length=100, null=True, blank=True)


class StoreGame(models.Model):
    game = models.OneToOneField(SteamGame, on_delete=models.CASCADE, related_name='storegame')

    external_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.game.name} ({self.external_id})"


class StoreOffer(models.Model):
    store_game = models.ForeignKey(StoreGame, on_delete=models.CASCADE, related_name='offers')

    store_id = models.CharField(max_length=50)
    store_name = models.CharField(max_length=100)

    price = models.FloatField()
    url = models.URLField(null=True, blank=True)

    class Meta:
        unique_together = ('store_game', 'store_id')

    def __str__(self):
        return f"{self.store_name} - {self.price}"

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')

    games = models.ManyToManyField(SteamGame, related_name='wishlist_by', blank=True)

    def __str__(self):
        return f"{self.user.username} wishlist"