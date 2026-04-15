import os
import time
import django
import requests

# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projecte.settings")
django.setup()

from projecte.games.models import StoreGame, SteamGame

session = requests.Session()


def procesar_lote(batch_ids, stores):
    """
    Recibe una lista de IDs de Steam, busca sus GameIDs y luego pide
    las ofertas en un solo paquete (batch).
    """
    # 1. Mapear SteamIDs a GameIDs (CheapShark necesita su GameID interno)
    # Lamentablemente, la búsqueda por SteamID sigue siendo individual en la API,
    # pero podemos hacer esta parte rápido y luego agrupar la de precios.
    game_id_map = {}  # {gameID: steamID}

    for s_id in batch_ids:
        try:
            resp = session.get(f'https://www.cheapshark.com/api/1.0/games?steamAppID={s_id}', timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    g_id = data[0].get('gameID')
                    game_id_map[g_id] = s_id
            time.sleep(0.2)  # Un pequeño respiro entre búsquedas de ID
        except:
            continue

    if not game_id_map:
        return 0

    # 2. Pedir todas las ofertas del lote en UNA sola llamada
    ids_string = ",".join(game_id_map.keys())
    url_batch = f'https://www.cheapshark.com/api/1.0/games?ids={ids_string}'

    try:
        response = session.get(url_batch, timeout=15)
        if response.status_code == 429:
            print("  [!] Límite alcanzado en lote. Esperando 10s...")
            time.sleep(10)
            return 0

        if response.status_code != 200:
            return 0

        data = response.json()  # Esto devuelve un dict con GameIDs como llaves

        juegos_actualizados = 0
        for g_id, info in data.items():
            steam_id = game_id_map.get(g_id)
            deals = info.get('deals', [])

            if deals and steam_id:
                try:
                    steam_game_obj = SteamGame.objects.get(steam_id=steam_id)
                    for deal in deals:
                        store_id = deal.get('storeID')
                        store_name = stores.get(store_id)

                        if not store_name: continue

                        StoreGame.objects.update_or_create(
                            game=steam_game_obj,
                            external_id=store_id,
                            defaults={
                                'store_name': store_name,
                                'price': deal.get('price'),
                                'url': f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}"
                            }
                        )
                    juegos_actualizados += 1
                except SteamGame.DoesNotExist:
                    continue

        return juegos_actualizados

    except Exception as e:
        print(f"  [ERROR] Error en el lote: {e}")
        return 0


def main():
    # 1. Cargar Tiendas
    try:
        r_stores = session.get('https://www.cheapshark.com/api/1.0/stores').json()
        stores = {s['storeID']: s['storeName'] for s in r_stores if s['isActive'] == 1}
    except:
        print("Error al cargar tiendas.")
        return

    # 2. Obtener IDs y dividir en trozos de 25
    ids = list(SteamGame.objects.values_list("steam_id", flat=True))
    size = len(ids)
    batch_size = 25

    print(f"--- Iniciando carga masiva: {size} juegos ---")

    count_total = 0
    for i in range(0, size, batch_size):
        lote = ids[i: i + batch_size]
        print(f"Procesando lote {i // batch_size + 1} ({len(lote)} juegos)...")

        actualizados = procesar_lote(lote, stores)
        count_total += actualizados

        # Pausa de seguridad entre lotes
        time.sleep(2)

    print(f"--- Proceso finalizado. Juegos con ofertas guardadas: {count_total} ---")


if __name__ == "__main__":
    main()