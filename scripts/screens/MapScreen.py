import random

import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from scripts.clan import OtherClan
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import screen_scale, MANAGER, screen
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UISurfaceImageButton,
)
from scripts.screens.Screens import Screens
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.utility import (
    ui_scale,
    get_text_box_theme,
    get_other_clan_relation,
    get_other_clan,
    clan_symbol_sprite,
    shorten_text_to_fit,
    get_alive_status_cats,
    get_living_clan_cat_count,
    ui_scale_dimensions,
    get_baron_colour
)

class MapScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)

        # UI containers
        self.map_container = None
        self.baronies_container = None
        self.focus_barony_info_container = None

        # buttons
        self.back_button = None
        self.view_all_button = None
        self.hide_borders_button = None

        self.map_elements = {}
        self.barony_button_elements = {}
        self.info_elements = {}

        self.map_tiles = {}

        # variables
        self.focus_barony = None
        self.borders_hidden = False
        self.view_all_borders = False

    def handle_event(self, event):
        """
        Handles button presses / events
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.view_all_button:
                if self.view_all_borders:
                    self.view_all_borders = False
                else:
                    self.view_all_borders = True
            elif event.ui_element == self.hide_borders_button:
                if self.borders_hidden:
                    self.borders_hidden = False
                else:
                    self.borders_hidden = True
            elif event.ui_element in self.barony_button_elements.values():
                all_clans_list = [game.clan] + game.clan.all_clans
                for i in range(0, 6):
                    if f"{i}_button" not in self.barony_button_elements:
                        continue
                    if (
                        event.ui_element
                        == self.barony_button_elements[f"{i}_button"]
                    ):
                        self.focus_barony = all_clans_list[i]
                        self.update_focus_baron_info()
            self.update_buttons()
    
    def screen_switches(self):
        """
        Handle creating new elements when switching to this screen
        """
        super().screen_switches()

        self.show_mute_buttons()

        self.focus_barony = game.clan

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        # CONTAINERS
        self.map_container = UIContainer(
            ui_scale(pygame.Rect((75, 75), (365, 365))),
            starting_height=3,
            manager=MANAGER,
        )
        self.baronies_container = UIContainer(
            ui_scale(pygame.Rect((75, 20), (365, 210))),
            starting_height=3,
            manager=MANAGER,
            anchors={"top_target": self.map_container}
        )
        self.focus_barony_info_container = UIContainer(
            ui_scale(pygame.Rect((20, 75), (280, 510))),
            starting_height=3,
            manager=MANAGER,
            anchors={"left_target": self.map_container}
        )

        # map
        self.map_elements["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (365, 365))),
            get_box(BoxStyles.FRAME, (365, 365)),
            manager=MANAGER,
            container = self.map_container
        )

        # barony buttons
        x_pos = 0
        for i, clan in enumerate([game.clan] + game.clan.all_clans):
            self.barony_button_elements[f"{i}_button"] = UIImageButton(
                ui_scale(pygame.Rect((x_pos, 10), (50, 50))),
                "",
                object_id="#other_clan_select_button",
                starting_height=2,
                container=self.baronies_container,
                manager=MANAGER
            )

            self.barony_button_elements[
                f"{i}_symbol"
            ] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_pos, 10), (50, 50))),
                clan_symbol_sprite(clan),
                object_id=f"#clan_symbol{i}",
                starting_height=1,
                container=self.baronies_container,
                manager=MANAGER
            )
            x_pos += 60

        
        self.view_all_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 80), (130, 35))),
            "View all Borders",
            get_button_dict(ButtonStyles.SQUOVAL, (130, 35)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self.baronies_container,
            anchors={"centerx": "centerx"}
        )
        
        self.hide_borders_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 120), (200, 35))),
            "Toggle Border Visibility",
            get_button_dict(ButtonStyles.SQUOVAL, (200, 35)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self.baronies_container,
            anchors={"centerx": "centerx"}
        )

        self.update_map()
        self.update_focus_baron_info()

    
    def on_use(self):
        super().on_use()

        self.update_map()
    
    def exit_screen(self):
        """
        Deletes all elements when this screen is closed
        """
        self.back_button.kill()
        self.view_all_button.kill()
        self.hide_borders_button.kill()

        # killing containers kills all inner elements as well
        self.map_container.kill()
        self.baronies_container.kill()
        self.focus_barony_info_container.kill()
        
        for ele in self.map_elements:
            self.map_elements[ele].kill()
        self.map_elements = {}
        
        for ele in self.barony_button_elements:
            self.barony_button_elements[ele].kill()
        self.barony_button_elements = {}
        
        for ele in self.info_elements:
            self.info_elements[ele].kill()
        self.info_elements = {}
        
        for ele in self.map_tiles:
            self.map_tiles[ele].kill()
        self.map_tiles = {}

    def update_focus_baron_info(self):
        """
        Updates the rightside container for Barony info
        """
        for ele in self.info_elements:
            self.info_elements[ele].kill()
        self.info_elements = {}

        self.info_elements["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (280, 510))),
            get_box(BoxStyles.FRAME, (280, 510)),
            manager=MANAGER,
            container = self.focus_barony_info_container
        )

        self.info_elements["name"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((0, 15), (260, 40))),
            html_text=str(Cat.fetch_cat(self.focus_barony.baron).name) + " | <i>" + self.focus_barony.territory_type.capitalize() + "</i>",
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.focus_barony_info_container,
            manager=MANAGER,
            text_kwargs={},
            anchors={
                "centerx": "centerx"
            }
        )
        self.info_elements["desc"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((0, 60), (260, 300))),
            html_text="Here is where information about this Baron and their cats will be displayed in the future. For now, it's empty.",
            object_id=get_text_box_theme("#text_box_26_horizcenter"),
            container=self.focus_barony_info_container,
            manager=MANAGER,
            text_kwargs={},
            anchors={
                "centerx": "centerx"
            }
        )

    def update_buttons(self):
        if self.borders_hidden is True:
            self.view_all_button.disable()
        else:
            self.view_all_button.enable()

    def update_map(self):
        """
        Generates coloured borders for the map
        """

        # the map image has to be blitted onto the screen
        # so the lines can blit on top of it.
        # and it has to be done here instead of screen_switches or itll disappear :C
        map_image = pygame.image.load("resources/images/badlands/map_small.png").convert_alpha()
        scaled_image = pygame.transform.scale(map_image, (350, 350))
        scaled_image.set_alpha(145)
        screen.blit(scaled_image, (80, 80))

        x_pos = 80
        y_pos = 80

        if not self.view_all_borders:
            all_clans_list = [self.focus_barony]
        else:
            all_clans_list = game.clan.all_clans + [game.clan]

        if self.borders_hidden is False:
            for y in range(1, 8):
                for x in range(1, 8):
                    tile_colour = "#FAFAFA"
                    tile_string = str(y) + "-" + str(x)

                    NORTH_TILE_STRING = str(y - 1) + "-" + str(x)
                    EAST_TILE_STRING = str(y) + "-" + str(x + 1)
                    SOUTH_TILE_STRING = str(y + 1) + "-" + str(x)
                    WEST_TILE_STRING = str(y) + "-" + str(x - 1)

                    for clan in all_clans_list:
                        if tile_string in clan.territory:
                            # grab the border colour
                            if clan == game.clan:
                                tile_colour = get_baron_colour(game.clan.baron.ID)
                            else:
                                tile_colour = get_baron_colour(Cat.fetch_cat(clan.baron).ID)

                            # convert the colour to RGB and generate a rect
                            # i stole the rgb function i didnt write that shoutout da internet
                            rgb_tile_colour = self.hex_to_rgb(tile_colour)
                            rect = ui_scale(pygame.Rect((x_pos, y_pos), (50, 50)))

                            # now, check if the neighbouring territory in each direction belongs to them
                            # if it doesnt, draw the border line
                            if NORTH_TILE_STRING not in clan.territory:
                                point1 = rect.topleft
                                point2 = rect.topright
                                pygame.draw.line(screen, rgb_tile_colour, point1, point2, 2)
                            if EAST_TILE_STRING not in clan.territory:
                                point1 = rect.topright
                                point2 = rect.bottomright
                                pygame.draw.line(screen, rgb_tile_colour, point1, point2, 2)
                            if SOUTH_TILE_STRING not in clan.territory:
                                point1 = rect.bottomleft
                                point2 = rect.bottomright
                                pygame.draw.line(screen, rgb_tile_colour, point1, point2, 2)
                            if WEST_TILE_STRING not in clan.territory:
                                point1 = rect.topleft
                                point2 = rect.bottomleft
                                pygame.draw.line(screen, rgb_tile_colour, point1, point2, 2)
                    x_pos += 50
                y_pos += 50
                x_pos = 80

    def hex_to_rgb(self, hex_color):
        """
        Converts hex codes to RGB
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

