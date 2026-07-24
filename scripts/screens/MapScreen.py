import pygame
import pygame_gui

from scripts.screens.Screens import Screens
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.sprite_button import UISpriteButton
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.game_structure import game
from pygame_gui.core import UIContainer
from scripts.ui.elements.map_tile import MapTileButton
from scripts.cat.enums import CatRank, CatGroup, CatSocial
from scripts.territory import territory_class
from scripts.game_structure.screen_settings import screen


class MapScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.tile_size = 38
        self.elements = {}
        self.back_button = None
        self.selected_tile = None

        self.map_tile_buttons = {}
        self.map_container = None

    def screen_switches(self):
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.elements["map_box"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((40, 80), (self.tile_size*11 + 40, self.tile_size*11 + 40))),
            get_box(BoxStyles.ROUNDED_BOX, (self.tile_size*11 + 40, self.tile_size*11 + 40)),
            starting_height=3,
            manager=MANAGER,
        )
        self.map_container = UIContainer(
            ui_scale(pygame.Rect((60, 100), (self.tile_size*11, self.tile_size*11))),
            starting_height=3,
            manager=MANAGER,
        )

        self.create_map()

        return super().screen_switches()
    

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            
            for key, button in self.map_tile_buttons.items():
                if event.ui_element == button:
                    if button.selected:
                        button.deselect()
                        self.selected_tile = None
                    else:
                        button.select()
                        self.selected_tile = key
                    self.update_tiles()
        return super().handle_event(event)
    
    def exit_screen(self):
        self.back_button.kill()
        self.map_container.kill()

        for ele in self.elements:
            self.elements[ele].kill()
        self.elements = {}
        for ele in self.map_tile_buttons:
            self.map_tile_buttons[ele].kill()
        self.map_tile_buttons = {}
        return super().exit_screen()
    
    # now the fun stuff
    def create_map(self):
        for tile, tile_info in game.clan.territory_tile_info.items():
            x = int(tile.split("-")[0])
            y = int(tile.split("-")[1])

            tile_owner = territory_class.get_tile_owner(tile)

            self.map_tile_buttons[tile] = MapTileButton(
                relative_rect=ui_scale(pygame.Rect((x * self.tile_size, y * self.tile_size), (self.tile_size, self.tile_size))),
                text="",
                container=self.map_container,
                tool_tip_text=tile_owner.name,
                manager=MANAGER,
                tile_owner=tile_owner,
                tile_string = tile
            )
    def update_tiles(self):
        for key, button in self.map_tile_buttons.items():
            if key != self.selected_tile:
                button.deselect()
