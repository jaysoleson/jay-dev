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
from scripts.game_structure import game
from scripts.game_structure.windows import DeleteCheck, UpdateAvailablePopup, ChangelogPopup, SaveError
from scripts.utility import get_text_box_theme, check_achievements  # pylint: disable=redefined-builtin
from scripts.cat.history import History
from .Screens import Screens
from ..housekeeping.datadir import get_data_dir, get_cache_dir
from ..housekeeping.update import has_update, UpdateChannel, get_latest_version_number
from ..housekeeping.version import get_version_info
from scripts.utility import get_text_box_theme, ui_scale, load_lang_resource
from scripts.game_structure.screen_settings import MANAGER


logger = logging.getLogger(__name__)
has_checked_for_update = False
update_available = False

class AchievementScreen(Screens):
    """
    TODO: DOCS
    """

    def screen_switches(self):
        """
        TODO: DOCS
        """
        super().screen_switches()
        
        self.set_disabled_menu_buttons(["stats"])
        self.show_menu_buttons()
        self.update_heading_text(f'{game.clan.name}Clan')

        a_txt = load_lang_resource("achievements.json")

        check_achievements(Cat)

        # Determine stats
        stats_text = "Achievements:"
        for i in game.clan.achievements:
            stats_text += "\n" + a_txt[i][0] + " - " + a_txt[i][1] 

        self.stats_box = pygame_gui.elements.UITextBox(
            stats_text,
            ui_scale(pygame.Rect((100, 150), (600, 500))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizcenter"))


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
        super().on_use()
