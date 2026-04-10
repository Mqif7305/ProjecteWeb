import dotenv
import django
import os

from src.apis import SteamApi

if __name__ == '__main__':
    dotenv.load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projecte.settings")
    django.setup()
    SteamApi.main()


