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
        self.war_info_container = None
        self.focus_barony_info_container = None

        # individual buttons
        self.back_button = None
        self.view_all_button = None
        self.hide_borders_button = None

        self.cycle_war_left_button = None
        self.cycle_war_right_button = None

        # element dicts
        self.map_elements = {}
        self.barony_button_elements = {}
        self.war_elements = {}
        self.info_elements = {}

        self.map_tiles = {}

        # variables
        self.focus_barony = None
        self.borders_hidden = False
        self.view_all_borders = False
        self.viewing_war = 0

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
            elif event.ui_element == self.cycle_war_right_button:
                if self.viewing_war != len(game.clan.war):
                    self.viewing_war += 1
                else:
                    self.viewing_war = 0
                self.update_war_display()
            elif event.ui_element == self.cycle_war_left_button:
                if self.viewing_war != 0:
                    self.viewing_war -= 1
                else:
                    self.viewing_war = len(game.clan.war)
                self.update_war_display()
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
        self.war_info_container = UIContainer(
            ui_scale(pygame.Rect((20, 45), (280, 155))),
            starting_height=3,
            manager=MANAGER,
            anchors={"left_target": self.map_container}
        )
        self.focus_barony_info_container = UIContainer(
            ui_scale(pygame.Rect((20, 205), (280, 370))),
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

        self.war_elements["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 30), (280, 125))),
            get_box(BoxStyles.FRAME, (280, 125)),
            manager=MANAGER,
            container = self.war_info_container
        )

        # war info
        self.war_elements["heading"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((0, 0), (180, 30))),
            html_text="<b>CURRENT WARS</b>",
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            container=self.war_info_container,
            text_kwargs={},
            anchors={
                "centerx": "centerx"
            }
        )
        self.cycle_war_left_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((440, 110), (25, 40))),
            "<",
            get_button_dict(ButtonStyles.MENU_LEFT, (25, 40)),
            object_id="@buttonstyles_menu_left",
            manager=MANAGER
        )
        self.cycle_war_right_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((733, 110), (25, 40))),
            ">",
            get_button_dict(ButtonStyles.MENU_RIGHT, (25, 40)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER
        )


        self.update_map()
        self.update_focus_baron_info()
        self.update_war_display()
        self.update_buttons()

    def update_war_display(self):

        war_heading, war_desc = self.get_war_info()

        self.war_elements["info"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((0, 40), (240, 80))),
            html_text=war_heading,
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            container=self.war_info_container,
            manager=MANAGER,
            text_kwargs={},
            anchors={
                "centerx": "centerx"
            }
        )

        self.war_elements["desc"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((0, 63), (240, 80))),
            html_text=war_desc,
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            container=self.war_info_container,
            manager=MANAGER,
            text_kwargs={},
            anchors={
                "centerx": "centerx"
            }
        )

    
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
        self.cycle_war_left_button.kill()
        self.cycle_war_right_button.kill()

        # killing containers kills all inner elements as well
        self.map_container.kill()
        self.baronies_container.kill()
        self.war_info_container.kill()
        self.focus_barony_info_container.kill()
        
        for ele in self.map_elements:
            self.map_elements[ele].kill()
        self.map_elements = {}
        
        for ele in self.barony_button_elements:
            self.barony_button_elements[ele].kill()
        self.barony_button_elements = {}
        
        for ele in self.war_elements:
            self.war_elements[ele].kill()
        self.war_elements = {}
        
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
            ui_scale(pygame.Rect((0, 0), (280, 370))),
            get_box(BoxStyles.FRAME, (280, 370)),
            manager=MANAGER,
            container = self.focus_barony_info_container
        )

        self.info_elements["name"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((0, 8), (260, 40))),
            html_text=(
                "<b>" + 
                f"<font color='{get_baron_colour(Cat.fetch_cat(self.focus_barony.baron).ID)}'>" +
                str(Cat.fetch_cat(self.focus_barony.baron).name) +
                "</font></b> | <i>" +
                self.focus_barony.territory_type.capitalize() +
                "</i>"
                ),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            container=self.focus_barony_info_container,
            manager=MANAGER,
            text_kwargs={},
            anchors={
                "centerx": "centerx"
            }
        )

        clipper_num = 0
        if self.focus_barony == game.clan:
            clipper_num = len(get_alive_status_cats(
                Cat,
                get_status=["clipper"],
                working=True
            ))
        else:
            clipper_num = self.focus_barony.clippers

        self.info_elements["desc"] = pygame_gui.elements.UITextBox(
            relative_rect=ui_scale(pygame.Rect((0, 60), (260, 270))),
            html_text=(
                "<b>Territory</b>: " + str(len(self.focus_barony.territory)) + "<br>" +
                "<b>Clippers</b>: " + str(clipper_num) + "<br>" +
                "<b>Export</b>: " + self.focus_barony.export
                ),
            object_id=get_text_box_theme("#text_box_26_horizleft"),
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
        if len(game.clan.war) < 2:
            self.cycle_war_left_button.disable()
            self.cycle_war_right_button.disable()
        else:
            self.cycle_war_left_button.enable()
            self.cycle_war_right_button.enable()
    
    def get_war_info(self):
        """ puts together a string of war info """

        war_heading = "None!"
        war_desc = ""

        if game.clan.war:
            # for war in game.clan.war:
            war = game.clan.war[self.viewing_war]
            offense_clan_name = None
            offense_clan = None
            defense_clan_name = None
            defense_clan = None

            offense_clan_name = war["offense"]["name"]
            for clan in game.clan.all_clans + [game.clan]:
                if clan.name == offense_clan_name:
                    offense_clan = clan
                    break
            defense_clan_name = war["defense"]["name"]
            for clan in game.clan.all_clans + [game.clan]:
                if clan.name == defense_clan_name:
                    defense_clan = clan
                    break
            if offense_clan and defense_clan:
                if offense_clan == game.clan:
                    offense_baron = game.clan.baron
                else:
                    offense_baron = Cat.fetch_cat(offense_clan.baron)
                if defense_clan == game.clan:
                    defense_baron = game.clan.baron
                else:
                    defense_baron = Cat.fetch_cat(defense_clan.baron)
                war_heading = (
                    f"<font color='{get_baron_colour(offense_baron.ID)}'>{offense_baron.name}</font>" +
                    "  =>  "
                    f"<font color='{get_baron_colour(defense_baron.ID)}'>{defense_baron.name}</font>"
                    )
                war_desc = (
                    f"<b>Duration</b>: {war['duration']} moons" +
                    "\n" +
                    f"<b>Demand</b>: {war['reason'].capitalize()}"
                    )

        return war_heading, war_desc


    def update_map(self):
        """
        Generates coloured borders for the map
        """

        # the map image has to be blitted onto the screen
        # so the lines can blit on top of it.
        # and it has to be done here instead of screen_switches or itll disappear :C
        map_image = pygame.image.load("resources/images/badlands/map_small.png").convert_alpha()

        if game.settings["fullscreen"]:
            scaled_image = pygame.transform.scale(map_image, (435, 435))

            x_pos = 295
            y_pos = 112
            position = (370, 145)
        else:
            scaled_image = pygame.transform.scale(map_image, (350, 350))

            x_pos = 80
            y_pos = 80
            position = (80, 80)
        
        scaled_image.set_alpha(220) #255 is full opaque
        screen.blit(scaled_image, position)

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
                            rect = ui_scale(pygame.Rect((x_pos+1, y_pos+1), (50, 50)))

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
                if game.settings["fullscreen"]:
                    x_pos = 295
                else:
                    x_pos = 80

    def hex_to_rgb(self, hex_color):
        """
        Converts hex codes to RGB
        i didnt write this this is completely stolen idk how this works lol
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

