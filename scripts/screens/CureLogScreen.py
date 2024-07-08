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

    def screen_switches(self):
        """
        TODO: DOCS
        """
        
        self.set_disabled_menu_buttons(["stats"])
        self.show_menu_buttons()
        self.update_heading_text(f'{game.clan.name}Clan')
        a_txt = ""
        with open('resources/dicts/infection/logs.json', 'r', encoding='utf-8') as f:
            a_txt = ujson.load(f)

        self.check_logs()
        
        
        # Determine stats
        stats_text = "Logs:"
        for i in game.clan.infection["logs"]:
            stats_text += "\n" + a_txt[i]
            
            

        self.stats_box = pygame_gui.elements.UITextBox(
            stats_text,
            scale(pygame.Rect((200, 300), (1200, 1000))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizcenter"))

    def check_logs(self):
        you = game.clan.your_cat
        cure_logs = set()
        clan_cats = game.clan.clan_cats

        print(game.clan.infection)
  
        if game.clan.infection["clan_infected"] is True:
            cure_logs.add("1")

        for i in game.clan.infection["logs"]:
            cure_logs.add(i)
        
        game.clan.infection["logs"] = list(cure_logs)
    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.stats_box.kill()
        del self.stats_box

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)

    def on_use(self):
        """
        TODO: DOCS
        """
