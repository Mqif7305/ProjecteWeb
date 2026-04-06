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
    score = models.FloatField(null=True, blank=True)
    header_image = models.URLField(null=True, blank=True)

class StoreGame(models.Model):
    game = models.ForeignKey(SteamGame, on_delete=models.CASCADE, related_name='ThirdPartyStore_offers')

    store_name = models.CharField(max_length=100)
    external_id = models.CharField(max_length=100)

    price = models.FloatField()
    url = models.URLField()