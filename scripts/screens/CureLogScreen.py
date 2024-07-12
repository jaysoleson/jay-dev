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

from re import sub

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
from ..housekeeping.datadir import get_data_dir, get_cache_dir, get_save_dir
from ..housekeeping.update import has_update, UpdateChannel, get_latest_version_number
from ..housekeeping.version import get_version_info

from scripts.game_structure.image_button import UITextBoxTweaked


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
        self.screen_art = None

        # notes
        self.editing_notes = False
        self.user_notes = None
        self.save_text = None
        self.edit_text = None
        self.display_notes = None

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
            self.screen_art = None
            self.notes_entry = None
            self.display_notes = None
            self.edit_text = None
            self.save_text = None

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
                log = a_txt[i].replace("herb1", str(game.clan.infection["cure"][0])).replace("herb2", str(game.clan.infection["cure"][1])).replace("herb3", str(game.clan.infection["cure"][2])).replace("herb4", str(game.clan.infection["cure"][3]))

                stats_text += "\n" + log
                
            
            self.previous_page_button = UIImageButton(scale(pygame.Rect((100, 700), (68, 68))), "",
                                                    object_id="#arrow_left_button", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((1430, 700), (68, 68))), "",
                                                object_id="#arrow_right_button", manager=MANAGER)

            self.stats_box = pygame_gui.elements.UITextBox(
                stats_text,
                scale(pygame.Rect((200, 250), (1200, 1000))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
            
            if len(game.clan.infection["treatments"]) > 0:
                self.next_page_button.enable()
            else:
                self.next_page_button.disable()
            
        elif self.stage == "treatments":
            logs = 0
            self.set_disabled_menu_buttons(["stats"])
            self.show_menu_buttons()
            self.update_heading_text(f'{game.clan.name}Clan')
            self.notes_entry = None
            self.display_notes = None
            self.edit_text = None
            self.save_text = None

            self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect(
            (100, 350), (730, 790))),
            allow_scroll_x=False,
            manager=MANAGER)

            stats_text = "<b>Treatments:</b>"

            if game.settings["fullscreen"]:
                log_width = 660
                y_offset = 440
            else:
                log_width = 260
                y_offset = 0
                # fullscreen i hate u
            
            
            for treatment in game.clan.infection['treatments']:
                logs += 1
                self.moon_text = f"<b>Moon {treatment['moon']}</b>"
                self.moon_text_box = pygame_gui.elements.UITextBox(self.moon_text,
                                    pygame.Rect((80, y_offset), (log_width, 50)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                
                self.treatment_text = f"{', '.join([herb.replace('_', ' ') for herb in treatment['herbs']])}"
                self.treatment_text_box = pygame_gui.elements.UITextBox(self.treatment_text,
                                    pygame.Rect((80, (y_offset + 20)), (log_width, 100)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                
                # correct_text = f"Effective Herbs: {treatment['correct_herbs']}"
                if int(treatment['correct_herbs']) > 0 and int(treatment['correct_herbs']) < 4:
                    if game.settings["dark mode"]:
                        self.correct_text = f"<font color = '#DBD076'> At least one effective herb </font>"
                    else:
                        self.correct_text = f"<font color = '#473B0A'> At least one effective herb </font>"
                elif int(treatment['correct_herbs']) == 4:
                    if game.settings["dark mode"]:
                        self.correct_text = f"<font color='#A2D86C'>Cure Found!</font>"
                    else:
                        self.correct_text = f"<font color='#136D05'>Cure Found!</font>"
                else:
                    if game.settings["dark mode"]:
                        self.correct_text = f"<font color='#FF0000'>Zero Effective Herbs</font>"
                    else:
                        self.correct_text = f"<font color='#550D0D'>Zero Effective Herbs</font>"

                self.correct_text_box = pygame_gui.elements.UITextBox(self.correct_text,
                                    pygame.Rect((80, (y_offset + 67)), (log_width, 50)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                y_offset += 140

            self.previous_page_button = UIImageButton(scale(pygame.Rect((100, 700), (68, 68))), "",
                                                    object_id="#arrow_left_button", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((1430, 700), (68, 68))), "",
                                                object_id="#arrow_right_button", manager=MANAGER)
            
            if game.settings["dark mode"]:
                self.screen_art = pygame_gui.elements.UIImage(scale(pygame.Rect(((120, 155), (1453, 1260)))),
                                                                 pygame.transform.scale(
                                                                     pygame.image.load(
                                                                         "resources/images/treatment_log_dark.png").convert_alpha(),
                                                                     (1600, 1400)), manager=MANAGER)
            else:
                self.screen_art = pygame_gui.elements.UIImage(scale(pygame.Rect(((120, 155), (1453, 1260)))),
                                                                 pygame.transform.scale(
                                                                     pygame.image.load(
                                                                         "resources/images/treatment_log_light.png").convert_alpha(),
                                                                     (1600, 1400)), manager=MANAGER)

            self.stats_box = pygame_gui.elements.UITextBox(
                stats_text,
                scale(pygame.Rect((270, 250), (500, 1000))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
           
            self.scroll_container.set_scrollable_area_dimensions((1360 / 1600 * screen_x, y_offset + 50))  # Add some padding to y_offset

            # Set the scroll bar to the bottom
            # self.scroll_container.vert_scroll_bar.start_percentage = 1.0

        if self.stage == "notes":
            self.moon_text = None
            self.moon_text_box = None
            self.treatment_text = None
            self.treatment_text_box = None
            self.correct_text = None
            self.correct_text_box = None
            self.scroll_container = None
            self.screen_art = None
            self.save_text = None
            self.edit_text = None

            self.set_disabled_menu_buttons(["stats"])
            self.show_menu_buttons()
            self.update_heading_text(f'{game.clan.name}Clan')
        
            # Determine stats
            stats_text = "<b>Notes:</b>"
            self.load_user_notes()
            if self.user_notes is None:
                self.user_notes = 'INFECTION notes entry'

            self.notes_entry = pygame_gui.elements.UITextEntryBox(
                scale(pygame.Rect((200, 450), (1200, 750))),
                initial_text=self.user_notes,
                object_id='#text_box_26_horizleft_pad_10_14',
                manager=MANAGER
            )
            self.display_notes = UITextBoxTweaked(self.user_notes,
                                              scale(pygame.Rect((200, 450), (120, 750))),
                                              object_id="#text_box_26_horizleft_pad_10_14",
                                              line_spacing=1, manager=MANAGER)
            
            self.previous_page_button = UIImageButton(scale(pygame.Rect((100, 700), (68, 68))), "",
                                                    object_id="#arrow_left_button",manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((1430, 700), (68, 68))), "",
                                                object_id="#arrow_right_button", manager=MANAGER)
            
            self.stats_box = pygame_gui.elements.UITextBox(
                stats_text,
                scale(pygame.Rect((160, 350), (200, 80))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
            
            self.update_notes_buttons()
    
    def save_user_notes(self):
        """Saves user-entered notes. """
        clanname = game.clan.name

        notes = self.user_notes

        notes_directory = get_save_dir() + '/' + clanname + '/notes'
        notes_file_path = 'infection_notes.json'

        if not os.path.exists(notes_directory):
            print("making notes folder")
            os.makedirs(notes_directory)

        if notes is None or notes == 'nonINFECTION notes entry':
            return

        new_notes = {"infection_notes": notes}

        game.safe_save(f"{get_save_dir()}/{clanname}/notes/infection_notes.json", new_notes)

    def load_user_notes(self):
        """Loads user-entered notes. """
        clanname = game.clan.name

        notes_directory = get_save_dir() + '/' + clanname + '/notes'
        notes_file_path = notes_directory + '/infection_notes.json'

        if not os.path.exists(notes_file_path):
            return

        try:
            with open(notes_file_path, 'r') as read_file:
                rel_data = ujson.loads(read_file.read())
                if "infection_notes" in rel_data:
                    self.user_notes = rel_data.get("infection_notes")
        except Exception as e:
            print(f"ERROR: there was an error reading the INFECTION notes file.\n", e)


    def check_logs(self):
        you = game.clan.your_cat
        cure_logs = set()
        clan_cats = game.clan.clan_cats
  
        if game.clan.infection["clan_infected"] is True:
            cure_logs.add("start")

        for i in game.clan.infection["logs"]:
            cure_logs.add(i)
        
        game.clan.infection["logs"] = list(cure_logs)

    def update_notes_buttons(self):
        """ wee """

        if self.save_text:
            self.save_text.kill()
        if self.notes_entry:
            self.notes_entry.kill()
        if self.edit_text:
            self.edit_text.kill()
        if self.display_notes:
            self.display_notes.kill()

        if self.editing_notes is True:
            self.save_text = UIImageButton(scale(pygame.Rect(
                (104, 1028), (68, 68))),
                "",
                object_id="#unchecked_checkbox",
                tool_tip_text='lock and save text', manager=MANAGER
            )

            self.notes_entry = pygame_gui.elements.UITextEntryBox(
                scale(pygame.Rect((200, 450), (1200, 750))),
                initial_text=self.user_notes,
                object_id='#text_box_26_horizleft_pad_10_14', manager=MANAGER
            )
        else:
            self.edit_text = UIImageButton(scale(pygame.Rect(
                (104, 1028), (68, 68))),
                "",
                object_id="#checked_checkbox_smalltooltip",
                tool_tip_text='edit text', manager=MANAGER
            )

            self.display_notes = UITextBoxTweaked(self.user_notes,
                                                    scale(pygame.Rect((200, 450), (1200, 750))),
                                                    object_id="#text_box_26_horizleft_pad_10_14",
                                                    line_spacing=1, manager=MANAGER)
    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.stats_box.kill()
        del self.stats_box

        if self.screen_art:
            self.screen_art.kill()
            del self.screen_art

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
        if self.notes_entry:
            self.notes_entry.kill()
            del self.notes_entry
        if self.display_notes:
            self.display_notes.kill()
            del self.display_notes
        if self.edit_text:
            self.edit_text.kill()
            del self.edit_text
        if self.save_text:
            self.save_text.kill()
            del self.save_text

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
                elif self.stage == "treatments":
                    self.exit_screen()
                    self.stage = "notes"
                    self.screen_switches()
                elif self.stage == "notes":
                    self.exit_screen()
                    self.stage = "logs"
                    self.screen_switches()
            elif event.ui_element == self.previous_page_button:
                if self.stage == "logs":
                    self.exit_screen()
                    self.stage = "notes"
                    self.screen_switches()
                elif self.stage == "treatments":
                    self.exit_screen()
                    self.stage = "logs"
                    self.screen_switches()
                elif self.stage == "notes":
                    self.exit_screen()
                    self.stage = "treatments"
                    self.screen_switches()
            elif event.ui_element == self.save_text:
                self.user_notes = sub(r"[^A-Za-z0-9<->/.()*'&#!?,| _+=@~:;[]{}%$^`]+", "", self.notes_entry.get_text())
                self.save_user_notes()
                self.editing_notes = False
                self.update_notes_buttons()
            elif event.ui_element == self.edit_text:
                self.editing_notes = True
                self.update_notes_buttons()
    def on_use(self):
        """
        TODO: DOCS
        """
