import random
import traceback
from copy import deepcopy

import math
import os

import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y
from scripts.game_structure.ui_elements import UISpriteButton, UIImageButton
from scripts.game_structure.windows import SaveError
from scripts.utility import scale, check_possible_directions
from .Screens import Screens


class ClanScreen(Screens):
    max_sprites_displayed = 400  # we don't want 100,000 sprites rendering at once. 400 is enough.
    cat_buttons = []
    platforms = {}
    direction_buttons = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.show_den_labels = None
        self.show_den_text = None
        self.label_toggle = None
        self.app_den_label = None
        self.clearing_label = None
        self.nursery_label = None
        self.elder_den_label = None
        self.med_den_label = None
        self.leader_den_label = None
        self.warrior_den_label = None
        self.layout = None

    def on_use(self):
        if game.clan.clan_settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_bg, (0, 0))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_bg, (0, 0))

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.save_button:
                try:
                    self.save_button_saving_state.show()
                    self.save_button.disable()
                    game.save_cats()
                    game.clan.save_clan()
                    game.clan.save_pregnancy(game.clan)
                    game.save_events()
                    game.save_settings()
                    game.switches['saved_clan'] = True
                    self.update_buttons_and_text()
                except RuntimeError:
                    SaveError(traceback.format_exc())
                    self.change_screen("start screen")
            if event.ui_element in self.cat_buttons:
                game.switches["cat"] = event.ui_element.return_cat_id()
                self.change_screen('profile screen')
            
            if event.ui_element == self.direction_buttons["north"]:
                game.clan.next_direction = "north"
                self.update_buttons_and_text()
            elif event.ui_element == self.direction_buttons["east"]:
                game.clan.next_direction = "east"
                self.update_buttons_and_text()
            elif event.ui_element == self.direction_buttons["south"]:
                game.clan.next_direction = "south"
                self.update_buttons_and_text()
            elif event.ui_element == self.direction_buttons["west"]:
                game.clan.next_direction = "west"
                self.update_buttons_and_text()
            elif event.ui_element == self.direction_buttons["bloodbath"]:
                game.clan.next_direction = None
                self.update_buttons_and_text()
            if event.ui_element == self.label_toggle:
                if game.clan.clan_settings['den labels']:
                    game.clan.clan_settings['den labels'] = False
                else:
                    game.clan.clan_settings['den labels'] = True
                self.update_buttons_and_text()
            if event.ui_element == self.med_den_label:
                self.change_screen('med den screen')
            else:
                self.menu_button_pressed(event)
            if event.ui_element == self.clearing_label:
                self.change_screen('clearing screen')
            else:
                self.menu_button_pressed(event)
            if event.ui_element == self.warrior_den_label:
                self.change_screen('warrior den screen')
            if event.ui_element == self.leader_den_label:
                self.change_screen('leader den screen')

        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_RIGHT:
                self.change_screen('list screen')
            elif event.key == pygame.K_LEFT:
                self.change_screen('events screen')
            elif event.key == pygame.K_SPACE:
                self.save_button_saving_state.show()
                self.save_button.disable()
                game.save_cats()
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
                game.save_events()
                game.save_settings()
                game.switches['saved_clan'] = True
                self.update_buttons_and_text()

    def screen_switches(self):
        self.update_current_map()
        game.switches['cat'] = None
        if game.clan.biome + game.clan.camp_bg in game.clan.layouts:
            self.layout = game.clan.layouts[game.clan.biome + game.clan.camp_bg]
        else:
            self.layout = game.clan.layouts["default"]
        self.choose_cat_positions()

        self.set_disabled_menu_buttons(["camp_screen"])
        self.update_heading_text('The Arena')
        self.show_menu_buttons()

        self.cat_buttons = []  # To contain all the buttons.

        self.direction_buttons["north"] = UIImageButton(scale(pygame.Rect(
            (760, 200), (70, 70))),
            "^",
            tool_tip_text="Travel north",
            object_id="",
            starting_height=2
        )
        self.direction_buttons["east"] = UIImageButton(scale(pygame.Rect(
            (1400, 710), (70, 70))),
            ">",
            tool_tip_text="Travel east",
            object_id="",
            starting_height=2
        )
        self.direction_buttons["south"] = UIImageButton(scale(pygame.Rect(
            (770, 1200), (70, 70))),
            "v",
            tool_tip_text="Travel south",
            object_id="",
            starting_height=2
        )
        self.direction_buttons["west"] = UIImageButton(scale(pygame.Rect(
            (140, 710), (70, 70))),
            "<",
            tool_tip_text="Travel west",
            object_id="",
            starting_height=2
        )
        self.direction_buttons["bloodbath"] = UIImageButton(scale(pygame.Rect(
            (760, 710), (70, 70))),
            "X",
            tool_tip_text="Join the bloodbath",
            object_id="",
            starting_height=2
        )

        self.direction_buttons["north"].enable()
        self.direction_buttons["east"].enable()
        self.direction_buttons["south"].enable()
        self.direction_buttons["west"].enable()

        # We have to convert the positions to something pygame_gui buttons will understand
        # This should be a temp solution. We should change the code that determines positions.
        i = 0
        for x in game.clan.clan_cats:
            if Cat.all_cats[x].moons != -1 and not Cat.all_cats[x].dead and Cat.all_cats[x].in_camp and \
                    not (Cat.all_cats[x].exiled or Cat.all_cats[x].outside) and (Cat.all_cats[x].status != 'newborn' or game.config['fun']['all_cats_are_newborn'] or game.config['fun']['newborns_can_roam']) and Cat.all_cats[x].map_position == game.clan.your_cat.map_position:

                i += 1
                if i > self.max_sprites_displayed:
                    break

                try:
                    self.cat_buttons.append(
                        UISpriteButton(scale(pygame.Rect(tuple(Cat.all_cats[x].placement), (100, 100))),
                                       Cat.all_cats[x].sprite,
                                       cat_id=x,
                                       starting_height=i)
                    )
                except:
                    print(f"ERROR: placing {Cat.all_cats[x].name}\'s sprite on Clan page")

        # Den Labels
        # Redo the locations, so that it uses layout on the Clan page
        self.warrior_den_label = UIImageButton(scale(pygame.Rect(
            self.layout["warrior den"], (242, 56))),
            "",
            object_id="#warrior_den_button",
            starting_height=2
        )
        self.leader_den_label = UIImageButton(
            scale(pygame.Rect(self.layout["leader den"], (224, 56))),
            "",
            object_id="#lead_den_button",
            starting_height=2
            )
        self.med_den_label = UIImageButton(
            scale(pygame.Rect(self.layout["medicine den"], (302, 56))),
            "",
            object_id="#med_den_button",
            starting_height=2
        )
        self.elder_den_label = pygame_gui.elements.UIImage(
            scale(pygame.Rect(self.layout["elder den"], (206, 56))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/elder_den.png'),
                (206, 56)),
        )
        self.nursery_label = pygame_gui.elements.UIImage(scale(pygame.Rect(self.layout['nursery'], (160, 56))),
                                                        pygame.transform.scale(
                                                            image_cache.load_image('resources/images/nursery_den.png'),
                                                            (160, 56)))
        if game.clan.game_mode == 'classic':
            self.clearing_label = pygame_gui.elements.UIImage(
                scale(pygame.Rect(self.layout['clearing'], (162, 56))),
                pygame.transform.scale(
                    image_cache.load_image('resources/images/buttons/clearing.png'),
                    (162, 56)))
        else:
            self.clearing_label = UIImageButton(scale(pygame.Rect(
                self.layout['clearing'], (162, 56))),
                "",
                object_id="#clearing_button",
                starting_height=2
            )
        self.app_den_label = pygame_gui.elements.UIImage(
            scale(pygame.Rect(self.layout['apprentice den'], (294, 56))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/app_den.png'),
                (294, 56)))

        # Draw the toggle and text
        self.show_den_labels = pygame_gui.elements.UIImage(scale(pygame.Rect((50, 1282), (334, 68))),
                                                           pygame.transform.scale(
                                                               image_cache.load_image(
                                                                   'resources/images/show_den_labels.png'),
                                                               (334, 68)))
        
        # HUNGER GAMES: no den labels!!!
        # self.show_den_labels.disable()
        self.show_den_labels.hide()
        self.label_toggle = UIImageButton(scale(pygame.Rect((50, 1282), (64, 64))), "", object_id="#checked_checkbox")
        self.label_toggle.hide()

        self.save_button = UIImageButton(scale(pygame.Rect(((686, 1286), (228, 60)))), "", object_id="#save_button")
        self.save_button.enable()
        self.save_button_saved_state = pygame_gui.elements.UIImage(
            scale(pygame.Rect((686, 1286), (228, 60))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/save_clan_saved.png'),
                (228, 60)))
        self.save_button_saved_state.hide()
        self.save_button_saving_state = pygame_gui.elements.UIImage(
            scale(pygame.Rect((686, 1286), (228, 60))),
            pygame.transform.scale(
                image_cache.load_image('resources/images/save_clan_saving.png'),
                (228, 60)))
        self.save_button_saving_state.hide()

        self.update_buttons_and_text()

    def exit_screen(self):
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

        # Kill all other elements, and destroy the reference so they aren't hanging around
        self.save_button.kill()
        del self.save_button
        self.save_button_saved_state.kill()
        del self.save_button_saved_state
        self.save_button_saving_state.kill()
        del self.save_button_saving_state
        self.warrior_den_label.kill()
        del self.warrior_den_label
        self.leader_den_label.kill()
        del self.leader_den_label
        self.med_den_label.kill()
        del self.med_den_label
        self.elder_den_label.kill()
        del self.elder_den_label
        self.nursery_label.kill()
        del self.nursery_label
        self.clearing_label.kill()
        del self.clearing_label
        self.app_den_label.kill()
        del self.app_den_label
        self.label_toggle.kill()
        del self.label_toggle
        self.show_den_labels.kill()
        del self.show_den_labels

        # reset save status
        game.switches['saved_clan'] = False

    def update_current_map(self):

        camp_bg_base_dir = 'resources/images/hg_maps/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        position = game.clan.your_cat.map_position

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome
        if biome not in available_biome:
            biome = available_biome[0]
            game.clan.biome = biome
        biome = biome.lower()

        all_backgrounds = []
        for leaf in leaves:
            platform_dir = f'{camp_bg_base_dir}/{biome}/{leaf}_{position}.png'
            all_backgrounds.append(platform_dir)

        self.newleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[0]).convert(), (screen_x, screen_y))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (screen_x, screen_y))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (screen_x, screen_y))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (screen_x, screen_y))

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

        all_dens = ["nursery place", "leader place", "elder place", "medicine place", "apprentice place",
                    "clearing place", "warrior place"]

        # Allow two cat in the same position.
        for x in all_dens:
            first_choices[x].extend(first_choices[x])
            
        x_radius = 500
        y_radius = 350
        center_x = 750
        center_y = 690

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

                Cat.all_cats[x].placement = (item_x, item_y)

                self.platforms[x] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((item_x, item_y + 55), (100, 60))),
                    pygame.transform.scale(
                    image_cache.load_image('resources/images/buttons/fav_marker.png'),
                    (206, 56))
                )

        else:
            for x in game.clan.clan_cats:
                Cat.all_cats[x].placement = None

                if Cat.all_cats[x].dead or Cat.all_cats[x].outside or Cat.all_cats[x].moons <= 0:
                    continue
                if Cat.all_cats[x].map_position != game.clan.your_cat.map_position:
                    continue
                
                if Cat.all_cats[x].ID == game.clan.your_cat.ID:
                    Cat.all_cats[x].placement = (775, 675)

                else:
                    if Cat.all_cats[x].status == 'newborn' or Cat.all_cats[x].moons == -1 or game.config['fun']['all_cats_are_newborn']:
                        if game.config['fun']['all_cats_are_newborn'] or game.config['fun']['newborns_can_roam']:
                            # Free them
                            Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                            [1, 100, 1, 1, 1, 100, 50])
                        else:
                            continue
        
                    if Cat.all_cats[x].status in ['apprentice', 'mediator apprentice', "queen's apprentice"]:
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [1, 50, 1, 1, 100, 100, 1])
                    elif Cat.all_cats[x].status == 'deputy':
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [1, 50, 1, 1, 1, 50, 1])

                    elif Cat.all_cats[x].status == 'elder':
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [1, 1, 2000, 1, 1, 1, 1])
                    elif Cat.all_cats[x].status == 'kitten':
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [60, 8, 1, 1, 1, 1, 1])
                    elif Cat.all_cats[x].status == 'queen':
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [60, 8, 1, 1, 1, 1, 1])
                    elif Cat.all_cats[x].status == "queen's apprentice":
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [60, 8, 1, 1, 1, 1, 1])                                                                     
                    elif Cat.all_cats[x].status in [
                        'medicine cat apprentice', 'medicine cat'
                    ]:
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [20, 20, 20, 400, 1, 1, 1])
                    elif Cat.all_cats[x].status in ['warrior', 'mediator']:
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [1, 1, 1, 1, 1, 60, 60])
                    elif Cat.all_cats[x].status == "leader":
                        Cat.all_cats[x].placement = self.choose_nonoverlapping_positions(first_choices, all_dens,
                                                                                        [1, 200, 1, 1, 1, 1, 1])

    def update_buttons_and_text(self):
        if game.switches['saved_clan']:
            self.save_button_saving_state.hide()
            self.save_button_saved_state.show()
            self.save_button.disable()
        else:
            self.save_button.enable()

        self.label_toggle.kill()
        if game.clan.clan_settings['den labels']:
            self.label_toggle = UIImageButton(scale(pygame.Rect((50, 1282), (68, 68))), "", starting_height=2,
                                              object_id="#checked_checkbox")
            self.label_toggle.hide()
            self.warrior_den_label.show()
            self.clearing_label.show()
            self.nursery_label.show()
            self.app_den_label.show()
            self.leader_den_label.show()
            self.med_den_label.show()
            self.elder_den_label.show()
        else:
            self.label_toggle = UIImageButton(scale(pygame.Rect((50, 1282), (68, 68))), "", starting_height=2,
                                              object_id="#unchecked_checkbox")
            self.label_toggle.hide()
            self.warrior_den_label.hide()
            self.clearing_label.hide()
            self.nursery_label.hide()
            self.app_den_label.hide()
            self.leader_den_label.hide()
            self.med_den_label.hide()
            self.elder_den_label.hide()
        
        row_position, column_position = game.clan.your_cat.map_position.split("_")

        north, east, south, west = check_possible_directions(row_position, column_position)

        if not north:
            self.direction_buttons["north"].hide()
        else:
            self.direction_buttons["north"].show()

        if not east:
            self.direction_buttons["east"].hide()
        else:
            self.direction_buttons["east"].show()

        if not south:
            self.direction_buttons["south"].hide()
        else:
            self.direction_buttons["south"].show()

        if not west:
            self.direction_buttons["west"].hide()
        else:
            self.direction_buttons["west"].show()


        directions = ["north", "east", "south", "west"]
        for x in directions:
            if game.clan.next_direction == x:
                self.direction_buttons[x].disable()
            else:
                self.direction_buttons[x].enable()
        
        if game.clan.timeskips == 1 and game.clan.days == 0:
            if game.clan.next_direction is None:
                self.direction_buttons["bloodbath"].disable()
            else:
                self.direction_buttons["bloodbath"].enable()
        else:
            self.direction_buttons["bloodbath"].kill()
