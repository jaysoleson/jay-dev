import os
import i18n

import pygame
import pygame_gui

from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.elements.checkbox import UICheckbox
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.modified_scrolling_container import UIModifiedScrollingContainer
from scripts.game_structure import game
from scripts.ui.icon import Icon
from scripts.territory import territory_class
from scripts.config import get_config
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.game_structure.game.switches import (
    Switch,
    switch_get_value,
    switch_set_value,
)
from scripts.clan_resources.point_of_interest import (
    get_poi_save_dict
)

class EditMapOptions(GameWindow):
    def __init__(self, current_information):
        super().__init__(
            ui_scale(pygame.Rect((90, 125), (620, 450))),
        )
        self.info = current_information
        self.elements = {}
        self.checkboxes = {}
        self.checkbox_labels = {}
        self.heading = pygame_gui.elements.UITextBox(
                "<b>Change Edit Options</b>",
                ui_scale(pygame.Rect((5, 10), (510, 55))),
                manager=MANAGER,
                container=self,
                anchors={"centerx": "centerx"},
                object_id="#text_box_30_horizcenter_spacing_95"
            )
        self.subtitle = None

        self.page = 0

        self.container = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((0, 20), (600, 330))),
            allow_scroll_y=True,
            container=self,
            starting_height=3,
            manager=MANAGER,
            anchors={"centerx": "centerx"}
        )

        self.draw_options()

        self.elements["save"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 350), (120, 30))),
            "save",
            get_button_dict(ButtonStyles.SQUOVAL, (120, 30)),
            starting_height=5,
            container=self,
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"centerx":"centerx"}
        )

        self.elements["cycle_page_left"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((200, 350), (30, 30))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (30, 30)),
            starting_height=5,
            container=self,
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.elements["cycle_page_right"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((390, 350), (30, 30))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (30, 30)),
            starting_height=5,
            container=self,
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )

    def draw_options(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}
        for ele in self.checkbox_labels:
            self.checkbox_labels[ele].kill()
        self.checkbox_labels = {}

        if self.subtitle:
            self.subtitle.kill()
        subtitle = ""

        if self.page == 0:
            subtitle = "Tile Owner"
            self.create_option_checkboxes("owner", game.clan.all_other_clans + [game.clan] + [None])
        elif self.page == 1:
            subtitle = "Points of Interest"
            option_list = []
            for poi_type in get_poi_save_dict():
                if poi_type == "terrain":
                    option_list.extend(get_poi_save_dict()[poi_type])
                else:
                    option_list.append(poi_type)
            self.create_option_checkboxes("poi", option_list)
        elif self.page == 2:
            subtitle = "Terrain"
            self.create_option_checkboxes("terrain", ["river", "ocean", "lake", "land", "thunderpath", "silverpath"])
        elif self.page == 3:
            subtitle = "Camp"
            self.create_option_checkboxes("camp", [True])
        elif self.page == 4:
            subtitle = "Herbs"
            self.create_option_checkboxes("herb", list(game.clan.herb_supply.base_herb_list.keys()) + [None])

        self.subtitle = pygame_gui.elements.UITextBox(
                subtitle,
                ui_scale(pygame.Rect((5, 40), (510, 55))),
                manager=MANAGER,
                container=self,
                anchors={"centerx": "centerx"},
                object_id="#text_box_30_horizcenter_spacing_95"
            )

    def create_option_checkboxes(self, option_type, option_list):
        y_val = 110
        for option in option_list:
            name = str(option)
            if option_type == "owner":
                if option:
                    name = option.name
                    option = option.group_ID
            self.checkboxes[f"{option_type}-{option}"] = UICheckbox(
                position=(-60, y_val),
                check=option_type in self.info and self.info[option_type] == option,
                container=self.container,
                manager=MANAGER,
                anchors={"centerx":"centerx"}
            )
            self.checkbox_labels[f"label-{option_type}-{option}"] = pygame_gui.elements.UITextBox(
                name,
                ui_scale(pygame.Rect((70, y_val), (190, 30))),
                container=self.container,
                manager=MANAGER,
                anchors={"centerx": "centerx"},
                object_id="#text_box_26_horizleft",
            )
            y_val += 45

    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.kill()
            for name, checkbox in self.checkboxes.items():
                if event.ui_element == checkbox:
                    change_type, change_value = name.split("-")
                    if change_value == "None":
                        change_value = None
                    elif change_value == "True":
                        change_value = True
                    elif change_value == "False":
                        change_value = False

                    if change_type not in self.info:
                        self.info[change_type] = change_value
                    else:
                        if self.info[change_type] == change_value:
                            self.info.pop(change_type)
                        else:
                            self.info[change_type] = change_value
                    self.draw_options()
            if event.ui_element == self.elements["save"]:
                switch_set_value(Switch.edit_map_info, self.info)
            elif event.ui_element == self.elements["cycle_page_right"]:
                self.page += 1
                if self.page > 4:
                    self.page = 0
                self.draw_options()
            elif event.ui_element == self.elements["cycle_page_left"]:
                self.page -= 1
                if self.page < 0:
                    self.page = 4
                self.draw_options()
