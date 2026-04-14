import os
import time
import django
import requests

# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projecte.settings")
django.setup()

from projecte.games.models import StoreGame, SteamGame, GameDetails

# Crea una sesión global para reutilizar la conexión TCP
session = requests.Session()


def buscar_juego(id):

    urlID = 'https://www.cheapshark.com/api/1.0/games?steamAppID='
    urlID = urlID + str(id)

    response = session.get(urlID, timeout=15)

    if response.status_code == 429:
        raise Exception(f"  [!] Error API Status: 429, too many requests encontrado.")

    if response.status_code != 200:
        raise Exception(f"  [!] Error API Status: {response.status_code} para ID {id}")

    response= response.json()
    return response



def insertarDatos(id, data):

    steamGame = SteamGame.objects.get(steam_id=id)
    data =data[0]
    gameID = data["gameID"]

    obj, created = StoreGame.objects.update_or_create(
        game=steamGame,
        external_id=gameID,
        defaults={
            'store_name':"PENDIENTE"
        }
    )


def main():

    print("iniciando proceso IDs...")
    ids = SteamGame.objects.values_list("steam_id", flat=True)

    count=0
    deletions=0

    inicio = 0
    ids2 = ids[inicio:]

    sobrescribir = False

    try:
        if sobrescribir:
            for id in ids2:
                data = buscar_juego(id)
                steamGame = SteamGame.objects.filter(steam_id=id)
                if not data:
                    GameDetails.objects.filter(game=steamGame[0]).delete()
                    deletions += 1
                    print(f"  [!] No se encuentra el juego {id} - {deletions} elementos borrados")
                    continue

                print(f"  [+] {count} -Iniciando proceso ID {id}")
                insertarDatos(id,data)
                time.sleep(5)
                count+=1

        else:
            for id in ids:
                steamGame = SteamGame.objects.filter(steam_id=id)
                if not StoreGame.objects.filter(game=steamGame[0]).exists():
                    data = buscar_juego(id)
                    if not data:
                        GameDetails.objects.filter(game=steamGame[0]).delete()
                        deletions += 1
                        print(f"  [!] No se encuentra el juego {id} - {deletions} elementos borrados")
                        continue

                    print(f"  [+] {count} -Iniciando proceso ID {id}")
                    insertarDatos(id, data)
                    time.sleep(5)
                    count += 1

    except Exception as e:
        print(f"Error cargar juegos: \n {e}")


    print(f"--- Proceso finalizado. Total juegos procesados con ofertas:  ---")


if __name__ == "__main__":
    main()