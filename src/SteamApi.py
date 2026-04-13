import os
import sys
import django
import dotenv
import requests

# Configuración de entorno para Django
sys.path.append(os.getcwd())
dotenv.load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projecte.settings")
django.setup()

from projecte.games.models import SteamGame, GameDetails, StoreGame


def getGamesBatch():
    url = "https://steamspy.com/api.php?request=all"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def procesarJuegos(data):
    games_to_insert = []
    count=0

    sorted_apps = sorted(data.items(), key=lambda x: int(x[0]))

    for appid, info in sorted_apps:
        if len(games_to_insert) >= 500:
            print("yatta")
            break

        if count%20 ==0:
            print(count)


        price_raw = info.get("price", 0)
        price_formatted = f"{int(price_raw) / 100}€"

        if price_raw == "0" or price_raw=="0.0":
            continue

        #porcentaje de votos positivos
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        total_votes = pos + neg
        score_percentage = int((pos / total_votes) * 100) if total_votes > 0 else 0

        #

        game_data = {
            "id": int(appid),
            "name": info.get("name"),
            "price": price_formatted,
            "description": f"",
            "description_brief": f"",
            "score": score_percentage,
            "header_image": f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
            "developers": [info.get("developer")] if info.get("developer") else [],
            "publishers": [info.get("publisher")] if info.get("publisher") else [],
            "photos": [],
            "release_date": None,
        }
        games_to_insert.append(game_data)
        count = count + 1

    return games_to_insert

def insertGames(games):
    for game_data in games:
        steam_obj, created = SteamGame.objects.update_or_create(
            steam_id=game_data['id'],
            defaults={
                'name': game_data['name'],
                'price': game_data['price'],
                'url': f"https://store.steampowered.com/app/{game_data['id']}/"
            }
        )

        GameDetails.objects.update_or_create(
            game=steam_obj,
            defaults={
                'description': game_data['description'],
                'description_brief': game_data['description_brief'],
                'score': game_data['score'],
                'header_image': game_data['header_image'],
                'developers': game_data['developers'],
                'publishers': game_data['publishers'],
                'photos': game_data['photos'],
                'release_date': game_data['release_date'],
            }
        )

def main():

    SteamGame.objects.all().delete()
    GameDetails.objects.all().delete()
    StoreGame.objects.all().delete()
    data = getGamesBatch()

    if not data:
        print("No se han podido obtener datos de SteamSpy.")
        return

    games = procesarJuegos(data)

    insertGames(games)

    print(f"Proceso finalizado. Se han procesado {len(games)} juegos.")

if __name__ == "__main__":
    main()