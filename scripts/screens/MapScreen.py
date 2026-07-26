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


class MapScreen(Screens):
    ui_images = {
        "arrow": image_cache.load_image(
                    "resources/images/maparrow.png"
                ).convert_alpha(),
        "map": image_cache.load_image(
                    "resources/images/cgwar_map.png"
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

    def screen_switches(self):
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

        self.create_map()
        self.update_tile_info()
        self.update_checkboxes()
        self.update_buttons()

        return super().screen_switches()

    def update_buttons(self):
        # tabs
        x_val = 194
        options = {
            "borders": Icon.CAT_HEAD,
            "herbs": Icon.HERB,
            "strength": Icon.SCRATCHES
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
            x_val += 50
        
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
            for interaction in self.all_interaction_buttons:
                if interaction in self.elements and event.ui_element == self.elements[interaction]:
                    print(interaction)
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

        for tile, tile_info in game.clan.territory_tile_info.items():
            x = int(tile.split("-")[0])
            y = int(tile.split("-")[1])

            tile_owner = territory_class.get_tile_owner(tile)

            text = ""
            icon_tile = False
            if self.view_icons:
                if "poi" in tile_info:
                    icon_tile = True
                    if tile_info["poi"] == "gathering":
                        text = Icon.CLAN_OTHER
                    elif tile_info["poi"] == "moonplace":
                        text = Icon.HERB
                    elif "terrain" in tile_info["poi"]:
                        text = Icon.PAW
                elif "camp" in tile_info and tile_info["camp"]:
                    text = Icon.CLAN_PLAYER
                    icon_tile = True
            
            if game_setting_get("fullscreen"):
                modifier = 2
            else:
                modifier = 1

            self.map_tile_buttons[tile] = MapTileButton(
                relative_rect=ui_scale(
                    pygame.Rect(
                        (x * self.TILE_SIZE, y * self.TILE_SIZE),
                        (self.TILE_SIZE + modifier, self.TILE_SIZE + modifier)
                        )
                    ),
                text=text,
                # object_id="#text_box_22_horizcenter",
                container=self.map_container,
                manager=MANAGER,
                tile_owner=tile_owner,
                tile_string = tile,
                view_colours=self.view_colours,
                view_icons=self.view_icons,
                icon_tile=icon_tile,
                opacity=225,
                herb=tile_info["herb"] if "herb" in tile_info else None,
                current_view=self.current_view
            )
            if tile == self.selected_tile:
                self.map_tile_buttons[tile].select()
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
            ui_scale(pygame.Rect((492, 105 + int(self.selected_tile.split("-")[1]) * self.TILE_SIZE), (44, 30))),
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
            tile_owner = territory_class.get_tile_owner(self.selected_tile)
            tile_info = game.clan.territory_tile_info[self.selected_tile]

            name = ""
            if "poi" in tile_info:
                if "terrain" in tile_info["poi"]:
                    name = "<b>" + event_text_adjust(Cat, text="{POI/name/" + tile_info["poi"] + "}").title() + "</b>"
                else:
                    name = "<b>" + event_text_adjust(Cat, text="{POI/category/" + tile_info["poi"] + "}").title() + "</b>"
            elif "camp" in tile_info and tile_info["camp"]:
                name = "<b>" + str(tile_owner.name) + " Camp</b>"
            else:
                name = f"<b>{game.clan.biome}</b>"

            self.elements["selected_tile_owner"] = pygame_gui.elements.UITextBox(
                name,
                ui_scale(pygame.Rect((0, 0), (200, 40))),
                manager=MANAGER,
                container=self.tile_info_container,
                object_id="#text_box_40_horizcenter",
                anchors={"centerx": "centerx"}
            )

            strength_dict = {
                0: "Unguarded",
                1: "Often forgotten",
                2: "Patrolled infrequently",
                3: "Patrolled regularly",
                4: "Effectively guarded"
            }

            # herb info
            info = ""
            if tile_owner:
                info += f"<b>{tile_owner.name}'s Territory</b>"
            else:
                info += "<b>Unclaimed Land</b>"
            info += "<br>"

            # info += f"({self.selected_tile.split('-')[0]}, {self.selected_tile.split('-')[1]})<br>"
            if "strength" in tile_info:
                info += strength_dict[(tile_info["strength"])]
            info += "<br>"


            if "herb" in tile_info:
                info += "---<br>"
                info += "Effective source of <br><b>" + tile_info["herb"].replace("_", " ") + "</b>"

            self.elements["selected_tile_info_text"] = pygame_gui.elements.UITextBox(
                info,
                ui_scale(pygame.Rect((0, 35), (180, 250))),
                manager=MANAGER,
                container=self.tile_info_container,
                object_id="#text_box_26_horizcenter_vert_spacing_95",
                anchors={"centerx": "centerx"},
            )
        
        # events
        self.elements["view_events"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 145), (95, 30))),
            "buttons.map_view_events",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (95, 30)),
            object_id="@buttonstyles_rounded_rect",
            manager=MANAGER,
            container=self.tile_info_container,
            anchors={"centerx":"centerx"},
            tool_tip_text="buttons.map_view_events_tooltip"
        )

        # interaction buttons
        # kill them all first
        for button in self.all_interaction_buttons:
            if button in self.elements:
                self.elements[button].kill()
        
        y_positions = [260, 300, 340]
        button_width = 115
    
        # CLAIM
        if tile_info["owner"] != game.clan.group_ID:
            if "camp" in tile_info:
                self.elements["attack"] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((0, y_positions[0]), (button_width, 30))),
                    "buttons.attack_camp",
                    get_button_dict(ButtonStyles.SQUOVAL, (button_width, 30)),
                    object_id="@buttonstyles_squoval",
                    manager=MANAGER,
                    container=self.tile_info_container,
                    anchors={"centerx":"centerx"},
                    tool_tip_text="buttons.attack_camp_tooltip"
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
                    ("poi" in tile_info and tile_info["poi"] in ["moonplace", "gathering", "terrain_twolegplace"])
                    or "camp" in tile_info and tile_info["camp"]
                    ):
                    self.elements["claim"].disable()
                    self.elements["take"].disable()
        
        # FORFEIT
        elif tile_info["owner"] == game.clan.group_ID:
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
            if "camp" in tile_info and tile_info["camp"]:
                self.elements["forfeit"].disable()
