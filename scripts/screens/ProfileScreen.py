#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
from random import choice, randint

import pygame

from ..cat.history import History
from ..housekeeping.datadir import get_save_dir
from ..game_structure.windows import ChangeCatName, KillCat, ChangeCatToggles
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events

import ujson

from scripts.utility import event_text_adjust, ACC_DISPLAY, process_text, chunks, get_cluster

from .Screens import Screens

from scripts.utility import get_text_box_theme, shorten_text_to_fit, clan_symbol_sprite
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.game_structure import image_cache
import pygame_gui
from re import sub
from scripts.cat.skills import SkillPath

import math
from scripts.cat.sprites import sprites
from scripts.game_structure.game_essentials import game
from random import choice
from re import sub

import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.clan_resources.freshkill import FRESHKILL_ACTIVE
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UITextBoxTweaked,
    UISurfaceImageButton,
)
from scripts.utility import (
    event_text_adjust,
    ui_scale,
    ACC_DISPLAY,
    process_text,
    chunks,
    get_text_box_theme,
    ui_scale_dimensions,
    shorten_text_to_fit,
    ui_scale_offset,
    adjust_list_text,
    pronoun_repl,
)
from .Screens import Screens
from ..cat.history import History
from ..game_structure.screen_settings import MANAGER
from ..game_structure.windows import ChangeCatName, KillCat, ChangeCatToggles
from ..housekeeping.datadir import get_save_dir
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import ButtonStyles, get_button_dict
from ..ui.get_arrow import get_arrow
from ..ui.icon import Icon

from scripts.clan import ITEM_VALUES, HERBS

resource_directory = "resources/dicts/conditions/"
ILLNESSES = None
with open(f"{resource_directory}illnesses.json", "r") as read_file:
    ILLNESSES = ujson.loads(read_file.read())

INJURIES = None
with open(f"{resource_directory}injuries.json", "r") as read_file:
    INJURIES = ujson.loads(read_file.read())

# ---------------------------------------------------------------------------- #
#             change how accessory info displays on cat profiles               #
# ---------------------------------------------------------------------------- #
def accessory_display_name(cat):
    accessory = cat.pelt.accessory

    if accessory is None:
        return ""
    acc_display = accessory.lower()

    if accessory in Pelt.collars:
        collar_colors = {
            "crimson": "red",
            "blue": "blue",
            "yellow": "yellow",
            "cyan": "cyan",
            "red": "orange",
            "lime": "lime",
            "green": "green",
            "rainbow": "rainbow",
            "black": "black",
            "spikes": "spiky",
            "white": "white",
            "pink": "pink",
            "purple": "purple",
            "multi": "multi",
            "indigo": "indigo",
        }
        collar_color = next(
            (color for color in collar_colors if acc_display.startswith(color)), None
        )

        if collar_color:
            if acc_display.endswith("bow") and not collar_color == "rainbow":
                acc_display = collar_colors[collar_color] + " bow"
            elif acc_display.endswith("bell"):
                acc_display = collar_colors[collar_color] + " bell collar"
            else:
                acc_display = collar_colors[collar_color] + " collar"

    elif accessory in Pelt.wild_accessories:
        if acc_display == "blue feathers":
            acc_display = "crow feathers"
        elif acc_display == "red feathers":
            acc_display = "cardinal feathers"

    return acc_display


# ---------------------------------------------------------------------------- #
#               assigns backstory blurbs to the backstory                      #
# ---------------------------------------------------------------------------- #
def bs_blurb_text(cat):
    backstory = cat.backstory
    backstory_text = BACKSTORIES["backstories"][backstory]

    if cat.status in ["kittypet", "loner", "rogue", "former Clancat"]:
        return f"This cat is a {cat.status} and currently resides outside of the Clans."

    return backstory_text


# ---------------------------------------------------------------------------- #
#             change how backstory info displays on cat profiles               #
# ---------------------------------------------------------------------------- #
def backstory_text(cat):
    backstory = cat.backstory
    if backstory is None:
        return ""
    bs_category = None

    for category in BACKSTORIES["backstory_categories"]:
        if backstory in category:
            bs_category = category
            break
    bs_display = BACKSTORIES["backstory_display"][bs_category]

    return bs_display


