import random
import traceback
from copy import deepcopy

import ujson

import math
import os

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from ..game_structure.screen_settings import MANAGER, screen

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import (
    game,
)
from scripts.game_structure.ui_elements import (
    UISpriteButton,
    UIImageButton,
    UISurfaceImageButton,
)
from scripts.game_structure.windows import SaveError
from scripts.utility import (
    ui_scale,
    check_possible_directions,
    ui_scale_dimensions,
    get_current_season,
    get_text_box_theme,
    ui_scale_blit,
)
from .Screens import Screens
from ..ui.generate_button import ButtonStyles, get_button_dict
from ..ui.generate_box import get_box, BoxStyles
from ..ui.get_arrow import get_arrow
from ..ui.icon import Icon

# pylint: disable=consider-using-dict-items


class ClanScreen(Screens):
    max_sprites_displayed = (
        400  # we don't want 100,000 sprites rendering at once. 400 is enough.
    )
    cat_buttons = []
    platforms = {}
    direction_buttons = {}
    activity_buttons = {}
    activity_button_popups = {}
    activity_labels = {}
    popup_buttons = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.show_den_labels = None
        self.show_den_text = None
        self.layout = None

        self.open_popup = None
        self.activity_list = None

    def on_use(self):
        # if game.clan.clan_settings['backgrounds']:
        #     screen.blit(self.arena_bg, (0, 0))
        if not game.clan.clan_settings["backgrounds"]:
            self.set_bg(None)
        super().on_use()

        if game.clan.clan_settings["backgrounds"]:
            # wildfire!
            if game.clan.disaster == "Wildfire" and game.clan.disaster_moon >= 2:
                position = game.clan.your_cat.map_position
                if game.clan.your_cat.dead:
                    if game.clan.spectating:
                        position = game.clan.spectating.map_position

                filepath = f"resources/images/hg_maps/wildfire/{position}.png"

                if os.path.exists(filepath):
                    fireimage = pygame.transform.scale(
                        image_cache.load_image(filepath),
                        ui_scale_dimensions((800, 700))
                    )
                    screen.blit(fireimage,(0, 0))
                elif position != "0_0":
                    fireimage = pygame.transform.scale(
                        image_cache.load_image("resources/images/hg_maps/wildfire/1_1.png"),
                        ui_scale_dimensions((800, 700))
                    )
                    screen.blit(fireimage,(0, 0))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)
            self.menu_button_pressed(event)
            if event.ui_element == self.save_button:
                try:
                    self.save_button_saving_state.show()
                    self.save_button.disable()
                    game.save_cats()
                    game.clan.save_clan()
                    game.clan.save_pregnancy(game.clan)
                    game.save_events()
                    game.save_settings(self)
                    game.switches["saved_clan"] = True
                    self.update_buttons_and_text()
                except RuntimeError:
                    SaveError(traceback.format_exc())
                    self.change_screen("start screen")
            if event.ui_element in self.cat_buttons:
                game.switches["cat"] = event.ui_element.return_cat_id()
                self.change_screen('profile screen')
            
            if event.ui_element == self.direction_buttons["north"]:
                game.clan.next_activity = "north"
                self.update_activity_buttons()
            elif event.ui_element == self.direction_buttons["east"]:
                game.clan.next_activity = "east"
                self.update_activity_buttons()
            elif event.ui_element == self.direction_buttons["south"]:
                game.clan.next_activity = "south"
                self.update_activity_buttons()
            elif event.ui_element == self.direction_buttons["west"]:
                game.clan.next_activity = "west"
                self.update_activity_buttons()
            elif event.ui_element == self.direction_buttons["bloodbath"]:
                game.clan.next_activity = None
                self.update_activity_buttons()

            for item in self.activity_buttons:
                if event.ui_element == self.activity_buttons[item]:
                    if self.open_popup != item:
                        self.open_popup = item
                    else:
                        self.open_popup = None

            if self.popup_buttons:
                for item in self.popup_buttons:
                    if event.ui_element == self.popup_buttons[item]:
                        if game.clan.next_activity != item:
                            game.clan.next_activity = item
                        else:
                            game.clan.next_activity = None
                    
            self.update_activity_buttons()

        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if event.key == pygame.K_RIGHT:
                self.change_screen("list screen")
            elif event.key == pygame.K_LEFT:
                self.change_screen("events screen")
            elif event.key == pygame.K_SPACE:
                self.save_button_saving_state.show()
                self.save_button.disable()
                game.save_cats()
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
                game.save_events()
                game.save_settings(self)
                game.switches["saved_clan"] = True
                self.update_buttons_and_text()

    def screen_switches(self):
        super().screen_switches()
        self.update_current_map()
        self.show_mute_buttons()
        game.switches["cat"] = None

        # print(game.clan.your_cat.map_position)

        # # this has to be opened before placements
        with open(f"resources/dicts/hunger_games_dicts/{(game.clan.biome).lower()}/item_dict.json", "r", encoding="utf-8") as read_file:
            self.MAP_POSITION_INFO = ujson.loads(read_file.read())

        if not (game.clan.timeskips == 1 and game.clan.days == 0):
            try:
                ACTIVITIES = None
                base_dir = 'resources/dicts/hunger_games_dicts'
                with open(f"{base_dir}/{(game.clan.biome).lower()}/activity_locations.json", "r", encoding="utf-8") as read_file:
                    ACTIVITIES = ujson.loads(read_file.read())
                self.activity_list = ACTIVITIES[game.clan.your_cat.map_position]

                # print("ACTIVITIES FOR", game.clan.your_cat.map_position, ":", self.activity_list)
                if not game.clan.your_cat.dead:
                    self.place_activity_buttons()
            except:
                print("No activity placements for", game.clan.your_cat.map_position)
                self.activity_list = {}
        else:
            self.activity_list = {}

        game.switches['cat'] = None
        if game.clan.biome + game.clan.camp_bg in game.clan.layouts:
            self.layout = game.clan.layouts[game.clan.biome + game.clan.camp_bg]
        else:
            self.layout = game.clan.layouts["default"]

        if "cat_shading" not in self.layout:
            self.layout["cat_shading"] = game.clan.layouts["default"]["cat_shading"]

        self.choose_cat_positions()

        self.set_disabled_menu_buttons(["camp_screen"])
        self.update_heading_text("The Arena")
        self.show_menu_buttons()


        self.cat_buttons = []  # To contain all the buttons.

        self.direction_buttons["north"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 100), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            tool_tip_text="Travel north",
            manager=MANAGER,
            anchors={"centerx": "centerx"}
        )
        self.direction_buttons["east"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((700, 0), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            tool_tip_text="Travel east",
            manager=MANAGER,
            anchors={"centery": "centery"}
        )
        self.direction_buttons["south"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 600), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            tool_tip_text="Travel south",
            manager=MANAGER,
            anchors={"centerx": "centerx"}
        )

        self.direction_buttons["west"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((70, 0), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            tool_tip_text="Travel west",
            manager=MANAGER,
            anchors={"centery": "centery"}
        )

        self.direction_buttons["bloodbath"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 0), (34, 34))),
            Icon.SCRATCHES,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            tool_tip_text="Partake in the bloodbath!",
            manager=MANAGER,
            anchors={"centery": "centery", "centerx": "centerx"}
        )

        # We have to convert the positions to something pygame_gui buttons will understand
        # This should be a temp solution. We should change the code that determines positions.
        i = 0
        for x in game.clan.clan_cats:
            if (
                not Cat.all_cats[x].dead
                and Cat.all_cats[x].in_camp
                and not Cat.all_cats[x].moons < 0
                and not (Cat.all_cats[x].exiled or Cat.all_cats[x].outside)
                and (
                    Cat.all_cats[x].status != "newborn"
                    or game.config["fun"]["all_cats_are_newborn"]
                    or game.config["fun"]["newborns_can_roam"]
                )
                and Cat.all_cats[x].map_position == game.clan.your_cat.map_position
            ):
                i += 1
                if i > self.max_sprites_displayed:
                    break

                try:
                    image = Cat.all_cats[x].sprite.convert_alpha()
                    blend_layer = (
                        self.game_bgs[self.active_bg]
                        .subsurface(
                            ui_scale(
                                pygame.Rect(tuple(Cat.all_cats[x].moon_placement), (50, 50))
                            )
                        )
                        .convert_alpha()
                    )
                    blend_layer = pygame.transform.box_blur(
                        blend_layer, self.layout["cat_shading"]["blur"]
                    )

                    sprite = image.copy()
                    sprite.fill(
                        (255, 255, 255, 255), special_flags=pygame.BLEND_RGB_MAX
                    )
                    sprite.blit(
                        blend_layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
                    )
                    image.set_alpha(self.layout["cat_shading"]["blend_strength"])
                    sprite.blit(image, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
                    sprite.set_alpha(255)

                    self.cat_buttons.append(
                        UISpriteButton(
                            ui_scale(
                                pygame.Rect(tuple(Cat.all_cats[x].moon_placement), (50, 50))
                            ),
                            sprite,
                            cat_id=x,
                            starting_height=i,
                        )
                    )
                except Exception as e:
                    print(
                        f"ERROR: placing {Cat.all_cats[x].name}'s sprite on Clan page"
                    )
                    print(e)

        self.save_button = UIImageButton(
            ui_scale(pygame.Rect(((343, 643), (114, 30)))),
            "",
            object_id="#save_button",
            sound_id="save",
        )
        self.save_button.enable()
        self.save_button_saved_state = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((343, 643), (114, 30))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/save_clan_saved.png"),
                ui_scale_dimensions((114, 30)),
            ),
        )
        self.save_button_saved_state.hide()
        self.save_button_saving_state = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((343, 643), (114, 30))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/save_clan_saving.png"),
                ui_scale_dimensions((114, 30)),
            ),
        )
        self.save_button_saving_state.hide()

        self.update_activity_buttons()
        self.update_buttons_and_text()

    def exit_screen(self):
        self.open_popup = None
        
        # removes the cat sprites.
        for button in self.cat_buttons:
            button.kill()
        self.cat_buttons = []

        for ele in self.platforms:
            self.platforms[ele].kill()
        self.platforms = {}

        for ele in self.direction_buttons:
            self.direction_buttons[ele].kill()
        self.direction_buttons = {}

        for ele in self.activity_buttons:
            self.activity_buttons[ele].kill()
        self.activity_buttons = {}

        for ele in self.activity_button_popups:
            self.activity_button_popups[ele].kill()
        self.activity_button_popups = {}

        for ele in self.activity_labels:
            self.activity_labels[ele].kill()
        self.activity_labels = {}

        for ele in self.popup_buttons:
            self.popup_buttons[ele].kill()
        self.popup_buttons = {}

        # Kill all other elements, and destroy the reference so they aren't hanging around
        self.save_button.kill()
        del self.save_button
        self.save_button_saved_state.kill()
        del self.save_button_saved_state
        self.save_button_saving_state.kill()
        del self.save_button_saving_state

        # reset save status
        game.switches["saved_clan"] = False

    def place_activity_buttons(self):
        """ places activity buttons on da page """
        for ele in self.activity_buttons:
            self.activity_buttons[ele].kill()
        self.activity_buttons = {}

        for ele in self.activity_button_popups:
            self.activity_button_popups[ele].kill()
        self.activity_button_popups = {}

        for ele in self.activity_labels:
            self.activity_labels[ele].kill()
        self.activity_labels = {}

        for ele in self.popup_buttons:
            self.popup_buttons[ele].kill()
        self.popup_buttons = {}

        for activity in self.activity_list.items():
            # get the right icon
            name = activity[0]
            if name in ["hunt", "fish"]:
                icon = Icon.MOUSE
            elif name == "train":
                icon = Icon.SCRATCHES
            elif "gather" in name:
                icon = Icon.HERB
            else:
                icon = Icon.CLAN_UNKNOWN
            self.activity_buttons[f"{name}"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((activity[1][0], activity[1][1]), (25, 25))),
                icon,
                get_button_dict(ButtonStyles.ICON, (25, 25)),
                object_id="@buttonstyles_icon",
            )

    def update_activity_buttons(self):
        """ updates buttons when theyre pressed """

        for ele in self.activity_button_popups:
            self.activity_button_popups[ele].kill()
        self.activity_button_popups = {}

        for ele in self.activity_labels:
            self.activity_labels[ele].kill()
        self.activity_labels = {}

        for ele in self.popup_buttons:
            self.popup_buttons[ele].kill()
        self.popup_buttons = {}
        
        for activity in self.activity_list.items():
            if self.open_popup == activity[0]:
                # open a new popup

                if not (game.clan.timeskips == 1 and game.clan.days == 0):

                    self.activity_button_popups[f"{activity[0]}"] = pygame_gui.elements.UIImage(
                        ui_scale(pygame.Rect((activity[1][0] - 19, activity[1][1] - 35), (75, 30))),
                        pygame.transform.scale(
                        image_cache.load_image("resources/images/search_bar.png"),
                        (103, 28))
                    )
                    if "gather" in activity[0]:
                        textdisplay = "Gather"
                    else:
                        textdisplay = (activity[0]).capitalize()
                    if activity[0] == game.clan.next_activity:
                        insert = f"<u><font color='#000000'>{textdisplay}</font><u>"
                        insert2 = "Cancel activity"
                    else:
                        insert = f"<font color='#000000'>{textdisplay}</font>"
                        if "gather" in activity[0]:
                            insert2 = (activity[0]).capitalize().replace('_', ' ')
                        else:
                            insert2 = None
                    
                    self.activity_labels[f"{activity[0]}"] = pygame_gui.elements.UITextBox(
                        insert,
                        ui_scale(pygame.Rect((activity[1][0] - 20, activity[1][1] - 35), (75, 30))),
                        object_id=get_text_box_theme(
                        "#text_box_22_horizcenter"),
                    )

                    if insert2:
                        self.popup_buttons[f"{activity[0]}"] = UISurfaceImageButton(
                            ui_scale(pygame.Rect((activity[1][0] - 49, activity[1][1] - 35), (30, 30))),
                            Icon.PAW,
                            get_button_dict(ButtonStyles.ICON, (30, 30)),
                            object_id="@buttonstyles_icon",
                            tool_tip_text=insert2
                        )
                    else:
                        self.popup_buttons[f"{activity[0]}"] = UISurfaceImageButton(
                            ui_scale(pygame.Rect((activity[1][0] - 49, activity[1][1] - 35), (30, 30))),
                            Icon.PAW,
                            get_button_dict(ButtonStyles.ICON, (30, 30)),
                            object_id="@buttonstyles_icon"
                        )

        directions = ["north", "east", "south", "west"]
        if game.clan.next_activity is not None:
            if game.clan.next_activity in directions:
                for i in directions:
                    self.direction_buttons[i].enable()
                self.direction_buttons[game.clan.next_activity].disable()
                for i in self.activity_buttons:
                    self.activity_buttons[i].enable()
            else:
                for i in self.direction_buttons:
                    self.direction_buttons[i].disable()
                for i in self.activity_buttons:
                    self.activity_buttons[i].disable()
                self.activity_buttons[game.clan.next_activity].enable()
        else:
            for i in self.activity_buttons:
                self.activity_buttons[i].enable()
            for i in self.direction_buttons:
                self.direction_buttons[i].enable()


        if game.clan.your_cat.sleeping is True:
            self.direction_buttons["north"].disable()
            self.direction_buttons["east"].disable()
            self.direction_buttons["south"].disable()
            self.direction_buttons["west"].disable()
            for ele in self.activity_buttons:
                self.activity_buttons[ele].disable()

    def update_current_map(self):
        camp_bg_base_dir = 'resources/images/hg_maps/'
        position = game.clan.your_cat.map_position

        time = ""
        if game.clan.timeskips in [2, 3, 4]:
            time = "day"
        elif game.clan.timeskips in [1, 5, 6, 10]:
            time = "sunset"
        else:
            time = "night"

        platform_dir = f'{camp_bg_base_dir}/{(game.clan.biome).lower()}/{time}/{position}.png'
        
        self.add_bgs(
            {
                "Newleaf": pygame.transform.scale(
                    pygame.image.load(platform_dir).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Greenleaf": pygame.transform.scale(
                    pygame.image.load(platform_dir).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Leaf-bare": pygame.transform.scale(
                    pygame.image.load(platform_dir).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Leaf-fall": pygame.transform.scale(
                    pygame.image.load(platform_dir).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
            },
            {
                "Newleaf": None,
                "Greenleaf": None,
                "Leaf-bare": None,
                "Leaf-fall": None,
            },
        )

        self.set_bg(get_current_season())

    def choose_nonoverlapping_positions(self, first_choices, dens, weights=None):
        if not weights:
            weights = [1] * len(dens)

        dens = dens.copy()

        chosen_index = random.choices(range(0, len(dens)), weights=weights, k=1)[0]
        first_chosen_den = dens[chosen_index]
        while True:
            chosen_den = dens[chosen_index]
            if first_choices[chosen_den]:
                pos = random.choice(first_choices[chosen_den])
                first_choices[chosen_den].remove(pos)
                just_pos = pos[0].copy()
                if pos not in first_choices[chosen_den]:
                    # Then this is the second cat to be places here, given an offset

                    # Offset based on the "tag" in pos[1]. If "y" is in the tag,
                    # the cat will be offset down. If "x" is in the tag, the behavior depends on
                    # the presence of the "y" tag. If "y" is not present, always shift the cat left or right
                    # if it is present, shift the cat left or right 3/4 of the time.
                    if "x" in pos[1] and ("y" not in pos[1] or random.getrandbits(2)):
                        just_pos[0] += 15 * random.choice([-1, 1])
                    if "y" in pos[1]:
                        just_pos[1] += 15
                return tuple(just_pos)
            dens.pop(chosen_index)
            weights.pop(chosen_index)
            if not dens:
                break
            # Put finding the next index after the break condition, so it won't be done unless needed
            chosen_index = random.choices(range(0, len(dens)), weights=weights, k=1)[0]

        # If this code is reached, all position are filled.  Choose any position in the first den
        # checked, apply offsets.
        pos = random.choice(self.layout[first_chosen_den])
        just_pos = pos[0].copy()
        if "x" in pos[1] and random.getrandbits(1):
            just_pos[0] += 15 * random.choice([-1, 1])
        if "y" in pos[1]:
            just_pos[1] += 15
        return tuple(just_pos)
    
    def choose_cat_positions(self):
        """Determines the positions of cat on the clan screen."""
        # These are the first choices. As positions are chosen, they are removed from the options to indicate they are
        # taken.
        first_choices = deepcopy(self.layout)

        all_dens = [
            "nursery place",
            "leader place",
            "elder place",
            "medicine place",
            "apprentice place",
            "clearing place",
            "warrior place",
        ]

        # Allow two cat in the same position.
        for x in all_dens:
            first_choices[x].extend(first_choices[x])
            
        x_radius = 250
        y_radius = 175
        center_x = 375
        center_y = 345

        num_items = 24
        angle_increment = 2 * math.pi / num_items

        for ele in self.platforms:
            self.platforms[ele].kill()
        self.platforms = {}

        if game.clan.timeskips == 1 and game.clan.days == 0:
            for i, x in enumerate(game.clan.clan_cats):
                if Cat.all_cats[x].dead or Cat.all_cats[x].outside or Cat.all_cats[x].moons <= 0:
                    continue

                angle = i * angle_increment
                item_x = center_x + x_radius * math.cos(angle)
                item_y = center_y + y_radius * math.sin(angle)

                Cat.all_cats[x].moon_placement = (item_x, item_y)

                self.platforms[x] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((item_x, item_y + 26), (50, 34))),
                    pygame.transform.scale(
                    image_cache.load_image('resources/images/hg_platform.png'),
                    (50, 34))
                )

    def update_buttons_and_text(self):
        if game.switches["saved_clan"]:
            self.save_button_saving_state.hide()
            self.save_button_saved_state.show()
            self.save_button.disable()
        else:
            self.save_button.enable()

        row_position, column_position = game.clan.your_cat.map_position.split("_")

        north, east, south, west = check_possible_directions(row_position, column_position, game.clan.your_cat)

        if not north or game.clan.your_cat.dead:
            self.direction_buttons["north"].hide()
        else:
            self.direction_buttons["north"].show()

        if not east or game.clan.your_cat.dead:
            self.direction_buttons["east"].hide()
        else:
            self.direction_buttons["east"].show()

        if not south or game.clan.your_cat.dead:
            self.direction_buttons["south"].hide()
        else:
            self.direction_buttons["south"].show()

        if not west or game.clan.your_cat.dead:
            self.direction_buttons["west"].hide()
        else:
            self.direction_buttons["west"].show()

        if game.clan.timeskips == 1 and game.clan.days == 0:
            if game.clan.next_activity is None:
                self.direction_buttons["bloodbath"].disable()
            else:
                self.direction_buttons["bloodbath"].enable()
        else:
            self.direction_buttons["bloodbath"].kill()
