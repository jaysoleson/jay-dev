import pygame
import pygame_gui
import ujson
import random

from scripts.screens.Screens import Screens
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.modified_image import UIModifiedImage

from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.game_structure import image_cache
from scripts.game_structure import game
from pygame_gui.core import UIContainer
from scripts.ui.elements.map_tile import MapTileButton
from scripts.territory import territory_class
from scripts.events_module.text_adjust import event_text_adjust
from scripts.cat.cats import Cat
from scripts.ui.theme import get_text_box_theme
from ..ui.elements.checkbox import UICheckbox
from scripts.config import get_config
from scripts.game_structure.game.settings import game_setting_get
from scripts.ui.windows.map_view_events import MapViewEvents
from scripts.game_structure.game.switches import (
    Switch,
    switch_get_value
)
from scripts.clan_package.settings import get_clan_setting, set_clan_setting



class MapScreen(Screens):
    ui_images = {
        "arrow": image_cache.load_image(
                    "resources/images/maparrow.png"
                ).convert_alpha(),
        "map": image_cache.load_image(
                    "resources/images/cgwar_map.png"
                ).convert_alpha(),
        "compass": image_cache.load_image(
                    "resources/images/compass.png"
                ).convert_alpha(),
        "map_frame": image_cache.load_image(
                    "resources/images/map_frame.png"
                ).convert_alpha(),
    }
    def __init__(self, name=None):
        super().__init__(name)
        self.elements = {}
        self.back_button = None
        self.selected_tile = None

        self.map_tile_buttons = {}
        self.map_container = None
        self.tile_info_container = None

        # view toggle ui elements + bools
        self.view_checkboxes = {}
        self.view_colours = True
        self.view_icons = True
        self.view_terrain = False
        self.view_grid = True

        # different view tabs
        self.tabs = {}

        # what the colours are representing.
        self.current_view = "borders"

        self.X_TILES = get_config("bellsofwar.territory_grid_size")
        self.Y_TILES = get_config("bellsofwar.territory_grid_size")

        # map sixing info
        self.MAP_PADDING = 40
        self.BOX_SIZE = (400, 400)
        self.TILE_SIZE = self.BOX_SIZE[0] / self.X_TILES

        self.all_interaction_buttons = ["claim", "forfeit", "take", "attack"]

        self.selected_tile_owner = None

    def screen_switches(self):
        for tile in game.clan.territory_tiles:
            for event in tile.events.copy():
                if game.clan.age - event["moon"] >= get_config("bellsofwar.save_events_for"):
                    tile.events.remove(event)

        if switch_get_value(Switch.selected_tile):
            self.selected_tile = switch_get_value(Switch.selected_tile)

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.elements["map_box"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((40, 80), (self.BOX_SIZE[0] + self.MAP_PADDING, self.BOX_SIZE[1] + self.MAP_PADDING))),
            get_box(BoxStyles.ROUNDED_BOX, (self.BOX_SIZE[0] + self.MAP_PADDING, self.BOX_SIZE[1] + self.MAP_PADDING)),
            starting_height=3,
            manager=MANAGER,
        )

        self.map_container = UIContainer(
            ui_scale(pygame.Rect((60, 100), (self.BOX_SIZE[0], self.BOX_SIZE[1]))),
            starting_height=3,
            manager=MANAGER,
        )
        # this isnt in the container bc doing so makes it cover up the map tiles.
        # i dont actually know why
        self.elements["map_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((60, 100), (self.BOX_SIZE[0], self.BOX_SIZE[1]))),
            pygame.transform.scale(
                    self.ui_images["map"],
                    ui_scale_dimensions((self.BOX_SIZE[0], self.BOX_SIZE[0])),
                ),
            starting_height=3,
            manager=MANAGER,
        )

        self.tile_info_container = UIContainer(
            ui_scale(pygame.Rect((540, 100), (200, self.BOX_SIZE[1]))),
            starting_height=3,
            manager=MANAGER,
        )
        self.elements["tile_info_box"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((520, 80), (240, self.BOX_SIZE[1] + self.MAP_PADDING))),
            get_box(BoxStyles.ROUNDED_BOX, (240, self.BOX_SIZE[1] + self.MAP_PADDING)),
            starting_height=3,
            manager=MANAGER,
        )
        # events
        self.elements["view_events"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 260), (95, 30))),
            "buttons.map_view_events",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (95, 30)),
            object_id="@buttonstyles_rounded_rect",
            manager=MANAGER,
            container=self.tile_info_container,
            anchors={"centerx":"centerx"},
            tool_tip_text="buttons.map_view_events_tooltip"
        )

        # checkbox labels. boxes r made later
        self.elements["colour_label"] = pygame_gui.elements.UITextBox(
            "screens.map.toggle_colours",
            ui_scale(pygame.Rect((150, 565), (200, 40))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizleft"),
        )
        self.elements["icon_label"] = pygame_gui.elements.UITextBox(
            "screens.map.toggle_icons",
            ui_scale(pygame.Rect((310, 565), (200, 40))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizleft"),
        )
        self.elements["water_label"] = pygame_gui.elements.UITextBox(
            "screens.map.toggle_water",
            ui_scale(pygame.Rect((130, 600), (200, 40))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizleft"),
        )
        self.elements["grid_label"] = pygame_gui.elements.UITextBox(
            "screens.map.toggle_grid",
            ui_scale(pygame.Rect((325, 600), (200, 40))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizleft"),
        )

        self.update_tile_info()
        self.create_map()
        self.update_checkboxes()
        self.update_buttons()

        return super().screen_switches()

    def update_buttons(self):
        # tabs
        x_val = 105
        options = {
            "borders": Icon.CAT_HEAD,
            "terrain": Icon.MOUSE,
            "event_density": Icon.CLAN_UNKNOWN,
            "strength": Icon.SCRATCHES,
            "herbs": Icon.HERB,
        }
        for option, icon in options.items():
            if option in self.tabs:
                self.tabs[option].kill()
            self.tabs[option] = UISurfaceImageButton(
                ui_scale(pygame.Rect((x_val, -5), (32, 40))),
                icon,
                get_button_dict(ButtonStyles.HORIZONTAL_TAB_MIRRORED, (32, 40)),
                starting_height=2,
                object_id="@buttonstyles_horizontal_tab_mirrored",
                manager=MANAGER,
                anchors={"top_target": self.elements["map_box"]},
                tool_tip_text=f"screens.map.view_{option}"
            )
            if option == "event_density":
                x_val += 121
            else:
                x_val += 40
        
        for key, button in self.tabs.items():
            if self.current_view == key:
                button.disable()
            else:
                button.enable()


    def update_checkboxes(self):
        if "colour" in self.view_checkboxes:
            self.view_checkboxes["colour"].kill()
        if "icons" in self.view_checkboxes:
            self.view_checkboxes["icons"].kill()
        if "water" in self.view_checkboxes:
            self.view_checkboxes["water"].kill()
        if "grid" in self.view_checkboxes:
            self.view_checkboxes["grid"].kill()

        self.view_checkboxes["colour"] = UICheckbox(
            position=(115, 565),
            check=self.view_colours,
            manager=MANAGER,
        )
        self.view_checkboxes["icons"] = UICheckbox(
            position=(275, 565),
            check=self.view_icons,
            manager=MANAGER,
        )
        self.view_checkboxes["water"] = UICheckbox(
            position=(95, 600),
            check=self.view_terrain,
            manager=MANAGER,
        )
        self.view_checkboxes["grid"] = UICheckbox(
            position=(290, 600),
            check=self.view_grid,
            manager=MANAGER,
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            
            for key, button in self.map_tile_buttons.items():
                if event.ui_element == button:
                    if button.selected:
                        button.deselect()
                        self.selected_tile = None
                        self.update_tile_info()
                    else:
                        button.select()
                        self.selected_tile = key
                        self.update_tile_info()
                    self.update_tiles()
            for key, button in self.tabs.items():
                if event.ui_element == button:
                    self.current_view = key
                    self.update_buttons()
                    self.create_map()
            if event.ui_element == self.view_checkboxes["colour"]:
                if self.view_colours:
                    self.view_colours = False
                else:
                    self.view_colours = True
                self.create_map()
                self.update_checkboxes()
            elif event.ui_element == self.view_checkboxes["icons"]:
                if self.view_icons:
                    self.view_icons = False
                else:
                    self.view_icons = True
                self.create_map()
                self.update_checkboxes()
            elif event.ui_element == self.view_checkboxes["water"]:
                if self.view_terrain:
                    self.view_terrain = False
                else:
                    self.view_terrain = True
                self.create_map()
                self.update_checkboxes()
            elif event.ui_element == self.view_checkboxes["grid"]:
                if self.view_grid:
                    self.view_grid = False
                else:
                    self.view_grid = True
                self.create_map()
                self.update_checkboxes()
            elif event.ui_element == self.elements["view_events"]:
                MapViewEvents(self.selected_tile)
            for interaction in self.all_interaction_buttons:
                if interaction in self.elements and event.ui_element == self.elements[interaction]:
                    self.handle_map_interaction(interaction)
                    self.update_interaction_buttons()
                    self.create_map()
        return super().handle_event(event)
    
    def exit_screen(self):
        self.back_button.kill()
        self.map_container.kill()
        self.tile_info_container.kill()

        for ele in self.elements:
            self.elements[ele].kill()
        self.elements = {}
        for ele in self.map_tile_buttons:
            self.map_tile_buttons[ele].kill()
        self.map_tile_buttons = {}
        for ele in self.view_checkboxes:
            self.view_checkboxes[ele].kill()
        self.view_checkboxes = {}
        for ele in self.tabs:
            self.tabs[ele].kill()
        self.tabs = {}

        return super().exit_screen()

    # now the fun stuff
    def create_map(self):
        for ele in self.map_tile_buttons:
            self.map_tile_buttons[ele].kill()
        self.map_tile_buttons = {}

        for tile in game.clan.territory_tiles:

            text = ""
            icon_tile = False
            if self.view_icons:
                if tile.in_dispute():
                    icon_tile = True
                    text = Icon.SCRATCHES
                elif tile.poi:
                    icon_tile = True
                    if tile.poi == "gathering":
                        text = Icon.CLAN_OTHER
                    elif tile.poi == "moonplace":
                        text = Icon.HERB
                    elif "terrain" in tile.poi:
                        text = Icon.PAW
                elif tile.camp:
                    text = Icon.CLAN_PLAYER
                    icon_tile = True
                if get_clan_setting("map_interaction"):
                    if get_clan_setting("map_interaction")["tile"] == tile.tile_string:
                        icon_tile = True
                        text = Icon.NEWLEAF

            if game_setting_get("fullscreen"):
                modifier = 2
            else:
                modifier = 1

            self.map_tile_buttons[tile] = MapTileButton(
                relative_rect=ui_scale(
                    pygame.Rect(
                        (tile.x * self.TILE_SIZE, tile.y * self.TILE_SIZE),
                        (self.TILE_SIZE + modifier, self.TILE_SIZE + modifier)
                        )
                    ),
                text=text,
                # object_id="#text_box_22_horizcenter",
                container=self.map_container,
                manager=MANAGER,
                tile_object=tile,
                view_colours=self.view_colours,
                view_icons=self.view_icons,
                view_terrain=self.view_terrain,
                view_grid=self.view_grid,
                icon_tile=icon_tile,
                opacity=225,
                current_view=self.current_view
            )
            if tile == self.selected_tile:
                self.map_tile_buttons[tile].select()

        if "map_frame" in self.elements:
            self.elements["map_frame"].kill()

        # UIModifiedImage allows hover over the tiles below it
        # thank u whoever made this! i assume scribble! yay!
        self.elements["map_frame"] = UIModifiedImage(
            ui_scale(pygame.Rect((25, 65), (470, 470))),
            pygame.transform.scale(
                    self.ui_images["map_frame"],
                    ui_scale_dimensions((470, 470)),
                ),
            starting_height=10,
            manager=MANAGER,
        )
        self.elements["map_frame"].disable()

        if "compass" in self.elements:
            self.elements["compass"].kill()
        self.elements["compass"] = UIModifiedImage(
            ui_scale(pygame.Rect((403, 43), (114, 114))),
            pygame.transform.scale(
                    self.ui_images["compass"],
                    ui_scale_dimensions((114, 114)),
                ),
            starting_height=10,
            manager=MANAGER,
        )
        self.elements["compass"].disable()

    def update_tiles(self):
        for key, button in self.map_tile_buttons.items():
            if key != self.selected_tile:
                button.deselect()
    
    def update_tile_info(self):
        if not self.selected_tile:
            self.tile_info_container.hide()
            self.elements["tile_info_box"].hide()
            if "tile_info_pointer" in self.elements:
                self.elements["tile_info_pointer"].hide()
            return
        self.tile_info_container.show()
        self.elements["tile_info_box"].show()

        # remake the arrow
        if "tile_info_pointer" in self.elements:
            self.elements["tile_info_pointer"].kill()
        self.elements["tile_info_pointer"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((492, 98 + self.selected_tile.y * self.TILE_SIZE), (44, 30))),
            pygame.transform.scale(
                    self.ui_images["arrow"],
                    ui_scale_dimensions((44, 30)),
                ),
            starting_height=3,
            manager=MANAGER,
        )

        if "selected_tile_owner" in self.elements:
            self.elements["selected_tile_owner"].kill()
        if "selected_tile_info_text" in self.elements:
            self.elements["selected_tile_info_text"].kill()

        if self.selected_tile:

            self.elements["selected_tile_owner"] = pygame_gui.elements.UITextBox(
                self.selected_tile.name_string(),
                ui_scale(pygame.Rect((0, 0), (200, -1))),
                manager=MANAGER,
                container=self.tile_info_container,
                object_id="#text_box_40_horizcenter_spacing_95",
                anchors={"centerx": "centerx"}
            )

            info = ""

            info += f"{self.selected_tile.owner_string()}"
            info += "<br>"

            info += self.selected_tile.security_string()
            info += "<br>"

            if self.selected_tile.herb:
                info += "---<br>"
                info += self.selected_tile.herb_string()
                info += "<br>"

            current_war = None
            if self.selected_tile.owner:
                current_war = self.selected_tile.owner.get_current_war()
            if current_war and not self.selected_tile.in_dispute():
                info += "---<br>"
                info += current_war.get_full_opposition_string(self.selected_tile.owner)

            self.elements["selected_tile_info_text"] = pygame_gui.elements.UITextBox(
                info,
                ui_scale(pygame.Rect((0, 10), (180, 180))),
                manager=MANAGER,
                container=self.tile_info_container,
                object_id="#text_box_26_horizcenter_vert_spacing_95",
                anchors={"centerx": "centerx", "top_target": self.elements["selected_tile_owner"]},
            )

        at_war = game.clan.get_current_war(self.selected_tile.owner)

        # interaction buttons
        # kill them all first
        for button in self.all_interaction_buttons:
            if button in self.elements:
                self.elements[button].kill()
        
        y_positions = [315, 350]
        button_width = 115
    
        # CLAIM
        if self.selected_tile.owner != game.clan:
            if self.selected_tile.camp or at_war:
                if at_war:
                    tooltip = "buttons.attack_war_tooltip"
                else:
                    tooltip = "buttons.attack_camp_tooltip"
                self.elements["attack"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((0, y_positions[0]), (button_width, 30))),
                    "buttons.attack_camp",
                    get_button_dict(ButtonStyles.SQUOVAL, (button_width, 30)),
                    object_id="@buttonstyles_squoval",
                    manager=MANAGER,
                    container=self.tile_info_container,
                    anchors={"centerx":"centerx"},
                    tool_tip_text=tooltip
                )
            else:
                self.elements["claim"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((0, y_positions[0]), (button_width, 30))),
                    "buttons.claim",
                    get_button_dict(ButtonStyles.SQUOVAL, (button_width, 30)),
                    object_id="@buttonstyles_squoval",
                    manager=MANAGER,
                    container=self.tile_info_container,
                    anchors={"centerx":"centerx"},
                    tool_tip_text="buttons.claim_tooltip"
                )
                if self.selected_tile.owner:
                    self.elements["take"] = UISurfaceImageButton(
                        ui_scale(pygame.Rect((0, y_positions[1]), (button_width, 30))),
                        "buttons.take",
                        get_button_dict(ButtonStyles.SQUOVAL, (button_width, 30)),
                        object_id="@buttonstyles_squoval",
                        manager=MANAGER,
                        container=self.tile_info_container,
                        anchors={"centerx":"centerx"},
                        tool_tip_text="buttons.take_tooltip"
                    )
                # gathering, moonplaces, and camps cant be claimed
                if (
                    self.selected_tile.poi in ["moonplace", "gathering", "terrain_twolegplace"] or
                    self.selected_tile.camp
                    ):
                    self.elements["claim"].disable()
                    if "take" in self.elements:
                        self.elements["take"].disable()
        
        # FORFEIT
        elif self.selected_tile.owner == game.clan:
            self.elements["forfeit"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_positions[0]), (button_width, 30))),
                "buttons.forfeit",
                get_button_dict(ButtonStyles.SQUOVAL, (button_width, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
                container=self.tile_info_container,
                anchors={"centerx":"centerx"},
                tool_tip_text="buttons.forfeit_tooltip"
            )
            if self.selected_tile.camp:
                self.elements["forfeit"].disable()

        self.update_interaction_buttons()
    
    def update_interaction_buttons(self):
        if get_clan_setting("map_interaction"):
            for interaction in self.all_interaction_buttons:
                if interaction in self.elements:
                    if (
                        get_clan_setting("map_interaction")["interaction"] == interaction and
                        get_clan_setting("map_interaction")["tile"] == self.selected_tile.tile_string
                        ):
                        self.elements[interaction].disable()
                    else:
                        self.elements[interaction].enable()

    def handle_map_interaction(self, interaction_type):
        """
        Sets the dict for the map interaction.
        """
        set_clan_setting(
            "map_interaction",
            {
                "tile": self.selected_tile.tile_string,
                "owner_ID": self.selected_tile.owner.group_ID if self.selected_tile.owner else None,
                "interaction": interaction_type
            }
        )

