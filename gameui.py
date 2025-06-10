from ursina import *

class GameUI:
    def __init__(self):
        self.lose_text = None

    def display_lose_screen(self, score):
        display = dedent(f'''
            <red>Game Over!<default>
            Score: <yellow>{score}<default>
            Press R to restart
        ''').strip()
        self.lose_text = Text(text=display, position=(0, 0), scale=2, origin=(0, 0))

    def clear_lose_screen(self):
        if self.lose_text is not None:
            destroy(self.lose_text)
            self.lose_text = None