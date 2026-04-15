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


def buscar_juego(ids):
    urlID = 'https://www.cheapshark.com/api/1.0/games?steamAppID='
    urlPrices = 'https://www.cheapshark.com/api/1.0/games?id='


    for id in ids:
        if id is ids[-1]:
            urlID = urlID + str(id).strip()
        else:
            urlID += str(id).strip() + ","

    response = session.get(urlID, timeout=15)

    if response.status_code == 429:
        raise Exception(f"  [!] Error API Status: 429, too many requests encontrado.")

    if response.status_code != 200:
        raise Exception(f"  [!] Error API Status: {response.status_code} para ID {id}")

    response= response.json()
    IDgames = []

    for i in enumerate(response):
        IDgame= response.get(i).get('gameID')
        if not IDgame:
            continue

        IDgames.append(IDgame)











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
                'url': f""
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

    time.sleep(2)

    batch_size=25
    batch = []
    count = 0

    while ids:
        batch = ids[:batch_size]
        ids = ids[batch_size:]

        try:
            deals= buscar_juego(batch)

            for idx, deal in enumerate(batch):
                if deal:
                    insertarDatos(batch[idx], deal, stores)

            count += 1
            print(f">> Progreso: {count} batch")

            time.sleep(10)

        except Exception as e:
            print(f"Error en batch {count + 1}: {e}")
            continue



    print(f"--- Proceso finalizado. Total juegos procesados con ofertas: {count} ---")


if __name__ == "__main__":
    main()