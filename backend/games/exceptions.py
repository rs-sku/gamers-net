class GameNotFound(Exception):
    def __init__(self, game_name: str):
        self.game_name = game_name
        super().__init__(f"Game with name '{game_name}' not found")
