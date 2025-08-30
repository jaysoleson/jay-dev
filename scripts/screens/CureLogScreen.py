# pylint: disable=line-too-long
# pylint: enable=line-too-long

import logging
import os

from re import sub

import pygame
import pygame_gui
import ujson

from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import UIImageButton
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    get_infection_herb,
    ui_scale_dimensions
    )  # pylint: disable=redefined-builtin
from .Screens import Screens
from ..housekeeping.datadir import get_save_dir

from scripts.game_structure import image_cache

from scripts.cat.history import History
from scripts.cat.cats import Cat
from scripts.clan import Clan
from scripts.cat.pelts import Pelt

from scripts.game_structure.ui_elements import UITextBoxTweaked, UISurfaceImageButton
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon


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

        self.x_buttons = {}
        self.x_treatment = None

        # notes
        self.editing_notes = False
        self.user_notes = None
        self.save_text = None
        self.edit_text = None
        self.display_notes = None

        self.journalart = None
        self.stamps = {}

    
    def check_achivements(self):
        # this is still here for the stamps
        you = game.clan.your_cat
        achievements = set()
        murder_history = History.get_murders(you)
        clan_cats = game.clan.clan_cats
        count_alive_cats = 0
        if murder_history:
            if 'is_murderer' in murder_history:
                num_victims = len(murder_history["is_murderer"])
                if num_victims >= 0:
                    achievements.add("1")
                if num_victims >= 5:
                    achievements.add("2")
                if num_victims >= 20:
                    achievements.add("3")
                if num_victims >= 50:
                    achievements.add("4")
        else:
            if you.moons >= 120:
                achievements.add("25")
                
        for cat in clan_cats:
            if Cat.all_cats.get(cat).pelt.tortiebase and Cat.all_cats.get(cat).gender == 'male':
                achievements.add("5")
            if Cat.all_cats.get(cat).insulted == True:
                achievements.add("29")
            if (Cat.all_cats.get(cat).name.prefix == "Coffee" and Cat.all_cats.get(cat).name.suffix == "dot") or (Cat.all_cats.get(cat).name.prefix == "Chibi" and Cat.all_cats.get(cat).name.suffix == "Galaxies"):
                achievements.add("30")
            if Cat.all_cats.get(cat).status == 'apprentice' and Cat.all_cats.get(cat).name.prefix == "Pea" and Cat.all_cats.get(cat).pelt.white_colours:
                achievements.add("33")
            if Cat.all_cats.get(cat).status == 'kitten' and Cat.all_cats.get(cat).moons > 5:
                achievements.add("34")
            ##WILDCARD check, because I've lost control of my life
            ##Declare Lists of wildcard combos for comparison. (Will be made more professional later.)
            not_wildcard_patterns = ['tabby', 'ticked', 'mackerel', 'classic', 'agouti', 'smoke', 'single']
            ##Actual check for wildcardness
            if Cat.all_cats.get(cat).pelt.name == "Tortie" or Cat.all_cats.get(cat).pelt.name == "Calico":
                ID_check = Cat.all_cats.get(cat).ID 
                ##Check if wildcard colour combo
                if (Cat.all_cats.get(cat).pelt.colour == "WHITE" and not Cat.all_cats.get(cat).pelt.tortiecolour == "WHITE"):
                    achievements.add("6")
                elif ((Cat.all_cats.get(cat).pelt.colour in Pelt.black_colours or Cat.all_cats.get(cat).pelt.colour in Pelt.white_colours) and Cat.all_cats.get(cat).pelt.tortiecolour in Pelt.black_colours or Cat.all_cats.get(cat).pelt.tortiecolour in Pelt.white_colours):
                    achievements.add("6")
                elif ((Cat.all_cats.get(cat).pelt.colour in Pelt.ginger_colours) and Cat.all_cats.get(cat).pelt.tortiecolour in Pelt.ginger_colours or Cat.all_cats.get(cat).pelt.tortiecolour in Pelt.white_colours):
                    achievements.add("6")
                elif ((Cat.all_cats.get(cat).pelt.colour in Pelt.brown_colours) and Cat.all_cats.get(cat).pelt.tortiecolour in Pelt.white_colours):
                    achievements.add("6")
                ##Check if wildcard pattern combo       
                ##rewritten wildcard pattern combo
                if Cat.all_cats.get(cat).pelt.tortiebase in Pelt.tabbies and not Cat.all_cats.get(cat).pelt.tortiepattern == "single" and Cat.all_cats.get(cat).pelt.tortiebase != Cat.all_cats.get(cat).pelt.tortiepattern:
                    achievements.add("6")
                if Cat.all_cats.get(cat).pelt.tortiebase in Pelt.spotted and not Cat.all_cats.get(cat).pelt.tortiepattern == "single" and Cat.all_cats.get(cat).pelt.tortiebase != Cat.all_cats.get(cat).pelt.tortiepattern:
                    achievements.add("6")
                if Cat.all_cats.get(cat).pelt.tortiebase in Pelt.exotic and not Cat.all_cats.get(cat).pelt.tortiepattern == "single" and Cat.all_cats.get(cat).pelt.tortiebase != Cat.all_cats.get(cat).pelt.tortiepattern:
                    achievements.add("6")
                if Cat.all_cats.get(cat).pelt.tortiebase in Pelt.plain and not Cat.all_cats.get(cat).pelt.tortiepattern in not_wildcard_patterns and Cat.all_cats.get(cat).pelt.tortiebase != Cat.all_cats.get(cat).pelt.tortiepattern:
                    achievements.add("6")
            ##code block for achievement 31
            achieve31RankList = ['warrior', 'mediator', 'leader']
            achieve31UsedRanks = []
            if len(Cat.all_cats.get(cat).mates) >= 2:
                catMateIDs = Cat.all_cats.get(cat).mate.copy()
                if Cat.all_cats.get(cat).status in achieve31RankList:
                    achieve31UsedRanks.append(Cat.all_cats.get(cat).status)
                    for cat in clan_cats:
                        if Cat.all_cats.get(cat).ID in catMateIDs:
                            if (Cat.all_cats.get(cat).status in achieve31RankList) and (Cat.all_cats.get(cat).status not in achieve31UsedRanks):
                                achieve31UsedRanks.append(Cat.all_cats.get(cat).status)
                        countranks = 0
                        for i in achieve31UsedRanks:
                            if i in achieve31RankList:
                                countranks += 1
                            if countranks >= 3:
                                achievements.add("31")
        #code for achievement 23 + 24
            if Clan.age >= 1:                          
                if not Cat.all_cats.get(cat).dead and not Cat.all_cats.get(cat).outside:
                    count_alive_cats += 1
                if count_alive_cats == 1 and Cat.all_cats.get(cat).ID == you.ID:
                    achievements.add('23')
                elif count_alive_cats >= 100:
                    achievements.add('24')

        if you.joined_df:
            achievements.add("7")
        
        if len(you.former_apprentices) >= 1:
            achievements.add("8")
        if len(you.former_apprentices) >= 5:
            achievements.add("9")
        
        if you.inheritance.get_children():
            achievements.add("10")
        for i in you.relationships.keys():
            if you.relationships.get(i).dislike >= 60:
                achievements.add("11")
            if you.relationships.get(i).romantic_love >= 60:
                achievements.add('12')
            
        if len(you.mates) >= 5:
            achievements.add('13')
        if you.status == 'warrior':
            achievements.add('14')
        elif you.status == 'medicine cat':
            achievements.add('15')
        elif you.status == 'mediator':
            achievements.add('16')
        elif you.status == 'deputy':
            achievements.add('17')
        elif you.status == 'leader':
            achievements.add('18')
        elif you.status == 'elder':
            achievements.add('19')
        elif you.status == 'queen':
            achievements.add('32')
        
        if you.moons >= 200:
            achievements.add('20')
        if you.exiled:
            achievements.add('21')
        elif you.outside:
            achievements.add('22')
            
        if you.experience >= 100:
            achievements.add('26')
        if you.experience >= 200:
            achievements.add('27')
        if you.experience >= 300:
            achievements.add('28')        
        
        for i in game.clan.achievements:
            achievements.add(i)
        
        game.clan.achievements = list(achievements)


    def screen_switches(self):
        """
        TODO: DOCS
        """
        super().screen_switches()
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
            self.x_buttons = {}
            self.x_treatment = None

            self.set_disabled_menu_buttons(["stats"])
            self.show_menu_buttons()
            self.update_heading_text(f'{game.clan.name}Clan')
            a_txt = ""
            with open('resources/dicts/infection/logs.json', 'r', encoding='utf-8') as f:
                a_txt = ujson.load(f)
                
            journal = pygame.transform.scale(image_cache.load_image("resources/images/journal_dark.png").convert_alpha(), (800, 700))
            
            # notes
            self.scroll_container = pygame_gui.elements.UIScrollingContainer(ui_scale(pygame.Rect(
            (385, 160), (270, 370))),
            allow_scroll_x=False,
            manager=MANAGER)

            self.set_disabled_menu_buttons(["stats"])
            self.show_menu_buttons()
            self.update_heading_text(f'{game.clan.name}Clan')

            stats_text = "<b>Journal:</b>"
            self.load_user_notes()
            if self.user_notes is None:
                self.user_notes = 'Take your notes here.'

            self.notes_entry = pygame_gui.elements.UITextEntryBox(
                ui_scale(pygame.Rect((22, 25), (240, 375))),
                initial_text=self.user_notes,
                container=self.scroll_container,
                object_id='#text_box_26_horizleft_pad_10_14',
                manager=MANAGER
            )
            self.display_notes = UITextBoxTweaked(
                self.user_notes,
                ui_scale(pygame.Rect((22, 25), (60, 375))),
                object_id="#text_box_26_horizleft_pad_10_14",
                container=self.scroll_container,
                line_spacing=1, manager=MANAGER
                )

            self.journalart = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (582, 416))),
                journal,
                manager=MANAGER,
                anchors={"centerx": "centerx",
                         "centery": "centery"},
            )
                
            self.previous_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((315, 595), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((451, 595), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            # logs !

            infologs = [i for i in game.clan.infection["logs"]]
            stats_text = ""
            cure_herbs = []
            for num in game.clan.infection["cure"]:
                cure_herbs.append(get_infection_herb(num))
            for i in infologs:
                log = a_txt[i].replace(
                    "herb1", str(cure_herbs[0])
                    ).replace(
                        "herb2", str(cure_herbs[1])
                        ).replace(
                            "herb3", str(cure_herbs[2])
                            ).replace(
                                "herb4", str(cure_herbs[3])
                                ) # lol
                
                stats_text += "- " + log.replace("_", " ") + "\n" + "<br>"

            self.heading1 = pygame_gui.elements.UITextBox(
                "<b>Events:</b>",
                ui_scale(pygame.Rect((105, 110), (280, 30))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))

            self.heading2 = pygame_gui.elements.UITextBox(
                "<b>Information:</b>",
                ui_scale(pygame.Rect((400, 110), (280, 30))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
            
            self.stats_box = pygame_gui.elements.UITextBox(
                f"<font color='#120905'>{stats_text}</font>",
                ui_scale(pygame.Rect((155, 170), (235, 360))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_26_horizleft_pad_10_14"))
            
            if len(game.clan.infection["treatments"]) > 0:
                self.next_page_button.enable()
            else:
                self.next_page_button.disable()

            self.update_notes_buttons()
            
        elif self.stage == "treatments":
            logs = 0
            self.set_disabled_menu_buttons(["stats"])
            self.show_menu_buttons()
            self.update_heading_text(f'{game.clan.name}Clan')
            self.notes_entry = None
            self.display_notes = None
            self.edit_text = None
            self.save_text = None
            self.journalart = None
            self.heading1 = None
            self.heading2 = None

            # fixes asters crash
            self.moon_text = None
            self.moon_text_box = None
            self.treatment_text = None
            self.treatment_text_box = None
            self.correct_text_box = None
            self.x_buttons = {}

            self.scroll_container = pygame_gui.elements.UIScrollingContainer(ui_scale(pygame.Rect(
            (50, 175), (365, 395))),
            allow_scroll_x=False,
            manager=MANAGER)

            stats_text = "<b>Treatments</b>"

            if game.settings["fullscreen"]:
                fullscreen = True
            else:
                fullscreen = False

            if fullscreen:
                log_width = 300
                y_offset = 0
                info_x = 125
            else:
                log_width = 230
                y_offset = 0
                info_x = 105
            
            x_button_y_offset = 5
            button_x = 70
            
            
            for treatment in game.clan.infection['treatments']:
                logs += 1

                self.x_buttons[str(treatment['moon'])] = UIImageButton(ui_scale(pygame.Rect((button_x, x_button_y_offset), (25, 25))),
                                "",
                                object_id="#exit_window_button",
                                tool_tip_text=f"Delete moon {str(treatment['moon'])}'s entry (cannot be undone!)",
                                container=self.scroll_container,
                                manager=MANAGER
                            )
                
                self.x_treatment = treatment

                self.moon_text = f"<b>Moon {treatment['moon']}</b>"
                self.moon_text_box = pygame_gui.elements.UITextBox(self.moon_text,
                                    pygame.Rect((info_x, y_offset), (log_width, 35)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizleft"))
                
                offset2 = 25
                self.treatment_text = f"{', '.join([herb.replace('_', ' ') for herb in treatment['herbs']])}"
                
                # correct_text = f"Effective Herbs: {treatment['correct_herbs']}"
                if int(treatment['correct_herbs']) > 0 and int(treatment['correct_herbs']) < 4:
                    if game.settings["dark mode"]:
                        self.correct_text = "<font color='#DBD076'>At least one effective herb</font>"
                    else:
                        self.correct_text = "<font color='#473B0A'>At least one effective herb</font>"
                elif int(treatment['correct_herbs']) == 4:
                    if game.settings["dark mode"]:
                        self.correct_text = "<font color='#A2D86C'>Cure Found!</font>"
                    else:
                        self.correct_text = "<font color='#136D05'>Cure Found!</font>"
                else:
                    if game.settings["dark mode"]:
                        self.correct_text = "<font color='#FF0000'>Zero Effective Herbs</font>"
                    else:
                        self.correct_text = "<font color='#550D0D'>Zero Effective Herbs</font>"

                self.treatment_text_box = pygame_gui.elements.UITextBox(
                    self.treatment_text + "\n" + self.correct_text,
                    pygame.Rect((info_x, (y_offset + offset2)), (log_width, 90)),
                    container=self.scroll_container,
                    manager=MANAGER,
                    object_id=get_text_box_theme("#text_box_26_horizleft"))
                
                y_offset += 120
                if fullscreen:
                    x_button_y_offset += 96
                else:
                    x_button_y_offset += 120

            self.previous_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((315, 595), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((451, 595), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            
            if game.settings["dark mode"]:
                imagesrc = "resources/images/treatment_log_dark.png"
            else:
                imagesrc = "resources/images/treatment_log_light.png"

            self.screen_art = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect(((60, 77), (726, 630)))),
                pygame.transform.scale(
                    pygame.image.load(
                        "resources/images/treatment_log_dark.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((726, 630))
                    ),
                manager=MANAGER
                )

            self.stats_box = pygame_gui.elements.UITextBox(
                stats_text,
                ui_scale(pygame.Rect((120, 125), (350, 50))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizleft"))
           
            self.scroll_container.set_scrollable_area_dimensions((100, y_offset + 25))

        elif self.stage == "stamps":
            self.set_disabled_menu_buttons(["stats"])
            self.show_menu_buttons()
            self.update_heading_text(f'{game.clan.name}Clan')
            self.notes_entry = None
            self.moon_text = None
            self.moon_text_box = None
            self.treatment_text = None
            self.treatment_text_box = None
            self.correct_text = None
            self.correct_text_box = None
            self.save_text = None
            self.edit_text = None
            self.screen_art = None
            self.scroll_container = None
            self.display_notes = None
            self.journalart = None

            self.x_buttons = {}
            self.x_treatment = None

            self.heading1 = None
            self.heading2 = None
            
            self.previous_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((315, 595), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((451, 595), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )

            self.stats_box = pygame_gui.elements.UITextBox(
                "<b>Journal Stamps</b>",
                ui_scale(pygame.Rect((0, 110), (350, 50))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                anchors={"centerx": "centerx"})

            if len(game.clan.infection["treatments"]) > 0:
                self.previous_page_button.enable()
            else:
                self.previous_page_button.disable()

            # JOURNAL STAMPS
            # wwhoooaaaaoo
            self.show_journal_stamps()
    
    def show_journal_stamps(self):
        self.check_achivements()
        # chibi misspelled the function and im keeping it that way bc its funny

        debug_all_stamps = False

        # MURDER
        murderer = False
        # doing this so stamps can change if u switch mc to a non murderer
        if not game.clan.your_cat.history:
            game.clan.your_cat.load_history()
        if game.clan.your_cat.history:
            if game.clan.your_cat.history.murder:
                if "is_murderer" in game.clan.your_cat.history.murder:
                    for murder in game.clan.your_cat.history.murder["is_murderer"]:
                        victim = Cat.fetch_cat(murder["victim"])
                        if not victim.history:
                            victim.load_history()
                        if victim.history:
                            if victim.history.died_infected:
                                if victim.history.died_infected is True:
                                    murderer = True
                                    break

        if murderer or debug_all_stamps:
            hover = "<b>The Greater Good</b>\nTake matters into your own hands and kill an infected Clanmate."
            self.stamps["murder"] = UIImageButton(
                ui_scale(pygame.Rect((200, 205), (94, 94))),
                "",
                object_id="#stamp_infection_murder",
                tool_tip_text=f"{hover}",
                manager=MANAGER
                )

        elif "25" in game.clan.achievements:
            self.stamps["pacifist"] = UIImageButton(
                ui_scale(pygame.Rect((190, 225), (78, 38))),
                "",
                object_id="#stamp_pacifist",
                tool_tip_text="<b>Pacifist</b>\nLived to be 120 moons without committing a murder",
                manager=MANAGER
                )
        
        empty_stamp = pygame.transform.scale(
            image_cache.load_image("resources/images/journal_stamps/empty_stamp.png").convert_alpha(), (134, 94))
        empty_stamps = 0
    
        if "pacifist" not in self.stamps and "murder" not in self.stamps:
            empty_stamps += 1
            self.stamps[str(empty_stamps)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((200, 205), (94, 94))),
                empty_stamp,
                manager=MANAGER
            )
        
        if "start" in game.clan.infection["logs"] or debug_all_stamps:
            self.stamps["start"] = UIImageButton(
                ui_scale(pygame.Rect((0, 0), (74, 118))),
                "",
                object_id=f"#{game.clan.infection['infection_type']}_stamp_start",
                tool_tip_text=f"<b>LifeGen: INFECTION</b>\nYou've discovered the infection ({game.clan.infection['infection_type']}).",
                manager=MANAGER,
                anchors={"centerx": "centerx", "centery": "centery"}
                )
            
        if "cure_found" in game.clan.infection["logs"] or debug_all_stamps:
            self.stamps["cure_discovered"] = UIImageButton(
                ui_scale(pygame.Rect((0, 160), (94, 94))),
                "",
                object_id="#stamp_cure",
                tool_tip_text="<b>Cured!</b>\nYou've discovered the cure!",
                manager=MANAGER,
                anchors={"centerx": "centerx"}
                )
        elif "partial_cure" in game.clan.infection["logs"]:
            self.stamps["partial_cure"] = UIImageButton(
                ui_scale(pygame.Rect((0, 160), (94, 94))),
                "",
                object_id="#stamp_partial_cure",
                tool_tip_text="<b>Partial Cure</b>\nPart of the cure has been discovered!",
                manager=MANAGER,
                anchors={"centerx": "centerx"}
                )
        else:
            empty_stamps += 1
            self.stamps[str(empty_stamps)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 160), (94, 94))),
                empty_stamp,
                manager=MANAGER,
                anchors={"centerx": "centerx"}
            )

        cured_cats = len(game.clan.infection["cured_infected"].split(",")) if game.clan.infection["cured_infected"] else 0
        killed_cats = len(game.clan.infection["killed_infected"].split(",")) if game.clan.infection["killed_infected"] else 0
        exiled_cats = len(game.clan.infection["exiled_infected"].split(",")) if game.clan.infection["exiled_infected"] else 0

        largest = max(cured_cats, killed_cats, exiled_cats)

        if debug_all_stamps:
            killed_cats = 5
            largest = killed_cats

        if largest == cured_cats:
            text = f"You've chosen to deal with the infection by curing your Clanmates ({cured_cats} cats cured)!"
            stamp_id = "#stamp_cured_infected"
        elif largest == killed_cats:
            text = f"You've chosen to deal with the infection by killing the infected ({killed_cats} infected cats killed)."
            stamp_id = "#stamp_killed_infected"
        else:
            text = f"You've chosen to deal with the infection by exiling the infected ({exiled_cats} infected cats exiled)."
            stamp_id = "#stamp_exiled_infected"

        if largest == 0:
            self.stamps["playstyle"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 460), (94, 94))),
                empty_stamp,
                manager=MANAGER,
                anchors={"centerx": "centerx"}
            )
        else:
            self.stamps["playstyle"] = UIImageButton(
                ui_scale(pygame.Rect((0, 460), (94, 94))),
                "",
                object_id=stamp_id,
                tool_tip_text="<b>Damage Control</b>\n" + text,
                manager=MANAGER,
                anchors={"centerx": "centerx"}
                )
            
        fallenclans = []
        for clan in game.clan.all_clans:
            if clan.fallen:
                fallenclans.append(clan)
        
        if fallenclans or debug_all_stamps:
            if debug_all_stamps:
                fallenclans = 5
            
            if fallenclans == 1:
                hovertext = f"<b>Fallen Clans</b>\n{fallenclans} Clan has fallen to the infection."
            else:
                hovertext = f"<b>Fallen Clans</b>\n{fallenclans} Clans have fallen to the infection."

            self.stamps["fallen_clans"] = UIImageButton(
                ui_scale(pygame.Rect((500, 205), (94, 94))),
                "",
                object_id=f"#stamp_fallen_clans_{fallenclans}",
                tool_tip_text=hovertext,
                manager=MANAGER
                )
        else:
            empty_stamps += 1
            self.stamps[str(empty_stamps)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((500, 205), (94, 94))),
                empty_stamp,
                manager=MANAGER
            )

        if "zombie" in game.clan.infection["logs"] or debug_all_stamps:
            self.stamps["zombie"] = UIImageButton(
                ui_scale(pygame.Rect((500, 360), (94, 94))),
                "",
                object_id="#stamp_zombie",
                tool_tip_text="<b>Zombie</b>\nCats have begun dying and coming back to life.",
                manager=MANAGER
                )
        else:
            empty_stamps += 1
            self.stamps[str(empty_stamps)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((500, 360), (94, 94))),
                empty_stamp,
                manager=MANAGER
            )

        if game.clan.your_cat.status in ["warrior", "leader", "deputy", "medicine cat", "mediator", "queen"]:
            self.stamps["status"] = UIImageButton(
                ui_scale(pygame.Rect((200, 360), (94, 94))),
                "",
                object_id=f"#stamp_{(game.clan.your_cat.status).replace(' ', '_')}",
                tool_tip_text=f"<b>Your Calling</b>\nYou've chosen the path of a {game.clan.your_cat.status}!",
                manager=MANAGER
                )
        elif game.clan.your_cat.status == "elder":
            self.stamps["status"] = UIImageButton(
                ui_scale(pygame.Rect((200, 360), (94, 94))),
                "",
                object_id="#stamp_warrior",
                tool_tip_text="You've lived to be an elder.",
                manager=MANAGER
                )
        else:
            empty_stamps += 1
            self.stamps[str(empty_stamps)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((200, 400), (94, 94))),
                empty_stamp,
                manager=MANAGER
            )
    
    def on_use(self):
        super().on_use()
    
    def save_user_notes(self):
        """Saves user-entered notes. """
        clanname = game.clan.name

        notes = self.user_notes

        notes_directory = get_save_dir() + '/' + clanname + '/notes'

        if not os.path.exists(notes_directory):
            os.makedirs(notes_directory)

        if notes is None or notes == 'Take your notes here.':
            return

        new_notes = {"infection_notes": notes}

        game.safe_save(f"{get_save_dir()}/{clanname}/notes/infection_notes.json", new_notes)

    def load_user_notes(self):
        """Loads user-entered notes. """
        clanname = game.clan.name

        notes_directory = get_save_dir() + '/' + clanname + '/notes'
        notes_file_path = notes_directory + '/infection_notes.json'

        if not os.path.exists(notes_file_path):
            self.user_notes = None
            return

        try:
            with open(notes_file_path, 'r') as read_file:
                rel_data = ujson.loads(read_file.read())
                if "infection_notes" in rel_data:
                    self.user_notes = rel_data.get("infection_notes")
        except Exception as e:
            print("ERROR: there was an error reading the INFECTION notes file.\n", e)

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
            self.save_text = UISurfaceImageButton(
                ui_scale(pygame.Rect((705, 175), (80, 30))),
                "save",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (80, 30)),
                object_id="@buttonstyles_rounded_rect",
                starting_height=0,
            )

            self.notes_entry = pygame_gui.elements.UITextEntryBox(
                ui_scale(pygame.Rect((22, 25), (240, 305))),
                initial_text=self.user_notes,
                container=self.scroll_container,
                object_id='#text_box_26_horizleft_pad_10_14', manager=MANAGER
            )
        else:
            self.edit_text = UISurfaceImageButton(
                ui_scale(pygame.Rect((705, 175), (80, 30))),
                "edit",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (80, 30)),
                object_id="@buttonstyles_rounded_rect",
                starting_height=0,
            )

            self.display_notes = UITextBoxTweaked(
                self.user_notes,
                ui_scale(pygame.Rect((22, 20), (240, 305))),
                object_id="#text_box_26_horizleft_pad_10_14",
                container=self.scroll_container,
                line_spacing=1,
                manager=MANAGER
                )
            
    def exit_screen(self):
        """
        TODO: DOCS
        """
        if self.stats_box:
            self.stats_box.kill()
            del self.stats_box

        if self.heading1:
            self.heading1.kill()
            del self.heading1
        
        if self.heading2:
            self.heading2.kill()
            del self.heading2

        for ele in self.stamps:
            self.stamps[ele].kill()
        self.stamps = {}

        for ele in self.x_buttons:
            self.x_buttons[ele].kill()
        self.x_buttons = {}

        if self.screen_art:
            self.screen_art.kill()
            del self.screen_art

        if self.journalart:
            self.journalart.kill()
            del self.journalart

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

        
        self.x_treatment = None

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

    def delete_entry(self, treatment):
        treatment_to_remove = None
        for i in game.clan.infection["treatments"]:
            if int(i["moon"]) == int(treatment):
                treatment_to_remove = i
                break
        if treatment_to_remove is not None:
            if treatment_to_remove in game.clan.infection["treatments"]:
                game.clan.infection["treatments"].remove(treatment_to_remove)
                self.exit_screen()
                self.screen_switches()

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
                    self.stage = "stamps"
                    self.screen_switches()
                elif self.stage == "stamps":
                    self.exit_screen()
                    self.stage = "logs"
                    self.screen_switches()
            elif event.ui_element == self.previous_page_button:
                if self.stage == "logs":
                    self.exit_screen()
                    self.stage = "stamps"
                    self.screen_switches()
                elif self.stage == "treatments":
                    self.exit_screen()
                    self.stage = "logs"
                    self.screen_switches()
                elif self.stage == "stamps":
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
            for treatment, button in self.x_buttons.items():
                if event.ui_element == button:
                    self.delete_entry(treatment)