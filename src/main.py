import dotenv

from src.apis import SteamApi

if __name__ == '__main__':
    dotenv.load_dotenv()
    SteamApi.main()


