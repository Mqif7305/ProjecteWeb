import os
import time

import django
import requests

from projecte.games.models import SteamGame, GameDetails

# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projecte.settings")
django.setup()

def get_info(id , count = 0 ):

    url = "https://store.steampowered.com/api/appdetails?appid=" + str(id)

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 429:
            if count == 3:
                return None

            time.sleep(20)
            return get_info(id, count+1 )

        elif response.status_code != 200:
            return None

        data = response.json()

        if data == None or data.get(str(id), {}).get("success")==False:
            return None

        return data[str(id)]["data"]

    except Exception:
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



    gamedetails.description = description
    gamedetails.description_brief = description_brief
    gamedetails.photos = p
    gamedetails.release_date = release_date
    gamedetails.save()

    return


def get_info_games(id):
    data = get_info(id)

    if data == None:
        return

    insert_data(id, data)





