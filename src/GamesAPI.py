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
        # Debug 1: ¿Qué estamos enviando?
        full_url = urlID + str(id).strip()
        response = session.get(full_url, timeout=10)

        if response.status_code != 200:
            print(f"  [!] Error API Status: {response.status_code} para ID {id}")
            return None

        data = response.json()

        # Debug 2: ¿Qué nos devuelve la búsqueda por SteamID?
        if not isinstance(data, list) or len(data) == 0:
            # Descomenta la siguiente línea si quieres ver TODOS los fallos (puede ser mucho spam)
            # print(f"  [?] SteamID {id} no tiene mapeo en CheapShark")
            return None

        gameID = data[0].get('gameID')
        if not gameID:
            return None

        # Debug 3: Hemos encontrado un GameID interno, vamos a por los precios
        response = session.get(urlPrices + str(gameID), timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            deals = res_data.get('deals')
            if not deals:
                print(f"  [i] ID {id} (GameID {gameID}) encontrado, pero sin ofertas activas.")
            return deals

    except Exception as e:
        print(f"  [ERROR API] ID {id}: {e}")
        return None

def insertarDatos(id, deals, stores):
    if not deals:
        return

    try:
        steamGame = SteamGame.objects.get(steam_id=id)
    except SteamGame.DoesNotExist:
        print(f"  [!] Error DB: SteamGame ID {id} no existe en tu base de datos.")
        return

    creados = 0
    actualizados = 0

    for deal in deals:
        storeID = deal.get('storeID')
        storeName = stores.get(storeID)

        # Si la tienda no está en nuestro diccionario de activas, saltamos
        if not storeName:
            continue

        obj, created = StoreGame.objects.update_or_create(
            game=steamGame,
            external_id=storeID,
            defaults={
                'store_name': storeName,
                'price': deal.get('price'),
                'url': f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}"
            }
        )
        if created:
            creados += 1
        else:
            actualizados += 1

    # Print discreto por cada juego procesado con éxito
    print(f"  [OK] ID {id}: {creados} nuevos, {actualizados} actualizados.")


def main():

    print("iniciando...")
    ids = SteamGame.objects.values_list("steam_id", flat=True)
    size = len(ids)

    print(f"--- Iniciando proceso para {size} juegos ---")

    urlStore = 'https://www.cheapshark.com/api/1.0/stores'
    try:
        r_stores = session.get(urlStore).json()
        stores = {s['storeID']: s['storeName'] for s in r_stores if s['isActive'] == 1}
        print(f"--- Tiendas cargadas: {len(stores)} activas ---")
    except Exception as e:
        print(f"Error crítico cargando tiendas: {e}")
        return

    count = 0
    for id in ids:
        try:
            deals = buscar_juego(id)
            if deals:
                insertarDatos(id, deals, stores)
                count += 1

            if count % 10 == 0 and count > 0:
                print(f">> Progreso: {count} juegos con ofertas encontrados...")

            time.sleep(0.5)
        except Exception as e:
            print(f"  [ERROR CRÍTICO] En bucle para ID {id}: {e}")
            continue

    print(f"--- Proceso finalizado. Total juegos procesados con ofertas: {count} ---")


if __name__ == "__main__":
    main()