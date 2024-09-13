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
from scripts.game_structure.ui_elements import UIImageButton, UISpriteButton, UIRelationStatusBar
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.windows import RelationshipLog
from scripts.game_structure.propagating_thread import PropagatingThread

class TreatmentScreen(Screens):
    selected_cat = None
    current_page = 1
    list_frame = None
    apprentice_details = {}
    selected_details = {}
    cat_list_buttons = {}
    herb_buttons = {}
    herb_displays = {}
    additional_infected_sprites = {}
    stage = 'choose patient'

    def __init__(self, name=None):
        super().__init__(name)
        self.list_page = None
        self.next_cat = None
        self.previous_cat = None
        self.next_page_button = None
        self.previous_page_button = None
        self.current_mentor_warning = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.mentor_icon = None
        self.app_frame = None
        self.mentor_frame = None
        self.current_mentor_text = None
        self.info = None
        self.heading = None
        self.subtitle = None
        self.screenart = None
        self.mentor = None
        self.the_cat = None
        self.patient = None

        self.previous_stage_button = None
        self.next_stage_button = None

        # shamelessly stolen talk stuff
        self.text_index = 0
        self.frame_index = 0
        self.typing_delay = 20
        self.next_frame_time = pygame.time.get_ticks() + self.typing_delay
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.textbox_graphic = None
        self.talk_box_img = None
        self.possible_texts = {}
        self.text = None
        self.texts = ""
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        self.chosen_text_key = ""
        self.choice_buttons = {}
        self.text_choices = {}
        self.option_bgs = {}
        self.current_scene = ""
        self.created_choice_buttons = False
        self.choicepanel = False
        self.textbox_graphic = None
        self.cat_dict = {}
        self.replaced_index = (False, 0)
        self.other_dict = {}

        #herbs

        self.herb1 = None
        self.herb2 = None
        self.herb3 = None
        self.herb4 = None
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.cat_list_buttons.values():
                self.selected_cat = event.ui_element.return_cat_object()
                self.update_selected_cat()
                if self.selected_cat:
                    self.next_stage_button.enable()
                else:
                    self.next_stage_button.disable()

            elif event.ui_element == self.next_stage_button and self.selected_cat and self.stage == 'choose patient':
                if not self.selected_cat.dead:
                    self.exit_screen()
                    self.update_selected_cat()
                    self.stage = 'choose treatment'
                    self.screen_switches()
            
            elif event.ui_element == self.next_stage_button and self.stage == 'choose treatment' and not (self.herb1 is None and self.herb2 is None and self.herb3 is None and self.herb4 is None):
                self.exit_screen()
                self.update_selected_cat()
                self.stage = 'treatment results'
                self.screen_switches()
            
            elif event.ui_element == self.previous_stage_button and self.stage == 'choose treatment':
                self.exit_screen()
                self.update_selected_cat()
                self.stage = 'choose patient'
                self.screen_switches()

            elif event.ui_element == self.next_stage_button and self.selected_cat and self.stage == 'treatment results':
                self.change_cat(self.selected_cat)
            
            elif event.ui_element == self.back_button:
                self.change_screen('med den screen')
                self.stage = 'choose patient'
                self.herb1 = None
                self.herb2 = None
                self.herb3 = None
                self.herb4 = None

            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches['cat'] = self.next_cat
                    self.update_cat_list()
                    self.update_selected_cat()
                    # self.update_buttons()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches['cat'] = self.previous_cat
                    self.update_cat_list()
                    self.update_selected_cat()
                    # self.update_buttons()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_list()
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_list()
            elif "cure_button" in self.herb_displays and event.ui_element == self.herb_displays["cure_button"]:
                self.herb1 = game.clan.infection["cure"][0]
                self.herb2 = game.clan.infection["cure"][1]
                self.herb3 = game.clan.infection["cure"][2]
                self.herb4 = game.clan.infection["cure"][3]
                self.update_herb_buttons()
                self.update_treatment_display()

            for herb, button in self.herb_buttons.items():
                if self.herb1 is None and self.herb2 is None and self.herb3 is None and self.herb4 is None:
                    self.next_stage_button.disable()
                else:
                    self.next_stage_button.enable()

                if event.ui_element == button:
                    if herb == self.herb1:
                        self.herb1 = None
                    elif herb == self.herb2:
                        self.herb2 = None
                    elif herb == self.herb3:
                        self.herb3 = None
                    elif herb == self.herb4:
                        self.herb4 = None
                    else:
                        if self.herb1 is None:
                            self.herb1 = herb
                        elif self.herb2 is None:
                            self.herb2 = herb
                        elif self.herb3 is None:
                            self.herb3 = herb
                        elif self.herb4 is None:
                            self.herb4 = herb

                    self.update_herb_buttons()
                    self.update_treatment_display()

        if self.stage == "treatment results" and event.type == pygame.MOUSEBUTTONDOWN:
            if self.text_frames:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1  # Go to the last frame

    def update_treatment_display(self):
        for ele in self.herb_displays:
            self.herb_displays[ele].kill()
        self.herb_displays = {}

        self.herb_displays["desc"] = pygame_gui.elements.UITextBox(
            "<u>Pick up to four herbs to try.</u>",
            scale(pygame.Rect((300, 880), (1000, 80))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            manager=MANAGER
            )
        
        self_herbs = [self.herb1, self.herb2, self.herb3, self.herb4]
        herb_list = []
        for herb in self_herbs:
            if herb is not None:
                herb_list.append(herb)

        if len(herb_list) == 0:
            text = ""
        elif len(herb_list) == 1:
            text = f"{herb_list[-1].replace('_', ' ')}"
        else:
            text = f"{', '.join([herb.replace('_', ' ') for herb in herb_list[:-1]])}, {herb_list[-1].replace('_', ' ')}"

        self.herb_displays["herbs"] = pygame_gui.elements.UITextBox(
            f"<i>{text}</i>",
            scale(pygame.Rect((300, 950), (1000, 80))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            manager=MANAGER
            )
        
        if "cure_found" in game.clan.infection["logs"]:
            self.herb_displays["cure_button"] = UIImageButton(
                    scale(pygame.Rect((300, 780), (160, 80))), 
                    "Use cure",
                    object_id="",
                    manager=MANAGER
                )
        
        if "cure_button" in self.herb_displays:
            cure_unstocked = False
            for herb in game.clan.infection["cure"]:
                if herb not in game.clan.herbs.keys():
                    cure_unstocked = True
                    break
            if cure_unstocked is True:
                self.herb_displays["cure_button"].disable()

    def update_herb_buttons(self):
        """ Displays and updates herb buttons """

        for ele in self.herb_buttons:
            self.herb_buttons[ele].kill()
        self.herb_buttons = {}

        x_start = 880
        y_start = 190
        x_spacing = 130
        y_spacing = 130
        grid_size = 5

        x_pos = x_start
        y_pos = y_start

        selected_herbs = [self.herb1, self.herb2, self.herb3, self.herb4]
        picked = 0
        for h in selected_herbs:
            if h is not None:
                picked += 1

        for index, herb in enumerate(HERBS):
            if herb not in selected_herbs:
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
            
            if picked == 4:
                if herb not in selected_herbs:
                    self.herb_buttons[herb].disable()
            
                
            
            if (index + 1) % grid_size == 0:
                x_pos = x_start  # Reset x position for new row
                y_pos += y_spacing  # Move to the next row
            else:
                x_pos += x_spacing  # Move to the next column

            if herb not in game.clan.herbs:
                self.herb_buttons[herb].disable()


    def screen_switches(self):
        if self.stage == 'choose patient':
            self.frame_index = 0
            self.text_index = 0
            self.paw = None
            self.selected_cat = None
            self.talk_box = None
            self.patient_sprite = None
            self.medcat_sprite = None
            self.text = None
            self.textbox_graphic = None
            self.subtitle = None
            self.screenart = None

            self.list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 355 / 1300 * screen_y))
            
            self.heading = pygame_gui.elements.UITextBox("Choose the patient",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((200, 226), (562, 394))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/choosing_cat1_frame_ment.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            
            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)
            
            self.previous_stage_button = UIImageButton(scale(pygame.Rect((220, 670), (68, 68))), "",
                                                    object_id="#arrow_left_button", manager=MANAGER)
            self.next_stage_button = UIImageButton(scale(pygame.Rect((450, 670), (68, 68))), "",
                                                object_id="#arrow_right_button", manager=MANAGER)
            
            self.previous_stage_button.disable()
            self.next_stage_button.disable()

            self.update_selected_cat()  # Updates the image and details of selected cat
            self.update_cat_list()
        elif self.stage == "choose treatment":
            self.frame_index = 0
            self.text_index = 0
            self.paw = None
            self.list_frame = None
            self.talk_box = None
            self.patient_sprite = None
            self.medcat_sprite = None
            self.text = None
            self.textbox_graphic = None
            self.subtitle = None
            self.screenart = None

            self.heading = pygame_gui.elements.UITextBox("Choose a treatment",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((200, 226), (562, 394))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/choosing_cat1_frame_ment.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            
            self.update_herb_buttons()

            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")

            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)
            
            self.previous_stage_button = UIImageButton(scale(pygame.Rect((220, 670), (68, 68))), "",
                                                    object_id="#arrow_left_button", manager=MANAGER)
            self.next_stage_button = UIImageButton(scale(pygame.Rect((450, 670), (68, 68))), "",
                                                object_id="#arrow_right_button", tool_tip_text="Proceed to treatment",manager=MANAGER)
            
            self.next_stage_button.disable()
            self.update_selected_cat()
            self.previous_page_button.hide()
            self.next_page_button.hide()

            self.update_treatment_display()
        else:
            self.frame_index = 0
            self.text_index = 0
            self.mentor_frame = None
            for ele in self.selected_details:
                self.selected_details[ele].kill()

            if game.settings["dark mode"]:
                img = "treatment_den_dark"
            else:
                img = "treatment_den_light"
            self.screenart = pygame_gui.elements.UIImage(
                scale(pygame.Rect((0, 0), (1600, 806))),
                image_cache.load_image(f"resources/images/{img}.png").convert_alpha()
            )

            infected_cats = [
                i for i in Cat.all_cats_list if\
                not i.dead and not i.outside and \
                i.infected_for > 0 and \
                i not in [self.selected_cat, self.the_cat]
                ]

            infected = len(infected_cats)
            if infected > 0:
                infected_cat_1 = choice(infected_cats)
                infected_cats.remove(infected_cat_1)
                self.additional_infected_sprites["1"] = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((150, 400), (300, 300))),
                                            pygame.transform.scale(
                                            infected_cat_1.sprite,
                                            (300, 300)), manager=MANAGER
                                            )
            if infected > 1:
                infected_cat_2 = choice(infected_cats)
                infected_cats.remove(infected_cat_2)
                self.additional_infected_sprites["2"] = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((1010, 430), (250, 250))),
                                            pygame.transform.scale(
                                            infected_cat_2.sprite,
                                            (300, 300)), manager=MANAGER
                                            )
            if infected > 2:
                infected_cat_3 = choice(infected_cats)
                infected_cats.remove(infected_cat_3)
                self.additional_infected_sprites["3"] = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((450, 460), (200, 200))),
                                            pygame.transform.scale(
                                            infected_cat_3.sprite,
                                            (300, 300)), manager=MANAGER
                                            )
            if infected > 3:
                infected_cat_4 = choice(infected_cats)
                infected_cats.remove(infected_cat_4)
                self.additional_infected_sprites["4"] = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((1250, 460), (200, 200))),
                                            pygame.transform.scale(
                                            infected_cat_4.sprite,
                                            (300, 300)), manager=MANAGER
                                            )
            
            self.text_type = ""
            self.texts = self.choose_treatment_text(self.selected_cat)
            self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
            self.talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()

            self.talk_box = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((178, 942), (1248, 302))),
                    self.talk_box_img
                )
            self.textbox_graphic = pygame_gui.elements.UIImage(
                scale(pygame.Rect((170, 942), (346, 302))),
                image_cache.load_image("resources/images/textbox_graphic.png").convert_alpha()
            )

            self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((500, 970), (900, 300))))
            self.text = pygame_gui.elements.UITextBox("",
                                                    scale(pygame.Rect((0, 0), (900, -100))),
                                                    object_id="#text_box_30_horizleft",
                                                    container=self.scroll_container,
                                                    manager=MANAGER)
            
            self.heading = pygame_gui.elements.UITextBox("Results",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)

            herb_list = [self.herb1, self.herb2, self.herb3, self.herb4]
            newlist = []
            for i in herb_list:
                if i is not None:
                    newlist.append(i)
            
            if len(newlist) > 1:
                text = f"{', '.join([herb.replace('_', ' ') for herb in newlist[:-1]])}, {newlist[-1].replace('_', ' ')}"
            else:
                text = f"{', '.join([herb.replace('_', ' ') for herb in newlist[:-1]])} {newlist[-1].replace('_', ' ')}"


            string = f"{self.selected_cat.name} - Moon {game.clan.age} - {text}"
            
            self.subtitle = pygame_gui.elements.UITextBox(string,
                                                        scale(pygame.Rect((300, 100), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:

            self.patient_sprite = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((650, 360), (380, 380))),
                                            pygame.transform.scale(
                                                self.selected_cat.sprite,
                                                (300, 300)), manager=MANAGER)
            self.medcat_sprite = pygame_gui.elements.UIImage(scale(pygame.Rect((70, 900), (400, 400))),
                                                                        pygame.transform.scale(
                                                                            self.the_cat.sprite,
                                                                            (400, 400)), manager=MANAGER)
            
            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)
            
            self.previous_stage_button = UIImageButton(scale(pygame.Rect((630, 1005), (68, 68))), "",
                                                    object_id="#arrow_left_button", manager=MANAGER)
            self.next_stage_button = UIImageButton(scale(pygame.Rect((902, 1005), (68, 68))), "",
                                                object_id="#arrow_right_button", manager=MANAGER)
            
            self.paw = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1370, 1180), (30, 30))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
            self.paw.visible = False
            
            self.previous_page_button.hide()
            self.next_page_button.hide()
            self.previous_stage_button.hide()
            self.next_stage_button.hide()

    def exit_screen(self):

        if self.text:
            self.text.kill()
            del self.text
        
        if self.paw:
            self.paw.kill()
            del self.paw

        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        for ele in self.herb_buttons:
            self.herb_buttons[ele].kill()
        self.herb_buttons = {}

        for ele in self.herb_displays:
            self.herb_displays[ele].kill()
        self.herb_displays = {}

        for ele in self.additional_infected_sprites:
            self.additional_infected_sprites[ele].kill()
        self.additional_infected_sprites = {}

        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        
        if self.heading:
            self.heading.kill()
            del self.heading
      
        if self.subtitle:
            self.subtitle.kill()
            del self.subtitle
      
        if self.screenart:
            self.screenart.kill()
            del self.screenart
      
        if self.mentor_frame:
            self.mentor_frame.kill()
            del self.mentor_frame

        if self.back_button:
            self.back_button.kill()
            del self.back_button
        if self.previous_page_button:
            self.previous_page_button.kill()
            del self.previous_page_button
            
        if self.next_page_button:
            self.next_page_button.kill()
            del self.next_page_button

        if self.next_stage_button:
            self.next_stage_button.kill()
            del self.next_stage_button
        if self.previous_stage_button:
            self.previous_stage_button.kill()
            del self.previous_stage_button

        if self.talk_box:
            self.talk_box.kill()
            del self.talk_box
        
        if self.patient_sprite:
            self.patient_sprite.kill()
            del self.patient_sprite

        if self.medcat_sprite:
            self.medcat_sprite.kill()
            del self.medcat_sprite
        
        if self.textbox_graphic:
            self.textbox_graphic.kill()
            del self.textbox_graphic

    def get_adjusted_txt(self, text, patient, the_cat):
        you = game.clan.your_cat
        for i in range(len(text)):
            if text[i] == "":
                print("here capn")
                return ""

        process_text_dict = self.cat_dict.copy()
    
        for abbrev in process_text_dict.keys():
            abbrev_cat = process_text_dict[abbrev]
            process_text_dict[abbrev] = (abbrev_cat, choice(abbrev_cat.pronouns))
        
        if the_cat != game.clan.your_cat:
            process_text_dict["r_m"] = (the_cat, choice(the_cat.pronouns))
        process_text_dict["m_c"] = (patient, choice(patient.pronouns))
        
        for i in range(len(text)):
            text[i] = re.sub(r"\{(.*?)\}", lambda x: pronoun_repl(x, process_text_dict, False), text[i])

        text = [t1.replace("c_n", game.clan.name) for t1 in text]
        text = [t1.replace("m_c", str(patient.name)) for t1 in text]
        if the_cat != game.clan.your_cat:
            text = [t1.replace("r_m", str(the_cat.name)) for t1 in text]

        # text = [t1.replace("herb1", self.herb1) for t1 in text if self.herb1 is not None]
        # text = [t1.replace("herb2", self.herb2) for t1 in text if self.herb2 is not None]
        # text = [t1.replace("herb3", self.herb3) for t1 in text if self.herb3 is not None]
        # text = [t1.replace("herb4", self.herb4) for t1 in text if self.herb4 is not None]

        return text

    def get_failure_chance(self, patient):
        """ determine if the medcat will even be effective in attempting treatment. if a treatment is failed, no information on the herbs is given to the player. """
        
        stageone = True if f"{game.clan.infection['infection_type']} stage one" in patient.illnesses else False
        stagetwo = True if "{game.clan.infection['infection_type']} stage two" in patient.illnesses else False
        stagethree = True if f"{game.clan.infection['infection_type']} stage three" in patient.illnesses else False
        stagefour = True if f"{game.clan.infection['infection_type']} stage four" in patient.illnesses else False

        failchance = 0

        if stageone:
            failchance += 30
        elif stagetwo:
            failchance += 40
        elif stagethree:
            failchance += 60
        elif stagefour:
            failchance += 80

        if self.the_cat.status == "medicine cat":
            failchance = failchance * 0.8
            # more likely to work if theyre not an app
        
        medcats = [i for i in Cat.all_cats.values() if
                  (i.status == 'medicine cat' or i.status == 'medicine cat apprentice') and not i.dead and not i.outside and not i.not_working() and i.infected_for < 1]
        

        if len(medcats) == 2:
            failchance -= 10
        elif len(medcats) > 2:
            failchance -= 10 + 2 * (len(medcats) - 2)

        chance = randint(1,100)
        if chance < failchance:
            return False
        else:
            return True

    RESOURCE_DIR = "resources/dicts/infection"

    def choose_treatment_text(self, patient):
        """ choosing text from the json regarding the success or failure of the treatment."""
        inftype = game.clan.infection["infection_type"]
        with open(f"{self.RESOURCE_DIR}/treatment_results.json",
                encoding="ascii") as read_file:
            self.m_txt = ujson.loads(read_file.read())

        medcats = []
        for cat in Cat.all_cats_list:
            if cat.status in ["medicine cat", "medicine cat apprentice"] and not cat.not_working() and cat.infected_for < 1 and not cat.outside and not cat.dead:
                medcats.append(cat)
        self.the_cat = choice(medcats)

        who_key = ""
        if self.the_cat == game.clan.your_cat:
            who_key = "you "

        successkey = ""
        success = self.get_failure_chance(patient)

        # success = False
        # ^ debug

        if not success:
            successkey = " failure"
        
        if self.herb1 in game.clan.infection["cure"]:
            herb_1 = True
        else:
            herb_1 = False
        if self.herb2 in game.clan.infection["cure"]:
            herb_2 = True
        else:
            herb_2 = False
        if self.herb3 in game.clan.infection["cure"]:
            herb_3 = True
        else:
            herb_3 = False
        if self.herb4 in game.clan.infection["cure"]:
            herb_4 = True
        else:
            herb_4 = False

        herblist = [herb_1, herb_2, herb_3, herb_4]
        self_herblist = [self.herb1, self.herb2, self.herb3, self.herb4]

        correct = 0
        for guess in herblist:
            if guess is True:
                correct += 1
        
        correctherbs = "zeroright"

        if correct == 1:
            correctherbs = "oneright"
        elif correct == 2:
            correctherbs = "tworight"
        elif correct == 3:
            correctherbs = "threeright"
        elif correct == 4:
            correctherbs = "fourright"

        herbcount = 0
        for herb in self_herblist:
            if herb is not None:
                herbcount += 1
        
        herbinsert = f" {str(herbcount)}herb"

        infection_stage = [i for i in self.selected_cat.illnesses if i in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three", f"{inftype} stage four"]]
        infection_stage_stripped = str(infection_stage).replace('[', '').replace(']', '').replace("'", '')
        print([infection_stage_stripped.replace(' ', '').replace(f'{inftype}', '') + " " + correctherbs + herbinsert + successkey])
        if len(game.clan.infection["cure_discovered"]) < 4 or (len(game.clan.infection["cure_discovered"]) == 4 and correct < 4):
            if self.selected_cat.status == "newborn":
                ceremony_txt = (self.m_txt[who_key + "newborn" + successkey])
            try:
                if success:
                    ceremony_txt = self.m_txt[who_key + infection_stage_stripped.replace(' ', '').replace(f'{inftype}', '') + " " + correctherbs + herbinsert + successkey]
                else:
                    ceremony_txt = self.m_txt[who_key + infection_stage_stripped.replace(' ', '').replace(f'{inftype}', '') + herbinsert + successkey]

                    
            except KeyError:
                try:
                    if success:
                        ceremony_txt =(self.m_txt[who_key + " " + correctherbs + herbinsert + successkey])
                    else:
                        ceremony_txt =(self.m_txt[who_key + herbinsert + successkey])
                except:
                    try:
                        if success:
                            ceremony_txt = (self.m_txt[who_key + " " + correctherbs  + successkey])
                        else:
                            ceremony_txt = (self.m_txt[who_key + " " + successkey])
                    except:
                        print("NO TEXT FOUND")
                        ceremony_txt = (self.m_txt[who_key + "anystage anyright anyherb" + successkey])
        
        else:
           ceremony_txt = (self.m_txt[who_key + "cure_found"])

        if success:
            self.add_to_treatments(patient)
        game.clan.infection["cure_attempt"] = True

        chosenkey = choice(ceremony_txt)
        return self.get_adjusted_txt(chosenkey, self.selected_cat, self.the_cat)

    def add_to_treatments(self, patient):
        """ Adds the treatment information to the json for logging. """
        inftype = game.clan.infection["infection_type"]

        herblist = [self.herb1, self.herb2, self.herb3, self.herb4]
        correctherbs = [herb for herb in herblist if herb in game.clan.infection["cure"]]

        cure_one = False
        if len(correctherbs) == 1:
            cure_one = True

        cure_two = False
        if len(correctherbs) == 2:
            cure_two = True

        cure_three = False
        if len(correctherbs) == 3:
            cure_three = True

        cure = False
        if len(correctherbs) == 4:
            cure = True

        if cure_one or cure_two or cure_three:
            remission_chance = 20
            if not patient.is_injured():
                remission_chance -= 8
            sick = False
            for illness in patient.illnesses:
                if illness not in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three", f"{inftype} stage four"]:
                    sick = True
            if not sick:
                remission_chance -= 8

            if cure_one:
                remission_chance -= remission_chance / 4
            elif cure_two:
                remission_chance -= remission_chance / 3
            elif cure_three:
                remission_chance -= remission_chance / 2
            
            medcats = [i for i in Cat.all_cats.values() if
                (i.status == 'medicine cat' or i.status == 'medicine cat apprentice') and not i.dead and not i.outside and not i.not_working() and i.infected_for < 1]
            
            if len(medcats) < 2:
                remission_chance += len(medcats) / 5
            elif len(medcats) < 4:
                remission_chance += len(medcats) / 3
            else:
                remission_chance += len(medcats) / 2

            if remission_chance <= 1:
                remission_chance = 1

            # if int(random.random() * remission_chance):
            # ^ debug
            if not int(random.random() * remission_chance):
                patient.cure_progress += 1
                print("REMISSION CHANCE HIT")

        if cure:
            patient.cure_progress += 1
            for herb in correctherbs:
                if herb not in game.clan.infection["cure_discovered"]:
                    game.clan.infection["cure_discovered"].append(herb)

        if len(game.clan.infection["cure_discovered"]) < 4:
            treatment = {
                "moon": game.clan.age,
                "herbs": [herb for herb in herblist if herb is not None],
                "correct_herbs": len(correctherbs)
            }

            game.clan.infection["treatments"].append(treatment)
        
        herbs = game.clan.herbs.copy()
        for herb in herbs:
            if herb in herblist:
                game.clan.herbs[herb] -= 1
                if game.clan.herbs[herb] <= 0:
                    game.clan.herbs.pop(herb)

        used_herbs = []
        for herb in herblist:
            if herb != None:
                used_herbs.append(herb)

        if self.the_cat.ID == game.clan.your_cat.ID:
            insert = "You"
        else:
            insert = self.the_cat.name

        if len(used_herbs) == 1:
            medlog = f"{insert} used {used_herbs[-1].replace('_', ' ')} as an attempt to cure the infection."
        elif len(used_herbs) == 2:
            medlog = f"{insert} used {' '.join([herb.replace('_', ' ') for herb in used_herbs[:-1]])} and {used_herbs[-1].replace('_', ' ')} as an attempt to cure the infection."
        else:
            medlog = f"{insert} used {', '.join([herb.replace('_', ' ') for herb in used_herbs[:-1]])}, and {used_herbs[-1].replace('_', ' ')} as an attempt to cure the infection."

        game.herb_events_list.append(medlog)

    def change_cat(self, patient):
        self.exit_screen()
        patient = self.selected_cat
        self.choose_treatment_text(patient)
        
    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        inftype = game.clan.infection["infection_type"]
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_cat:

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((233, 310), (270, 270))),
                pygame.transform.scale(
                    self.selected_cat.sprite,
                    (270, 270)), manager=MANAGER)

            infection_stage = [i for i in self.selected_cat.illnesses if i in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three", f"{inftype} stage four"]]

            infection_stage_stripped = str(infection_stage).replace('[', '').replace(']', '').replace("'", '').replace(f"{inftype} ", "")

            info = self.selected_cat.status + "\n" + \
                   self.selected_cat.genderalign + "\n <b>" + infection_stage_stripped + "</b> \n"
            
            self.selected_details["selected_info"] = pygame_gui.elements.UITextBox(info,
                                                                                   scale(pygame.Rect((540, 325),
                                                                                                     (210, 250))),
                                                                                   object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                   manager=MANAGER)

            name = str(self.selected_cat.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["victim_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((260, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter", manager=MANAGER)

    def update_cat_list(self):
        """Updates the cat sprite buttons. """
        valid_mentors = self.chunks(self.get_valid_cats(), 30)

        # If the number of pages becomes smaller than the number of our current page, set
        #   the current page to the last page
        if self.current_page > len(valid_mentors):
            self.list_page = len(valid_mentors)

        # Handle which next buttons are clickable.
        if len(valid_mentors) <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.current_page >= len(valid_mentors):
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.current_page == 1 and len(valid_mentors) > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()
        display_cats = []
        if valid_mentors:
            display_cats = valid_mentors[self.current_page - 1]

        # Kill all the currently displayed cats.
        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        pos_x = 0
        pos_y = 90
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))),
                cat.sprite, cat_object=cat, manager=MANAGER)
            pos_x += 120
            if pos_x >= 1100:
                pos_x = 0
                pos_y += 120
            i += 1

    def get_valid_cats(self):
        """ find all of the infected cats to choose from """
        inftype = game.clan.infection["infection_type"]
        infected_cats = []

        for cat in Cat.all_cats_list:
            if not cat.dead and not cat.outside and (f"{inftype} stage one" in cat.illnesses or f"{inftype} stage two" in cat.illnesses or f"{inftype} stage three" in cat.illnesses or f"{inftype} stage four" in cat.illnesses):
                infected_cats.append(cat)
        
        return infected_cats

    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blited
        if self.list_frame:
            screen.blit(self.list_frame, (150 / 1600 * screen_x, 790 / 1400 * screen_y))

        now = pygame.time.get_ticks()

        if self.stage == "treatment results":
            self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
            if self.text_index < len(self.text_frames):
                if now >= self.next_frame_time and self.frame_index < len(self.text_frames[self.text_index]) - 1:
                    self.frame_index += 1
                    self.next_frame_time = now + self.typing_delay
            if self.text_index == len(self.text_frames) - 1:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_type != "choices":
                        self.paw.visible = True

            if self.text_frames:
                self.text.html_text = self.text_frames[self.text_index][self.frame_index]

            self.text.rebuild()
            self.clock.tick(60)

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
