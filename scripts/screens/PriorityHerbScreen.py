import pygame.transform
import pygame_gui.elements
from random import choice, randint
import ujson
import re
import random

from scripts.cat_relations.inheritance import Inheritance
from scripts.cat.history import History
from scripts.event_class import Single_Event
from scripts.events import events_class

from scripts.clan import HERBS

from .Screens import Screens
from scripts.utility import get_personality_compatibility, get_text_box_theme, scale, scale_dimentions, shorten_text_to_fit, pronoun_repl
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.cat.pelts import Pelt
from scripts.game_structure.windows import GameOver, PickPath, DeathScreen
from scripts.game_structure.image_button import UIImageButton, UISpriteButton, UIRelationStatusBar
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.windows import RelationshipLog
from scripts.game_structure.propagating_thread import PropagatingThread

class PriorityHerbScreen(Screens):
    herb_buttons = {}
    herb_displays = {}
    back_button = None

    def __init__(self, name=None):
        super().__init__(name)

        #herb!
        self.priorityherb = None
        self.back_button = None
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
           
            if event.ui_element == self.back_button:
                self.exit_screen()
                self.change_screen('events screen')

            for herb, button in self.herb_buttons.items():

                if event.ui_element == button:
                    if herb == self.priorityherb:
                        self.priorityherb = None
                    else:
                        self.priorityherb = herb
                    self.update_herb_buttons()
                    self.update_text()

    def update_text(self):
        for ele in self.herb_displays:
            self.herb_displays[ele].kill()
        self.herb_displays = {}

        self.herb_displays["title"] = pygame_gui.elements.UITextBox("<u>Priority Herb</u>",
                                                        scale(pygame.Rect((300, 80), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
        
        self.herb_displays["subtitle"] = pygame_gui.elements.UITextBox(f"{game.clan.name}Clan will focus their efforts into finding more:",
                                                        scale(pygame.Rect((300, 880), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)

        if game.settings["dark mode"]:
            self.herb_displays["herbs"] = pygame_gui.elements.UITextBox(f"<font color='#A2D86C'>{self.priorityherb.replace('_', ' ')}</font>",
                                                    scale(pygame.Rect((300, 950), (1000, 80))),
                                                    object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                    manager=MANAGER)
        else:
            self.herb_displays["herbs"] = pygame_gui.elements.UITextBox(f"<font color='#136D05'>{self.priorityherb.replace('_', ' ')}</font>",
                                                    scale(pygame.Rect((300, 950), (1000, 80))),
                                                    object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                    manager=MANAGER)

    def update_herb_buttons(self):
        """ Displays and updates herb buttons """

        for ele in self.herb_buttons:
            self.herb_buttons[ele].kill()
        self.herb_buttons = {}

        x_start = 480
        y_start = 190
        x_spacing = 130
        y_spacing = 130
        grid_size = 5

        x_pos = x_start
        y_pos = y_start

        selected_herbs = [self.priorityherb]
        picked = 0
        for h in selected_herbs:
            if h is not None:
                picked += 1

        for index, herb in enumerate(HERBS):
            if herb != self.priorityherb:
                self.herb_buttons[herb] = UIImageButton(
                    scale(pygame.Rect((x_pos, y_pos), (110, 110))), 
                    "",
                    tool_tip_text=f"{herb.replace('_', ' ')}",
                    object_id=f"#{herb}",
                    manager=MANAGER
                )
            else:
                self.herb_buttons[herb] = UIImageButton(
                    scale(pygame.Rect((x_pos, y_pos), (110, 110))), 
                    "",
                    tool_tip_text=f"{herb.replace('_', ' ')}",
                    object_id=f"#{herb}_selected",
                    manager=MANAGER
                )
            
            if (index + 1) % grid_size == 0:
                x_pos = x_start  # Reset x position for new row
                y_pos += y_spacing  # Move to the next row
            else:
                x_pos += x_spacing  # Move to the next column

    def screen_switches(self):
        
        self.priorityherb = game.clan.infection["priority_herb"]
        self.update_herb_buttons()

        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")

        self.update_text()

    def exit_screen(self):
        game.clan.infection["priority_herb"] = self.priorityherb

        for ele in self.herb_buttons:
            self.herb_buttons[ele].kill()
        self.herb_buttons = {}

        for ele in self.herb_displays:
            self.herb_displays[ele].kill()
        self.herb_displays = {}
    
        if self.back_button:
            self.back_button.kill()
            del self.back_button