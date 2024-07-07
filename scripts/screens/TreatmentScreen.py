import pygame.transform
import pygame_gui.elements
from random import choice, randint
import ujson
import re

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

class TreatmentScreen(Screens):
    selected_cat = None
    current_page = 1
    list_frame = None
    apprentice_details = {}
    selected_details = {}
    cat_list_buttons = {}
    herb_buttons = {}
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

                    print("HERB1:", self.herb1)
                    print("HERB2:", self.herb2)
                    print("HERB3:", self.herb3)
                    print("HERB4:", self.herb4)

        if self.stage == "treatment results" and event.type == pygame.MOUSEBUTTONDOWN:
            if self.text_frames:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1  # Go to the last frame


    def screen_switches(self):
        if self.stage == 'choose patient':
            self.frame_index = 0
            self.text_index = 0
            self.paw = None
            self.selected_cat = None
            self.talk_box = None
            self.patient_sprite = None
            self.text = None
            self.textbox_graphic = None

            self.list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 355 / 1300 * screen_y))
            
            self.heading = pygame_gui.elements.UITextBox("Choose the patient",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((200, 226), (569, 399))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/murder_select.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            
            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)
            
            self.previous_stage_button = UIImageButton(scale(pygame.Rect((630, 1005), (120, 80))), "Back",
                                                    object_id="", manager=MANAGER)
            self.next_stage_button = UIImageButton(scale(pygame.Rect((902, 1005), (120, 80))), "Next",
                                                object_id="", manager=MANAGER)
            
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
            self.text = None
            self.textbox_graphic = None

            self.heading = pygame_gui.elements.UITextBox("Choose a treatment",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((200, 226), (569, 399))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/murder_select.png").convert_alpha(),
                                                                (569, 399)), manager=MANAGER)
            

            x_start = 880
            y_start = 190
            x_spacing = 130
            y_spacing = 130
            grid_size = 5

            x_pos = x_start
            y_pos = y_start

            for index, herb in enumerate(HERBS):
                self.herb_buttons[herb] = UIImageButton(
                    scale(pygame.Rect((x_pos, y_pos), (110, 110))), 
                    f"{herb}",
                    tool_tip_text=f"{herb}",
                    object_id="", 
                    manager=MANAGER
                )
                
                if (index + 1) % grid_size == 0:
                    x_pos = x_start  # Reset x position for new row
                    y_pos += y_spacing  # Move to the next row
                else:
                    x_pos += x_spacing  # Move to the next column

                if herb not in game.clan.herbs:
                    self.herb_buttons[herb].disable()

            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")

            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)
            
            self.previous_stage_button = UIImageButton(scale(pygame.Rect((630, 1005), (120, 80))), "Back",
                                                    object_id="", manager=MANAGER)
            self.next_stage_button = UIImageButton(scale(pygame.Rect((902, 1005), (120, 80))), "Next",
                                                object_id="", manager=MANAGER)
            
            self.next_stage_button.disable()
            self.update_selected_cat()
            self.previous_page_button.hide()
            self.next_page_button.hide()
        else:
            self.frame_index = 0
            self.text_index = 0
            self.mentor_frame = None
            for ele in self.selected_details:
                self.selected_details[ele].kill()
            
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
            
            self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((500, 970), (900, 300))))
            
            self.heading = pygame_gui.elements.UITextBox("Results",
                                                        scale(pygame.Rect((300, 50), (1000, 80))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:

            self.patient_sprite = pygame_gui.elements.UIImage(
                                            scale(pygame.Rect((650, 360), (320, 320))),
                                            pygame.transform.scale(
                                                self.selected_cat.sprite,
                                                (300, 300)), manager=MANAGER)
            
            self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
        
            self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1155), (68, 68))), "",
                                                    object_id="#relation_list_previous", manager=MANAGER)
            self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1155), (68, 68))), "",
                                                object_id="#relation_list_next", manager=MANAGER)
            
            self.previous_stage_button = UIImageButton(scale(pygame.Rect((630, 1005), (120, 80))), "Back",
                                                    object_id="", manager=MANAGER)
            self.next_stage_button = UIImageButton(scale(pygame.Rect((902, 1005), (120, 80))), "Next",
                                                object_id="", manager=MANAGER)
            
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

        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        
        if self.heading:
            self.heading.kill()
            del self.heading
      
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
        
        if self.textbox_graphic:
            self.textbox_graphic.kill()
            del self.textbox_graphic

    def get_adjusted_txt(self, text, cat):
        you = game.clan.your_cat
        for i in range(len(text)):
            if text[i] == "":
                return ""

        process_text_dict = self.cat_dict.copy()
    
        for abbrev in process_text_dict.keys():
            abbrev_cat = process_text_dict[abbrev]
            process_text_dict[abbrev] = (abbrev_cat, choice(abbrev_cat.pronouns))
        
        process_text_dict["y_c"] = (game.clan.your_cat, choice(game.clan.your_cat.pronouns))
        process_text_dict["m_c"] = (self.selected_cat, choice(self.selected_cat.pronouns))
        
        for i in range(len(text)):
            text[i] = re.sub(r"\{(.*?)\}", lambda x: pronoun_repl(x, process_text_dict, False), text[i])
        
        text = [t1.replace("c_n", game.clan.name) for t1 in text]
        text = [t1.replace("y_c", str(you.name)) for t1 in text]
        text = [t1.replace("m_c", str(self.selected_cat.name)) for t1 in text]

        text = [t1.replace("herb1", self.herb1) for t1 in text]
        text = [t1.replace("herb2", self.herb2) for t1 in text]
        text = [t1.replace("herb3", self.herb3) for t1 in text]
        text = [t1.replace("herb4", self.herb4) for t1 in text]

        return text

    def find_next_previous_cats(self):
        """Determines where the previous and next buttons lead"""
        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        self.previous_cat = 0
        self.next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            self.previous_cat = game.clan.instructor.ID

        if is_instructor:
            self.next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                self.next_cat = 1

            if self.next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and check_cat.status in \
                    ["apprentice", "medicine cat apprentice", "mediator apprentice", "queen's apprentice"] \
                    and check_cat.df == self.the_cat.df:
                self.previous_cat = check_cat.ID

            elif self.next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and check_cat.status in \
                    ["apprentice", "medicine cat apprentice", "mediator apprentice", "queen's apprentice"] \
                    and check_cat.df == self.the_cat.df:
                self.next_cat = check_cat.ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

    RESOURCE_DIR = "resources/dicts/events/lifegen_events/infection"

    def choose_treatment_text(self, patient):
        """ choosing text from the json regarding the success or failure of the treatment."""
        with open(f"{self.RESOURCE_DIR}/treatment_results.json",
                encoding="ascii") as read_file:
            self.m_txt = ujson.loads(read_file.read())

        
        if self.herb1 in game.infection["cure"]:
            herb_1 = True
        else:
            herb_1 = False
        if self.herb2 in game.infection["cure"]:
            herb_2 = True
        else:
            herb_2 = False
        if self.herb3 in game.infection["cure"]:
            herb_3 = True
        else:
            herb_3 = False
        if self.herb4 in game.infection["cure"]:
            herb_4 = True
        else:
            herb_4 = False

        herblist = [herb_1, herb_2, herb_3, herb_4]

        correct = 0
        correctherbs = ""

        for guess in herblist:
            if guess is True:
                correct += 1
        
        if correct == 0:
            correctherbs = "noneright"
        elif correct == 1:
            correctherbs = "oneright"
        elif correct == 2:
            correctherbs = "tworight"
        elif correct == 3:
            correctherbs = "threeright"
        elif correct == 4:
            correctherbs = "fourright"

        herbcount = 0
        for herb in herblist:
            if herb is not None:
                herbcount += 1
        
        herbinsert = f" {str(herbcount)}herb"

        infection_stage = [i for i in self.selected_cat.illnesses if i in ["stage one", "stage two", "stage three", "stage four"]]
        infection_stage_stripped = str(infection_stage).replace('[', '').replace(']', '').replace("'", '')
        print(infection_stage_stripped.replace(' ', '') + " " + correctherbs + herbinsert)
        try:
            ceremony_txt = self.m_txt[infection_stage_stripped.replace(' ', '') + " " + correctherbs + herbinsert]
            ceremony_txt = choice(ceremony_txt)
        except:
            ceremony_txt = choice(self.m_txt["error text"])
            
        return self.get_adjusted_txt(ceremony_txt, self.selected_cat)
        # return ceremony_txt

    def change_cat(self, patient):
        self.exit_screen()
        patient = self.selected_cat
        game.infection["cure_attempt"] = True
        self.choose_treatment_text(patient)
        
    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_cat:

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((233, 310), (270, 270))),
                pygame.transform.scale(
                    self.selected_cat.sprite,
                    (270, 270)), manager=MANAGER)

            infection_stage = [i for i in self.selected_cat.illnesses if i in ["stage one", "stage two", "stage three", "stage four"]]

            infection_stage_stripped = str(infection_stage).replace('[', '').replace(']', '').replace("'", '')

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
        infected_cats = []

        for cat in Cat.all_cats_list:
            if not cat.dead and not cat.outside and ("stage one" in cat.illnesses or "stage two" in cat.illnesses or "stage three" in cat.illnesses or "stage four" in cat.illnesses):
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
