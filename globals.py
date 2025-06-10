from enum import Enum

class GameState(Enum):
    PLAYING = 1
    LOST = 2
    MENU = 3
    PAUSED = 4

def init():
    global bullets, asteroids, game_state
    bullets = []
    asteroids = []
    game_state = GameState.MENU