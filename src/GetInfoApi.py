import os
import sys
import time

import django
import requests

# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projecte.settings")
django.setup()

from projecte.games.models import SteamGame, GameDetails



def get_info(id , count = 0 ):

    url = "https://store.steampowered.com/api/appdetails?appids=" + str(id)

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 429:
            if count == 3:
                print("point0")
                return None

            time.sleep(20)
            return get_info(id, count+1 )

        elif response.status_code != 200:
            print("point1")
            return None

        data = response.json()

        if data == None or data.get(str(id), {}).get("success")==False:
            print("point2")
            return None
        print("point3")
        return data[str(id)]["data"]

    except Exception:
        print("point4")
        return None



def insert_data(id,data):

    description = data.get("detailed_description")
    description_brief = data.get("short_description")

    release_date = data.get("release_date", {}).get("date")

    photos = data.get("screenshots")
    p = []
    for photo in photos:
        p.append(photo.get("path_full"))

    steamGame= SteamGame.objects.get(steam_id=id)

    gamedetails= GameDetails.objects.get(game=steamGame)

    print(description)
    print(description_brief)
    print(release_date)

    gamedetails.description = description
    gamedetails.description_brief = description_brief
    gamedetails.photos = p
    gamedetails.release_date = release_date
    gamedetails.save()

    return


def get_info_games(id):
    data = get_info(id)

    if data == None:
        print("No games found")
        print("point5")
        return

    insert_data(id, data)

    print("tot correcte")


def manual():
    argv = sys.argv
    get_info_games(argv[1])


if __name__ == "__main__":
    manual()
