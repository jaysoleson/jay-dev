# pylint: disable=line-too-long
# pylint: enable=line-too-long

import logging
import os

from re import sub

import pygame
import pygame_gui
import ujson

from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.ui_elements import UIImageButton
from scripts.utility import get_text_box_theme, scale  # pylint: disable=redefined-builtin
from .Screens import Screens
from ..housekeeping.datadir import get_save_dir

from scripts.game_structure import image_cache

from scripts.cat.history import History
from scripts.cat.cats import Cat
from scripts.clan import Clan
from scripts.cat.pelts import Pelt

from scripts.game_structure.ui_elements import UITextBoxTweaked


logger = logging.getLogger(__name__)
has_checked_for_update = False
update_available = False



class CureLogScreen(Screens):
    """
    TODO: DOCS
    """
    stamps = {}
    journalart = None

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
            if len(Cat.all_cats.get(cat).mate) >= 2:
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
            
        if len(you.mate) >= 5:
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
        

            width_scale_factor = 1300 / 1600
            height_scale_factor = 820 / 1300

            # Adjust scaling factors to make the image smaller
            adjustment_factor = 0.95  # 90% of the original size
            width_scale_factor *= adjustment_factor
            height_scale_factor *= adjustment_factor
                
            if game.settings["dark mode"]:
                self.journalart = pygame.transform.scale(image_cache.load_image("resources/images/journal_dark.png").convert_alpha(),
                                        (width_scale_factor * screen_x, height_scale_factor * screen_y))
            else:
                self.journalart = pygame.transform.scale(image_cache.load_image("resources/images/journal_dark.png").convert_alpha(),
                                        (width_scale_factor * screen_x, height_scale_factor * screen_y))
                
            self.previous_page_button = UIImageButton(scale(pygame.Rect((100, 700), (68, 68))), "",
                                                    object_id="#arrow_left_button", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((1430, 700), (68, 68))), "",
                                                object_id="#arrow_right_button", manager=MANAGER)
            # logs !
            sc1 = Cat.all_cats.get(game.clan.infection["story_cat_1"])
            sc2 = Cat.all_cats.get(game.clan.infection["story_cat_2"])
            sc3 = Cat.all_cats.get(game.clan.infection["story_cat_3"])
            sc4 = Cat.all_cats.get(game.clan.infection["story_cat_4"])

            infologs = [i for i in game.clan.infection["logs"] if not i.startswith("story_")]
            storylogs = [i for i in game.clan.infection["logs"] if i.startswith("story_")]
            stats_text = ""
            for i in infologs:
                log = a_txt[i].replace("herb1", str(game.clan.infection["cure"][0])).replace("herb2", str(game.clan.infection["cure"][1])).replace("herb3", str(game.clan.infection["cure"][2])).replace("herb4", str(game.clan.infection["cure"][3]))
                
                stats_text += "-" + log + "\n" + "<br>"

            stats_text2 = ""
            for i in storylogs:
                sc1name = str(sc1.name) if sc1 else ""
                sc2name = str(sc2.name) if sc2 else ""
                sc3name = str(sc3.name) if sc3 else ""
                sc4name = str(sc4.name) if sc4 else ""

                log2 = a_txt[i].replace("sc1", f"<font color='#011E39'><b>{sc1name}</b></font>").replace("sc2", f"<font color='#263518'><b>{sc2name}</b></font>").replace("sc3", f"<font color='#331A56'><b>{sc3name}</b></font>").replace("sc4", f"<font color='#24123D'><b>{sc4name}</b></font>")

                stats_text2 += "-" + log2 + "\n" + "<br>"

            self.heading1 = pygame_gui.elements.UITextBox(
                f"<b>Information:</b>",
                scale(pygame.Rect((200, 220), (560, 60))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))

            self.heading2 = pygame_gui.elements.UITextBox(
                f"<b>Story:</b>",
                scale(pygame.Rect((800, 220), (560, 60))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
            
            self.stats_box = pygame_gui.elements.UITextBox(
                f"<font color='#120905'>{stats_text}</font>",
                scale(pygame.Rect((260, 340), (530, 720))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
            
            self.stats_box2 = pygame_gui.elements.UITextBox(
                f"<font color='#120905'>{stats_text2}</font>",
                scale(pygame.Rect((820, 340), (530, 720))),
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
            self.journalart = None
            self.heading1 = None
            self.heading2 = None

            self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect(
            (100, 350), (730, 790))),
            allow_scroll_x=False,
            manager=MANAGER)

            stats_text = "<b>Treatments:</b>"

            if game.settings["fullscreen"]:
                log_width = 660
                y_offset = 0
                x_button_y_offset = 0
            else:
                log_width = 260
                y_offset = 0
                x_button_y_offset = 25
                # fullscreen i hate u
            
            
            for treatment in game.clan.infection['treatments']:
                logs += 1

                self.x_buttons[str(treatment['moon'])] = UIImageButton(scale(pygame.Rect((120, x_button_y_offset), (50, 50))),
                                "X",
                                object_id="#exit_window_button",
                                tool_tip_text=f"Delete moon {str(treatment['moon'])}'s entry (cannot be undone!)",
                                container=self.scroll_container,
                                manager=MANAGER
                            )
                
                self.x_treatment = treatment

                self.moon_text = f"<b>Moon {treatment['moon']}</b>"
                self.moon_text_box = pygame_gui.elements.UITextBox(self.moon_text,
                                    pygame.Rect((80, y_offset), (log_width, 50)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                
                if game.settings["fullscreen"]:
                    offset2 = 40
                else:
                    offset2 = 20

                
                self.treatment_text = f"{', '.join([herb.replace('_', ' ') for herb in treatment['herbs']])}"
                self.treatment_text_box = pygame_gui.elements.UITextBox(self.treatment_text,
                                    pygame.Rect((80, (y_offset + offset2)), (log_width, 100)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                
                # correct_text = f"Effective Herbs: {treatment['correct_herbs']}"
                if int(treatment['correct_herbs']) > 0 and int(treatment['correct_herbs']) < 4:
                    if game.settings["dark mode"]:
                        self.correct_text = "<font color = '#DBD076'> At least one effective herb </font>"
                    else:
                        self.correct_text = "<font color = '#473B0A'> At least one effective herb </font>"
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

                if game.settings["fullscreen"]:
                    offset3 = 130
                else:
                    offset3 = 67
                self.correct_text_box = pygame_gui.elements.UITextBox(self.correct_text,
                                    pygame.Rect((80, (y_offset + offset3)), (log_width, 50)),
                                    container=self.scroll_container,
                                    manager=MANAGER,
                                    object_id=get_text_box_theme("#text_box_30_horizcenter"))
                
                if game.settings["fullscreen"]:
                    y_offset += 240
                    x_button_y_offset += 240
                else:
                    y_offset += 140
                    x_button_y_offset += 280
                # FULLSCREEN YOU SUCK

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
            
            self.stats_box2 = None
           
            self.scroll_container.set_scrollable_area_dimensions((1360 / 1600 * screen_x, y_offset + 50))

        if self.stage == "notes":
            self.moon_text = None
            self.moon_text_box = None
            self.treatment_text = None
            self.treatment_text_box = None
            self.correct_text = None
            self.correct_text_box = None
            self.save_text = None
            self.edit_text = None
            self.screen_art = None

            self.x_buttons = {}
            self.x_treatment = None

            self.heading1 = None
            self.heading2 = None

            self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect(
            (790, 290), (800, 910))),
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
                scale(pygame.Rect((45, 50), (480, 750))),
                initial_text=self.user_notes,
                container=self.scroll_container,
                object_id='#text_box_26_horizleft_pad_10_14',
                manager=MANAGER
            )
            self.display_notes = UITextBoxTweaked(self.user_notes,
                                              scale(pygame.Rect((45, 50), (120, 750))),
                                              object_id="#text_box_26_horizleft_pad_10_14",
                                              container=self.scroll_container,
                                              line_spacing=1, manager=MANAGER)
            
            self.previous_page_button = UIImageButton(scale(pygame.Rect((100, 700), (68, 68))), "",
                                                    object_id="#arrow_left_button",manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((1430, 700), (68, 68))), "",
                                                object_id="#arrow_right_button", manager=MANAGER)
            
            self.stats_box = pygame_gui.elements.UITextBox(
                stats_text,
                scale(pygame.Rect((200, 220), (1200, 100))),
                manager=MANAGER,
                object_id=get_text_box_theme("#text_box_30_horizcenter"))
            
            self.stats_box2 = None
            
            width_scale_factor = 1300 / 1600
            height_scale_factor = 820 / 1300

            # Adjust scaling factors to make the image smaller
            adjustment_factor = 0.95  # 90% of the original size
            width_scale_factor *= adjustment_factor
            height_scale_factor *= adjustment_factor
            
            if game.settings["dark mode"]:
                self.journalart = pygame.transform.scale(image_cache.load_image("resources/images/journal_dark.png").convert_alpha(),
                                        (width_scale_factor * screen_x, height_scale_factor * screen_y))
            else:
                self.journalart = pygame.transform.scale(image_cache.load_image("resources/images/journal_dark.png").convert_alpha(),
                                        (width_scale_factor * screen_x, height_scale_factor * screen_y))

            if len(game.clan.infection["treatments"]) > 0:
                self.previous_page_button.enable()
            else:
                self.previous_page_button.disable()

            self.scroll_container.set_scrollable_area_dimensions((1360 / 1600 * screen_x, 1400 * screen_y))

            # JOURNAL STAMPS
            # wwhoooaaaaoo
            self.check_achivements()
            # chibi misspelled the function and im keeping it that way bc its funny

            # MURDER
            murderer = False
            # doing this so stamps can change if u switch mc to a non murderer
            if not game.clan.your_cat.history:
                game.clan.your_cat.load_history()
            if game.clan.your_cat.history:
                if game.clan.your_cat.history.murder:
                    if "is_murderer" in game.clan.your_cat.history.murder:
                        murderer = True

            if "1" in game.clan.achievements and murderer:
                murder = "murder1"
                hover = "Killed one cat"
                self.stamps["murder"] = UIImageButton(scale(pygame.Rect((310, 380), (38, 72))), "",
                                                object_id=f"#stamp_{murder}", tool_tip_text=f"{hover}", manager=MANAGER)
            
                if "2" in game.clan.achievements:
                    murder = "murder1"
                    hover = "Killed five cats"
                    self.stamps["murder"] = UIImageButton(scale(pygame.Rect((310, 380), (38, 72))), "",
                                                    object_id=f"#stamp_{murder}", tool_tip_text=f"{hover}", manager=MANAGER)
                if "3" in game.clan.achievements:
                    murder = "murder2"
                    hover = "Killed twenty cats"
                    self.stamps["murder"] = UIImageButton(scale(pygame.Rect((310, 370), (67, 86))), "",
                                                    object_id=f"#stamp_{murder}", tool_tip_text=f"{hover}", manager=MANAGER)
                if "4" in game.clan.achievements:
                    murder = "murder3"
                    hover = "Killed fifty cats"
                    self.stamps["murder"] = UIImageButton(scale(pygame.Rect((280, 370), (116, 99))), "",
                                                    object_id=f"#stamp_{murder}", tool_tip_text=f"{hover}", manager=MANAGER)
            elif "25" in game.clan.achievements:
                self.stamps["pacifist"] = UIImageButton(scale(pygame.Rect((280, 350), (135, 77))), "",
                                                object_id="#stamp_pacifist", tool_tip_text="Lived to be 120 moons without committing a  murder", manager=MANAGER)
            
            if "start" in game.clan.infection["logs"]:
                self.stamps["start"] = UIImageButton(scale(pygame.Rect((425, 570), (206, 205))), "",
                                                object_id="#stamp_start", tool_tip_text="You've discovered the infection.", manager=MANAGER)
                
            if "cure_found" in game.clan.infection["logs"]:
                self.stamps["cure_discovered"] = UIImageButton(scale(pygame.Rect((425, 340), (195, 170))), "",
                                            object_id="#stamp_cure", tool_tip_text="You've discovered the cure!", manager=MANAGER)

            
            self.update_notes_buttons()
    
    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blited
        if self.journalart:
            screen.blit(self.journalart, (182 / 1600 * screen_x, 90 / 400 * screen_y))
    
    def save_user_notes(self):
        """Saves user-entered notes. """
        clanname = game.clan.name

        notes = self.user_notes

        notes_directory = get_save_dir() + '/' + clanname + '/notes'
        notes_file_path = 'infection_notes.json'

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
            self.save_text = UIImageButton(scale(pygame.Rect(
                (1430, 350), (68, 68))),
                "",
                object_id="#unchecked_checkbox",
                tool_tip_text='lock and save text', manager=MANAGER
            )

            self.notes_entry = pygame_gui.elements.UITextEntryBox(
                scale(pygame.Rect((45, 50), (480, 750))),
                initial_text=self.user_notes,
                container=self.scroll_container,
                object_id='#text_box_26_horizleft_pad_10_14', manager=MANAGER
            )
        else:
            self.edit_text = UIImageButton(scale(pygame.Rect(
                (1430, 350), (68, 68))),
                "",
                object_id="#checked_checkbox_smalltooltip",
                tool_tip_text='edit text', manager=MANAGER
            )

            self.display_notes = UITextBoxTweaked(self.user_notes,
                                                    scale(pygame.Rect((45, 50), (480, 750))),
                                                    object_id="#text_box_26_horizleft_pad_10_14",
                                                    container=self.scroll_container,
                                                    line_spacing=1, manager=MANAGER)
    def exit_screen(self):
        """
        TODO: DOCS
        """
        if self.stats_box:
            self.stats_box.kill()
            del self.stats_box
        
        if self.stats_box2:
            self.stats_box2.kill()
            del self.stats_box2
        
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

    # def on_use(self):
    #     # Due to a bug in pygame, any image with buttons over it must be blited
    #     if self.screen_art and self.stage == "notes":
    #         screen.blit(self.journal_surface, (175, 307), (1165, 832, 1165, 832))

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
            for treatment, button in self.x_buttons.items():
                if event.ui_element == button:
                    self.delete_entry(treatment)