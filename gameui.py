from ursina import *
import asteroidsconstants as ac

class WindowController(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def input(self, key):
        if key == 'f11 down':
            print('Toggling fullscreen')
            window.fullscreen = not window.fullscreen


class GameUI:
    def __init__(self, start_game_callback):
        self.start_game_callback = start_game_callback
        self.lose_text = None
    
    def draw_menu_screen(self):
        display = dedent('''
            Asteroidy :D
        ''').strip()
        self.menu_text = Text(text=display, position=(0, 0.2), scale=2, origin=(0, 0), font=ac.ASSET_DIR + ac.FONT_MENU)
        b = Button(model='quad', parent=camera.ui, color=color.lime, text='START', scale=(.18, .06), text_color=color.black)
        b.text_entity.font = ac.ASSET_DIR + ac.FONT_MENU
        b.on_click = Func(self.start_game)

        # options
        b_fullscreen = Button(model='quad', position=(0.5, 0), parent=camera.ui, color=color.lime, text='Fullscreen',
                               scale=(.18, .04), text_color=color.black, text_size=0.5)
        b_fullscreen.text_entity.font = ac.ASSET_DIR + ac.FONT_MENU
        b_fullscreen.on_click = Func(self.toggle_fullscreen)
    
    def toggle_fullscreen(self):
        window.fullscreen = not window.fullscreen

    def start_game(self):
        self.clear_menu_screen()
        self.start_game_callback()

    def clear_menu_screen(self):
        if hasattr(self, 'menu_text'):
            destroy(self.menu_text)
            self.menu_text = None
        for b in camera.ui.children:
            if isinstance(b, Button):
                destroy(b)
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