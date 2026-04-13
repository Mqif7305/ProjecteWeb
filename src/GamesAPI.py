import os
import time
import django
import requests

# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projecte.settings")
django.setup()

from projecte.games.models import StoreGame, SteamGame

# Crea una sesión global para reutilizar la conexión TCP
session = requests.Session()


def buscar_juego(id):
    urlID = 'https://www.cheapshark.com/api/1.0/games?steamAppID='
    urlPrices = 'https://www.cheapshark.com/api/1.0/games?id='

    try:
        response = session.get(urlID + str(id), timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            return None

        game = data[0]
        gameID = game.get('gameID')
        if not gameID:
            return None

        response = session.get(urlPrices + str(gameID), timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        if not isinstance(data, dict):
            return None

        deals = data.get('deals')
        if not deals:
            return None

        return deals

    except Exception as e:
        print(f"[ERROR API] ID {id}: {e}")
        return None

def insertarDatos(id, deals, stores):
    if deals is None:
        return

    try:
        steamGame = SteamGame.objects.get(steam_id=id)
    except SteamGame.DoesNotExist:
        return

    for deal in deals:
        storeID = deal.get('storeID')
        storeName = stores.get(storeID)

        StoreGame.objects.update_or_create(
            game=steamGame,
            external_id=storeID,  # Buscamos por juego y ID de tienda
            defaults={
                'store_name': storeName,
                'price': deal.get('price'),
                'url': f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}"
            }
        )


def main():
    ids = SteamGame.objects.values_list("steam_id", flat=True)

    count = 0
    size = len(ids)

    urlStore = 'https://www.cheapshark.com/api/1.0/stores'
    try:
        stores = session.get(urlStore).json()[1:]  # quitamos steam pq ya la tenemos
        stores = {s['storeID']: s['storeName'] for s in stores if s['isActive'] == 1}
    except Exception as e:
        print(f"Error cargando tiendas: {e}")
        return

    for id in ids:
        try:
            deals = buscar_juego(id)
            if not deals:
                continue

            insertarDatos(id, deals, stores)
            if count % 20 == 0:
                print(f"Se han procesado {count} / {size}")

            count += 1
            time.sleep(0.5)  # Subido a 0.5 para mayor seguridad contra bloqueos
        except:
            continue

    return


if __name__ == "__main__":
    main()