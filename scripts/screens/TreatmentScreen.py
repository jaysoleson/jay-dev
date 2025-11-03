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
from scripts.utility import (
    get_personality_compatibility,
    get_text_box_theme,
    ui_scale,
    shorten_text_to_fit,
    pronoun_repl,
    get_infection_herb,
    get_alive_status_cats,
    get_infection_info,
    update_infection_info,
    get_infection_type
    )
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.cat.pelts import Pelt
from scripts.game_structure.windows import GameOver, PickPath, DeathScreen
from scripts.game_structure.ui_elements import UIImageButton, UISpriteButton, UIRelationStatusBar, UISurfaceImageButton
from scripts.game_structure.game_essentials import game
from scripts.game_structure.windows import RelationshipLog
from scripts.game_structure.propagating_thread import PropagatingThread
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.get_arrow import get_arrow
from ..ui.icon import Icon

class TreatmentScreen(Screens):
    selected_cat = None
    current_page = 1
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
        self.list_frame = None
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
        self.medcats = []

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

        self.correct_cure = []
        
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
            
            elif (
                event.ui_element == self.next_stage_button and
                self.stage == 'choose treatment' and
                not (self.herb1 is None and
                     self.herb2 is None and
                     self.herb3 is None and
                     self.herb4 is None)
                     ):
                game.clan.infection["cure_attempt"] = True
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
                self.herb1 = get_infection_herb(self.correct_cure[0])
                self.herb2 = get_infection_herb(self.correct_cure[1])
                self.herb3 = get_infection_herb(self.correct_cure[2])
                self.herb4 = get_infection_herb(self.correct_cure[3])
                self.update_herb_buttons()
                self.update_treatment_display()

            for herb, button in self.herb_buttons.items():

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

        if self.herb1 is None and self.herb2 is None and self.herb3 is None and self.herb4 is None:
            self.next_stage_button.disable()
        else:
            self.next_stage_button.enable()
        
        # self.scroll_container = pygame_gui.elements.UIScrollingContainer(
        #     ui_scale(pygame.Rect((0, 455), (650, 145))),
        #     allow_scroll_x=False,
        #     manager=MANAGER,
        #     anchors={"centerx": "centerx"}
        #     )

        # cure logs
        logs = 0
        if game.settings["fullscreen"]:
            log_width = 700
        else:
            log_width = 500

        y_offset = 0

        current_type = get_infection_info("type", self.selected_cat)
        for treatment in game.clan.infection['treatments']:
            if "type" in treatment:
                if treatment["type"] != current_type:
                    continue
            logs += 1

            moon_text = f"<b>Moon {treatment['moon']}</b>"
            self.herb_displays["moon_text_box" + str(logs)] = pygame_gui.elements.UITextBox(
                moon_text,
                pygame.Rect((80, y_offset), (log_width, 30)),
                container=self.scroll_container,
                manager=MANAGER,
                object_id="#text_box_30_horizcenter")
            
            offset2 = 13
            
            treatment_text = f"{', '.join([herb.replace('_', ' ') for herb in treatment['herbs']])}"
            self.herb_displays["treatment_text_box" + str(logs)] = pygame_gui.elements.UITextBox(
                treatment_text,
                pygame.Rect((80, (y_offset + offset2)), (log_width, 100)),
                container=self.scroll_container,
                manager=MANAGER,
                object_id="#text_box_30_horizcenter")
            
            # correct_text = f"Effective Herbs: {treatment['correct_herbs']}"
            correct_text = ""
            if int(treatment['correct_herbs']) > 0 and int(treatment['correct_herbs']) < 4:
                correct_text = "<font color = '#473B0A'> At least one effective herb </font>"
            elif int(treatment['correct_herbs']) == 4:
                correct_text = "<font color='#136D05'>Cure Found!</font>"
            else:
                correct_text = "<font color='#550D0D'>Zero Effective Herbs</font>"

            offset3 = 32
            self.herb_displays["correct_text_box" + str(logs)] = pygame_gui.elements.UITextBox(
                correct_text,
                pygame.Rect((80, (y_offset + offset3)), (log_width, 50)),
                container=self.scroll_container,
                manager=MANAGER,
                object_id="#text_box_30_horizcenter"
                )
            y_offset += 70
        # -----
        
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
            f"<u>{text}</u>",
            ui_scale(pygame.Rect((0, 410), (500, 90))),
            object_id="#text_box_34_horizcenter",
            manager=MANAGER,
            anchors={"centerx": "centerx"}
            )
        
        if "cure_found" in get_infection_info("logs"):
            self.herb_displays["cure_button"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((150, 337), (80, 30))),
                "use cure",
                get_button_dict(ButtonStyles.SQUOVAL, (80, 30)),
                object_id="@buttonstyles_squoval",
                starting_height=0,
            )
        
        if "cure_button" in self.herb_displays:
            cure_unstocked = False
            for herb in self.correct_cure:
                if get_infection_herb(herb) not in game.clan.herbs.keys():
                    cure_unstocked = True
                    break
            if cure_unstocked is True:
                self.herb_displays["cure_button"].disable()

    def update_herb_buttons(self):
        """ Displays and updates herb buttons """

        for ele in self.herb_buttons:
            self.herb_buttons[ele].kill()
        self.herb_buttons = {}

        x_start = 430
        y_start = 78
        x_spacing = 60
        y_spacing = 60
        grid_size = 2

        x_pos = x_start
        y_pos = y_start

        selected_herbs = [self.herb1, self.herb2, self.herb3, self.herb4]
        picked = 0
        for h in selected_herbs:
            if h is not None:
                picked += 1

        count = 0
        for index, herb in enumerate(HERBS):
            count += 1
            if herb not in selected_herbs:
                if herb in game.clan.herbs:
                    stock_text = "\n In stock: " + str(game.clan.herbs[herb])
                else:
                    stock_text = ""
                self.herb_buttons[herb] = UIImageButton(
                    ui_scale(pygame.Rect((x_pos, y_pos), (55, 55))), 
                    "",
                    tool_tip_text=(
                        f"{herb.replace('_', ' ')}" + stock_text
                        ),
                    object_id=f"#{herb}",
                    manager=MANAGER
                )
            else:
                self.herb_buttons[herb] = UIImageButton(
                    ui_scale(pygame.Rect((x_pos, y_pos), (55, 55))), 
                    "",
                    tool_tip_text=f"{herb.replace('_', ' ')}",
                    object_id=f"#{herb}_selected",
                    manager=MANAGER
                )
            
            if picked == 4:
                if herb not in selected_herbs:
                    self.herb_buttons[herb].disable()

            if count == 5:
                count = 0
                x_pos = x_start
                y_pos += y_spacing
            else:
                x_pos += x_spacing

            if herb not in game.clan.herbs:
                self.herb_buttons[herb].disable()


    def screen_switches(self):
        super().screen_switches()
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
            self.scroll_container = None

            self.medcats = [
                i for i in Cat.all_cats_list if
                i.status in ["medicine cat", "medicine cat apprentice"] and
                not i.not_working() and
                not i.outside and
                not i.dead and
                i.infected_for < 1
            ]

            self.list_frame = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 390), (650, 226))),
                get_box(BoxStyles.ROUNDED_BOX, (650, 226)),
                manager=MANAGER,
                anchors={"centerx": "centerx"},
            )
            
            self.heading = pygame_gui.elements.UITextBox("Choose the patient",
                                                        ui_scale(pygame.Rect((150, 25), (500, 40))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(ui_scale(pygame.Rect((100, 113), (281, 197))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/choosing_cat1_frame_ment.png").convert_alpha(),
                                                                (284, 199)), manager=MANAGER)
            
            self.back_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 60), (105, 30))),
                get_arrow(2) + " Back",
                get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
            )
            
            self.previous_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((315, 615), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((451, 615), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )

            self.previous_stage_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((100, 335), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_stage_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((245, 335), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            
            self.previous_stage_button.disable()
            self.next_stage_button.disable()

            self.update_selected_cat()  # Updates the image and details of selected cat
            self.update_cat_list()
        elif self.stage == "choose treatment":
            self.frame_index = 0
            self.text_index = 0
            self.paw = None
            self.talk_box = None
            self.patient_sprite = None
            self.medcat_sprite = None
            self.text = None
            self.textbox_graphic = None
            self.subtitle = None
            self.screenart = None

            self.scroll_container = pygame_gui.elements.UIScrollingContainer(
                ui_scale(pygame.Rect((0, 455), (650, 145))),
                allow_scroll_x=False,
                manager=MANAGER,
                anchors={"centerx": "centerx"}
                )

            self.list_frame = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 390), (650, 226))),
                get_box(BoxStyles.ROUNDED_BOX, (650, 226)),
                manager=MANAGER,
                anchors={"centerx": "centerx"},
            )

            self.heading = pygame_gui.elements.UITextBox("<u>Pick up to four herbs to try.</u>",
                                                        ui_scale(pygame.Rect((150, 25), (500, 40))),
                                                        object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:
            self.mentor_frame = pygame_gui.elements.UIImage(ui_scale(pygame.Rect((100, 113), (281, 197))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/choosing_cat1_frame_ment.png").convert_alpha(),
                                                                (281, 197)), manager=MANAGER)
            
            self.update_herb_buttons()

            self.back_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 60), (105, 30))),
                get_arrow(2) + " Back",
                get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
            )

            self.previous_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((315, 615), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((451, 615), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )

            self.previous_stage_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((100, 335), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_stage_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((245, 335), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )

            self.next_stage_button.disable()
            self.update_selected_cat()
            self.previous_page_button.hide()
            self.next_page_button.hide()

            self.update_treatment_display()
        else:
            self.frame_index = 0
            self.text_index = 0
            self.mentor_frame = None
            self.list_frame = None
            self.scroll_container = None

            for ele in self.selected_details:
                self.selected_details[ele].kill()

            if game.settings["dark mode"]:
                img = "treatment_den_dark"
            else:
                img = "treatment_den_light"
            self.screenart = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (800, 403))),
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
                                            ui_scale(pygame.Rect((70, 220), (150, 150))),
                                            pygame.transform.scale(
                                            infected_cat_1.sprite,
                                            (150, 150)), manager=MANAGER
                                            )
            if infected > 1:
                infected_cat_2 = choice(infected_cats)
                infected_cats.remove(infected_cat_2)
                self.additional_infected_sprites["2"] = pygame_gui.elements.UIImage(
                                            ui_scale(pygame.Rect((505, 215), (125, 125))),
                                            pygame.transform.scale(
                                            infected_cat_2.sprite,
                                            (125, 125)), manager=MANAGER
                                            )
            if infected > 2:
                infected_cat_3 = choice(infected_cats)
                infected_cats.remove(infected_cat_3)
                self.additional_infected_sprites["3"] = pygame_gui.elements.UIImage(
                                            ui_scale(pygame.Rect((225, 230), (100, 100))),
                                            pygame.transform.scale(
                                            infected_cat_3.sprite,
                                            (100, 100)), manager=MANAGER
                                            )
            if infected > 3:
                infected_cat_4 = choice(infected_cats)
                infected_cats.remove(infected_cat_4)
                self.additional_infected_sprites["4"] = pygame_gui.elements.UIImage(
                                            ui_scale(pygame.Rect((625, 230), (100, 100))),
                                            pygame.transform.scale(
                                            infected_cat_4.sprite,
                                            (100, 100)), manager=MANAGER
                                            )
            
            self.text_type = ""
            self.texts = self.choose_treatment_text(self.selected_cat)
            self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
            self.talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()

            self.talk_box = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((89, 471), (624, 151))),
                    self.talk_box_img
                )
            self.textbox_graphic = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((85, 471), (173, 151))),
                image_cache.load_image("resources/images/textbox_graphic.png").convert_alpha()
            )

            self.scroll_container = pygame_gui.elements.UIScrollingContainer(ui_scale(pygame.Rect((250, 485), (450, 150))))
            self.text = pygame_gui.elements.UITextBox("",
                                                    ui_scale(pygame.Rect((0, 0), (450, -50))),
                                                    object_id="#text_box_30_horizleft",
                                                    container=self.scroll_container,
                                                    manager=MANAGER)
            
            self.heading = pygame_gui.elements.UITextBox("Results",
                                                        ui_scale(pygame.Rect((150, 25), (500, 40))),
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
                                                        ui_scale(pygame.Rect((150, 50), (500, 40))),
                                                        object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                        manager=MANAGER)
            
            # Layout Images:

            self.patient_sprite = pygame_gui.elements.UIImage(
                                            ui_scale(pygame.Rect((325, 170), (190, 190))),
                                            pygame.transform.scale(
                                                self.selected_cat.sprite,
                                                (190, 190)), manager=MANAGER)
            self.medcat_sprite = pygame_gui.elements.UIImage(ui_scale(pygame.Rect((35, 450), (200, 200))),
                                                                        pygame.transform.scale(
                                                                            self.the_cat.sprite,
                                                                            (200, 200)), manager=MANAGER)
            
            self.back_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((25, 60), (105, 30))),
                get_arrow(2) + " Back",
                get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
            )
        
            self.previous_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((315, 615), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_page_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((451, 615), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )

            self.previous_stage_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((100, 335), (34, 34))),
                Icon.ARROW_LEFT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            self.next_stage_button = UISurfaceImageButton(
                ui_scale(pygame.Rect((245, 335), (34, 34))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON, (34, 34)),
                object_id="@buttonstyles_icon",
                starting_height=0,
            )
            
            self.paw = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((685, 590), (15, 15))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
            self.paw.visible = False
            
            self.previous_page_button.hide()
            self.next_page_button.hide()
            self.previous_stage_button.hide()
            self.next_stage_button.hide()

        self.update_correct_cure()
    
    def update_correct_cure(self):
        # find the correct cure for the cat, since not all cats being treated
        # will necessary have the CURRENT infection.
        # it could be a newly invited outsider with an old infection
        # thanks to tami for reminding me this is possible lol

        self.correct_cure = get_infection_info("cure", self.selected_cat)

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

        if self.scroll_container:
            self.scroll_container.kill()
            del self.scroll_container
        
        if self.heading:
            self.heading.kill()
            del self.heading
      
        if self.subtitle:
            self.subtitle.kill()
            del self.subtitle
      
        if self.list_frame:
            self.list_frame.kill()
            del self.list_frame
      
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
        """ determine if the medcat will even be effective in attempting treatment.
        if a treatment is failed, no information on the herbs is given to the player. """

        stageone = True if "stage one infection" in patient.illnesses else False
        stagetwo = True if "stage two infection" in patient.illnesses else False
        stagethree = True if "stage three infection" in patient.illnesses else False
        stagefour = True if "stage four infection" in patient.illnesses else False

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

        if len(self.medcats) == 2:
            failchance -= 10
        elif len(self.medcats) > 2:
            failchance -= 10 + 2 * (len(self.medcats) - 2)

        chance = randint(1,100)
        if chance < failchance:
            return False
        else:
            return True

    RESOURCE_DIR = "resources/dicts/infection"

    def choose_treatment_text(self, patient):
        """ choosing text from the json regarding the success or failure of the treatment."""
        inftype = get_infection_info("type")
        with open(f"{self.RESOURCE_DIR}/treatment_results.json",
                encoding="ascii") as read_file:
            self.m_txt = ujson.loads(read_file.read())

        self.the_cat = choice(self.medcats)

        who_key = ""
        if self.the_cat == game.clan.your_cat:
            who_key = "you "
        
        curelist = []
        for num in self.correct_cure:
            curelist.append(get_infection_herb(num))
        
        if self.herb1 in curelist:
            herb_1 = True
        else:
            herb_1 = False
        if self.herb2 in curelist:
            herb_2 = True
        else:
            herb_2 = False
        if self.herb3 in curelist:
            herb_3 = True
        else:
            herb_3 = False
        if self.herb4 in curelist:
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

        successkey = ""
        success = self.get_failure_chance(patient)

        if correct == 4:
            success = True

        # success = False
        # ^ debug

        if not success:
            successkey = " failure"
        
        herbinsert = f" {str(herbcount)}herb"

        infection_stage = ""
        for illness in self.selected_cat.illnesses:
            if illness == "stage one infection":
                infection_stage = "stageone"
            if illness == "stage two infection":
                infection_stage = "stagetwo"
            if illness == "stage three infection":
                infection_stage = "stagethree"
            if illness == "stage four infection":
                infection_stage = "stagefour"

        if not get_infection_info("cure_discovered", self.selected_cat) or (get_infection_info("cure_discovered", self.selected_cat) and correct < 4):
            if self.selected_cat.status == "newborn":
                ceremony_txt = self.m_txt[who_key + "newborn" + successkey]
            try:
                if success:
                    ceremony_txt = self.m_txt[who_key + infection_stage + " " + correctherbs + herbinsert + successkey]
                else:
                    ceremony_txt = self.m_txt[who_key + infection_stage + herbinsert + successkey]

                    
            except KeyError:
                try:
                    if success:
                        ceremony_txt = self.m_txt[who_key + " " + correctherbs + herbinsert + successkey]
                    else:
                        ceremony_txt = self.m_txt[who_key + herbinsert + successkey]
                except:
                    try:
                        if success:
                            ceremony_txt = self.m_txt[who_key + " " + correctherbs  + successkey]
                        else:
                            ceremony_txt = self.m_txt[who_key + " " + successkey]
                    except Exception as e:
                        print("NO TEXT FOUND")
                        print(e)
                        print(success, "|", who_key + " " + correctherbs  + successkey)
                        ceremony_txt = (self.m_txt[who_key + "anystage anyright anyherb" + successkey])
        
        else:
           ceremony_txt = (self.m_txt[who_key + "cure_found"])

        self.add_to_treatments(patient, success)

        chosenkey = choice(ceremony_txt)
        return self.get_adjusted_txt(chosenkey, self.selected_cat, self.the_cat)

    def add_to_treatments(self, patient, success):
        """ Adds the treatment information to the json for logging. """
        if not success:
            return
        
        infection_type = get_infection_type(self.selected_cat)
        correct_infection = None
        for item in game.clan.infection:
            if isinstance(game.clan.infection[item], dict):
                if "type" in game.clan.infection[item]:
                    if game.clan.infection[item]["type"] == infection_type:
                        correct_infection = game.clan.infection[item]
                        break

        curelist = []
        for num in correct_infection["cure"]:
            curelist.append(get_infection_herb(num))

        herblist = [self.herb1, self.herb2, self.herb3, self.herb4]
        correctherbs = [herb for herb in herblist if herb in curelist]

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
                if illness not in ["stage one infection", "stage two infection", "stage three infection", "stage four infection"]:
                    sick = True
            if not sick:
                remission_chance -= 8

            if cure_one:
                remission_chance -= remission_chance / 4
            elif cure_two:
                remission_chance -= remission_chance / 3
            elif cure_three:
                remission_chance -= remission_chance / 2
            
            if len(self.medcats) < 2:
                remission_chance += len(self.medcats) / 5
            elif len(self.medcats) < 4:
                remission_chance += len(self.medcats) / 3
            else:
                remission_chance += len(self.medcats) / 2

            if remission_chance <= 1:
                remission_chance = 1

            # if int(random.random() * remission_chance):
            # ^ debug
            if not int(random.random() * remission_chance):
                game.clan.infection["treated"].append(patient.ID)

        treatment = {
            "type": infection_type,
            "moon": game.clan.age,
            "herbs": [herb for herb in herblist if herb is not None],
            "correct_herbs": len(correctherbs)
        }

        if (len(correctherbs) != 4) or (len(correctherbs) == 4 and get_infection_info("cure_discovered") is False):
            game.clan.infection["treatments"].append(treatment)
        
        if cure:
            print(patient.name, "appended to treated")
            game.clan.infection["treated"].append(patient.ID)
            if not get_infection_info("cure_discovered"):
                update_infection_info("cure_discovered", True)
        
        herbs = game.clan.herbs.copy()
        for herb in herbs:
            if herb in herblist:
                game.clan.herbs[herb] -= 1
                if game.clan.herbs[herb] <= 0:
                    game.clan.herbs.pop(herb)

        used_herbs = []
        for herb in herblist:
            if herb is not None:
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
        inftype = get_infection_info("type")
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_cat:

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((116, 155), (135, 135))),
                pygame.transform.scale(
                    self.selected_cat.sprite,
                    (135, 135)), manager=MANAGER)

            infection_stage = ""
            for illness in self.selected_cat.illnesses:
                if illness == "stage one infection":
                    infection_stage = "stage one"
                if illness == "stage two infection":
                    infection_stage = "stage two"
                if illness == "stage three infection":
                    infection_stage = "stage three"
                if illness == "stage four infection":
                    infection_stage = "stage four"
            
            quar = "quarantined" if self.selected_cat.quarantined else ""
            info = self.selected_cat.status + "\n" + \
                   self.selected_cat.genderalign + "\n <b>" + infection_stage + "</b> \n" + quar
            
            self.selected_details["selected_info"] = pygame_gui.elements.UITextBox(info,
                                                                                   ui_scale(pygame.Rect((270, 162),
                                                                                                     (105, 125))),
                                                                                   object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                   manager=MANAGER)

            name = str(self.selected_cat.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["victim_name"] = pygame_gui.elements.ui_label.UILabel(
                ui_scale(pygame.Rect((130, 115), (110, 30))),
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
        pos_y = 30
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((100 + pos_x, 390 + pos_y), (50, 50))),
                cat.sprite, cat_object=cat, manager=MANAGER)
            pos_x += 60
            if pos_x >= 550:
                pos_x = 0
                pos_y += 60
            i += 1

    def get_valid_cats(self):
        """ find all of the infected cats to choose from """
        inftype = get_infection_info("type")
        infected_cats = []

        for cat in Cat.all_cats_list:
            if (
                not cat.dead and
                not cat.outside and
                ("stage one infection" in cat.illnesses or
                 "stage two infection" in cat.illnesses or
                 "stage three infection" in cat.illnesses or
                 "stage four infection" in cat.illnesses) and
                 cat.ID not in game.clan.infection["treated"]):
                infected_cats.append(cat)
        
        return infected_cats

    def on_use(self):
        super().on_use()

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
