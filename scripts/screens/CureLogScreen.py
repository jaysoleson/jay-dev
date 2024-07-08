# pylint: disable=line-too-long
"""

This file contains:
  The start screen,
  The switch clan screen,
  The settings screen,
  And the statistics screen.



"""  # pylint: enable=line-too-long

import logging
import os
import platform
import subprocess
import traceback
import logging
import random
from html import escape

import pygame
import pygame_gui
import ujson
from requests.exceptions import RequestException, Timeout

from scripts.cat.cats import Cat
from scripts.clan import Clan
from scripts.cat.pelts import Pelt
from scripts.game_structure import image_cache
from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.windows import DeleteCheck, UpdateAvailablePopup, ChangelogPopup, SaveError
from scripts.utility import get_text_box_theme, scale, quit  # pylint: disable=redefined-builtin
from scripts.cat.history import History
from .Screens import Screens
from ..housekeeping.datadir import get_data_dir, get_cache_dir
from ..housekeeping.update import has_update, UpdateChannel, get_latest_version_number
from ..housekeeping.version import get_version_info


logger = logging.getLogger(__name__)
has_checked_for_update = False
update_available = False



class CureLogScreen(Screens):
    """
    TODO: DOCS
    """

    def __init__(self, name=None):
        super().__init__(name)
        self.next_page_button = None
        self.previous_page_button = None
        self.stage = "logs"
        self.treatment_logs = {}
        self.moon_text = None
        self.moon_text_box = None
        self.treatment_text = None
        self.treatment_text_box = None
        self.correct_text = None
        self.correct_text_box = None

    def screen_switches(self):
        """
        TODO: DOCS
        """
        if self.stage == "logs":
            self.moon_text = None
            self.moon_text_box = None
            self.treatment_text = None
            self.treatment_text_box = None
            self.correct_text = None
            self.correct_text_box = None
            self.scroll_container = None

            self.set_disabled_menu_buttons(["stats"])
            self.show_menu_buttons()
            self.update_heading_text(f'{game.clan.name}Clan')
            a_txt = ""
            with open('resources/dicts/infection/logs.json', 'r', encoding='utf-8') as f:
                a_txt = ujson.load(f)

            self.check_logs()
        
            # Determine stats
            stats_text = "Information:"
            for i in game.clan.infection["logs"]:
                stats_text += "\n" + a_txt[i]
                
            
            self.previous_page_button = UIImageButton(scale(pygame.Rect((100, 700), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((1430, 700), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)

            self.stats_box = pygame_gui.elements.UITextBox(
                stats_text,
                scale(pygame.Rect((200, 250), (1200, 1000))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
            
            self.previous_page_button.disable()
            if len(game.clan.infection["treatments"]) > 0:
                self.next_page_button.enable()
            else:
                self.next_page_button.disable()
            
        elif self.stage == "treatments":

            self.set_disabled_menu_buttons(["stats"])
            self.show_menu_buttons()
            self.update_heading_text(f'{game.clan.name}Clan')

            self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect(
            (100, 350), (730, 790))),
            allow_scroll_x=False,
            manager=MANAGER)

            stats_text = "Treatments:"

            y_offset = 440
            for treatment in game.clan.infection['treatments']:
                self.moon_text = f"<b>Moon {treatment['moon']}</b>"
                self.moon_text_box = pygame_gui.elements.UITextBox(self.moon_text,
                                    pygame.Rect((80, y_offset), (260, 50)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                
                self.treatment_text = f"{', '.join([herb.replace('_', ' ') for herb in treatment['herbs']])}"
                self.treatment_text_box = pygame_gui.elements.UITextBox(self.treatment_text,
                                    pygame.Rect((80, (y_offset + 30)), (260, 100)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                
                # correct_text = f"Effective Herbs: {treatment['correct_herbs']}"
                if int(treatment['correct_herbs']) > 0:
                    self.correct_text = f"<font color = '#DBD076'> At least one effective herb </font>"
                elif int(treatment['correct_herbs']) == len(treatment["herbs"]) and len(treatment["herbs"]) == 4:
                    self.correct_text = f"<font color='#A2D86C'>Cure Found!</font>"
                else:
                    self.correct_text = f"<font color='#FF0000'>Zero Effective Herbs</font>"

                self.correct_text_box = pygame_gui.elements.UITextBox(self.correct_text,
                                    pygame.Rect((80, (y_offset + 80)), (260, 50)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                y_offset -= 140

            self.previous_page_button = UIImageButton(scale(pygame.Rect((100, 700), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((1430, 700), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)

            self.stats_box = pygame_gui.elements.UITextBox(
                stats_text,
                scale(pygame.Rect((200, 250), (1200, 1000))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
            
            self.scroll_container.set_scrollable_area_dimensions((1360 / 1600 * screen_x, y_offset / 1400 * screen_y))
            
            # self.scroll_container.vert_scroll_bar.scroll_position = self.scroll_container.vert_scroll_bar.scrollable_height
            # self.scroll_container.vert_scroll_bar.start_percentage = self.scroll_container.vert_scroll_bar.scroll_position / self.scroll_container.vert_scroll_bar.scrollable_height
            # self.scroll_container.vert_scroll_bar.has_moved_recently = True

            self.previous_page_button.enable()
            self.next_page_button.disable()

    def check_logs(self):
        you = game.clan.your_cat
        cure_logs = set()
        clan_cats = game.clan.clan_cats
  
        if game.clan.infection["clan_infected"] is True:
            cure_logs.add("start")

        for i in game.clan.infection["logs"]:
            cure_logs.add(i)
        
        game.clan.infection["logs"] = list(cure_logs)
    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.stats_box.kill()
        del self.stats_box

        if self.scroll_container:
            self.scroll_container.kill()
            del self.scroll_container

        if self.next_page_button:
            self.next_page_button.kill()
            del self.next_page_button
        if self.previous_page_button:
            self.previous_page_button.kill()
            del self.previous_page_button

        if self.moon_text_box:
            self.moon_text_box.kill()
            del self.moon_text_box

        if self.treatment_text_box:
            self.treatment_text_box.kill()
            del self.treatment_text_box

        if self.correct_text_box:
            self.correct_text_box.kill()
            del self.correct_text_box

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)
            if event.ui_element == self.next_page_button:
                if self.stage == "logs":
                    self.exit_screen()
                    self.stage = "treatments"
                    self.screen_switches()
            if event.ui_element == self.previous_page_button:
                if self.stage == "treatments":
                    self.exit_screen()
                    self.stage = "logs"
                    self.screen_switches()
    def on_use(self):
        """
        TODO: DOCS
        """
