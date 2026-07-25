import pygame
import pygame_gui
import ujson

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


class MapScreen(Screens):
    ui_images = {
        "arrow": image_cache.load_image(
                    "resources/images/buttons/arrow_left_fancy.png"
                ).convert_alpha(),
        "map": image_cache.load_image(
                    "resources/images/cgwar_map.png"
                ).convert_alpha(),
    }
    def __init__(self, name=None):
        super().__init__(name)
        self.tile_size = 38
        self.elements = {}
        self.back_button = None
        self.selected_tile = None

        self.map_tile_buttons = {}
        self.map_container = None
        self.tile_info_container = None

        self.view_checkboxes = {}
        self.view_colours = True
        self.view_icons = True

        self.tabs = {}

        # what the colours are representing.
        self.current_view = "borders"

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
        self.elements["map_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((60, 100), (self.tile_size * 11, self.tile_size * 11))),
            pygame.transform.scale(
                    self.ui_images["map"],
                    ui_scale_dimensions((self.tile_size * 11, self.tile_size * 11)),
                ),
            starting_height=3,
            manager=MANAGER,
        )

        self.tile_info_container = UIContainer(
            ui_scale(pygame.Rect((540, 100), (200, self.tile_size*11))),
            starting_height=3,
            manager=MANAGER,
        )
        self.elements["tile_info_box"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((520, 80), (240, self.tile_size*11 + 40))),
            get_box(BoxStyles.ROUNDED_BOX, (240, self.tile_size*11 + 40)),
            starting_height=3,
            manager=MANAGER,
        )
        # dummy to get replaced later
        self.elements["tile_info_pointer"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (30, 30))),
            pygame.transform.scale(
                    self.ui_images["arrow"],
                    ui_scale_dimensions((30, 30)),
                ),
            starting_height=3,
            manager=MANAGER,
        )

        # checkbox labels. boxes r made later
        self.elements["colour_label"] = pygame_gui.elements.UITextBox(
            "screens.map.toggle_colours",
            ui_scale(pygame.Rect((140, 600), (200, 40))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizleft"),
        )
        self.elements["icon_label"] = pygame_gui.elements.UITextBox(
            "screens.map.toggle_icons",
            ui_scale(pygame.Rect((310, 600), (200, 40))),
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
        x_val = 225
        options = {
            "borders": Icon.CAT_HEAD,
            "herbs": Icon.HERB
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
            position=(100, 600),
            check=self.view_colours,
            manager=MANAGER,
        )
        self.view_checkboxes["icons"] = UICheckbox(
            position=(270, 600),
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

            self.map_tile_buttons[tile] = MapTileButton(
                relative_rect=ui_scale(pygame.Rect((x * self.tile_size, y * self.tile_size), (self.tile_size, self.tile_size))),
                text=text,
                container=self.map_container,
                manager=MANAGER,
                tile_owner=tile_owner,
                tile_string = tile,
                view_colours=self.view_colours,
                view_icons=self.view_icons,
                icon_tile=icon_tile,
                opacity=225 if self.current_view == "borders" else 190,
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
            self.elements["tile_info_pointer"].hide()
            return
        self.tile_info_container.show()
        self.elements["tile_info_box"].show()

        # remake the arrow
        self.elements["tile_info_pointer"].kill()
        self.elements["tile_info_pointer"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((505, 104 + int(self.selected_tile.split("-")[1]) * self.tile_size), (30, 30))),
            pygame.transform.scale(
                    self.ui_images["arrow"],
                    ui_scale_dimensions((30, 30)),
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
                    name = event_text_adjust(Cat, text="{POI/name/" + tile_info["poi"] + "}").title()
                else:
                    name = event_text_adjust(Cat, text="{POI/category/" + tile_info["poi"] + "}").title()
            elif "camp" in tile_info and tile_info["camp"]:
                name = str(tile_owner.name) + "'s Camp"
            else:
                name = str(tile_owner.name) + "'s Territory" if tile_owner else "Unclaimed Land"

            self.elements["selected_tile_owner"] = pygame_gui.elements.UITextBox(
                name,
                ui_scale(pygame.Rect((0, 0), (200, 40))),
                manager=MANAGER,
                container=self.tile_info_container,
                object_id="#text_box_34_horizcenter",
                anchors={"centerx": "centerx"}
            )

            # herb info
            if "herb" in tile_info:
                self.elements["selected_tile_info_text"] = pygame_gui.elements.UITextBox(
                    "<b>Main Herb</b>: " + tile_info["herb"].replace("_", " ").capitalize(),
                    ui_scale(pygame.Rect((0, 40), (200, 40))),
                    manager=MANAGER,
                    container=self.tile_info_container,
                    object_id="#text_box_26_horizcenter",
                    anchors={"centerx": "centerx"}
                )
        # interaction buttons
        # kill them all first
        for button in ["claim", "forfeit", "take"]:
            if button in self.elements:
                self.elements[button].kill()
        
        y_positions = [260, 300, 340]
        button_width = 115
    
        # CLAIM
        if tile_info["owner"] != game.clan.group_ID:
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
