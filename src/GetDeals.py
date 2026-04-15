import os
import time
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projecte.settings")
django.setup()

from projecte.games.models import StoreGame, StoreOffer, SteamGame

session = requests.Session()


def buscar_deals(batch):
    url = 'https://www.cheapshark.com/api/1.0/games?ids='
    ids = ",".join(str(g.external_id) for g in batch)

    r = session.get(url + ids, timeout=15)

    if r.status_code == 429:
        time.sleep(20)
        return buscar_deals(batch)

    if r.status_code != 200:
        raise Exception(f"API error {r.status_code}")

    return r.json()


def insertar_deals(store_game, deals, stores):
    if not deals:
        return

    creados = 0
    actualizados = 0

    for d in deals:
        store_id = d.get('storeID')
        if store_id == '1':
            continue

        store_name = stores.get(store_id)
        price = float(d.get('price'))

        obj, created = StoreOffer.objects.update_or_create(
            store_game=store_game,
            store_id=store_id,
            defaults={
                'store_name': store_name,
                'price': price,
            }
        )

        if created:
            creados += 1
        else:
            actualizados += 1

    if creados + actualizados < 1:
        id_steam = store_game.game.steam_id
        print(f"  [!] Borrando {id_steam}: No tiene ofertas externas (solo Steam).")

        store_game.game.delete()
        return

    print(f"[OK] {store_game.external_id}: {creados} nuevos, {actualizados} actualizados")


def main():
    print("iniciando obtencion de ofertas...")

    games = list(StoreGame.objects.select_related('game').all())
    print(f"total juegos: {len(games)}")

    url_store = 'https://www.cheapshark.com/api/1.0/stores'

    try:
        r = session.get(url_store).json()
        stores = {s['storeID']: s['storeName'] for s in r if s['isActive'] == 1 and s['storeID'] != '1'}
    except Exception as e:
        print(f"error tiendas: {e}")
        return

    batch_size = 25
    count = 0

    try:
        for i in range(0, len(games), batch_size):
            batch = games[i:i + batch_size]

            deals_data = buscar_deals(batch)

            for g in batch:
                data = deals_data.get(g.external_id)

                if not data:
                    print(f"[!] sin datos {g.external_id}")
                    continue

                insertar_deals(
                    g,
                    data.get('deals', []),
                    stores
                )

            count += 1
            print(f"batch {count}")

            time.sleep(8)

    except Exception as e:
        print(f"error batch {count}: {e}")

    print("finalizado")


if __name__ == "__main__":
    main()