# ---------------------------------------------------------------------------- #
#                               Profile Screen                                 #
# ---------------------------------------------------------------------------- #
class ProfileScreen(Screens):
    # UI Images
    lvl3_inventory_tab = image_cache.load_image(
        "resources/images/lvl3_inventory_bg.png"
    ).convert_alpha()
    conditions_tab = image_cache.load_image(
        "resources/images/conditions_tab_backdrop.png"
    ).convert_alpha()

    # Keep track of current tabs open. Can be used to keep tabs open when pages are switched, and
    # helps with exiting the screen
    open_tab = None

    def __init__(self, name=None):
        super().__init__(name)
        self.condition_data = {}
        self.show_moons = None
        self.no_moons = None
        self.help_button = None
        self.open_sub_tab = None
        self.editing_notes = False
        self.user_notes = None
        self.save_text = None
        self.not_fav_tab = None
        self.fav_tab = None
        self.edit_text = None
        self.sub_tab_4 = None
        self.sub_tab_3 = None
        self.sub_tab_2 = None
        self.sub_tab_1 = None
        self.backstory_background = None
        self.history_text_box = None
        self.conditions_tab_button = None
        self.condition_container = None
        self.left_conditions_arrow = None
        self.right_conditions_arrow = None
        self.conditions_background = None
        self.previous_cat = None
        self.next_cat = None
        self.cat_image = None
        self.background = None
        self.cat_info_column2 = None
        self.cat_info_column1 = None
        self.cat_thought = None
        self.cat_name = None
        self.placeholder_tab_4 = None
        self.placeholder_tab_3 = None
        self.placeholder_tab_2 = None
        self.faith_bar = None
        self.your_tab = None
        self.backstory_tab_button = None
        self.dangerous_tab_button = None
        self.personal_tab_button = None
        self.roles_tab_button = None
        self.relations_tab_button = None
        self.back_button = None
        self.previous_cat_button = None
        self.next_cat_button = None
        self.the_cat = None
        self.prevent_fading_text = None
        self.checkboxes = {}
        self.profile_elements = {}
        self.join_df_button = None
        self.exit_df_button = None
        self.accessories_tab_button = None
        self.page = 0
        self.max_pages = 1
        self.delete_accessory = None
        self.search_bar_image = None
        self.search_bar = None
        self.previous_page_button = None
        self.next_page_button = None
        self.accessory_tab_button = None
        self.previous_search_text = "search"
        self.cat_list_buttons = None
        self.search_inventory = []
        self.faith_text = None
        self.item_window_elements = {}

        self.selected_item = None

        # stat bars!
        self.stat_elements = {}

        # LG: all accs
        self.cat_inventory = []

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:

            if game.switches["window_open"]:
                pass
            elif event.ui_element == self.back_button:
                self.close_current_tab()
                self.change_screen(game.last_screen_forProfile)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat) and Cat.fetch_cat(self.previous_cat).moons >= 0:
                    self.selected_item = None
                    self.clear_profile()
                    game.switches["cat"] = self.previous_cat
                    self.build_profile()
                    self.page = 0
                    if self.previous_page_button:

                        inventory_len = 0
                        if self.search_bar.get_text() in ["", "search"]:
                            inventory_len = len(self.the_cat.pelt.inventory.keys())
                        else:
                            for ac in self.the_cat.pelt.inventory.keys():
                                if self.search_bar.get_text().lower() in ac.lower():
                                    inventory_len+=1
                        self.max_pages = math.ceil(inventory_len/18)
                        if self.page == 0 and self.max_pages == 1:
                            self.previous_page_button.disable()
                            self.next_page_button.disable()
                        elif self.page == 0:
                            self.previous_page_button.disable()
                            self.next_page_button.enable()
                        elif self.page == self.max_pages - 1:
                            self.previous_page_button.enable()
                            self.next_page_button.disable()
                        else:
                            self.previous_page_button.enable()
                            self.next_page_button.enable()
                    self.update_disabled_buttons_and_text()
                    if self.open_tab == 'accessories':
                        self.close_current_tab()
                        self.toggle_accessories_tab()
                        # need to do this for the inventory BG to update
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat) and Cat.fetch_cat(self.next_cat).moons >= 0:
                    self.selected_item = None
                    self.clear_profile()
                    game.switches["cat"] = self.next_cat
                    self.build_profile()
                    self.inventory_item_options()
                    self.page = 0
                    if self.previous_page_button:
                        self.previous_page_button.enable()
                        self.next_page_button.enable()
                        inventory_len = 0
                        if self.search_bar.get_text() in ["", "search"]:
                            inventory_len = len(self.the_cat.pelt.inventory.keys())
                        else:
                            for ac in self.the_cat.pelt.inventory.keys():
                                if self.search_bar.get_text().lower() in ac.lower():
                                    inventory_len+=1
                        self.max_pages = math.ceil(inventory_len/18)
                        if self.page == 0 and (self.max_pages == 1 or self.max_pages == 0):
                            self.previous_page_button.disable()
                            self.next_page_button.disable()
                        elif self.page == 0:
                            self.previous_page_button.disable()
                            self.next_page_button.enable()
                        elif self.page == self.max_pages - 1:
                            self.previous_page_button.enable()
                            self.next_page_button.disable()
                        else:
                            self.previous_page_button.enable()
                            self.next_page_button.enable()
                    self.update_disabled_buttons_and_text()
                    if self.open_tab == 'accessories':
                        self.close_current_tab()
                        self.toggle_accessories_tab()
                        # need to do this for the inventory BG to update
                else:
                    print("invalid next cat", self.previous_cat)
            elif event.ui_element == self.inspect_button:
                self.close_current_tab()
                self.change_screen("sprite inspect screen")
            elif (
                self.the_cat.ID == game.clan.your_cat.ID and
                "sleep" in self.profile_elements and
                event.ui_element == self.profile_elements["sleep"]):
                if game.clan.your_cat.sleeping:
                    game.clan.your_cat.sleeping = False
                else:
                    game.clan.your_cat.sleeping = True
                self.clear_profile()
                self.build_profile()
            elif event.ui_element == self.relations_tab_button:
                self.toggle_relations_tab()
                self.selected_item = None
            elif event.ui_element == self.roles_tab_button:
                self.toggle_roles_tab()
                self.selected_item = None
            elif event.ui_element == self.personal_tab_button:
                self.toggle_personal_tab()
                self.selected_item = None
            elif event.ui_element == self.your_tab:
                self.toggle_your_tab()
                self.selected_item = None
            elif event.ui_element == self.dangerous_tab_button:
                self.toggle_dangerous_tab()
                self.selected_item = None
            elif event.ui_element == self.backstory_tab_button:
                if self.open_sub_tab is None:
                    if game.switches["favorite_sub_tab"] is None:
                        self.open_sub_tab = "life events"
                    else:
                        self.open_sub_tab = game.switches["favorite_sub_tab"]

                self.toggle_history_tab()
            elif event.ui_element == self.conditions_tab_button:
                self.toggle_conditions_tab()
            elif event.ui_element == self.accessories_tab_button:
                self.toggle_accessories_tab()
            elif event.ui_element == self.placeholder_tab_3:
                self.toggle_faith_tab()
            elif event.ui_element == self.previous_page_button:
                if self.page > 0:
                    self.page -= 1
                if self.page == 0:
                    self.previous_page_button.disable()
                    self.next_page_button.enable()
                elif self.page == self.max_pages - 1:
                    self.previous_page_button.enable()
                    self.next_page_button.disable()
                else:
                    self.previous_page_button.enable()
                    self.next_page_button.enable()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.next_page_button:
                if self.page < self.max_pages - 1:
                    self.page += 1

                if self.page == 0 and (self.max_pages == 1 or self.max_pages == 0):
                    self.previous_page_button.disable()
                    self.next_page_button.disable()
                elif self.page == 0:
                    self.previous_page_button.disable()
                    self.next_page_button.enable()
                elif self.page == self.max_pages - 1:
                    self.previous_page_button.enable()
                    self.next_page_button.disable()
                else:
                    self.previous_page_button.enable()
                    self.next_page_button.enable()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.delete_accessory:
                for acc in self.the_cat.pelt.accessories:
                    self.the_cat.pelt.inventory.pop(acc)
                    self.the_cat.pelt.accessories.remove(acc)
                self.close_current_tab()
                self.clear_profile()
                self.build_profile()
                self.toggle_accessories_tab()
            elif "leader_ceremony" in self.profile_elements and \
                    event.ui_element == self.profile_elements["leader_ceremony"]:
                self.change_screen('ceremony screen')
            elif "talk" in self.profile_elements and \
                    event.ui_element == self.profile_elements["talk"]:
                self.close_current_tab()
                self.the_cat.talked_to = True
                game.switches["talk_category"] = "talk"
                self.change_screen('talk screen')
            elif (
                "attack" in self.profile_elements and
                event.ui_element == self.profile_elements["attack"]
                ):
                if game.clan.your_cat.dead:
                    game.clan.spectating = self.the_cat
                    game.clan.your_cat.map_position = game.clan.spectating.map_position
                    self.clear_profile()
                    self.build_profile()
                else:
                    self.change_screen("attack screen")
            elif event.ui_element == self.profile_elements["favourite_button"]:
                if self.the_cat.favourite == 3:
                    self.the_cat.favourite = 0
                else:
                    self.the_cat.favourite += 1
                self.clear_profile()
                self.build_profile()
            elif self.selected_item and event.ui_element == self.item_window_elements["eat_button"]:
                if self.selected_item in HERBS:
                    self.use_herb()
                elif self.selected_item in ITEM_VALUES[game.clan.biome]:
                    self.eat()
                else:
                    if self.selected_item in self.the_cat.pelt.accessories:
                        self.the_cat.pelt.accessories.remove(self.selected_item)
                    else:
                        self.the_cat.pelt.accessories.append(self.selected_item)
                self.clear_profile()
                self.build_profile()
            elif self.selected_item and event.ui_element == self.item_window_elements["discard"]:
                self.the_cat.pelt.inventory.pop(self.selected_item)
                if self.selected_item in self.the_cat.pelt.accessories:
                    self.the_cat.pelt.accessories.remove(self.selected_item)
                self.selected_item = None
                self.clear_profile()
                self.build_profile()
                self.close_current_tab()
                self.toggle_accessories_tab()
            else:
                self.handle_tab_events(event)

        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if event.key == pygame.K_LEFT:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat) and Cat.fetch_cat(self.previous_cat).moons >= 0:
                    self.clear_profile()
                    game.switches["cat"] = self.previous_cat
                    self.build_profile()
                    self.update_disabled_buttons_and_text()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.key == pygame.K_RIGHT:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat) and Cat.fetch_cat(self.next_cat).moons >= 0:
                    self.clear_profile()
                    game.switches["cat"] = self.next_cat
                    self.build_profile()
                    self.update_disabled_buttons_and_text()
                else:
                    print("invalid next cat", self.previous_cat)

            elif event.key == pygame.K_ESCAPE:
                self.close_current_tab()
                self.change_screen(game.last_screen_forProfile)

    def handle_tab_events(self, event):
        # Relations Tab
        if self.open_tab == "relations":
            if event.ui_element == self.family_tree_button:
                self.change_screen("family tree screen")
            elif event.ui_element == self.see_relationships_button:
                self.change_screen("relationship screen")
            elif event.ui_element == self.choose_mate_button:
                self.change_screen("choose mate screen")
            elif event.ui_element == self.change_adoptive_parent_button:
                self.change_screen("choose adoptive parent screen")

        # Roles Tab
        elif self.open_tab == "roles":
            if event.ui_element == self.manage_roles:
                self.change_screen("role screen")
            elif event.ui_element == self.change_mentor_button:
                self.change_screen("choose mentor screen")
        # Personal Tab
        elif self.open_tab == "personal":
            if event.ui_element == self.change_name_button:
                ChangeCatName(self.the_cat)
            elif event.ui_element == self.specify_gender_button:
                self.change_screen("change gender screen")
            # when button is pressed...
            elif event.ui_element == self.cis_trans_button:
                # if the cat is anything besides m/f/transm/transf then turn them back to cis
                if self.the_cat.genderalign not in [
                    "female",
                    "trans female",
                    "male",
                    "trans male",
                ]:
                    self.the_cat.genderalign = self.the_cat.gender
                elif (
                    self.the_cat.gender == "male"
                    and self.the_cat.genderalign == "female"
                ):
                    self.the_cat.genderalign = self.the_cat.gender
                elif (
                    self.the_cat.gender == "female"
                    and self.the_cat.genderalign == "male"
                ):
                    self.the_cat.genderalign = self.the_cat.gender

                # if the cat is cis (gender & gender align are the same) then set them to trans
                # cis males -> trans female first
                elif (
                    self.the_cat.gender == "male" and self.the_cat.genderalign == "male"
                ):
                    self.the_cat.genderalign = "trans female"
                # cis females -> trans male
                elif (
                    self.the_cat.gender == "female"
                    and self.the_cat.genderalign == "female"
                ):
                    self.the_cat.genderalign = "trans male"
                # if the cat is trans then set them to nonbinary
                elif self.the_cat.genderalign in ["trans female", "trans male"]:
                    self.the_cat.genderalign = "nonbinary"
                # pronoun handler
                if self.the_cat.genderalign in ["female", "trans female"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[1].copy()]
                elif self.the_cat.genderalign in ["male", "trans male"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[2].copy()]
                elif self.the_cat.genderalign in ["nonbinary"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[0].copy()]
                elif self.the_cat.genderalign not in [
                    "female",
                    "trans female",
                    "male",
                    "trans male",
                ]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[0].copy()]
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.cat_toggles_button:
                ChangeCatToggles(self.the_cat)
        elif self.open_tab == 'your tab':
            if event.ui_element == self.have_kits_button:
                if 'have kits' not in game.switches:
                    game.switches['have kits'] = True
                if game.switches.get('have kits'):
                    game.clan.your_cat.no_kits = False
                    relation = Pregnancy_Events()
                    relation.handle_having_kits(game.clan.your_cat, game.clan)
                    game.switches['have kits'] = False
                    self.have_kits_button.disable()
            elif event.ui_element == self.request_apprentice_button:
                if 'request apprentice' not in game.switches:
                    game.switches['request apprentice'] = False
                if not game.switches['request apprentice']:
                    game.switches['request apprentice'] = True
                    self.request_apprentice_button.disable()
            elif event.ui_element == self.gift_accessory_button:
                self.change_screen("gift screen")
            elif event.ui_element == self.your_faith_button:
                self.toggle_faith_tab()
        # Dangerous Tab
        elif self.open_tab == "dangerous":
            
           
           
                if self.the_cat.dead:
                #     elif self.the_cat.dead:
                # if not self.the_cat.outside and not self.the_cat.df:
                #     object_id = "#exile_df_button"
                # elif self.the_cat.df and not self.the_cat.outside:
                #     object_id = "#send_ur_button"
                # else:
                #     object_id = "#guide_sc_button"
                    if self.the_cat.ID != game.clan.instructor.ID and self.the_cat.ID != game.clan.demon.ID:
                        if event.ui_object_id == "#guide_sc_button":
                            self.the_cat.outside, self.the_cat.exiled = False, False
                            self.the_cat.df = False
                            game.clan.add_to_starclan(self.the_cat)
                            self.the_cat.thought = "Is relieved to once again hunt in StarClan"
                        elif event.ui_object_id == "#exile_df_button":
                            self.the_cat.outside, self.the_cat.exiled = False, False
                            self.the_cat.df = True
                            game.clan.add_to_darkforest(self.the_cat)
                            self.the_cat.thought = "Is distraught after being sent to the Place of No Stars"
                        elif event.ui_object_id == "#send_ur_button":
                            self.the_cat.outside, self.the_cat.exiled = True, False
                            self.the_cat.df = False
                            game.clan.add_to_unknown(self.the_cat)
                            self.the_cat.thought = "Is wandering the Unknown Residence"


                    if self.the_cat.ID == game.clan.demon.ID and game.clan.followingsc == True:
                        game.clan.followingsc = False
                        for i in game.clan.clan_cats:
                            clan_cat = Cat.fetch_cat(i)
                            if clan_cat:
                                clan_cat.faith-=1

                    elif self.the_cat.ID == game.clan.instructor.ID and not game.clan.followingsc:
                        game.clan.followingsc = True
                        for i in game.clan.clan_cats:
                            clan_cat = Cat.fetch_cat(i)
                            if clan_cat:
                                clan_cat.faith+=1

                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
        # History Tab
        elif self.open_tab == "history":
            if event.ui_element == self.sub_tab_1:
                if self.open_sub_tab == "user notes":
                    self.notes_entry.kill()
                    self.display_notes.kill()
                    if self.edit_text:
                        self.edit_text.kill()
                    if self.save_text:
                        self.save_text.kill()
                    self.help_button.kill()
                self.open_sub_tab = "life events"
                self.toggle_history_sub_tab()
            elif event.ui_element == self.sub_tab_2:
                if self.open_sub_tab == "life events":
                    self.history_text_box.kill()
                self.open_sub_tab = "user notes"
                self.toggle_history_sub_tab()
            elif event.ui_element == self.fav_tab:
                game.switches["favorite_sub_tab"] = None
                self.fav_tab.hide()
                self.not_fav_tab.show()
            elif event.ui_element == self.not_fav_tab:
                game.switches["favorite_sub_tab"] = self.open_sub_tab
                self.fav_tab.show()
                self.not_fav_tab.hide()
            elif event.ui_element == self.save_text:
                self.user_notes = sub(
                    r"[^A-Za-z0-9<->/.()*'&#!?,| _+=@~:;[]{}%$^`]+",
                    "",
                    self.notes_entry.get_text(),
                )
                self.save_user_notes()
                self.editing_notes = False
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.edit_text:
                self.editing_notes = True
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.no_moons:
                game.switches["show_history_moons"] = True
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.show_moons:
                game.switches["show_history_moons"] = False
                self.update_disabled_buttons_and_text()

        # Conditions Tab
        elif self.open_tab == "conditions":
            if event.ui_element == self.right_conditions_arrow:
                self.conditions_page += 1
                self.display_conditions_page()
            if event.ui_element == self.left_conditions_arrow:
                self.conditions_page -= 1
                self.display_conditions_page()

        elif self.open_tab == 'accessories':
            b_data = event.ui_element.blit_data[1]
            inventory_blit_data = []
            pos_x = 10
            pos_y = 125
            i = 0
            cat = self.the_cat
            age = cat.age

            for b in self.inventory_buttons.values():
                inventory_blit_data.append(b.blit_data[1])
            
            if b_data in inventory_blit_data:
                if b_data in inventory_blit_data:
                    value = inventory_blit_data.index(b_data)
                n = value
                if b_data in inventory_blit_data:
                    # if self.the_cat.ID == game.clan.your_cat.ID:
                    if self.inventory_items_list[n] != self.selected_item:
                        self.selected_item = self.inventory_items_list[n]
                    elif self.inventory_items_list[n] == self.selected_item:
                        self.selected_item = None
                    self.inventory_item_options()

                for acc in self.inventory_buttons:
                    self.inventory_buttons[acc].kill()
                for acc in self.inventory_items:
                    self.inventory_items[acc].kill()
                for acc in self.cat_list_buttons:
                    self.cat_list_buttons[acc].kill()

                start_index = self.page * 18
                end_index = start_index + 18

                if self.search_bar.get_text() in ["", "search"]:
                    inventory_len = len(cat.pelt.inventory.keys())
                    new_inv = cat.pelt.inventory
                else:
                    for ac in cat.pelt.inventory.keys():
                        if ac and self.search_bar.get_text() and self.search_bar.get_text().lower() in ac.lower():
                            inventory_len+=1
                            new_inv.append(ac)
               
                self.max_pages = math.ceil(inventory_len/18)
                if (self.max_pages == 1 or self.max_pages == 0):
                    self.previous_page_button.disable()
                    self.next_page_button.disable()
                if self.page == 0:
                    self.previous_page_button.disable()
                if cat.pelt.inventory:
                    # new_inv = list(new_inv.items())
                    # pos_x = 10
                    # pos_y = 115
                    # i = 0
                    # for a, accessory in enumerate(new_inv[start_index:min(end_index, inventory_len + start_index)], start = start_index):
                    # # for accessory in cat.pelt.inventory.items():
                    #     try:
                    #         self.item_list(accessory, cat, pos_x, pos_y, i)
                    #         pos_x += 67
                    #         if pos_x >= 585:
                    #             pos_x = 10
                    #             pos_y += 77
                    #         i += 1
                    #     except:
                    #         continue
                    self.open_accessories()

                self.profile_elements["cat_image"].kill()

                self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((100, 200), (150, 150))),
                    pygame.transform.scale(
                        self.the_cat.sprite, ui_scale_dimensions((150, 150))
                    ),
                    manager=MANAGER,
                )
                self.profile_elements["cat_image"].disable()

                self.profile_elements["cat_info_column1"].kill()
                self.profile_elements["cat_info_column1"] = UITextBoxTweaked(
                    self.generate_column1(self.the_cat),
                    ui_scale(pygame.Rect((300, 220), (180, 200))),
                    object_id=get_text_box_theme("#text_box_22_horizleft"),
                    line_spacing=1,
                    manager=MANAGER,
                )
                self.column_adjust()


    def screen_switches(self):
        super().screen_switches()
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.page = 0
        self.selected_item = None

        # Set up the menu buttons, which appear on all cat profile images.
        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "Next Cat " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            get_arrow(2, arrow_left=True) + " Previous Cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.relations_tab_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 420), (176, 30))),
            "relations",
            get_button_dict(ButtonStyles.PROFILE_LEFT, (176, 30)),
            object_id="@buttonstyles_profile_left",
            manager=MANAGER,
        )
        self.roles_tab_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((224, 420), (176, 30))),
            "roles",
            get_button_dict(ButtonStyles.PROFILE_MIDDLE, (176, 30)),
            object_id="@buttonstyles_profile_middle",
            manager=MANAGER,
        )
        self.personal_tab_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((400, 420), (176, 30))),
            "personal",
            get_button_dict(ButtonStyles.PROFILE_MIDDLE, (176, 30)),
            object_id="@buttonstyles_profile_middle",
            manager=MANAGER,
        )
        self.dangerous_tab_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((576, 420), (176, 30))),
            "dangerous",
            get_button_dict(ButtonStyles.PROFILE_RIGHT, (176, 30)),
            object_id="@buttonstyles_profile_right",
            manager=MANAGER,
        )
        self.dangerous_tab_button.disable()

        self.backstory_tab_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 622), (176, 30))),
            "history",
            get_button_dict(ButtonStyles.PROFILE_LEFT, (176, 30)),
            object_id="@buttonstyles_profile_left",
            manager=MANAGER,
        )

        self.conditions_tab_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((224, 622), (176, 30))),
            "conditions",
            get_button_dict(ButtonStyles.PROFILE_MIDDLE, (176, 30)),
            object_id="@buttonstyles_profile_middle",
            manager=MANAGER,
        )

        self.placeholder_tab_3 = UISurfaceImageButton(
            ui_scale(pygame.Rect((400, 622), (176, 30))),
            "faith",
            get_button_dict(ButtonStyles.PROFILE_MIDDLE, (176, 30)),
            object_id="@buttonstyles_profile_middle",
            manager=MANAGER,
        )

        self.accessories_tab_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((576, 622), (176, 30))),
            "inventory",
            get_button_dict(ButtonStyles.PROFILE_RIGHT, (176, 30)),
            object_id="@buttonstyles_profile_right",
            manager=MANAGER,
        )

        if self.the_cat.moons == 0:
            self.accessories_tab_button.disable()
        else:
            self.accessories_tab_button.enable()
        self.build_profile()

        self.hide_mute_buttons()  # no space for mute button on this screen
        self.hide_menu_buttons()  # Menu buttons don't appear on the profile screen
        if game.last_screen_forProfile == "med den screen":
            self.toggle_conditions_tab()
        # game.clan.load_accessories()

        self.set_cat_location_bg(self.the_cat)

    def clear_profile(self):
        """Clears all profile objects."""
        for ele in self.profile_elements:
            self.profile_elements[ele].kill()
        self.profile_elements = {}

        for ele in self.stat_elements:
            self.stat_elements[ele].kill()
        self.stat_elements = {}

        # self.selected_item = None
        if self.your_tab:
            self.your_tab.kill()

        if self.user_notes:
            self.user_notes = "Click the check mark to enter notes about your cat!"

        for box in self.checkboxes:
            self.checkboxes[box].kill()
        self.checkboxes = {}

        # hg
        self.inspect_button.kill()

    def exit_screen(self):
        for ele in self.stat_elements:
            self.stat_elements[ele].kill()
        self.stat_elements = {}

        for ele in self.item_window_elements:
            self.item_window_elements[ele].kill()
        self.item_window_elements = {}

        self.clear_profile()
        self.back_button.kill()
        self.next_cat_button.kill()
        self.previous_cat_button.kill()
        self.relations_tab_button.kill()
        self.roles_tab_button.kill()
        self.personal_tab_button.kill()
        self.dangerous_tab_button.kill()
        self.backstory_tab_button.kill()
        self.conditions_tab_button.kill()
        if self.your_tab:
            self.your_tab.kill()
        self.placeholder_tab_3.kill()
        self.accessories_tab_button.kill()
        self.inspect_button.kill()
        self.close_current_tab()

    def column_adjust(self):
        """ need to shorten columns when the eat button comes up so nothing gets covered"""
        # if self.the_cat.ID != game.clan.your_cat.ID:
        #     return
        if self.profile_elements["cat_info_column1"]:
            self.profile_elements["cat_info_column1"].kill()
        if self.profile_elements["cat_info_column2"]:
            self.profile_elements["cat_info_column2"].kill()

        if self.selected_item is None:
            value1 = 180
            value2 = 180
        else:
            value1 = 112
            value2 = 125

        self.profile_elements["cat_info_column1"] = UITextBoxTweaked(
            self.generate_column1(self.the_cat),
            ui_scale(pygame.Rect((300, 230), (180, value1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            line_spacing=0.95, manager=MANAGER
        )
        self.profile_elements["cat_info_column2"] = UITextBoxTweaked(
            self.generate_column2(self.the_cat),
            ui_scale(pygame.Rect((490, 230), (250, value2))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            line_spacing=0.95, manager=MANAGER
        )

        if self.selected_item is None:
            self.profile_elements["cat_info_column1"].show()
            self.profile_elements["cat_info_column2"].show()
        else:
            self.profile_elements["cat_info_column1"].hide()
            self.profile_elements["cat_info_column2"].hide()


    def build_profile(self):
        """Rebuild builds the cat profile. Run when you switch cats
        or for changes in the profile."""
        self.the_cat = Cat.all_cats.get(game.switches["cat"])

        # LG: accessory bull shit
        if game.clan.clan_settings['all accessories']:
            self.cat_inventory = game.clan.load_accessories()
        else:
            self.cat_inventory = self.the_cat.pelt.inventory
        
        if self.the_cat.pelt.accessory:
            if self.the_cat.pelt.accessory not in self.the_cat.pelt.inventory:
                self.the_cat.pelt.inventory.update({self.the_cat.pelt.accessory: 1})
                self.the_cat.pelt.accessory = None

        for acc in self.the_cat.pelt.accessories:
            if acc not in self.the_cat.pelt.inventory:
                self.the_cat.pelt.inventory.update({acc: 1})
        # ---

        if self.the_cat.dead and game.clan.demon.ID == self.the_cat.ID:
            self.the_cat.df = True

        # use these attributes to create differing profiles for StarClan cats etc.
        is_sc_instructor = False
        is_df_instructor = False
        if self.the_cat is None:
            return
        if (
            self.the_cat.dead
            and game.clan.instructor.ID == self.the_cat.ID
            and self.the_cat.df is False
        ):
            is_sc_instructor = True
        elif self.the_cat.dead and game.clan.demon.ID == self.the_cat.ID and self.the_cat.df is True:
            is_df_instructor = True

        # Info in string
        cat_name = str(self.the_cat.name)
        cat_name = shorten_text_to_fit(cat_name, 500, 20)
        if self.the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name


        if is_sc_instructor:

            if game.clan.followingsc == True:
                self.the_cat.thought = "Hello. I will be guiding the tributes of the Games into StarClan"
            else:
                self.the_cat.thought = "Misses watching over the tributes"

        if is_df_instructor:
            if game.clan.followingsc == True:
                self.the_cat.thought = "Hello. I am here to drag the tributes of the Games into the Dark Forest"
                self.the_cat.df
            else:
                self.the_cat.thought = "Is picking more cats to join them"

        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(cat_name,
                                                                        ui_scale(pygame.Rect((50, 280), (-1, 105))),
                                                                        object_id=get_text_box_theme(
                                                                            "#text_box_40_horizcenter"),
                                                                        manager=MANAGER)
        name_text_size = self.profile_elements["cat_name"].get_relative_rect()
        self.profile_elements["cat_name"].kill()

        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(
            cat_name,
            ui_scale(pygame.Rect((0, 0), (-1, 40))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            anchors={"centerx": "centerx"},
        )
        self.profile_elements["cat_name"].set_relative_position(
            ui_scale_offset((0, 140))
        )

        self.profile_elements["cat_info_column1"] = UITextBoxTweaked(
            self.generate_column1(self.the_cat),
            ui_scale(pygame.Rect((300, 220), (180, 200))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            line_spacing=1,
            manager=MANAGER,
        )
    
        self.profile_elements["cat_info_column2"] = UITextBoxTweaked(
            self.generate_column2(self.the_cat),
            ui_scale(pygame.Rect((490, 220), (250, 200))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            line_spacing=1,
            manager=MANAGER,
        )

        # inspect
        # moved here from switches bc it moves in HG
        if self.the_cat.dead:
            y_val = 60
        else:
            y_val = 215
        self.inspect_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((741, y_val), (34, 34))),
            Icon.MAGNIFY,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )

        # Set the cat backgrounds.
        if game.clan.clan_settings["backgrounds"]:
            if not self.the_cat.dead and self.the_cat.cat_clan is not None:
                theclan = None
                cat_clan = self.the_cat.cat_clan
                if cat_clan != game.clan.name:
                    cat_clan += "Clan"
                    for clan in game.clan.all_clans:
                        if str(clan) == cat_clan:
                            theclan = clan
                            break
                else:
                    theclan = game.clan
                if theclan:
                    self.profile_elements["clan_symbol_background"] = pygame_gui.elements.UIImage(
                        ui_scale(pygame.Rect((110, 175), (125, 125))),
                        pygame.transform.scale(
                            clan_symbol_sprite(theclan, force_light=True), ui_scale_dimensions((125, 125))
                        ),
                        object_id=f"clan_symbol",
                        starting_height=1,
                        manager=MANAGER,
                    )
                    self.profile_elements["clan_symbol_background"].disable()

            self.profile_elements["background"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((55, 200), (240, 210))),
                pygame.transform.scale(
                    self.get_platform(), ui_scale_dimensions((240, 210))
                ),
                manager=MANAGER,
            )
            self.profile_elements["background"].disable()

        # HG stats: now visable on every tab

        if not self.the_cat.dead and not self.the_cat.outside and self.the_cat.stats:
            stats_dict = {
                "satiation": self.the_cat.stats.hunger,
                "health": self.the_cat.stats.health,
                "energy": self.the_cat.stats.energy
            }
            # background box
            self.stat_elements["back"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((610, 60), (166, 150))),
                get_box(
                    BoxStyles.ROUNDED_BOX, (166, 150), sides=(True, True, True, True)
                ),
            )

            # stat value bars
            y_val = 90
            for stat in stats_dict.items():
                x_val = 630
                # label text for each stat
                self.stat_elements[stat[0] + "_text"] = UITextBoxTweaked(
                    "<b>" + stat[0].capitalize() + f"</b> ({str(stat[1])}/100)",
                    ui_scale(pygame.Rect((x_val - 5, y_val - 23), (170, 50))),
                    object_id="#text_box_26_horizleft_pad_10_14",
                    line_spacing=1,
                    manager=MANAGER,
                )
                # the individual bars
                for value in range(round(stat[1] / 10)): # divide by ten so i dont draw 100 images lol
                    self.stat_elements[stat[0] + str(value)] = pygame_gui.elements.UIImage(
                        ui_scale(pygame.Rect((x_val, y_val), (11, 20))),
                        image_cache.load_image(f"resources/images/relation_bar.png").convert_alpha())
                    x_val += 12
                y_val += 40

        # Write cat thought
        # moved down here for hunger games so the symbol doesnt cover it

        if self.the_cat.dead:
            thought_width = 600
        else:
            thought_width = 400

        self.profile_elements["cat_thought"] = pygame_gui.elements.UITextBox(
            self.the_cat.thought,
            ui_scale(pygame.Rect((0, 170), (thought_width, -1))),
            wrap_to_height=True,
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )
        # Create cat image object
        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((100, 200), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )
        self.profile_elements["cat_image"].disable()

        favorite_button_rect = ui_scale(pygame.Rect((0, 0), (28, 28)))
        favorite_button_rect.topright = ui_scale_offset((-5, 146))

        # LG changes
        if self.the_cat.favourite != 0:
            if self.the_cat.favourite == 1:
                fav_star_id = "#fav_star"
            else:
                fav_star_id = f"#fav_star_{str(self.the_cat.favourite)}"
        else:
            fav_star_id = "#not_fav_star"

        self.profile_elements["favourite_button"] = UIImageButton(
            favorite_button_rect,
            "",
            object_id=fav_star_id,
            manager=MANAGER,
            tool_tip_text=f"Move to {self.the_cat.favourite + 1}" if self.the_cat.favourite < 3 else "Remove favourite"
            if self.the_cat.favourite != 0
            else "Mark as favorite",
            starting_height=2,
            anchors={
                "right": "right",
                "right_target": self.profile_elements["cat_name"],
            },
        )
        self.profile_elements["favourite_button"].rebuild()
        del favorite_button_rect


        if self.accessory_tab_button:
            if self.the_cat.moons == 0:
                self.accessory_tab_button.disable()
            else:
                self.accessory_tab_button.enable()

        # Determine where the next and previous cat buttons lead
        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()

        # Disable and enable next and previous cat buttons as needed.
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

        if self.open_tab == "history" and self.open_sub_tab == "user notes":
            self.load_user_notes()

        if not game.clan.your_cat:
            print("Are you playing a normal ClanGen save? Switch to a LifeGen save or create a new cat!")
            print("Choosing random cat to play...")
            game.clan.your_cat = Cat.all_cats[choice(game.clan.clan_cats)]
            counter = 0
            while game.clan.your_cat.dead or game.clan.your_cat.outside:
                if counter == 25:
                    break
                game.clan.your_cat = Cat.all_cats[choice(game.clan.clan_cats)]
                counter+=1

            print("Chose " + str(game.clan.your_cat.name))

        if self.the_cat.ID == game.clan.your_cat.ID and not game.clan.your_cat.dead:
            # HG
            sleeptext = ""
            if game.clan.your_cat.sleeping:
                sleeptext = "wake up"
            else:
                sleeptext = "sleep"
            self.profile_elements["sleep"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((655, 215), (80, 34))),
                sleeptext,
                get_button_dict(ButtonStyles.SQUOVAL, (80, 34)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
            )
            if (
                (game.clan.timeskips == 1 and game.clan.days == 0) or
                game.clan.your_cat.sleeping and game.clan.your_cat.stats.energy <= 0
                ):
                self.profile_elements["sleep"].disable()
            else:
                self.profile_elements["sleep"].enable()
            
        # TALK BUTTONS

        if self.the_cat.ID != game.clan.your_cat.ID:

            # TALK
            cant_talk = False
            dead_talk = self.get_dead_cat_talk()

            if (
                (not self.the_cat.dead and self.the_cat.outside) or
                (not self.the_cat.dead and not self.the_cat.outside and game.clan.your_cat.outside and not game.clan.your_cat.dead) or 
                game.clan.your_cat.moons < 0 or
                self.the_cat.ID == game.clan.your_cat.ID or
                ((game.clan.your_cat.dead or self.the_cat.dead) and dead_talk is False) or
                (not game.clan.your_cat.dead and game.clan.your_cat.map_position != self.the_cat.map_position) or
                game.clan.your_cat.sleeping or self.the_cat.sleeping
            ):
                cant_talk = True
                
            self.profile_elements["talk"] = UIImageButton(ui_scale(pygame.Rect(
                (383, 105), (34, 34))),
                "",
                object_id="#talk_button",
                tool_tip_text="Talk to this Cat",
                manager=MANAGER
            )
            if self.the_cat.talked_to or cant_talk is True:
                self.profile_elements["talk"].disable()
            else:
                self.profile_elements["talk"].enable()
            
            if game.clan.your_cat.dead:
                button_text = "follow"
                hover_text = "Watch this cat"
            else:
                button_text = Icon.SCRATCHES + " attack " + Icon.SCRATCHES
                hover_text = "Attempt to kill this cat"

            self.profile_elements["attack"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, 50), (100, 30))),
                button_text,
                get_button_dict(ButtonStyles.SQUOVAL, (100, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
                tool_tip_text=hover_text,
                anchors={"centerx": "centerx"}
            )

            cant_attack = False
            if (
                (
                    not game.clan.your_cat.dead and
                    self.the_cat.map_position != game.clan.your_cat.map_position
                ) or (
                    game.clan.timeskips == 1 and game.clan.days == 0
                ) or
                self.the_cat.dead or
                self.the_cat.outside or
                game.clan.your_cat.outside or
                game.clan.your_cat.sleeping or
                (
                    game.clan.your_cat.dead and
                    game.clan.spectating and
                    self.the_cat.ID == game.clan.spectating.ID
                )
            ):
                cant_attack = True

            if cant_attack:
                self.profile_elements["attack"].disable()
            else:
                self.profile_elements["attack"].enable()
        
        # HG: tab enabling
        if self.the_cat.dead:
            self.dangerous_tab_button.enable()
            self.accessories_tab_button.disable()
        else:
            self.dangerous_tab_button.disable()
            self.accessories_tab_button.enable()

        if self.the_cat.ID == game.clan.your_cat.ID and not game.clan.your_cat.dead:
            if self.open_tab == "faith":
                self.close_current_tab()
            self.placeholder_tab_3.kill()

            self.your_tab = UISurfaceImageButton(
                ui_scale(pygame.Rect((400, 622), (176, 30))),
                "your tab",
                get_button_dict(ButtonStyles.PROFILE_MIDDLE, (176, 30)),
                object_id="@buttonstyles_profile_middle",
                manager=MANAGER,
            )
            
        else:
            if self.open_tab == 'your tab':
                self.close_current_tab()
            if self.open_tab == "faith" and (self.the_cat.dead or self.the_cat.outside or self.the_cat.moons < 6):
                self.close_current_tab()
            self.placeholder_tab_3.kill()
            self.placeholder_tab_3 = None

            self.placeholder_tab_3 = UISurfaceImageButton(
                ui_scale(pygame.Rect((400, 622), (176, 30))),
                "faith",
                get_button_dict(ButtonStyles.PROFILE_MIDDLE, (176, 30)),
                object_id="@buttonstyles_profile_middle",
                manager=MANAGER,
            )
            if self.the_cat.dead or self.the_cat.outside or self.the_cat.moons < 6:
                self.placeholder_tab_3.disable()
            else:
                self.placeholder_tab_3.enable()

        self.inventory_item_options()

    def generate_column1(self, the_cat):
        """Generate the left column information"""
        output = ""
        # SEX/GENDER
        if the_cat.genderalign is None or the_cat.genderalign == the_cat.gender:
            output += str(the_cat.gender)
        else:
            output += str(the_cat.genderalign)
        # NEWLINE ----------
        output += "\n"

        # AGE
        if the_cat.age == "kitten":
            output += "young"
        elif the_cat.age == "senior":
            output += "senior"
        else:
            output += the_cat.age
        # NEWLINE ----------
        output += "\n"

        # EYE COLOR
        output += "eyes: " + str(the_cat.describe_eyes())
        # NEWLINE ----------
        output += "\n"

        # PELT TYPE
        output += "pelt: " + the_cat.pelt.name.lower()
        # NEWLINE ----------
        output += "\n"

        # PELT LENGTH
        output += "fur length: " + the_cat.pelt.length
        # NEWLINE ----------

        # ACCESSORY
        if the_cat.pelt.accessories:
            if len(the_cat.pelt.accessories) > 0:
                if the_cat.pelt.accessories[0]:
                    try:
                        output += "\n"
                        output += 'accessories: ' + str(ACC_DISPLAY[the_cat.pelt.accessories[0]]["default"])
                        if len(the_cat.pelt.accessories) > 1:
                            output += ' and ' + str(len(the_cat.pelt.accessories) - 1) + ' more'
                    except:
                        print("error with column1")

        elif the_cat.pelt.accessory and the_cat.pelt.accessory in the_cat.pelt.accessories:
            output += "\n"
            output += "accessory: " + str(
                ACC_DISPLAY[the_cat.pelt.accessory]["default"]
            )
            # NEWLINE ----------

        # PARENTS
        all_parents = [Cat.fetch_cat(i) for i in the_cat.get_parents()]
        if all_parents:
            output += "\n"
            if len(all_parents) == 1:
                output += "parent: " + str(all_parents[0].name)
            elif len(all_parents) > 2:
                output += (
                    "parents: "
                    + ", ".join([str(i.name) for i in all_parents[:2]])
                    + f", and {len(all_parents) - 2} "
                )
                if len(all_parents) - 2 == 1:
                    output += "other"
                else:
                    output += "others"
            else:
                output += "parents: " + ", ".join([str(i.name) for i in all_parents if i])


        # MOONS
        output += "\n"
        if the_cat.dead:
            output += str(the_cat.moons)
            if the_cat.moons == 1:
                output += " moon (in life)\n"
            elif the_cat.moons != 1:
                output += " moons (in life)\n"

            output += str(the_cat.dead_for)
            if the_cat.dead_for == 1:
                output += " moon (in death)"
            elif the_cat.dead_for != 1:
                output += " moons (in death)"
        else:
            if the_cat.moons == -1:
                output += 'Unborn'
            else:
                output += str(the_cat.moons)
                if the_cat.moons == 1:
                    output += ' moon'
                elif the_cat.moons != 1:
                    output += ' moons'

        # MATE
        if len(the_cat.mate) > 0:
            output += "\n"

            mate_names = []
            # Grab the names of only the first two, since that's all we will display
            for _m in the_cat.mate[:2]:
                mate_ob = Cat.fetch_cat(_m)
                if not isinstance(mate_ob, Cat):
                    continue
                if mate_ob.dead != self.the_cat.dead:
                    if the_cat.dead:
                        former_indicate = "(living)"
                    else:
                        former_indicate = "(dead)"

                    mate_names.append(f"{str(mate_ob.name)} {former_indicate}")
                elif mate_ob.outside != self.the_cat.outside:
                    mate_names.append(f"{str(mate_ob.name)} (away)")
                else:
                    mate_names.append(f"{str(mate_ob.name)}")

            if len(the_cat.mate) == 1:
                output += "mate: "
            else:
                output += "mates: "

            output += ", ".join(mate_names)

            if len(the_cat.mate) > 2:
                output += f", and {len(the_cat.mate) - 2}"
                if len(the_cat.mate) - 2 > 1:
                    output += " others"
                else:
                    output += " other"
        
        # MATE
        if len(the_cat.allies) > 0:
            output += "\n"
            
            
            ally_names = []
            # Grab the names of only the first two, since that's all we will display
            for _m in the_cat.allies[:2]:
                ally_ob = Cat.fetch_cat(_m)
                if not isinstance(ally_ob, Cat):
                    continue
                if ally_ob.dead != self.the_cat.dead:
                    if the_cat.dead:
                        former_indicate = "(living)"
                    else:
                        former_indicate = "(dead)"
                    
                    ally_names.append(f"{str(ally_ob.name)} {former_indicate}")
                elif ally_ob.outside != self.the_cat.outside:
                    ally_names.append(f"{str(ally_ob.name)} (away)")
                else:
                    ally_names.append(f"{str(ally_ob.name)}")
                    
            if len(the_cat.allies) == 1:
                output += "ally: " 
            else:
                output += "allies: "
            
            output += ", ".join(ally_names)
            
            if len(the_cat.allies) > 2:
                output += f", and {len(the_cat.allies) - 2}"
                if len(the_cat.allies) - 2 > 1:
                    output += " others"
                else:
                    output += " other"

        if not the_cat.dead:
            # NEWLINE ----------
            output += "\n"

        return output

    def generate_column2(self, the_cat):
        """Generate the right column information"""
        output = ""

        # STATUS
        if the_cat.outside and not (the_cat.exiled or the_cat.df) and the_cat.status not in ['kittypet', 'loner', 'rogue',
            'former Clancat'] and not the_cat.dead:
            output += "<font color='#FF0000'>lost</font>"
        elif the_cat.exiled:
            output += "<font color='#FF0000'>exiled</font>"
        elif the_cat.shunned > 0 and not the_cat.dead:
            if not the_cat.outside:

                # grabbing demoted statuses
                murder_history = History.get_murders(the_cat)
                history = None
                status = the_cat.status
                if "is_murderer" in murder_history:
                    history = murder_history["is_murderer"]
                if history:
                    if "demoted_from" in history[-1] and history[-1]["demoted_from"]:
                        status = history[-1]["demoted_from"]

                if game.settings['dark mode']:
                    output += "<font color='#FF9999'>shunned " + status+ "</font>"
                else:
                    output += "<font color='#950000'>shunned " + status + "</font>"
            else:
                output += the_cat.status
        elif the_cat.df:
            if game.settings['dark mode']:
                output += "<font color='#FF9999' >" + "Dark Forest "+ the_cat.status + "</font>"
            else:
                output += "<font color='#950000' >" + "Dark Forest "+ the_cat.status + "</font>"
        elif the_cat.dead and not the_cat.df and not the_cat.outside:
            if game.settings['dark mode']:
                output += "<font color ='#A8BBFF'>" "StarClan " + the_cat.status + "</font>"
            else:
                output += "<font color ='#2B3DC3'>" "StarClan " + the_cat.status + "</font>"
        elif the_cat.dead and not the_cat.df and the_cat.outside:
            if game.settings['dark mode']:
                output += "<font color ='#CE9DFF'>" "ghost " + the_cat.status + "</font>"
            else:
                output += "<font color ='#450E7B'>" "ghost " + the_cat.status + "</font>"
        else:
            output += the_cat.status

        # NEWLINE ----------
        output += "\n"
        if the_cat.cat_clan is not None:
            output += the_cat.cat_clan + "Clan"
            # NEWLINE ----------
            output += "\n"

        # LEADER LIVES:
        # Optional - Only shows up for leaders
        if not the_cat.dead and "leader" in the_cat.status:
            output += "remaining lives: " + str(game.clan.leader_lives)
            # NEWLINE ----------
            output += "\n"

        # MENTOR
        # Only shows up if the cat has a mentor.
        if the_cat.mentor:
            mentor_ob = Cat.fetch_cat(the_cat.mentor)
            if mentor_ob:
                output += "mentor: " + str(mentor_ob.name) + "\n"
        
        if the_cat.df_mentor and not the_cat.dead:
            mentor_ob = Cat.fetch_cat(the_cat.df_mentor)
            if mentor_ob:
                output += "dark forest mentor: " + str(mentor_ob.name) + "\n"

        # CURRENT APPRENTICES
        # Optional - only shows up if the cat has an apprentice currently
        if the_cat.apprentice:
            app_count = len(the_cat.apprentice)
            if app_count == 1 and Cat.fetch_cat(the_cat.apprentice[0]):
                output += "apprentice: " + str(
                    Cat.fetch_cat(the_cat.apprentice[0]).name
                )
            elif app_count > 1:
                output += "apprentice: " + ", ".join(
                    [
                        str(Cat.fetch_cat(i).name)
                        for i in the_cat.apprentice
                        if Cat.fetch_cat(i)
                    ]
                )
            # NEWLINE ----------
            output += "\n"

        # FORMER APPRENTICES
        # Optional - Only shows up if the cat has previous apprentice(s)
        if the_cat.former_apprentices:
            apprentices = [
                Cat.fetch_cat(i)
                for i in the_cat.former_apprentices
                if isinstance(Cat.fetch_cat(i), Cat)
            ]

            if len(apprentices) > 2:
                output += (
                    "former apprentices: "
                    + ", ".join([str(i.name) for i in apprentices[:2]])
                    + ", and "
                    + str(len(apprentices) - 2)
                )
                if len(apprentices) - 2 > 1:
                    output += " others"
                else:
                    output += " other"
            else:
                if len(apprentices) > 1:
                    output += "former apprentices: "
                else:
                    output += "former apprentice: "
                output += ", ".join(str(i.name) for i in apprentices)

            # NEWLINE ----------
            output += "\n"
        
        if the_cat.df_apprentices and the_cat.dead:
            app_count = len(the_cat.df_apprentices)
            if app_count == 1 and Cat.fetch_cat(the_cat.df_apprentices[0]) and not Cat.fetch_cat(the_cat.df_apprentices[0]).dead:
                output += 'dark forest apprentice: ' + str(Cat.fetch_cat(the_cat.df_apprentices[0]).name)

                # NEWLINE ----------
                output += "\n"
            elif app_count > 1:
                output += 'dark forest apprentices: ' + ", ".join([str(Cat.fetch_cat(i).name) for i in the_cat.df_apprentices if Cat.fetch_cat(i) and not Cat.fetch_cat(i).dead])

                # NEWLINE ----------
                output += "\n"

        # CHARACTER TRAIT
        output += the_cat.personality.trait
        # NEWLINE ----------
        output += "\n"
        # CAT SKILLS

        if the_cat.moons < 1:
            output += "???"
        else:
            output += the_cat.skills.skill_string()
        # NEWLINE ----------
        output += "\n"

        # EXPERIENCE
        output += "strength: " + str(the_cat.experience_level)

        if game.clan.clan_settings["showxp"]:
            output += " (" + str(the_cat.experience) + ")"
        # NEWLINE ----------
        output += "\n"

        # BACKSTORY
        bs_text = "this should not appear"
        if the_cat.status in ["kittypet", "loner", "rogue", "former Clancat"]:
            bs_text = the_cat.status
        else:
            if the_cat.backstory:
                for category in BACKSTORIES["backstory_categories"]:
                    if (
                        the_cat.backstory
                        in BACKSTORIES["backstory_categories"][category]
                    ):
                        bs_text = BACKSTORIES["backstory_display"][category]
                        break
            else:
                bs_text = "Clanborn"
        output += f"backstory: {bs_text}"
        # NEWLINE ----------
        output += "\n"

        # NUTRITION INFO (if the game is in the correct mode)
        if (
            game.clan.game_mode in ["expanded", "cruel season"]
            and the_cat.is_alive()
            and FRESHKILL_ACTIVE
        ):
            # Check to only show nutrition for clan cats
            if str(the_cat.status) not in [
                "loner",
                "kittypet",
                "rogue",
                "former Clancat",
                "exiled",
            ]:
                nutr = None
                if the_cat.ID in game.clan.freshkill_pile.nutrition_info:
                    nutr = game.clan.freshkill_pile.nutrition_info[the_cat.ID]
                if not nutr:
                    game.clan.freshkill_pile.add_cat_to_nutrition(the_cat)
                    nutr = game.clan.freshkill_pile.nutrition_info[the_cat.ID]
                output += "nutrition: " + nutr.nutrition_text
                if game.clan.clan_settings["showxp"]:
                    output += " (" + str(int(nutr.percentage)) + ")"
                output += "\n"

        if the_cat.is_disabled():
            for condition in the_cat.permanent_condition:
                if (
                    the_cat.permanent_condition[condition]["born_with"] is True
                    and the_cat.permanent_condition[condition]["moons_until"] != -2
                ):
                    continue
                output += "has a permanent condition"

                # NEWLINE ----------
                output += "\n"
                break

        if the_cat.is_injured():
            if "recovering from birth" in the_cat.injuries:
                output += "recovering from birth!"
            elif "pregnant" in the_cat.injuries:
                output += 'pregnant!'
            elif "guilt" in the_cat.injuries:
                output += "guilty!"
            else:
                output += "injured!"
            if the_cat.sleeping is True:
                output += "\n"
                output += "asleep!"
            output += "\n"

        elif the_cat.is_ill():
            if "grief stricken" in the_cat.illnesses:
                output += "grieving!"
            elif "fleas" in the_cat.illnesses:
                output += "flea-ridden!"
            else:
                output += "sick!"
        
            if the_cat.sleeping is True:
                output += "\n"
                output += "asleep!"
            output += "\n"
        else:
            if the_cat.sleeping is True:
                output += "asleep!\n"

        # HG: kills
        victims = self.get_murder_text()[1]
        if victims:
            kills = len(victims)
            output += "kills: " + str(kills)
        

        return output

    def toggle_history_tab(self, sub_tab_switch=False):
        """Opens the history tab
        param sub_tab_switch should be set to True if switching between sub tabs within the History tab
        """
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open at a time
        self.close_current_tab()

        if previous_open_tab == "history" and sub_tab_switch is False:
            """If the current open tab is history and we aren't switching between sub tabs,
            just close the tab and do nothing else."""
            pass
        else:
            self.open_tab = "history"
            rect = ui_scale(pygame.Rect((0, 0), (620, 157)))
            rect.bottomleft = ui_scale_offset((89, 0))
            self.backstory_background = pygame_gui.elements.UIImage(
                rect,
                get_box(
                    BoxStyles.ROUNDED_BOX, (620, 157), sides=(True, True, False, True)
                ),
                anchors={
                    "bottom": "bottom",
                    "bottom_target": self.conditions_tab_button,
                },
            )
            self.backstory_background.disable()
            self.sub_tab_1 = UIImageButton(
                ui_scale(pygame.Rect((709, 475), (42, 30))),
                "",
                object_id="#sub_tab_1_button",
                manager=MANAGER,
            )
            self.sub_tab_1.disable()
            self.sub_tab_2 = UIImageButton(
                ui_scale(pygame.Rect((709, 512), (42, 30))),
                "",
                object_id="#sub_tab_2_button",
                manager=MANAGER,
            )
            self.sub_tab_2.disable()
            self.sub_tab_3 = UIImageButton(
                ui_scale(pygame.Rect((709, 549), (42, 30))),
                "",
                object_id="#sub_tab_3_button",
                manager=MANAGER,
            )
            self.sub_tab_3.disable()
            self.sub_tab_4 = UIImageButton(
                ui_scale(pygame.Rect((709, 586), (42, 30))),
                "",
                object_id="#sub_tab_4_button",
                manager=MANAGER,
            )
            self.sub_tab_4.disable()
            self.fav_tab = UIImageButton(
                ui_scale(pygame.Rect((55, 480), (28, 28))),
                "",
                object_id="#fav_star",
                tool_tip_text="un-favorite this sub tab",
                manager=MANAGER,
            )
            self.not_fav_tab = UIImageButton(
                ui_scale(pygame.Rect((55, 480), (28, 28))),
                "",
                object_id="#not_fav_star",
                tool_tip_text="favorite this sub tab - it will be the default sub tab displayed when History is viewed",
                manager=MANAGER,
            )

            if self.open_sub_tab != "life events":
                self.toggle_history_sub_tab()
            else:
                # This will be overwritten in update_disabled_buttons_and_text()
                self.history_text_box = pygame_gui.elements.UITextBox(
                    "", ui_scale(pygame.Rect((40, 240), (307, 71))), manager=MANAGER
                )
                self.no_moons = UIImageButton(
                    ui_scale(pygame.Rect((52, 514), (34, 34))),
                    "",
                    object_id="@unchecked_checkbox",
                    tool_tip_text="Show the Moon that certain history events occurred on",
                    manager=MANAGER,
                )
                self.show_moons = UIImageButton(
                    ui_scale(pygame.Rect((52, 514), (34, 34))),
                    "",
                    object_id="@checked_checkbox",
                    tool_tip_text="Stop showing the Moon that certain history events occurred on",
                    manager=MANAGER,
                )

                self.update_disabled_buttons_and_text()

    def toggle_user_notes_tab(self):
        """Opens the User Notes portion of the History Tab"""
        self.load_user_notes()
        if self.user_notes is None:
            self.user_notes = "Click the check mark to enter notes about your cat!"

        self.notes_entry = pygame_gui.elements.UITextEntryBox(
            ui_scale(pygame.Rect((100, 473), (600, 149))),
            initial_text=self.user_notes,
            object_id="#text_box_26_horizleft_pad_10_14",
            manager=MANAGER,
        )

        self.display_notes = UITextBoxTweaked(
            self.user_notes,
            ui_scale(pygame.Rect((100, 473), (60, 149))),
            object_id="#text_box_26_horizleft_pad_10_14",
            line_spacing=1,
            manager=MANAGER,
        )

        self.update_disabled_buttons_and_text()

    def save_user_notes(self):
        """Saves user-entered notes."""
        clanname = game.clan.name

        notes = self.user_notes

        notes_directory = get_save_dir() + "/" + clanname + "/notes"
        notes_file_path = notes_directory + "/" + self.the_cat.ID + "_notes.json"

        if not os.path.exists(notes_directory):
            os.makedirs(notes_directory)

        if (
            notes is None
            or notes == "Click the check mark to enter notes about your cat!"
        ):
            return

        new_notes = {str(self.the_cat.ID): notes}

        game.safe_save(notes_file_path, new_notes)

    def load_user_notes(self):
        """Loads user-entered notes."""
        clanname = game.clan.name

        notes_directory = get_save_dir() + "/" + clanname + "/notes"
        notes_file_path = notes_directory + "/" + self.the_cat.ID + "_notes.json"

        if not os.path.exists(notes_file_path):
            return

        try:
            with open(notes_file_path, "r") as read_file:
                rel_data = ujson.loads(read_file.read())
                self.user_notes = "Click the check mark to enter notes about your cat!"
                if str(self.the_cat.ID) in rel_data:
                    self.user_notes = rel_data.get(str(self.the_cat.ID))
        except Exception as e:
            print(
                f"ERROR: there was an error reading the Notes file of cat #{self.the_cat.ID}.\n",
                e,
            )

    def toggle_history_sub_tab(self):
        """To toggle the history-sub-tab"""

        if self.open_sub_tab == "life events":
            self.toggle_history_tab(sub_tab_switch=True)

        elif self.open_sub_tab == "user notes":
            self.toggle_user_notes_tab()

    def get_all_history_text(self):
        """Generates a string with all important history information."""
        output = ""
        if self.open_sub_tab == "life events":
            # start our history with the backstory, since all cats get one
            life_history = [str(self.get_backstory_text())]

            # now get apprenticeship history and add that if any exists
            app_history = self.get_apprenticeship_text()
            if app_history:
                life_history.append(app_history)

            # Get mentorship text if it exists
            mentor_history = self.get_mentorship_text()
            if mentor_history:
                life_history.append(mentor_history)

            # now go get the scar history and add that if any exists
            body_history = []
            scar_history = self.get_scar_text()
            if scar_history:
                body_history.append(scar_history)
            death_history = self.get_death_text()
            if death_history:
                body_history.append(death_history)
            # join scar and death into one paragraph
            if body_history:
                life_history.append(" ".join(body_history))

            murder = self.get_murder_text()[0]
            if murder:
                life_history.append(murder)

            # join together history list with line breaks
            output = "\n\n".join(life_history)
        return output

    def get_living_cats(self):
        living_cats = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and not the_cat.outside and not the_cat.moons == -1:
                living_cats.append(the_cat)
        return living_cats

    def get_backstory_text(self):
        """
        returns the backstory blurb
        """
        cat_dict = {"m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))}
        bs_blurb = None
        if self.the_cat.backstory:
            bs_blurb = BACKSTORIES["backstories"][self.the_cat.backstory]
        if (
            self.the_cat.status in ["kittypet", "loner", "rogue", "former Clancat"]
            and self.the_cat.dead
        ):
            bs_blurb = f"This cat was a {self.the_cat.status} in life."
        elif self.the_cat.status in ["kittypet", "loner", "rogue", "former Clancat"]:
            bs_blurb = f"This cat is a {self.the_cat.status} and currently resides outside of the Clans."

        if bs_blurb is not None:
            adjust_text = str(bs_blurb).replace("This cat", str(self.the_cat.name))
            text = adjust_text
        else:
            text = str(self.the_cat.name) + "'s past history is unknown."

        beginning = History.get_beginning(self.the_cat)
        if beginning:
            if (
                ("encountered" in beginning and beginning['encountered'] is False)
                or "encountered" not in beginning
                ):
                if 'clan_born' in beginning and beginning['clan_born']:
                    text += " {PRONOUN/m_c/subject/CAP} {VERB/m_c/were/was} born on Moon " + str(
                        beginning['moon']) + " during " + str(beginning['birth_season']) + "."
                elif 'age' in beginning and beginning['age'] and not self.the_cat.outside:
                    text += " {PRONOUN/m_c/subject/CAP} joined the Clan on Moon " + str(
                        beginning['moon']) + " at the age of " + str(beginning['age']) + " Moons."
                else:
                    text += "<br>You met {PRONOUN/m_c/object} on Moon " + str(beginning['moon']) + "."
            else:
                text += "<br>You encountered {PRONOUN/m_c/object} on Moon " + str(beginning['moon']) + "."

        if self.the_cat.history and self.the_cat.history.wrong_placement and self.the_cat.dead and not self.the_cat.outside:
            if self.the_cat.df:
                text += f"<br>{self.the_cat.name} was wrongly placed in the Dark Forest."
            else:
                text += f"<br>{self.the_cat.name} was wrongly placed in StarClan."

        text = process_text(text, cat_dict)
        if "o_c_n" in text:
            if self.the_cat.backstory_str:
                text = text.replace("o_c_n", self.the_cat.backstory_str)
            else:
                other_clan = "a different Clan"
                if game.clan.all_clans:
                    other_clan = str(choice(game.clan.all_clans).name) + "Clan"
                self.the_cat.backstory_str = other_clan
                text = text.replace("o_c_n", other_clan)
        if "c_n" in text:
            text = text.replace("c_n", str(game.clan.name))
        if "r_c" in text:
            if self.the_cat.backstory_str:
                text = text.replace("r_c", self.the_cat.backstory_str)
            else:
                random_cat = choice(self.get_living_cats())
                counter = 0
                while random_cat.moons < self.the_cat.moons or random_cat.ID == self.the_cat.ID:
                    if counter == 30:
                        break
                    random_cat = choice(self.get_living_cats())
                    counter+=1
                self.the_cat.backstory_str = str(random_cat.name)
                text = text.replace("r_c", str(random_cat.name))
        return text

    def get_scar_text(self):
        """
        returns the adjusted scar text
        """
        scar_text = []
        scar_history = History.get_death_or_scars(self.the_cat, scar=True)
        if game.switches["show_history_moons"]:
            moons = True
        else:
            moons = False

        if scar_history:
            i = 0
            for scar in scar_history:
                # base adjustment to get the cat's name and moons if needed
                new_text = event_text_adjust(
                    Cat,
                    scar["text"],
                    main_cat=self.the_cat,
                    random_cat=Cat.fetch_cat(scar["involved"]),
                )

                if moons:
                    new_text += f" (Moon {scar['moon']})"

                # checking to see if we can throw out a duplicate
                if new_text in scar_text:
                    i += 1
                    continue

                # the first event keeps the cat's name, consecutive events get to switch it up a bit
                if i != 0:
                    sentence_beginners = [
                        "This cat",
                        "Then {PRONOUN/m_c/subject} {VERB/m_c/were/was}",
                        "{PRONOUN/m_c/subject/CAP} {VERB/m_c/were/was} also",
                        "Also, {PRONOUN/m_c/subject} {VERB/m_c/were/was}",
                        "As well as",
                        "{PRONOUN/m_c/subject/CAP} {VERB/m_c/were/was} then",
                    ]
                    chosen = choice(sentence_beginners)
                    if chosen == "This cat":
                        new_text = new_text.replace(str(self.the_cat.name), chosen, 1)
                    else:
                        new_text = new_text.replace(
                            f"{self.the_cat.name} was", f"{chosen}", 1
                        )
                cat_dict = {
                    "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
                }
                new_text = process_text(new_text, cat_dict)
                scar_text.append(new_text)
                i += 1

            scar_history = " ".join(scar_text)

        return scar_history

    def get_apprenticeship_text(self):
        """
        returns adjusted apprenticeship history text (mentor influence and app ceremony)
        """
        if self.the_cat.status in ["kittypet", "loner", "rogue", "former Clancat"]:
            return ""

        mentor_influence = History.get_mentor_influence(self.the_cat)
        influence_history = ""

        #First, just list the mentors:
        if self.the_cat.status in ['kitten', 'newborn']:
                influence_history = 'This cat has not begun training.'
        elif self.the_cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"]:
            influence_history = 'This cat has not finished training.'
        else:
            valid_formor_mentors = [
                Cat.fetch_cat(i)
                for i in self.the_cat.former_mentor
                if isinstance(Cat.fetch_cat(i), Cat)
            ]
            if valid_formor_mentors:
                influence_history += (
                    "{PRONOUN/m_c/subject/CAP} {VERB/m_c/were/was} mentored by "
                )
                if len(valid_formor_mentors) > 1:
                    influence_history += (
                        ", ".join([str(i.name) for i in valid_formor_mentors[:-1]])
                        + " and "
                        + str(valid_formor_mentors[-1].name)
                        + ". "
                    )
                else:
                    influence_history += str(valid_formor_mentors[0].name) + ". "
            else:
                influence_history += "This cat either did not have a mentor, or {PRONOUN/m_c/poss} mentor is unknown. "

            # Second, do the facet/personality effect
            trait_influence = []
            if "trait" in mentor_influence and isinstance(
                mentor_influence["trait"], dict
            ):
                for _mentor in mentor_influence["trait"]:
                    # If the strings are not set (empty list), continue.
                    if not mentor_influence["trait"][_mentor].get("strings"):
                        continue

                    ment_obj = Cat.fetch_cat(_mentor)
                    # Continue of the mentor is invalid too.
                    if not isinstance(ment_obj, Cat):
                        continue

                    if len(mentor_influence["trait"][_mentor].get("strings")) > 1:
                        string_snippet = (
                            ", ".join(
                                mentor_influence["trait"][_mentor].get("strings")[:-1]
                            )
                            + " and "
                            + mentor_influence["trait"][_mentor].get("strings")[-1]
                        )
                    else:
                        string_snippet = mentor_influence["trait"][_mentor].get(
                            "strings"
                        )[0]

                    trait_influence.append(
                        str(ment_obj.name)
                        + " influenced {PRONOUN/m_c/object} to be more likely to "
                        + string_snippet
                        + ". "
                    )

            influence_history += " ".join(trait_influence)

            skill_influence = []
            if "skill" in mentor_influence and isinstance(
                mentor_influence["skill"], dict
            ):
                for _mentor in mentor_influence["skill"]:
                    # If the strings are not set (empty list), continue.
                    if not mentor_influence["skill"][_mentor].get("strings"):
                        continue

                    ment_obj = Cat.fetch_cat(_mentor)
                    # Continue of the mentor is invalid too.
                    if not isinstance(ment_obj, Cat):
                        continue

                    if len(mentor_influence["skill"][_mentor].get("strings")) > 1:
                        string_snippet = (
                            ", ".join(
                                mentor_influence["skill"][_mentor].get("strings")[:-1]
                            )
                            + " and "
                            + mentor_influence["skill"][_mentor].get("strings")[-1]
                        )
                    else:
                        string_snippet = mentor_influence["skill"][_mentor].get(
                            "strings"
                        )[0]

                    skill_influence.append(
                        str(ment_obj.name)
                        + " helped {PRONOUN/m_c/object} become better at "
                        + string_snippet
                        + ". "
                    )

            influence_history += " ".join(skill_influence)

        app_ceremony = History.get_app_ceremony(self.the_cat)

        graduation_history = ""
        if app_ceremony:
            graduation_history = (
                "When {PRONOUN/m_c/subject} graduated, {PRONOUN/m_c/subject} {VERB/m_c/were/was} honored for {PRONOUN/m_c/poss} "
                + app_ceremony["honor"]
                + "."
            )

            grad_age = app_ceremony["graduation_age"]
            if int(grad_age) < 11:
                graduation_history += (
                    " {PRONOUN/m_c/poss/CAP} training went so well that {PRONOUN/m_c/subject} graduated early at "
                    + str(grad_age)
                    + " moons old."
                )
            elif int(grad_age) > 13:
                graduation_history += (
                    " {PRONOUN/m_c/subject/CAP} graduated late at "
                    + str(grad_age)
                    + " moons old."
                )
            else:
                graduation_history += (
                    " {PRONOUN/m_c/subject/CAP} graduated at "
                    + str(grad_age)
                    + " moons old."
                )

            if game.switches["show_history_moons"]:
                graduation_history += f" (Moon {app_ceremony['moon']})"
        cat_dict = {"m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))}
        apprenticeship_history = influence_history + " " + graduation_history
        apprenticeship_history = process_text(apprenticeship_history, cat_dict)
        return apprenticeship_history

    def get_mentorship_text(self):
        """

        returns full list of previously mentored apprentices.

        """

        text = ""
        # Doing this is two steps
        all_real_apprentices = [
            Cat.fetch_cat(i)
            for i in self.the_cat.former_apprentices
            if isinstance(Cat.fetch_cat(i), Cat)
        ]
        if all_real_apprentices:
            text = "{PRONOUN/m_c/subject/CAP} mentored "
            if len(all_real_apprentices) > 2:
                text += (
                    ", ".join([str(i.name) for i in all_real_apprentices[:-1]])
                    + ", and "
                    + str(all_real_apprentices[-1].name)
                    + "."
                )
            elif len(all_real_apprentices) == 2:
                text += (
                    str(all_real_apprentices[0].name)
                    + " and "
                    + str(all_real_apprentices[1].name)
                    + "."
                )
            elif len(all_real_apprentices) == 1:
                text += str(all_real_apprentices[0].name) + "."

            cat_dict = {"m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))}

            text = process_text(text, cat_dict)

        return text

    def get_text_for_murder_event(self, event, death):
        """Returns the adjusted murder history text for the victim"""

        if game.switches["show_history_moons"]:
            moons = True
        else:
            moons = False

        if event["text"] == death["text"] and event["moon"] == death["moon"]:
            if event["revealed"] is True:
                final_text = event_text_adjust(
                    Cat,
                    event["text"],
                    main_cat=self.the_cat,
                    random_cat=Cat.fetch_cat(death["involved"]),
                )

                if event.get("revelation_text"):
                    final_text = f"{final_text} {event['revelation_text']}"
                if moons:
                    if event.get("revelation_moon"):
                        final_text = f"{final_text} (Moon {event['revelation_moon']})."
                return final_text
            else:
                return event_text_adjust(
                    Cat,
                    event["text"],
                    main_cat=self.the_cat,
                    random_cat=Cat.fetch_cat(death["involved"]),
                )

        return None

    def get_death_text(self):
        """
        returns adjusted death history text
        """
        text = None
        death_history = self.the_cat.history.get_death_or_scars(
            self.the_cat, death=True
        )
        murder_history = self.the_cat.history.get_murders(self.the_cat)
        if game.switches["show_history_moons"]:
            moons = True
        else:
            moons = False

        if death_history:
            all_deaths = []
            death_number = len(death_history)
            multi_life_count = 0
            for index, death in enumerate(death_history):
                found_murder = (
                    False  # Add this line to track if a matching murder event is found
                )
                if "is_victim" in murder_history:
                    for event in murder_history["is_victim"]:
                        text = None
                        # text = self.get_text_for_murder_event(event, death)
                        if text is not None:
                            found_murder = True  # Update the flag if a matching murder event is found
                            break

                        if found_murder and text is not None and not event["revealed"]:
                            text = event_text_adjust(
                                Cat,
                                event["text"],
                                main_cat=self.the_cat,
                                random_cat=Cat.fetch_cat(death["involved"]),
                            )
                if not found_murder:
                    text = event_text_adjust(
                        Cat,
                        death["text"],
                        main_cat=self.the_cat,
                        random_cat=Cat.fetch_cat(death["involved"]),
                    )

                if self.the_cat.status == "leader":
                    if text == "multi_lives":
                        multi_life_count += 1
                        continue
                    if index == death_number - 1 and self.the_cat.dead:
                        if death_number == 9:
                            life_text = "lost {PRONOUN/m_c/poss} final life"
                        elif death_number == 1:
                            life_text = "lost all of {PRONOUN/m_c/poss} lives"
                        else:
                            life_text = "lost the rest of {PRONOUN/m_c/poss} lives"
                    else:
                        life_names = [
                            "first",
                            "second",
                            "third",
                            "fourth",
                            "fifth",
                            "sixth",
                            "seventh",
                            "eighth",
                        ]
                        if multi_life_count != 0:
                            temp_index = index - multi_life_count
                            lives = [life_names[temp_index]]
                            while multi_life_count != 0:
                                multi_life_count -= 1
                                temp_index += 1
                                lives.append(life_names[temp_index])
                        else:
                            lives = [life_names[index]]
                        life_text = (
                            "lost {PRONOUN/m_c/poss} "
                            + adjust_list_text(lives)
                            + (" life" if len(lives) == 1 else " lives")
                        )
                elif death_number > 1:
                    # for retired leaders
                    if index == death_number - 1 and self.the_cat.dead:
                        life_text = "lost {PRONOUN/m_c/poss} last remaining life"
                        # added code
                        if "This cat was" in text:
                            text = text.replace("This cat was", "{VERB/m_c/were/was}")
                        else:
                            text = text[0].lower() + text[1:]
                    else:
                        life_text = "lost a life"
                else:
                    life_text = ""

                if text:
                    if life_text:
                        text = f"{life_text} when {{PRONOUN/m_c/subject}} {text}"
                    else:
                        text = f"{text}"

                    if moons:
                        text += f" (Moon {death['moon']})"
                    all_deaths.append(text)

            if self.the_cat.status == "leader" or death_number > 1:
                if death_number > 1:
                    deaths = str("\n" + str(self.the_cat.name) + " ").join(all_deaths)
                else:
                    deaths = all_deaths[0]

                if not deaths.endswith("."):
                    deaths += "."

                text = str(self.the_cat.name) + " " + deaths

            else:
                text = all_deaths[0]

            cat_dict = {"m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))}
            text = process_text(text, cat_dict)

        return text

    def get_murder_text(self):
        """
        returns adjusted murder history text FOR THE MURDERER

        """
        murder_history = History.get_murders(self.the_cat)
        victim_text = ""

        if game.switches["show_history_moons"]:
            moons = True
        else:
            moons = False
        victims = []
        if murder_history:
            if "is_murderer" in murder_history:
                victims = murder_history["is_murderer"]

        name_list = []
        if len(victims) > 0:
            victim_names = {}
            reveal_text = None

            for victim in victims:
                if not Cat.fetch_cat(victim["victim"]):
                    continue
                name = str(Cat.fetch_cat(victim["victim"]).name)

                victim_names[name] = []
                if victim["revealed"]:
                    if victim.get("revelation_text"):
                        reveal_text = victim["revelation_text"]
                    if moons:
                        victim_names[name].append(victim["moon"])
                        if victim.get("revelation_moon"):
                            reveal_text = (
                                f"{reveal_text} (Moon {victim['revelation_moon']})"
                            )

            if victim_names:
                for name in victim_names:
                    if not moons:
                        name_list.append(name)
                    else:
                        name_list.append(f"{name} (Moon {victim_names[name][0]})")

                if len(name_list) == 1:
                    victim_text = f"{self.the_cat.name} killed {name_list[0]}."
                elif len(victim_names) == 2:
                    victim_text = (
                        f"{self.the_cat.name} killed {' and '.join(name_list)}."
                    )
                else:
                    victim_text = f"{self.the_cat.name} killed {', '.join(name_list[:-1])}, and {name_list[-1]}."

            if reveal_text:
                cat_dict = {
                    "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
                }
                victim_text = f"{victim_text} {process_text(reveal_text, cat_dict)}"

        return victim_text, name_list

    def toggle_conditions_tab(self):
        """Opens the conditions tab"""
        previous_open_tab = self.open_tab
        # This closes the current tab, so only one can be open at a time
        self.close_current_tab()

        if previous_open_tab == "conditions":
            """If the current open tab is conditions, just close the tab and do nothing else."""
            pass
        else:
            self.open_tab = "conditions"
            self.conditions_page = 0

            rect = ui_scale(pygame.Rect((0, 0), (624, 151)))
            rect.bottomleft = ui_scale_offset((0, 0))
            self.conditions_background = pygame_gui.elements.UIImage(
                rect,
                self.conditions_tab,
                starting_height=2,
                anchors={
                    "bottom": "bottom",
                    "bottom_target": self.conditions_tab_button,
                    "centerx": "centerx",
                },
            )
            del rect

            rect = ui_scale(pygame.Rect((-5, 537), (34, 34)))
            self.right_conditions_arrow = UISurfaceImageButton(
                rect,
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                anchors={"left_target": self.conditions_background},
            )
            del rect

            rect = ui_scale(pygame.Rect((0, 0), (34, 34)))
            rect.topright = ui_scale_offset((5, 537))
            self.left_conditions_arrow = UISurfaceImageButton(
                rect,
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                anchors={"right": "right", "right_target": self.conditions_background},
            )
            del rect

            # This will be overwritten in update_disabled_buttons_and_text()
            self.update_disabled_buttons_and_text()

    def display_conditions_page(self):
        # tracks the position of the detail boxes
        if self.condition_container:
            self.condition_container.kill()

        self.condition_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((89, 471), (624, 151))), MANAGER
        )

        # gather a list of all the conditions and info needed.
        all_illness_injuries = [
            (i, self.get_condition_details(i))
            for i in self.the_cat.permanent_condition
            if not (
                self.the_cat.permanent_condition[i]["born_with"]
                and self.the_cat.permanent_condition[i]["moons_until"] != -2
            )
        ]
        all_illness_injuries.extend(
            [(i, self.get_condition_details(i)) for i in self.the_cat.injuries]
        )
        all_illness_injuries.extend(
            [
                (i, self.get_condition_details(i))
                for i in self.the_cat.illnesses
                if i not in ("an infected wound", "a festering wound")
            ]
        )
        all_illness_injuries = chunks(all_illness_injuries, 4)

        if not all_illness_injuries:
            self.conditions_page = 0
            self.right_conditions_arrow.disable()
            self.left_conditions_arrow.disable()
            return

        # Adjust the page number if it somehow goes out of range.
        if self.conditions_page < 0:
            self.conditions_page = 0
        elif self.conditions_page > len(all_illness_injuries) - 1:
            self.conditions_page = len(all_illness_injuries) - 1

        # Disable the arrow buttons
        if self.conditions_page == 0:
            self.left_conditions_arrow.disable()
        else:
            self.left_conditions_arrow.enable()

        if self.conditions_page >= len(all_illness_injuries) - 1:
            self.right_conditions_arrow.disable()
        else:
            self.right_conditions_arrow.enable()

        x_pos = 13
        for x in self.condition_data.values():
            x.kill()
        self.condition_data = {}
        for con in all_illness_injuries[self.conditions_page]:
            # Background Box
            self.condition_data[f"bg_{con}"] = pygame_gui.elements.UIPanel(
                ui_scale(pygame.Rect((x_pos, 13), (142, 142))),
                manager=MANAGER,
                container=self.condition_container,
                object_id="#profile_condition_panel",
                margins={"left": 0, "right": 0, "top": 0, "bottom": 0},
            )

            self.condition_data[f"name_{con}"] = UITextBoxTweaked(
                con[0],
                ui_scale(pygame.Rect((0, 0), (120, -1))),
                line_spacing=0.90,
                object_id="#text_box_30_horizcenter",
                container=self.condition_data[f"bg_{con}"],
                manager=MANAGER,
                anchors={"centerx": "centerx"},
            )

            y_adjust = self.condition_data[f"name_{con}"].get_relative_rect().height
            details_rect = ui_scale(pygame.Rect((0, 0), (142, 100)))
            details_rect.bottomleft = (0, 0)

            self.condition_data[f"desc_{con}"] = UITextBoxTweaked(
                con[1],
                details_rect,
                line_spacing=0.75,
                object_id="#text_box_22_horizcenter",
                container=self.condition_data[f"bg_{con}"],
                manager=MANAGER,
                anchors={"bottom": "bottom", "centerx": "centerx"},
            )

            x_pos += 152
        return

    def get_condition_details(self, name):
        """returns the relevant condition details as one string with line breaks"""
        text_list = []
        cat_name = self.the_cat.name

        # collect details for perm conditions
        if name in self.the_cat.permanent_condition:
            # display if the cat was born with it
            if self.the_cat.permanent_condition[name]["born_with"] is True:
                text_list.append(f"born with this condition")
            else:
                # moons with the condition if not born with condition
                moons_with = (
                    game.clan.age - self.the_cat.permanent_condition[name]["moon_start"]
                )
                if moons_with != 1:
                    text_list.append(f"has had this condition for {moons_with} moons")
                else:
                    text_list.append(f"has had this condition for 1 moon")

            # is permanent
            text_list.append("permanent condition")

            # infected or festering
            complication = self.the_cat.permanent_condition[name].get(
                "complication", None
            )
            if complication is not None:
                if "a festering wound" in self.the_cat.illnesses:
                    complication = "festering"
                text_list.append(f"is {complication}!")

        # collect details for injuries
        if name in self.the_cat.injuries:
            # moons with condition
            keys = self.the_cat.injuries[name].keys()
            
            herbs1 = INJURIES[name]["herbs"]
            herbs = []

            for i in herbs1:
                i.replace("_", " ")
                herbs.append(i)

            if herbs:
                if len(herbs) > 1:
                    text = f"Needs {', '.join(herbs[:-1]).replace('_', ' ')} or {herbs[-1].replace('_', ' ')}."
                else:
                    text = f"Needs {herbs[0].replace('_', ' ')}."
                text_list.append(text)

            # infected or festering
            if "complication" in keys:
                complication = self.the_cat.injuries[name]["complication"]
                if complication is not None:
                    if "a festering wound" in self.the_cat.illnesses:
                        complication = "festering"
                    text_list.append(f"is {complication}!")

            # can or can't patrol
            if self.the_cat.injuries[name]["severity"] != "minor":
                text_list.append("Can't work with this condition")

        # collect details for illnesses
        if name in self.the_cat.illnesses:
            herbs1 = ILLNESSES[name]["herbs"]
            herbs = []

            for i in herbs1:
                i.replace("_", " ")
                herbs.append(i)

            if herbs:
                if len(herbs) > 1:
                    text = f"Needs {', '.join(herbs[:-1])} or {herbs[-1]}."
                else:
                    text = f"Needs {herbs[0]}."
                text_list.append(text)

            if self.the_cat.illnesses[name]["infectiousness"] != 0:
                text_list.append("infectious!")

            # can or can't patrol
            if self.the_cat.illnesses[name]["severity"] != "minor":
                text_list.append("Cannot travel with this condition")

        text = "<br><br>".join(text_list)
        return text
    
    def toggle_faith_tab(self):
        """Opens faith tab"""
        previous_open_tab = self.open_tab
        self.close_current_tab()

        if previous_open_tab == 'faith':
            pass
        else:
            self.open_tab = "faith"
            rect = ui_scale(pygame.Rect((0, 0), (620, 157)))
            rect.bottomleft = ui_scale_offset((89, 0))
            self.backstory_background = pygame_gui.elements.UIImage(
                rect,
                get_box(
                    BoxStyles.ROUNDED_BOX, (620, 157), sides=(True, True, False, True)
                ),
                anchors={
                    "bottom": "bottom",
                    "bottom_target": self.conditions_tab_button,
                },
            )
            self.backstory_background.disable()
            self.open_faith_tab()
            self.update_disabled_buttons_and_text()

    def open_faith_tab(self):
        if self.faith_bar and self.faith_text:
            self.faith_bar.kill()
            self.faith_text.kill()
        if self.the_cat.no_faith:
            self.the_cat.faith = 0
        cat_faith = round(self.the_cat.faith)
        if self.the_cat.lock_faith == "flexible":
            if cat_faith > 9:
                cat_faith = 9
            elif cat_faith < -9:
                cat_faith = -9
        elif self.the_cat.lock_faith == "starclan":
            if cat_faith > 9:
                cat_faith = 9
            elif cat_faith < 1:
                cat_faith = 1
        elif self.the_cat.lock_faith == "dark forest":
            if cat_faith > -1:
                cat_faith = -1
            elif cat_faith < -9:
                cat_faith = 9
        elif self.the_cat.lock_faith == "neutral":
            if cat_faith > 3:
                cat_faith = 3
            elif cat_faith < -3:
                cat_faith = -3
        self.faith_bar = pygame_gui.elements.UIImage(ui_scale(pygame.Rect((175, 500), (421, 39))),
                                                                image_cache.load_image(f"resources/images/faith{cat_faith}.png").convert_alpha())
        self.faith_bar.disable()
        self.faith_text = UITextBoxTweaked(self.get_faith_text(cat_faith),
                                                        ui_scale(pygame.Rect((175, 535), (425,75))),
                                                        object_id="#text_box_26_horizleft_pad_10_14",
                                                        line_spacing=1, manager=MANAGER)
        
    def get_faith_text(self, faith):
        faith_dict = {}
        with open("resources/dicts/faith_display.json", "r") as read_file:
            faith_dict = ujson.loads(read_file.read())
            cluster1, cluster2 = get_cluster(self.the_cat.personality.trait)

        faith_text = ""
        if faith == 0:
            faith_text = faith_dict[str(faith)]["All"]
        else:
            faith_text = faith_dict[str(faith)][str(cluster1)]

        process_text_dict = {}
        process_text_dict["m_c"] = self.the_cat
        for abbrev in process_text_dict.keys():
            abbrev_cat = process_text_dict[abbrev]
            process_text_dict[abbrev] = (abbrev_cat, choice(abbrev_cat.pronouns))
        faith_text = sub(r"\{(.*?)\}", lambda x: pronoun_repl(x, process_text_dict, False), faith_text)
        
        return faith_text
    
    def toggle_accessories_tab(self):
        """Opens accessories tab"""

        previous_open_tab = self.open_tab

        self.close_current_tab()
        self.page = 0

        if previous_open_tab == 'accessories':
            pass
        else:
            self.open_tab = "accessories"
            rect = ui_scale(pygame.Rect((0, 0), (620, 157)))
            rect.bottomleft = ui_scale_offset((89, 0))
            self.backstory_background = pygame_gui.elements.UIImage(
                rect,
                self.lvl3_inventory_tab,
                anchors={
                    "bottom": "bottom",
                    "bottom_target": self.conditions_tab_button,
                },
                )

            self.backstory_background.disable()

            self.delete_accessory = UIImageButton(
                ui_scale(pygame.Rect((709, 542), (34, 34))),
                "",
                object_id="#exit_window_button",
                tool_tip_text="Remove worn accessories from inventory",
                manager=MANAGER
                )
            
            self.next_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((709, 500), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
            )
            self.previous_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((55, 500), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
            )

            self.search_bar_image = pygame_gui.elements.UIImage(ui_scale(pygame.Rect((119, 455), (118, 34))),
                                                            pygame.image.load(
                                                                "resources/images/search_bar.png").convert_alpha(),
                                                            manager=MANAGER)
            self.search_bar = pygame_gui.elements.UITextEntryLine(ui_scale(pygame.Rect((129, 457), (102, 27))),
                                                              object_id="#search_entry_box",
                                                              initial_text="search",
                                                              manager=MANAGER)
            self.search_bar_image.hide()
            self.search_bar.hide()
            self.open_accessories()
            self.update_disabled_buttons_and_text()

    # def update_accessories(self):


    def open_accessories(self):

        cat = self.the_cat
        age = cat.age
        cat_sprite = str(cat.pelt.cat_sprites[cat.age])

        # setting the cat_sprite (bc this makes things much easier)
        if cat.not_working() and age != 'newborn' and game.config['cat_sprites']['sick_sprites']:
            if age in ['kitten', 'adolescent']:
                cat_sprite = str(19)
            else:
                cat_sprite = str(18)
        elif cat.pelt.paralyzed and age != 'newborn':
            if age in ['kitten', 'adolescent']:
                cat_sprite = str(17)
            else:
                if cat.pelt.length == 'long':
                    cat_sprite = str(16)
                else:
                    cat_sprite = str(15)
        else:
            if age == 'elder':
                age = 'senior'

            cat_sprite = str(cat.pelt.cat_sprites[age])


        self.cat_list_buttons = {}
        self.inventory_buttons = {}
        self.inventory_items = {}
        self.accessories_list = []
        self.inventory_items_list = []
        start_index = self.page * 18
        end_index = start_index + 18

        if cat.pelt.accessory:
            if cat.pelt.accessory not in cat.pelt.inventory.keys():
                cat.pelt.inventory.update({cat.pelt.accessory: 1})
                cat.pelt.accessories.append(cat.pelt.accessory)
                cat.pelt.accessory = None

        for i in cat.pelt.accessories:
            if i not in cat.pelt.inventory.keys():
                cat.pelt.inventory.update({i: 1})

        inventory_len = 0
        new_inv = []
        if self.search_bar.get_text() in ["", "search"]:
            inventory_len = len(cat.pelt.inventory.keys())
            new_inv = cat.pelt.inventory
        else:
            for ac in cat.pelt.inventory.keys():
                if ac and self.search_bar.get_text() and self.search_bar.get_text().lower() in ac.lower():
                    inventory_len+=1
                    new_inv.append(ac)
        self.max_pages = math.ceil(inventory_len/18)
        
        if (self.max_pages == 1 or self.max_pages == 0):
            self.previous_page_button.disable()
            self.next_page_button.disable()
        if self.page == 0:
            self.previous_page_button.disable()
        if cat.pelt.inventory:
            new_inv = list(new_inv.items())
            pos_x = 10
            pos_y = 115
            i = 0
            for a, accessory in enumerate(new_inv[start_index:min(end_index, inventory_len)], start = start_index):
                try:
                    self.item_list(accessory, cat, pos_x, pos_y, i)
                    pos_x += 67
                    if pos_x >= 585:
                        pos_x = 10
                        pos_y += 77
                    i += 1
                except:
                    continue

    def inventory_item_options(self):
        """ 
        UI popup for when an inventory item is selected
        For food, shows hunger, health and energy values
        For herbs, shows conditions needed for
        For accessories, just equips and unequips
        """
    
        # if self.the_cat.ID != game.clan.your_cat.ID:
        #     return

        for ele in self.item_window_elements:
            self.item_window_elements[ele].kill()
        self.item_window_elements = {}
        
        self.column_adjust()
        
        if self.selected_item is None:
            return

        if self.selected_item in ITEM_VALUES[game.clan.biome]:
            s_value = ITEM_VALUES[game.clan.biome][self.selected_item][0]
            h_value = ITEM_VALUES[game.clan.biome][self.selected_item][1]
            e_value = ITEM_VALUES[game.clan.biome][self.selected_item][2]


        self.item_window_elements["back"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((294, 214), (160, 170))),
            get_box(
                BoxStyles.ROUNDED_BOX, (160, 170), sides=(True, True, True, True)
            ),
        )
        self.item_window_elements["name_bg"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((460, 215), (180, 45))),
            get_box(
                BoxStyles.ROUNDED_BOX, (180, 45), sides=(True, True, True, True)
            ),
        )
        self.item_window_elements["hunger_bg"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((460, 262), (180, 80))),
            get_box(
                BoxStyles.ROUNDED_BOX, (180, 80), sides=(True, True, True, True)
            ),
        )
        item = self.selected_item
        item_pos = [310, 240]

        if item in HERBS or item in ITEM_VALUES[game.clan.biome].keys():
            try:
                itemimage = image_cache.load_image(f"resources/images/inventory_items/{item}.png").convert_alpha()
            except:
                itemimage = image_cache.load_image("resources/images/inventory_items/placeholder_herb.png").convert_alpha()
                
            self.item_window_elements["item"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((item_pos), (128, 128))),
                pygame.transform.scale(
                itemimage, ui_scale_dimensions((128, 128))
            ),
            )
        else:
            item = self.selected_item
            cat_sprite = str(self.the_cat.pelt.cat_sprites[self.the_cat.age])
            acc_dict = {
                "acc_herbs": Pelt.plant_accessories,
                "acc_wild": Pelt.wild_accessories,
                "collars": Pelt.collars,
                "acc_flower": Pelt.flower_accessories,
                "acc_plant2": Pelt.plant2_accessories,
                "acc_smallAnimal": Pelt.smallAnimal_accessories,
                "acc_deadInsect": Pelt.deadInsect_accessories,
                "acc_aliveInsect": Pelt.aliveInsect_accessories,
                "acc_fruit": Pelt.fruit_accessories,
                "acc_crafted": Pelt.crafted_accessories,
                "acc_tail": Pelt.tail_accessories,
                "acc_tail2": Pelt.tail2_accessories
            }
            for x in acc_dict.items():
                if item.upper() in x[1]:
                    itemimage = sprites.sprites[x[0] + item.upper() + cat_sprite]
                    self.item_window_elements["item"] = pygame_gui.elements.UIImage(
                        ui_scale(pygame.Rect((item_pos), (100, 100))),
                        pygame.transform.scale(
                        itemimage, ui_scale_dimensions((100, 100))
                    ))
                    break

        itemname = str(self.selected_item).lower()
        name = itemname.capitalize()
        if 17 <= len(name):
            short_name = str(name)[0:14]
            name = short_name + '...'

        self.item_window_elements["item_text"] = pygame_gui.elements.UITextBox(
            f"{name.replace('_', ' ')}",
            ui_scale(pygame.Rect((460, 218), (180, 50))),
            object_id="#text_box_34_horizcenter",
        )
        accessory = False
        if item in HERBS:
            self.item_window_elements["eat_button"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((460, 345), (140, 34))),
                "use",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (140, 34)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                sound_id="item_eaten"
            )
            self.item_window_elements["discard"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((6, 345), (34, 34))),
                Icon.NOTEPAD,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                anchors={"left_target": self.item_window_elements["eat_button"]},
                tool_tip_text="Discard stack"
            )

            treatable_conditions = []

            if self.the_cat.is_injured():
                for injury in self.the_cat.injuries.items():
                    if item in INJURIES[injury[0]]["herbs"]:
                        treatable_conditions.append(injury[0])

            if self.the_cat.is_ill():
                for condition in self.the_cat.illnesses.items():
                    if item in ILLNESSES[condition[0]]["herbs"]:
                        treatable_conditions.append(condition[0])
            
            if treatable_conditions:
                # displayed_condition = choice(treatable_conditions)
                displayed_condition = "Treats " + ", ".join(treatable_conditions) + "."
            else:
                displayed_condition = "Treats no current conditions."
            
            self.item_window_elements["item_info"] = pygame_gui.elements.UITextBox(
                displayed_condition,
                ui_scale(pygame.Rect((460, 280), (180, 70))),
                object_id="#text_box_26_horizcenter",
            )

        elif item.upper() in ITEM_VALUES[game.clan.biome]:
            self.item_window_elements["eat_button"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((460, 345), (140, 34))),
                "eat",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (140, 34)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                sound_id="item_eaten"
            )
            self.item_window_elements["discard"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((6, 345), (34, 34))),
                Icon.NOTEPAD,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                anchors={"left_target": self.item_window_elements["eat_button"]},
                tool_tip_text="Discard stack"
            )
            self.item_window_elements["eat_button"].disable()

            self.item_window_elements["hunger_value"] = pygame_gui.elements.UITextBox(
                (
                    "+" + str(s_value) +
                    " satiation\n" +
                    ("+" if h_value >= 0 else "") +
                    str(int(h_value)) +
                    " health\n"+
                    ("+" if e_value >= 0 else "") +
                    str(int(e_value)) +
                    " energy\n"
                    ),
                ui_scale(pygame.Rect((460, 265), (180, 70))),
                object_id=(
                    "#text_box_26_horizcenter_vertcenter_spacing_95"),
                manager=MANAGER)

            if (
                self.the_cat.stats.hunger == 100 and
                self.the_cat.stats.health == 100 and
                self.the_cat.stats.energy == 100
                ):
                self.item_window_elements["eat_button"].disable()
            else:
                self.item_window_elements["eat_button"].enable()
        else:
            # accessories
            accessory = True
            if item in self.the_cat.pelt.accessories:
                text = "unequip"
            else:
                text = "equip"
            self.item_window_elements["eat_button"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((460, 345), (140, 34))),
                text,
                get_button_dict(ButtonStyles.ROUNDED_RECT, (140, 34)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER
            )
            self.item_window_elements["discard"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((6, 345), (34, 34))),
                Icon.NOTEPAD,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                manager=MANAGER,
                anchors={"left_target": self.item_window_elements["eat_button"]},
                tool_tip_text="Discard stack"
            )
            self.item_window_elements["eat_button"].disable()

        if (
            (game.clan.your_cat.ID != self.the_cat.ID and not accessory) or
            (self.the_cat.sleeping and not accessory)
            ):
            self.item_window_elements["eat_button"].disable()
        else:
            self.item_window_elements["eat_button"].enable()
        
        if game.clan.your_cat.ID != self.the_cat.ID:
            self.item_window_elements["discard"].disable()
        else:
            self.item_window_elements["discard"].enable()

    def use_herb(self):
        cured_condition = None
        if self.the_cat.is_injured():
            for injury in self.the_cat.injuries:
                if self.selected_item in INJURIES[injury]["herbs"]:
                    cured_condition = injury

        if self.the_cat.is_ill():
            for condition in self.the_cat.illnesses:
                if self.selected_item in ILLNESSES[condition]["herbs"]:
                    cured_condition = condition

        game.clan.your_cat.pelt.inventory[self.selected_item] -= 1
        if game.clan.your_cat.pelt.inventory[self.selected_item] <= 0:
            game.clan.your_cat.pelt.inventory.pop(self.selected_item)
        if cured_condition is not None:
            if cured_condition in self.the_cat.illnesses:
                self.the_cat.illnesses.pop(cured_condition)

            elif cured_condition in self.the_cat.injuries:
                self.the_cat.injuries.pop(cured_condition)

            game.clan.your_cat.stats.health += randint(10, 30)
        else:
            game.clan.your_cat.stats.health += randint(3, 15)
            # less health is restored if the herb isnt curing a current condition
        if game.clan.your_cat.stats.health > 100:
            game.clan.your_cat.stats.health = 100

        self.close_current_tab()

        self.clear_profile()
        self.build_profile()
    
        if self.selected_item not in self.the_cat.pelt.inventory.keys():
            self.selected_item = None

        self.inventory_item_options()
        self.update_disabled_buttons_and_text()
        self.toggle_accessories_tab()

    def eat(self):
        """ eata da food """

        if self.selected_item in ITEM_VALUES[game.clan.biome]:
            game.clan.your_cat.stats.hunger += ITEM_VALUES[game.clan.biome][self.selected_item][0]
            game.clan.your_cat.stats.health += ITEM_VALUES[game.clan.biome][self.selected_item][1]
            game.clan.your_cat.stats.energy += ITEM_VALUES[game.clan.biome][self.selected_item][2]
        
        if self.selected_item.lower() == "deathberry":
            game.clan.your_cat.get_injured("poisoned")

        game.clan.your_cat.pelt.inventory[self.selected_item] -= 1

        if game.clan.your_cat.pelt.inventory[self.selected_item] <= 0:
            game.clan.your_cat.pelt.inventory.pop(self.selected_item)

        self.close_current_tab()
        
        if self.selected_item not in self.the_cat.pelt.inventory.keys():
            self.selected_item = None
        self.inventory_item_options()
        self.update_disabled_buttons_and_text()
        self.toggle_accessories_tab()

    def item_list(self, accessory, cat, pos_x, pos_y, i):
        
        cat = self.the_cat
        age = cat.age
        cat_sprite = str(cat.pelt.cat_sprites[cat.age])

        item_type = "accessory"

        if accessory[0] in ITEM_VALUES[game.clan.biome]:
            item_type = "item"

        if accessory[0].lower() in HERBS:
            item_type = "herb"

        if item_type == "accessory":
            item = str(accessory[0])
            try:
                acc_dict = {
                    "acc_herbs": Pelt.plant_accessories,
                    "acc_wild": Pelt.wild_accessories,
                    "collars": Pelt.collars,
                    "acc_flower": Pelt.flower_accessories,
                    "acc_plant2": Pelt.plant2_accessories,
                    "acc_smallAnimal": Pelt.smallAnimal_accessories,
                    "acc_deadInsect": Pelt.deadInsect_accessories,
                    "acc_aliveInsect": Pelt.aliveInsect_accessories,
                    "acc_fruit": Pelt.fruit_accessories,
                    "acc_crafted": Pelt.crafted_accessories,
                    "acc_tail": Pelt.tail_accessories,
                    "acc_tail2": Pelt.tail2_accessories
                }
                for x in acc_dict.items():
                    if item.upper() in x[1]:
                        itemimage = sprites.sprites[x[0] + item.upper() + cat_sprite]
                        self.inventory_items["item" + item] = pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((88 + pos_x, 365 + pos_y), ui_scale_dimensions((50, 50)))),
                            itemimage
                        )
                        break
            except Exception as e:
                print("Accessory Error with", item, ":", e)
        else:
            item = str(accessory[0]).lower().replace(" ", "_")
            try:
                itemimage = image_cache.load_image(f"resources/images/inventory_items/{item}.png").convert_alpha()
            except:
                itemimage = image_cache.load_image(f"resources/images/inventory_items/placeholder_herb.png").convert_alpha()
        
            # Item image
            self.inventory_items["item" + item] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((88 + pos_x, 365 + pos_y), (64, 64))),
                itemimage
            )

        # Item count elements-- only for items and herbs
        self.inventory_items[item + "_number_bg" + str(i)] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((132 + pos_x, 401 + pos_y), (25, 25))),
            image_cache.load_image(f"resources/images/fav_marker_1.png").convert_alpha())
        
        self.inventory_items[item + "_number_" + str(i)] = pygame_gui.elements.UITextBox(
                f"<b>{str(accessory[1])}</b>",
                ui_scale(pygame.Rect((132 + pos_x, 400 + pos_y), (25, 25))),
                object_id="#text_box_22_horizcenter",
            )
        
        # Clickable button
        self.inventory_buttons[item + str(i)] = UIImageButton(
            ui_scale(pygame.Rect((88 + pos_x, 365 + pos_y), (64, 64))),
            "",
            tool_tip_text=accessory[0],
            object_id="#blank_button")
            
        # Herb name
        if item_type == "herb":
            name = str(accessory[0]).lower().replace("_", " ")
            if 8 <= len(name):
                short_name = str(name)[0:5]
                name = short_name + '...'
            self.inventory_items[item + "_placeholdername" + str(i)] = pygame_gui.elements.UITextBox(
                f"{name}",
                ui_scale(pygame.Rect((87 + pos_x, 353 + pos_y), (60, 25))),
                object_id="#text_box_22_horizcenter",
            )

        self.inventory_items_list.append(accessory[0])

    def toggle_relations_tab(self):
        """Opens relations tab"""
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == "relations":
            """If the current open tab is relations, just close the tab and do nothing else."""
            pass
        else:
            self.open_tab = "relations"
            self.family_tree_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((50, 450), (172, 36))),
                "family tree",
                get_button_dict(ButtonStyles.LADDER_TOP, (172, 36)),
                object_id="@buttonstyles_ladder_top",
                starting_height=2,
                manager=MANAGER,
            )
            self.change_adoptive_parent_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((50, 486), (172, 36))),
                "adoptive parents",
                get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
                object_id="@buttonstyles_ladder_middle",
                starting_height=2,
                manager=MANAGER,
            )
            self.see_relationships_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((50, 522), (172, 36))),
                "see relationships",
                get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
                object_id="@buttonstyles_ladder_middle",
                starting_height=2,
                manager=MANAGER,
            )
            self.choose_mate_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((50, 558), (172, 36))),
                "choose mate",
                get_button_dict(ButtonStyles.LADDER_BOTTOM, (172, 36)),
                object_id="@buttonstyles_ladder_bottom",
                starting_height=2,
                manager=MANAGER,
            )
            self.update_disabled_buttons_and_text()

    def toggle_your_tab(self):
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'your tab':
            '''If the current open tab is relations, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'your tab'
            self.have_kits_button = None
            self.request_apprentice_button = None
            self.gift_accessory_button = None
            self.your_faith_button = None
            self.update_disabled_buttons_and_text()

    def toggle_roles_tab(self):
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == "roles":
            """If the current open tab is roles, just close the tab and do nothing else."""
            pass
        else:
            self.open_tab = "roles"

            self.manage_roles = UISurfaceImageButton(
                ui_scale(pygame.Rect((226, 450), (172, 36))),
                "manage roles",
                get_button_dict(ButtonStyles.LADDER_TOP, (172, 36)),
                object_id="@buttonstyles_ladder_top",
                starting_height=2,
                manager=MANAGER,
            )
            self.change_mentor_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((226, 486), (172, 36))),
                "change mentor",
                get_button_dict(ButtonStyles.LADDER_BOTTOM, (172, 36)),
                object_id="@buttonstyles_ladder_bottom",
                starting_height=2,
                manager=MANAGER,
            )
            self.update_disabled_buttons_and_text()

    def toggle_personal_tab(self):
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == "personal":
            """If the current open tab is personal, just close the tab and do nothing else."""
            pass
        else:
            self.open_tab = "personal"
            self.change_name_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((402, 450), (172, 36))),
                "change name",
                get_button_dict(ButtonStyles.LADDER_TOP, (172, 36)),
                object_id="@buttonstyles_ladder_top",
                starting_height=2,
                manager=MANAGER,
            )
            self.cis_trans_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((402, 0), (172, 52))),
                "debug\nuwu",
                get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
                object_id="@buttonstyles_ladder_middle",
                text_layer_object_id="@buttonstyles_ladder_multiline",
                starting_height=2,
                manager=MANAGER,
                anchors={"top_target": self.change_name_button},
                text_is_multiline=True,
            )
            self.specify_gender_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((402, 0), (172, 36))),
                "specify gender",
                get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
                object_id="@buttonstyles_ladder_middle",
                starting_height=2,
                manager=MANAGER,
                anchors={"top_target": self.cis_trans_button},
            )
            self.cat_toggles_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((402, 0), (172, 36))),
                "cat toggles",
                get_button_dict(ButtonStyles.LADDER_BOTTOM, (172, 36)),
                object_id="@buttonstyles_ladder_bottom",
                starting_height=2,
                manager=MANAGER,
                anchors={"top_target": self.specify_gender_button},
            )

            self.update_disabled_buttons_and_text()

    def toggle_dangerous_tab(self):
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == "dangerous":
            """If the current open tab is dangerous, just close the tab and do nothing else."""
            pass
        else:
            self.open_tab = "dangerous"

            self.update_disabled_buttons_and_text()

    def update_disabled_buttons_and_text(self):
        """Sets which tab buttons should be disabled. This is run when the cat is switched. """
        if self.the_cat.moons == 0:
            self.accessories_tab_button.disable()
        else:
            self.accessories_tab_button.enable()
        if self.open_tab is None:
            pass
        elif self.open_tab == "relations":
            if self.the_cat.dead:
                self.see_relationships_button.disable()
                self.change_adoptive_parent_button.disable()
            else:
                self.see_relationships_button.enable()
                self.change_adoptive_parent_button.enable()

            if (
                self.the_cat.age
                not in ["young adult", "adult", "senior adult", "senior"]
                or self.the_cat.exiled
                or self.the_cat.outside
            ):
                self.choose_mate_button.disable()
            else:
                self.choose_mate_button.enable()

        # Roles Tab
        elif self.open_tab == "roles":
            if self.the_cat.dead or self.the_cat.outside:
                self.manage_roles.disable()
            else:
                self.manage_roles.enable()
            # if self.the_cat.status not in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"] \
            #                                 or self.the_cat.dead or self.the_cat.outside:
            #     self.change_mentor_button.disable()
            # else:
            #     self.change_mentor_button.enable()
            
            self.change_mentor_button.disable()

        elif self.open_tab == "personal":
            # Button to trans or cis the cats.
            if self.the_cat.gender == "male" and self.the_cat.genderalign == "male":
                self.cis_trans_button.set_text("change to trans\nfemale")
            elif (
                self.the_cat.gender == "female" and self.the_cat.genderalign == "female"
            ):
                self.cis_trans_button.set_text("change to trans\nmale")
            elif self.the_cat.genderalign in ["trans female", "trans male"]:
                self.cis_trans_button.set_text("change to\nnonbinary")
            elif self.the_cat.genderalign not in [
                "female",
                "trans female",
                "male",
                "trans male",
            ]:
                self.cis_trans_button.set_text("change to \ncisgender")
            elif self.the_cat.gender == "male" and self.the_cat.genderalign == "female":
                self.cis_trans_button.set_text("change to \ncisgender")
            elif self.the_cat.gender == "female" and self.the_cat.genderalign == "male":
                self.cis_trans_button.set_text("change to \ncisgender")
            elif self.the_cat.genderalign:
                self.cis_trans_button.set_text("change to \ncisgender")
            else:
                self.cis_trans_button.set_text("change to \ncisgender")
                self.cis_trans_button.disable()

        elif self.open_tab == 'your tab':
            if 'have kits' not in game.switches:
                    game.switches['have kits'] = True
            self.have_kits_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((402, 580), (172, 36))),
                "have kits",
                get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
                object_id="@buttonstyles_ladder_middle",
                starting_height=2,
                tool_tip_text='You will be more likely to have kits the next moon.',
                manager=MANAGER,
                anchors={
                    "bottom_target": self.your_tab},
            )
            if self.the_cat.age in ['young adult', 'adult', 'senior adult', 'senior'] and not self.the_cat.dead and not self.the_cat.outside and game.switches['have kits']:
                self.have_kits_button.enable()
            else:
                self.have_kits_button.disable()

            self.request_apprentice_button = UISurfaceImageButton(
                    ui_scale(pygame.Rect((402, 544), (172, 36))),
                    "request apprentice",
                    get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
                    object_id="@buttonstyles_ladder_middle",
                    starting_height=2,
                    tool_tip_text='You will be more likely to receive an apprentice.', 
                    manager=MANAGER,
                    anchors={
                        "bottom_target": self.have_kits_button},
                )
            
            if self.the_cat.status in ['leader', 'deputy', 'medicine cat', 'mediator', 'queen', 'warrior'] and not self.the_cat.dead and not self.the_cat.outside:
                self.request_apprentice_button.enable()
            else:
                self.request_apprentice_button.disable()
            
            self.gift_accessory_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((402, 508), (172, 36))),
                "share supplies",
                get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
                object_id="@buttonstyles_ladder_middle",
                starting_height=2,
                manager=MANAGER,
                anchors={
                    "bottom_target": self.request_apprentice_button},
            )
            if (
                self.the_cat.moons > 0
                and not self.the_cat.dead
                and not self.the_cat.outside
                and len(self.the_cat.pelt.inventory.keys()) > 0
                ):
               
                self.gift_accessory_button.enable()
            else:
                self.gift_accessory_button.disable()

            self.your_faith_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((402, 472), (172, 36))),
                "faith",
                get_button_dict(ButtonStyles.LADDER_TOP, (172, 36)),
                object_id="@buttonstyles_ladder_top",
                starting_height=2,
                manager=MANAGER,
                anchors={
                    "bottom_target": self.gift_accessory_button},
            )
            if self.the_cat.status not in ["newborn", "kitten"] and not self.the_cat.dead and not self.the_cat.outside:
                self.your_faith_button.enable()
            else:
                self.your_faith_button.disable()
            

            if 'request apprentice' in game.switches:
                if game.switches['request apprentice']:
                    self.request_apprentice_button.disable()

        # Dangerous Tab
        elif self.open_tab == "dangerous":
            if self.the_cat.dead:
                tooltiptext = ""
                if self.the_cat.ID == game.clan.instructor.ID:
                    object_id = "follow_sc_button"
                    tooltiptext = "Your Clan will go to StarClan upon death."
                elif self.the_cat.ID == game.clan.demon.ID:
                    object_id = "follow_df_button"
                    tooltiptext = "Your Clan will go to the Dark Forest upon death."
                else:
                    if self.the_cat.dead:
                        if not self.the_cat.outside and not self.the_cat.df:
                            object_id = "#exile_df_button"
                        elif self.the_cat.df and not self.the_cat.outside:
                            object_id = "#send_ur_button"
                        else:
                            object_id = "#guide_sc_button"

                        self.exile_cat_button = UIImageButton(
                            ui_scale(pygame.Rect((578, 450), (172, 46))),
                            "",
                            object_id= object_id,
                            tool_tip_text=tooltiptext,
                            starting_height=2,
                            manager=MANAGER
                            )
                        if self.the_cat.ID == game.clan.instructor.ID:
                            if game.clan.followingsc:
                                self.exile_cat_button.disable()
                            else:
                                self.exile_cat_button.enable()
                        elif self.the_cat.ID == game.clan.demon.ID:
                            if not game.clan.followingsc:
                                self.exile_cat_button.disable()
                            else:
                                self.exile_cat_button.enable()
               
        elif self.open_tab == "accessories":
            for i in self.cat_list_buttons:
                self.cat_list_buttons[i].kill()
            for i in self.inventory_buttons:
                self.inventory_buttons[i].kill()
            for i in self.inventory_items:
                self.inventory_items[i].kill()
            self.open_accessories()
        elif self.open_tab == "faith":
            self.open_faith_tab()
        # History Tab:
        elif self.open_tab == "history":
            # show/hide fav tab star
            if self.open_sub_tab == game.switches["favorite_sub_tab"]:
                self.fav_tab.show()
                self.not_fav_tab.hide()
            else:
                self.fav_tab.hide()
                self.not_fav_tab.show()

            if self.open_sub_tab == "life events":
                self.sub_tab_1.disable()
                self.sub_tab_2.enable()
                self.history_text_box.kill()
                self.history_text_box = UITextBoxTweaked(
                    self.get_all_history_text(),
                    ui_scale(pygame.Rect((100, 473), (600, 149))),
                    object_id="#text_box_26_horizleft_pad_10_14",
                    line_spacing=1,
                    manager=MANAGER,
                )

                self.no_moons.kill()
                self.show_moons.kill()
                self.no_moons = UIImageButton(
                    ui_scale(pygame.Rect((52, 514), (34, 34))),
                    "",
                    object_id="@unchecked_checkbox",
                    tool_tip_text="Show the Moon that certain history events occurred on",
                    manager=MANAGER,
                )
                self.show_moons = UIImageButton(
                    ui_scale(pygame.Rect((52, 514), (34, 34))),
                    "",
                    object_id="@checked_checkbox",
                    tool_tip_text="Stop showing the Moon that certain history events occurred on",
                    manager=MANAGER,
                )
                if game.switches["show_history_moons"]:
                    self.no_moons.kill()
                else:
                    self.show_moons.kill()
            elif self.open_sub_tab == "user notes":
                self.sub_tab_1.enable()
                self.sub_tab_2.disable()
                if self.history_text_box:
                    self.history_text_box.kill()
                    self.no_moons.kill()
                    self.show_moons.kill()
                if self.save_text:
                    self.save_text.kill()
                if self.notes_entry:
                    self.notes_entry.kill()
                if self.edit_text:
                    self.edit_text.kill()
                if self.display_notes:
                    self.display_notes.kill()
                if self.help_button:
                    self.help_button.kill()

                self.help_button = UIImageButton(
                    ui_scale(pygame.Rect((52, 584), (34, 34))),
                    "",
                    object_id="#help_button",
                    manager=MANAGER,
                    tool_tip_text="The notes section has limited html capabilities.<br>"
                    "Use the following commands with < and > in place of the apostrophes.<br>"
                    "-'br' to start a new line.<br>"
                    "-Encase text between 'b' and '/b' to bold.<br>"
                    "-Encase text between 'i' and '/i' to italicize.<br>"
                    "-Encase text between 'u' and '/u' to underline.<br><br>"
                    "The following font related codes can be used, "
                    "but keep in mind that not all font faces will work.<br>"
                    "-Encase text between 'font face = name of font you wish to use' and '/font' to change the font face.<br>"
                    "-Encase text between 'font color= #hex code of the color' and '/font' to change the color of the text.<br>"
                    "-Encase text between 'font size=number of size' and '/font' to change the text size.",
                )
                if self.editing_notes is True:
                    self.save_text = UIImageButton(
                        ui_scale(pygame.Rect((52, 514), (34, 34))),
                        "",
                        object_id="@unchecked_checkbox",
                        tool_tip_text="lock and save text",
                        manager=MANAGER,
                    )

                    self.notes_entry = pygame_gui.elements.UITextEntryBox(
                        ui_scale(pygame.Rect((100, 473), (600, 149))),
                        initial_text=self.user_notes,
                        object_id="#text_box_26_horizleft_pad_10_14",
                        manager=MANAGER,
                    )
                else:
                    self.edit_text = UIImageButton(
                        ui_scale(pygame.Rect((52, 514), (34, 34))),
                        "",
                        object_id="@checked_checkbox_smalltooltip",
                        tool_tip_text="edit text",
                        manager=MANAGER,
                    )

                    self.display_notes = UITextBoxTweaked(
                        self.user_notes,
                        ui_scale(pygame.Rect((100, 473), (600, 149))),
                        object_id="#text_box_26_horizleft_pad_10_14",
                        line_spacing=1,
                        manager=MANAGER,
                    )

        # Conditions Tab
        elif self.open_tab == "conditions":
            self.display_conditions_page()

    def close_current_tab(self):
        """Closes current tab."""
        if self.open_tab is None:
            pass
        elif self.open_tab == "relations":
            self.family_tree_button.kill()
            self.see_relationships_button.kill()
            self.choose_mate_button.kill()
            self.change_adoptive_parent_button.kill()
        elif self.open_tab == "roles":
            self.manage_roles.kill()
            self.change_mentor_button.kill()
        elif self.open_tab == "personal":
            self.change_name_button.kill()
            self.cat_toggles_button.kill()
            self.specify_gender_button.kill()
            if self.cis_trans_button:
                self.cis_trans_button.kill()
        elif self.open_tab == "dangerous":
            if self.exile_cat_button:
                self.exile_cat_button.kill()
        elif self.open_tab == 'history':
            self.backstory_background.kill()
            self.sub_tab_1.kill()
            self.sub_tab_2.kill()
            self.sub_tab_3.kill()
            self.sub_tab_4.kill()
            self.fav_tab.kill()
            self.not_fav_tab.kill()
            if self.open_sub_tab == "user notes":
                if self.edit_text:
                    self.edit_text.kill()
                if self.save_text:
                    self.save_text.kill()
                if self.notes_entry:
                    self.notes_entry.kill()
                if self.display_notes:
                    self.display_notes.kill()
                self.help_button.kill()
            elif self.open_sub_tab == "life events":
                if self.history_text_box:
                    self.history_text_box.kill()
                self.show_moons.kill()
                self.no_moons.kill()
        elif self.open_tab == "accessories":
            self.backstory_background.kill()
            for i in self.cat_list_buttons:
                self.cat_list_buttons[i].kill()
            for i in self.inventory_buttons:
                self.inventory_buttons[i].kill()
            for i in self.inventory_items:
                self.inventory_items[i].kill()
            self.next_page_button.kill()
            self.previous_page_button.kill()
            self.delete_accessory.kill()
            self.search_bar_image.kill()
            self.search_bar.kill()
            self.inventory_item_options()
        elif self.open_tab == "faith":
            self.backstory_background.kill()
            self.faith_bar.kill()
            self.faith_text.kill()
        elif self.open_tab == 'your tab':
            if self.have_kits_button:
                self.have_kits_button.kill()
            if self.request_apprentice_button:
                self.request_apprentice_button.kill()
            if self.gift_accessory_button:
                self.gift_accessory_button.kill()
            if self.your_faith_button:
                self.your_faith_button.kill()
        elif self.open_tab == 'conditions':
            self.left_conditions_arrow.kill()
            self.right_conditions_arrow.kill()
            self.conditions_background.kill()
            self.condition_container.kill()
            for data in self.condition_data.values():
                data.kill()
            self.condition_data = {}

        self.open_tab = None



    # ---------------------------------------------------------------------------- #
    #                               cat platforms                                  #
    # ---------------------------------------------------------------------------- #
    def get_platform(self):
        the_cat = Cat.all_cats.get(game.switches["cat"], game.clan.instructor)

        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        available_biome = ["Forest", "Mountainous", "Plains", "Beach"]
        biome = game.clan.biome

        if biome not in available_biome:
            biome = available_biome[0]

        # HUNGER GAMES: not working cats get to sleep on the FLOOR NOW!!!!
        # if the_cat.age == "newborn" or the_cat.not_working():
        if the_cat.age == "newborn":
            biome = "nest"
            # newborns can still get a nest if they somehow manage to be born <3

        biome = biome.lower()

        platformsheet = pygame.image.load(
            "resources/images/platforms.png"
        ).convert_alpha()

        order = ["beach", "forest", "mountainous", "nest", "plains", "SC/DF"]

        biome_platforms = platformsheet.subsurface(
            pygame.Rect(0, order.index(biome) * 70, 640, 70)
        ).convert_alpha()

        biome_platforms = platformsheet.subsurface(
            pygame.Rect(0, order.index(biome) * 70, 640, 70)
        ).convert_alpha()

        offset = 0
        if light_dark == "light":
            offset = 80

        if the_cat.df:
            biome_platforms = platformsheet.subsurface(
                pygame.Rect(0, order.index("SC/DF") * 70, 640, 70)
            )
            return pygame.transform.scale(
                biome_platforms.subsurface(pygame.Rect(0 + offset, 0, 80, 70)),
                (240, 210),
            )
        elif the_cat.dead or game.clan.instructor.ID == the_cat.ID:
            biome_platforms = platformsheet.subsurface(
                pygame.Rect(0, order.index("SC/DF") * 70, 640, 70)
            )
            return pygame.transform.scale(
                biome_platforms.subsurface(pygame.Rect(160 + offset, 0, 80, 70)),
                (240, 210),
            )
        else:
            biome_platforms = platformsheet.subsurface(
                pygame.Rect(0, order.index(biome) * 70, 640, 70)
            ).convert_alpha()
            season_x = {
                "greenleaf": 0 + offset,
                "leaf-bare": 160 + offset,
                "leaf-fall": 320 + offset,
                "newleaf": 480 + offset,
            }

            return pygame.transform.scale(
                biome_platforms.subsurface(
                    pygame.Rect(
                        season_x.get(
                            game.clan.current_season.lower(), season_x["greenleaf"]
                        ),
                        0,
                        80,
                        70,
                    )
                ),
                (240, 210),
            )
        
    def get_dead_cat_talk(self):
        """ determining placing the talk button for dead cats """
        # They SC
        cat_dead_condition_sc = (
            self.the_cat.dead and
            not self.the_cat.df and
            not self.the_cat.outside and
            (game.clan.your_cat.dead or
            (game.clan.your_cat.skills.meets_skill_requirement(SkillPath.STAR)
            and game.clan.your_cat.moons >=1))
            )

        # They DF
        cat_dead_condition_df = (
            self.the_cat.dead and
            self.the_cat.df and
            (game.clan.your_cat.dead or
            (game.clan.your_cat.skills.meets_skill_requirement(SkillPath.DARK)
            and game.clan.your_cat.moons >=1) or
            game.clan.your_cat.joined_df)
            )

        # They UR
        cat_dead_condition_ur = (
            self.the_cat.dead and
            self.the_cat.ID in game.clan.unknown_cats and
            (game.clan.your_cat.dead or
            (game.clan.your_cat.skills.meets_skill_requirement(SkillPath.GHOST) and
            game.clan.your_cat.moons >=1))
            )

        # you SC
        cat_alive_condition_sc = (
            game.clan.your_cat.dead and
            not game.clan.your_cat.df and
            game.clan.your_cat.ID in game.clan.starclan_cats and
            (self.the_cat.dead or
            (self.the_cat.skills.meets_skill_requirement(SkillPath.STAR) and
            self.the_cat.moons >= 1))
            )

        # you DF
        cat_alive_condition_df = (
            game.clan.your_cat.dead and
            game.clan.your_cat.df and
            (self.the_cat.dead or
            (self.the_cat.skills.meets_skill_requirement(SkillPath.DARK) and
            self.the_cat.moons >= 1) or
            self.the_cat.joined_df)
            )

        # You UR
        cat_alive_condition_ur = (
            game.clan.your_cat.dead and
            game.clan.your_cat.ID in game.clan.unknown_cats and
            (self.the_cat.dead or
            (self.the_cat.skills.meets_skill_requirement(SkillPath.GHOST) and
            self.the_cat.moons >= 1))
            )

        if self.the_cat.dead and not self.the_cat.outside and not self.the_cat.df:
            if not cat_dead_condition_sc:
                return False
            else:
                return True
            
        if self.the_cat.dead and self.the_cat.outside and not self.the_cat.df:
            if not cat_dead_condition_ur:
                return False
            else:
                return True
            
        if self.the_cat.dead and not self.the_cat.outside and self.the_cat.df:
            if not cat_dead_condition_df:
                return False
            else:
                return True
            
        if game.clan.your_cat.dead:
            if game.clan.your_cat.df:
                if not cat_alive_condition_df:
                    return False
                else:
                    return True
            elif game.clan.your_cat.outside:
                if not cat_alive_condition_ur:
                    return False
                else:
                    return True
            else:
                if not cat_alive_condition_sc:
                    return False
                else:
                    return True
    def on_use(self):
        super().on_use()
        if self.search_bar:
            if self.search_bar.is_focused and self.search_bar.get_text() == "search":
                self.search_bar.set_text("")
                self.page = 0
                if self.page == 0 and (self.max_pages == 1 or self.max_pages == 0):
                    self.previous_page_button.disable()
                    self.next_page_button.disable()
                elif self.page == 0:
                    self.previous_page_button.disable()
                    self.next_page_button.enable()
                elif self.page == self.max_pages - 1:
                    self.previous_page_button.enable()
                    self.next_page_button.disable()
                else:
                    self.previous_page_button.enable()
                    self.next_page_button.enable()
            elif self.search_bar.get_text() != self.previous_search_text:
                self.page = 0
                if self.cat_list_buttons:
                    for i in self.cat_list_buttons:
                        self.cat_list_buttons[i].kill()
                    
                    # for i in self.inventory_items:
                    #     self.inventory_items[i].kill()
                self.open_accessories()

                if self.page == 0 and self.max_pages in [0, 1]:
                    self.previous_page_button.disable()
                    self.next_page_button.disable()
                elif self.page == 0:
                    self.previous_page_button.disable()
                    self.next_page_button.enable()
                elif self.page == self.max_pages - 1:
                    self.previous_page_button.enable()
                    self.next_page_button.disable()
                else:
                    self.previous_page_button.enable()
                    self.next_page_button.enable()
                self.previous_search_text = self.search_bar.get_text()
