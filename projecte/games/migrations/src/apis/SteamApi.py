import os
import threading

import requests

def getApps(api_key):
    url = "https://api.steampowered.com/IStoreService/GetAppList/v1/?key="
    url += api_key

    response = requests.get(url)
    return response.json()

def getGames(apps):

    numMaxGames= 10000
    games = []

    url = "https://store.steampowered.com/api/appdetails?appids="

    for app in apps:
        if len(games) >= numMaxGames:
            break

        id= str(app["appid"])
        respone = requests.get(url+id)
        if respone.status_code == 200:
            data = respone.json()
            if procesarJuego(data, id):
                games.append(getInfo(data,id))

    return games

def getInfo(data,id):
    game = data[id]["data"]

    return {
        "id": id,
        "name": game.get("name"),
        "price": game.get("price_overview", {}).get("final_formatted"),
        "description": game.get("detailed_description"),
        "description_brief": game.get("short_description"),
        "header_image": game.get("header_image"),
        "developers": game.get("developers"),
        "publishers": game.get("publishers"),
        "photos": game.get("screenshots"),
        "release_date": game.get("release_date", {}).get("date"),
        "score": game.get("metacritic", {}).get("score"),
    }

def procesarJuego(data, id):
    if not data[id]["success"]:
        return False

    game_data = data[id]["data"]

    if game_data.get("type") != "game":
        return False

    if game_data.get("is_free"):
        return False

    return True



def main():
    apps = getApps(os.getenv('STEAM_API_KEY'))
    games = getGames(apps)
