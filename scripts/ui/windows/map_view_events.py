import os
import i18n

import pygame
import pygame_gui

from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.modified_scrolling_container import UIModifiedScrollingContainer
from scripts.game_structure import game
from scripts.ui.icon import Icon
from scripts.territory import territory_class
from scripts.config import get_config
from scripts.ui.generate_box import get_box, BoxStyles


class MapViewEvents(GameWindow):
    def __init__(self, tile):
        super().__init__(
            ui_scale(pygame.Rect((90, 125), (620, 450))),
        )
        self.tile = tile
        self.event_elements = {}

        self.heading = pygame_gui.elements.UITextBox(
            "screens.map.view_events_header",
            ui_scale(pygame.Rect((5, 10), (510, 55))),
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
            object_id="#text_box_30_horizcenter_spacing_95",
            text_kwargs={"moons": get_config("bellsofwar.save_events_for")}
        )
        owner_string = territory_class.get_owner_string(self.tile)
        security_string = territory_class.get_security_string(self.tile)

        self.subtitle = pygame_gui.elements.UITextBox(
            game.clan.biome +
            " | " +
            "<b>" + owner_string + "</b>" +
            " | " +
            security_string,
            ui_scale(pygame.Rect((0, 65), (600, 30))),
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
            object_id="#text_box_26_horizcenter_vertcenter_spacing_95"
        )
        self.event_container = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((0, 95), (570, 325))),
            allow_scroll_y=True,
            container=self,
            starting_height=3,
            manager=MANAGER,
            anchors={"centerx": "centerx"}
        )

        self.build_events_list()
    
    def build_events_list(self):
        for item in self.event_elements:
            self.event_elements[item].kill()
        self.event_elements = {}

        self.events_list = []
        if "events" in game.clan.territory_tile_info[self.tile]:
            self.events_list = game.clan.territory_tile_info[self.tile]["events"]

        if not self.events_list:
            self.event_elements["no_events"] = pygame_gui.elements.UITextBox(
                "screens.map.no_events",
                ui_scale(pygame.Rect((5, 10), (530, 100))),
                manager=MANAGER,
                container=self.event_container,
                anchors={"centerx": "centerx"},
                object_id="#text_box_26_horizcenter_vertcenter_spacing_95",
            )
        else:
            for index, event in enumerate(self.events_list):
                previous_element = (
                    self.event_elements[str(index - 1) + "_frame"]
                    if index > 0
                    else None
                    )
                self.event_elements[str(index) + "_text"] = pygame_gui.elements.UITextBox(
                    event["text"],
                    ui_scale(pygame.Rect((32, 29), (375, -1))),
                    manager=MANAGER,
                    container=self.event_container,
                    anchors=(
                        {"centerx": "centerx"} if not previous_element else
                        {"centerx": "centerx", "top_target": previous_element}
                        ),
                    object_id="#text_box_26_horizcenter_vertcenter_spacing_95",
                )
                # find the height of the text element (varies based on hwo long the event is)
                # and adjust the frame accordingly.
                # theres a min height so the moon + buttons will always fit.
                min_height = 120
                height = self.event_elements[str(index) + "_text"].rect.height + 42
                if height < min_height:
                    height = min_height

                self.event_elements[str(index) + "_frame"] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((0, 15), (500, height))),
                    get_box(BoxStyles.FRAME, (520, height)),
                    starting_height=1,
                    container=self.event_container,
                    manager=MANAGER,
                    anchors=(
                        {"centerx": "centerx"} if not previous_element else
                        {"centerx": "centerx", "top_target": previous_element}
                    ),
                )
                self.event_elements[str(index) + "_moon"] = pygame_gui.elements.UITextBox(
                    "<b>Moon</b><br>" + str(event["moon"]),
                    ui_scale(pygame.Rect((52, 26), (70, 60))),
                    manager=MANAGER,
                    container=self.event_container,
                    anchors=(
                        None if not previous_element else
                        {"top_target": previous_element}
                        ),
                    object_id="#text_box_26_horizcenter_vertcenter_spacing_95",
                )
                tooltip = i18n.t("screens.map.save_event", moons=get_config("bellsofwar.save_events_for"))
                self.event_elements[str(index) + "_saveevent"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((62, 0), (20, 20))),
                    Icon.PAW,
                    get_button_dict(ButtonStyles.ROUNDED_RECT, (20, 20)),
                    starting_height=2,
                    object_id="@buttonstyles_rounded_rect",
                    container=self.event_container,
                    manager=MANAGER,
                    tool_tip_text=tooltip,
                    anchors={"top_target": self.event_elements[str(index) + "_moon"]}
                )
                if game.clan.territory_tile_info[self.tile]["events"][index]["saved"]:
                    self.event_elements[str(index) + "_saveevent"].disable()

                self.event_elements[str(index) + "_deleteevent"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((92, 0), (20, 20))),
                    Icon.SCRATCHES,
                    get_button_dict(ButtonStyles.ROUNDED_RECT, (20, 20)),
                    starting_height=2,
                    object_id="@buttonstyles_rounded_rect",
                    container=self.event_container,
                    manager=MANAGER,
                    tool_tip_text="screens.map.delete_event",
                    anchors={"top_target": self.event_elements[str(index) + "_moon"]},
                )
        
    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.event_container.kill()
                self.kill()
            for key, btn in self.event_elements.items():
                if event.ui_element == btn:
                    index, btn_type = key.split("_")
                    index = int(index)
                    if btn_type == "deleteevent":
                        game.clan.territory_tile_info[self.tile]["events"].remove(game.clan.territory_tile_info[self.tile]["events"][index])
                    elif btn_type == "saveevent":
                        game.clan.territory_tile_info[self.tile]["events"][index]["saved"] = True
                    self.build_events_list()