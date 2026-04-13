import django
import requests
from projecte.games.models import SteamGame

django.setup()

def buscar_juego(name):

    urlID = 'https://www.cheapshark.com/api/1.0/games?steamAppID='
    urlPrices = 'https://www.cheapshark.com/api/1.0/games?id='

    games = []

    ids = SteamGame.objects.values_list("id", flat=True)


    for id in ids:
        try:
            response = requests.get(urlID+id).json()
            gameID = response.get('gameID')

            response = requests.get(urlPrices+gameID).json()
            if response is not None:
                games.append(response)

        except Exception:
            return {}

    return games

def insertarDatos(data):
    return

def main():

    names = SteamGame.objects.values_list("name", flat=True)
    count=0
    size = len(names)

    urlStore = 'https://www.cheapshark.com/api/1.0/stores'

    try:
        stores = requests.get(urlStore).json()
    except:
        return {}

    for name in names:
        try:
            response = buscar_juego(name)
            insertarDatos(response)
            if count % 20 == 0:
                count=0
                print(f"Se han procesado en Instant Gaming {count} / {size}")
        except:
            continue

    return


if __name__ == "__main__":
    main()