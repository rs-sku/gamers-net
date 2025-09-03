import json

from backend.games.service import Service


async def load_games(service: Service) -> None:
    with open("backend/data/games.json", "r") as file:
        games_data = json.load(file)
    await service.add_games(games_data)
