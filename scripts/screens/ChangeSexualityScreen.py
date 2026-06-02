from re import sub
from typing import Dict, Union

import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from ..ui.elements.image_button import UIImageButton
from ..ui.elements.checkbox import UICheckbox
from ..ui.elements.surface_image_button import UISurfaceImageButton
from ..ui.theme import get_text_box_theme
from ..ui.scale import ui_scale, ui_scale_dimensions

from .Screens import Screens
from .enums import GameScreen
from ..game_structure.game.switches import switch_get_value, switch_set_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_button import get_button_dict, ButtonStyles

from scripts.cat.sexuality import Sexuality, Arospec, Acespec
from ..ui.icon import Icon

class ChangeSexualityScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.the_cat = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.back_button = None  
        self.save_button = None  
        self.elements: Dict[
            str,
            Union[
                pygame_gui.elements.UIPanel,
                pygame_gui.core.UIElement,
                pygame_gui.core.IContainerLikeInterface,
            ],
        ] = {}

        self.next_cat = None
        self.previous_cat = None
        self.selected_cat_elements = {}

        self.sexuality_panel_items = {}
        self.arospec_panel_items = {}
        self.acespec_panel_items = {}

        self.sexuality_cycle = []
        self.arospec_cycle = []
        self.acespec_cycle = []

        self.sexuality_checkboxes = {}
        self.acespec_checkboxes = {}
        self.arospec_checkboxes = {}


        # starting LABELS for the cycle buttons
        self.current_sexuality_label = None
        self.current_arospec_label = None
        self.current_acespec_label = None
        self.current_t4t = None
        # sexuality that is applied to the cat when Saved
        self.new_sexuality = {}

    def screen_switches(self):
        super().screen_switches()

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "buttons.next_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.previous_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )

        self.save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 645), (105, 30))),
            "buttons.save",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"centerx":"centerx"}
        )

        self.elements["switch_screen"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((15, 645), (30, 30))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (30, 30)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            anchors={"left_target":self.save_button},
            tool_tip_text="Edit Gender"
        )

        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 100), (699, 520))),
            pygame.transform.scale(
                pygame.image.load(
                    "resources/images/sexuality_framing.png"
                ).convert_alpha(),
                ui_scale_dimensions((699, 520)),
            ),
            manager=MANAGER,
        )

        self.update_selected_cat()

        self.update_cycle_progressions()
        self.get_initial_sexuality_labels()
        self.current_arospec_label = self.the_cat.sexuality.arospec
        self.current_acespec_label = self.the_cat.sexuality.acespec
        self.current_t4t = self.the_cat.sexuality.t4t

        self.create_sexuality_panels()

        self.update_save_button()

        self.elements["help"] = UIImageButton(
            ui_scale(pygame.Rect((100, 160), (34, 34))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text="<b>Welcome to the sexuality screen!</b>\nHere, you can set your cat's orientations to be one of the already existing ones ingame, or give them a custom one. Use the checkboxes to define their attraction and use the text box to give them a label.<br>There are only checkboxes for attraction to toms and she-cats. Nonbinary cats will always be included.",
        )
    def get_initial_sexuality_labels(self):
        self.current_sexuality_label = (
            self.the_cat.sexuality.sexuality_label if
            self.the_cat.sexuality.sexuality_label else
            self.the_cat.sexuality.generate_sexuality_label(
                self.the_cat.genderalign,
                change_sexuality_screen=True,
                existing_label=self.the_cat.sexuality.sexuality_label
            )
        )
        self.current_acespec_label = self.the_cat.sexuality.acespec

        self.current_arospec_label = self.the_cat.sexuality.arospec

    def update_save_button(self):
        if not self.new_sexuality:
            self.save_button.disable()
        else:
            self.save_button.enable()
    
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(GameScreen.PROFILE)
            if event.ui_element == self.save_button:
                self.save_new_sexuality()
                self.update_selected_cat()
                self.clear_sexuality_panels()
                self.create_sexuality_panels()
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    self.new_sexuality = {}
                    self.update_selected_cat()
                    self.get_initial_sexuality_labels()
                    self.update_cycle_progressions()
                    self.clear_sexuality_panels()
                    self.create_sexuality_panels()
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    self.new_sexuality = {}
                    self.update_selected_cat()
                    self.get_initial_sexuality_labels()
                    self.update_cycle_progressions()
                    self.clear_sexuality_panels()
                    self.create_sexuality_panels()
            elif event.ui_element == self.sexuality_panel_items["cycle"]:
                self.cycle_next_sexuality()
                self.clear_sexuality_panels()
                self.create_sexuality_panels()
            elif event.ui_element == self.acespec_panel_items["cycle"]:
                self.cycle_next_acespec()
                self.clear_sexuality_panels()
                self.create_sexuality_panels()
            elif event.ui_element == self.arospec_panel_items["cycle"]:
                self.cycle_next_arospec()
                self.clear_sexuality_panels()
                self.create_sexuality_panels()
            elif event.ui_element == self.selected_cat_elements["t4t_checkbox"]:
                if event.ui_element.checked:
                    event.ui_element.uncheck()
                    self.current_t4t = False
                else:
                    event.ui_element.check()
                    self.current_t4t = True
            elif event.ui_element == self.sexuality_panel_items["clear_label"]:
                self.the_cat.sexuality.custom_sexuality_label = ""
                self.update_selected_cat()
                self.clear_sexuality_panel()
                self.create_sexuality_panel()
            elif event.ui_element == self.acespec_panel_items["clear_label"]:
                self.the_cat.sexuality.acespec_label = ""
                self.update_selected_cat()
                self.clear_acespec_panel()
                self.create_acespec_panel()
            elif event.ui_element == self.arospec_panel_items["clear_label"]:
                self.the_cat.sexuality.arospec_label = ""
                self.update_selected_cat()
                self.clear_arospec_panel()
                self.create_arospec_panel()
            
            elif event.ui_element == self.elements["switch_screen"]:
                self.change_screen(GameScreen.CHANGE_GENDER)
            
            # CHECKBOXES
            for value, button in self.sexuality_checkboxes.items():
                if event.ui_element == button:
                    if value not in self.new_sexuality:
                        self.new_sexuality[value] = True
                    else:
                        if self.new_sexuality[value] is True:
                            self.new_sexuality[value] = False
                        else:
                            self.new_sexuality[value] = True
                    self.update_sexuality_checkboxes()
            for value, button in self.acespec_checkboxes.items():
                if event.ui_element == button:
                    if "acespec" in self.new_sexuality and self.new_sexuality["acespec"] == value:
                        self.new_sexuality.pop("acespec")
                    else:
                        self.new_sexuality["acespec"] = value
                    self.update_acespec_checkboxes()
            for value, button in self.arospec_checkboxes.items():
                if event.ui_element == button:
                    if "arospec" in self.new_sexuality and self.new_sexuality["arospec"] == value:
                        self.new_sexuality.pop("arospec")
                    else:
                        self.new_sexuality["arospec"] = value
                    self.update_arospec_checkboxes()
            self.update_save_button()

    def exit_screen(self):
        # kill everything
        self.back_button.kill()
        del self.back_button
        self.save_button.kill()
        del self.save_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        for ele in self.elements:
            self.elements[ele].kill()
        self.elements = {}

        for ele in self.sexuality_panel_items:
            self.sexuality_panel_items[ele].kill()
        self.sexuality_panel_items = {}

        for ele in self.arospec_panel_items:
            self.arospec_panel_items[ele].kill()
        self.arospec_panel_items = {}

        for ele in self.acespec_panel_items:
            self.acespec_panel_items[ele].kill()
        self.acespec_panel_items = {}

    def save_new_sexuality(self):
        self.the_cat.sexuality.clear_upcoming_sexuality()
        # print("Saving:", self.new_sexuality)

        if "likes_toms" in self.new_sexuality:
            self.the_cat.sexuality.likes_toms = self.new_sexuality["likes_toms"]
        if "likes_she_cats" in self.new_sexuality:
            self.the_cat.sexuality.likes_she_cats = self.new_sexuality["likes_she_cats"]

        if "acespec" in self.new_sexuality:
            self.the_cat.sexuality.acespec = self.new_sexuality["acespec"]
        if "arospec" in self.new_sexuality:
            self.the_cat.sexuality.arospec = self.new_sexuality["arospec"]

        self.the_cat.sexuality.sexuality_label = self.the_cat.sexuality.generate_sexuality_label(
            self.the_cat.genderalign,
            override_label=self.current_sexuality_label
            )
        # custom label
        custom_label = self.sexuality_panel_items["sexuality_label_input"].get_text()
        if custom_label and custom_label != self.the_cat.sexuality.sexuality_label:
            self.the_cat.sexuality.custom_sexuality_label = custom_label

        acespec_label = self.acespec_panel_items["acespec_label_input"].get_text()
        if (
            acespec_label and
            acespec_label != self.the_cat.sexuality.acespec and
            acespec_label not in self.acespec_cycle
            ):
            self.the_cat.sexuality.acespec_label = acespec_label

        arospec_label = self.arospec_panel_items["arospec_label_input"].get_text()
        if (
            arospec_label and
            arospec_label != self.the_cat.sexuality.arospec and
            arospec_label not in self.arospec_cycle
            ):
            self.the_cat.sexuality.arospec_label = arospec_label

        if self.current_t4t:
            self.the_cat.sexuality.t4t = True

        # variables
        self.current_acespec_label = self.the_cat.sexuality.acespec
        self.current_arospec_label = self.the_cat.sexuality.arospec

        self.new_sexuality = {}
        self.the_cat.sexuality.give_bandanas(self.the_cat)
        self.the_cat.pelt.rebuild_sprite = True

    def update_selected_cat(self):
        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        if not self.the_cat:
            return
        
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.new_sexuality["likes_toms"] = self.the_cat.sexuality.likes_toms
        self.new_sexuality["likes_she_cats"] = self.the_cat.sexuality.likes_she_cats
        self.new_sexuality["acespec"] = self.the_cat.sexuality.acespec
        self.new_sexuality["arospec"] = self.the_cat.sexuality.arospec

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((180, 115), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )
        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()
        self.update_previous_next_cat_buttons()

        self.selected_cat_elements["header"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 62), (325, 32))),
            "screens.change_sexuality.heading",
            text_kwargs={"name": str(self.the_cat.name), "m_c": self.the_cat},
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            anchors={"centerx": "centerx"},
        )
        info = ""
        info += self.the_cat.genderalign + "\n"
        info += self.the_cat.sexuality.get_sexuality_profile_display()

        self.selected_cat_elements["name"] = pygame_gui.elements.UITextBox(
            f"<b>{self.the_cat.name}</b>",
            ui_scale(pygame.Rect((355, 140), (400, 80))),
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
        )
        self.selected_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((355, 170), (145, 120))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
        )
        self.selected_cat_elements["t4t_label"] = pygame_gui.elements.UITextBox(
            "T4T",
            ui_scale(pygame.Rect((550, 192), (105, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
        )
        self.selected_cat_elements["t4t_checkbox"] = UICheckbox(
            (520, 190),
            container=None,
            manager=MANAGER,
            check=self.current_t4t,
            tool_tip_text="T4T cats will only become mates with other trans and nonbinary cats.",
        )
        if self.the_cat.genderalign == self.the_cat.gender:
            self.selected_cat_elements["t4t_checkbox"].disable()

    def clear_sexuality_panels(self):
        self.clear_acespec_panel()
        self.clear_sexuality_panel()
        self.clear_arospec_panel()

    def create_sexuality_panels(self):
        self.create_sexuality_panel()
        self.create_acespec_panel()
        self.create_arospec_panel()
    
    # individual ones
    # SEXUALITY PANEL
    def clear_sexuality_panel(self):
        for ele in self.sexuality_panel_items:
            self.sexuality_panel_items[ele].kill()
        self.sexuality_panel_items = {}

    def create_sexuality_panel(self):
        self.sexuality_panel_items["container"] = UIContainer(
            ui_scale(pygame.Rect((60, 295), (225, 315))),
            manager=MANAGER,
            starting_height=5,
        )

        next_sexuality = self.next_sexuality_label()
        self.sexuality_panel_items["cycle"] = UIImageButton(
            ui_scale(pygame.Rect((0, 20), (117, 45))),
            "",
            object_id=f"#change_to_{next_sexuality}_button",
            tool_tip_text=f"Change to {next_sexuality.replace('XX', '')}",
            manager=MANAGER,
            anchors={"centerx": "centerx"},
            container=self.sexuality_panel_items["container"]
        )
        self.sexuality_panel_items["sexuality_label_input_label"] = pygame_gui.elements.UITextBox(
            "Custom Sexuality",
            ui_scale(pygame.Rect((0, 107), (165, 30))),
            object_id="#text_box_26_horizcenter",
            manager=MANAGER,
            container=self.sexuality_panel_items["container"],
            anchors={"centerx": "centerx"}
        )
        self.sexuality_panel_items["clear_label"] = UIImageButton(
            ui_scale(pygame.Rect((8, 142), (25, 25))),
            "",
            object_id="#exit_window_button",
            tool_tip_text="Remove custom label",
            container=self.sexuality_panel_items["container"],
            manager=MANAGER,
            )
        if self.the_cat.sexuality.custom_sexuality_label:
            self.sexuality_panel_items["clear_label"].enable()
        else:
            self.sexuality_panel_items["clear_label"].disable()

        self.sexuality_panel_items["sexuality_label_input"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((10, 140), (165, 30))),
            placeholder_text=(
                self.current_sexuality_label.replace("XX", "")
                ),
            manager=MANAGER,
            container=self.sexuality_panel_items["container"],
            anchors={"centerx": "centerx"}
        )
        # checkbox labels
        self.sexuality_panel_items["likes_toms_label"] = pygame_gui.elements.UITextBox(
            "Toms",
            ui_scale(pygame.Rect((75, 180), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.sexuality_panel_items["container"]
        )
        self.sexuality_panel_items["likes_she_cats_label"] = pygame_gui.elements.UITextBox(
            "She-cats",
            ui_scale(pygame.Rect((75, 220), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.sexuality_panel_items["container"]
        )
        self.update_sexuality_checkboxes()

    def update_sexuality_checkboxes(self):
        for ele in self.sexuality_checkboxes:
            self.sexuality_checkboxes[ele].kill()
        self.sexuality_checkboxes = {}

        # LIKES TOMS
        self.sexuality_checkboxes["likes_toms"] = UICheckbox(
            (40, 180),
            container=self.sexuality_panel_items["container"],
            manager=MANAGER,
            check="likes_toms" in self.new_sexuality and self.new_sexuality["likes_toms"]
        )
        # LIKES SHECATS
        self.sexuality_checkboxes["likes_she_cats"] = UICheckbox(
            (40, 220),
            container=self.sexuality_panel_items["container"],
            manager=MANAGER,
            check="likes_she_cats" in self.new_sexuality and self.new_sexuality["likes_she_cats"]
        )

    def cycle_next_sexuality(self):
        next_sexuality = self.next_sexuality_label()

        # all labels with tuple values for (likes_toms, likes_she_cats)
        new_sexuality_dict = {
            "gay": (True, False),
            "lesbian": (False, True),
            "biXX": (True, True),
            "panXX": (True, True),
            "aroace": (False, False),
            "gynoXX": (False, True),
            "androXX": (True, False),
            "questioning": (None, None)
        }
        if self.the_cat.genderalign in Sexuality.male_genders:
            new_sexuality_dict["straight"] = (False, True)
        elif self.the_cat.genderalign in Sexuality.female_genders:
            new_sexuality_dict["straight"] = (True, False)
        
        self.current_sexuality_label = next_sexuality
        self.new_sexuality["likes_toms"] = new_sexuality_dict[next_sexuality][0]
        self.new_sexuality["likes_she_cats"] = new_sexuality_dict[next_sexuality][1]

        self.correct_other_labels("sexuality")
    
    def next_sexuality_label(self):
        current_index = self.sexuality_cycle.index(self.current_sexuality_label)
        next_index = current_index + 1
        if next_index >= len(self.sexuality_cycle):
            next_index = 0
        
        next_sexuality = self.sexuality_cycle[next_index]

        return next_sexuality

    def clear_acespec_panel(self):
        for ele in self.acespec_panel_items:
            self.acespec_panel_items[ele].kill()
        self.acespec_panel_items = {}

    def create_acespec_panel(self):
        self.acespec_panel_items["container"] = UIContainer(
            ui_scale(pygame.Rect((5, 295), (220, 315))),
            manager=MANAGER,
            starting_height=5,
            anchors={
                "left_target": self.sexuality_panel_items["container"]
                }
        )
        next_acespec = self.next_acespec_label()
        self.acespec_panel_items["cycle"] = UIImageButton(
            ui_scale(pygame.Rect((0, 20), (117, 45))),
            "",
            object_id=f"#change_to_{next_acespec}_button",
            tool_tip_text=f"Change to {next_acespec}",
            manager=MANAGER,
            anchors={"centerx": "centerx"},
            container=self.acespec_panel_items["container"]
        )
        self.acespec_panel_items["acespec_label_input_label"] = pygame_gui.elements.UITextBox(
            "Custom Acespec",
            ui_scale(pygame.Rect((0, 107), (165, 30))),
            object_id="#text_box_26_horizcenter",
            manager=MANAGER,
            container=self.acespec_panel_items["container"],
            anchors={"centerx": "centerx"}
        )
        self.acespec_panel_items["clear_label"] = UIImageButton(
            ui_scale(pygame.Rect((8, 142), (25, 25))),
            "",
            object_id="#exit_window_button",
            tool_tip_text="Remove custom label",
            container=self.acespec_panel_items["container"],
            manager=MANAGER,
            )
        if self.the_cat.sexuality.acespec_label:
            self.acespec_panel_items["clear_label"].enable()
        else:
            self.acespec_panel_items["clear_label"].disable()
        placeholdertext = (
                self.the_cat.sexuality.acespec_label if
                self.the_cat.sexuality.acespec_label else
                self.current_acespec_label
                )
        self.acespec_panel_items["acespec_label_input"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((10, 140), (165, 30))),
            placeholder_text=placeholdertext,
            manager=MANAGER,
            container=self.acespec_panel_items["container"],
            anchors={"centerx": "centerx"}
        )

        # checkbox labels
        y_pos = 170
        self.acespec_panel_items["allo_label"] = pygame_gui.elements.UITextBox(
            "Regular attraction",
            ui_scale(pygame.Rect((55, y_pos), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.acespec_panel_items["container"]
        )
        self.acespec_panel_items["demi_label"] = pygame_gui.elements.UITextBox(
            "Demi attraction",
            ui_scale(pygame.Rect((55, y_pos + 35), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.acespec_panel_items["container"]
        )
        self.acespec_panel_items["grey_label"] = pygame_gui.elements.UITextBox(
            "Rare attraction",
            ui_scale(pygame.Rect((55, y_pos + 35 * 2), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.acespec_panel_items["container"]
        )
        self.acespec_panel_items["ace_label"] = pygame_gui.elements.UITextBox(
            "No attraction",
            ui_scale(pygame.Rect((55, y_pos + 35 * 3), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.acespec_panel_items["container"]
        )
        self.update_acespec_checkboxes()

    def update_acespec_checkboxes(self):
        for ele in self.acespec_checkboxes:
            self.acespec_checkboxes[ele].kill()
        self.acespec_checkboxes = {}

        y_pos = 170
        for item in self.acespec_cycle:
            self.acespec_checkboxes[item] = UICheckbox(
                (25, y_pos),
                container=self.acespec_panel_items["container"],
                manager=MANAGER,
                check="acespec" in self.new_sexuality and self.new_sexuality["acespec"] == item
            )
            y_pos += 35
    
    def cycle_next_acespec(self):
        """
        Sets all variables to the newly selected acespec label
        """

        next_acespec = self.next_acespec_label()
        self.current_acespec_label = next_acespec
        self.new_sexuality["acespec"] = self.current_acespec_label

        self.correct_other_labels("acespec")
    
    def next_acespec_label(self):
        """
        Finds the next acespec label to cycle to
        """
        current_index = self.acespec_cycle.index(self.current_acespec_label)
        next_index = current_index + 1
        if next_index >= len(self.acespec_cycle):
            next_index = 0
        
        next_acespec = self.acespec_cycle[next_index]

        return next_acespec


    # AROSPEC PANEL
    def clear_arospec_panel(self):
        for ele in self.arospec_panel_items:
            self.arospec_panel_items[ele].kill()
        self.arospec_panel_items = {}

    def create_arospec_panel(self):
        self.arospec_panel_items["container"] = UIContainer(
            ui_scale(pygame.Rect((5, 295), (220, 315))),
            manager=MANAGER,
            starting_height=5,
            anchors={
                "left_target": self.acespec_panel_items["container"]
                }
        )
        next_arospec = self.next_arospec_label()
        self.arospec_panel_items["cycle"] = UIImageButton(
            ui_scale(pygame.Rect((0, 20), (117, 45))),
            "",
            object_id=f"#change_to_{next_arospec}_button",
            tool_tip_text=f"Change to {next_arospec}",
            manager=MANAGER,
            anchors={"centerx": "centerx"},
            container=self.arospec_panel_items["container"]
        )
        self.arospec_panel_items["arospec_label_input_label"] = pygame_gui.elements.UITextBox(
            "Custom Arospec",
            ui_scale(pygame.Rect((0, 107), (165, 30))),
            object_id="#text_box_26_horizcenter",
            manager=MANAGER,
            container=self.arospec_panel_items["container"],
            anchors={"centerx": "centerx"}
        )
        self.arospec_panel_items["clear_label"] = UIImageButton(
            ui_scale(pygame.Rect((8, 142), (25, 25))),
            "",
            object_id="#exit_window_button",
            tool_tip_text="Remove custom label",
            container=self.arospec_panel_items["container"],
            manager=MANAGER
            )
        if self.the_cat.sexuality.arospec_label:
            self.arospec_panel_items["clear_label"].enable()
        else:
            self.arospec_panel_items["clear_label"].disable()

        self.arospec_panel_items["arospec_label_input"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((10, 140), (165, 30))),
            placeholder_text=(
                self.the_cat.sexuality.arospec_label if
                self.the_cat.sexuality.arospec_label else
                self.current_arospec_label
                ),
            manager=MANAGER,
            container=self.arospec_panel_items["container"],
            anchors={"centerx": "centerx"}
        )
        # checkbox labels
        y_pos = 170
        self.arospec_panel_items["allo_label"] = pygame_gui.elements.UITextBox(
            "Regular attraction",
            ui_scale(pygame.Rect((55, y_pos), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.arospec_panel_items["container"]
        )
        self.arospec_panel_items["demi_label"] = pygame_gui.elements.UITextBox(
            "Demi attraction",
            ui_scale(pygame.Rect((55, y_pos + 35), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.arospec_panel_items["container"]
        )
        self.arospec_panel_items["grey_label"] = pygame_gui.elements.UITextBox(
            "Rare attraction",
            ui_scale(pygame.Rect((55, y_pos + 35 * 2), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.arospec_panel_items["container"]
        )
        self.arospec_panel_items["ace_label"] = pygame_gui.elements.UITextBox(
            "No attraction",
            ui_scale(pygame.Rect((55, y_pos + 35 * 3), (140, 30))),
            object_id="#text_box_26_horizleft",
            manager=MANAGER,
            container=self.arospec_panel_items["container"]
        )
        self.update_arospec_checkboxes()
    
    def update_arospec_checkboxes(self):
        for ele in self.arospec_checkboxes:
            self.arospec_checkboxes[ele].kill()
        self.arospec_checkboxes = {}

        y_pos = 170
        for item in self.arospec_cycle:
            self.arospec_checkboxes[item] = UICheckbox(
                (25, y_pos),
                container=self.arospec_panel_items["container"],
                manager=MANAGER,
                check="arospec" in self.new_sexuality and self.new_sexuality["arospec"] == item
            )
            y_pos += 35

    def cycle_next_arospec(self):
        """
        Sets all variables to the newly selected arospec label
        """

        next_arospec = self.next_arospec_label()
        self.current_arospec_label = next_arospec
        self.new_sexuality["arospec"] = self.current_arospec_label

        self.correct_other_labels("arospec")
    
    def next_arospec_label(self):
        """
        Finds the next arospec label to cycle to
        """
        current_index = self.arospec_cycle.index(self.current_arospec_label)
        next_index = current_index + 1
        if next_index >= len(self.arospec_cycle):
            next_index = 0
        
        next_arospec = self.arospec_cycle[next_index]

        return next_arospec


    def update_cycle_progressions(self):

        self.acespec_cycle = [
            Acespec.ALLO,
            Acespec.DEMI,
            Acespec.GREY,
            Acespec.ACE
        ]
        self.arospec_cycle = [
            Arospec.ALLO,
            Arospec.DEMI,
            Arospec.GREY,
            Arospec.ARO
        ]

        if self.the_cat.genderalign in Sexuality.male_genders:
            self.sexuality_cycle = [
                "straight",
                "biXX",
                "panXX",
                "gay",
                "aroace",
                "questioning"
            ]
        elif self.the_cat.genderalign in Sexuality.female_genders:
            self.sexuality_cycle = [
                "straight",
                "biXX",
                "panXX",
                "lesbian",
                "aroace",
                "questioning"
            ]
        else:
            self.sexuality_cycle = [
                "androXX",
                "biXX",
                "panXX",
                "gynoXX",
                "aroace",
                "questioning"
            ]

    def on_use(self):
        super().on_use()
        self.update_save_button()
        if (
                (
                self.sexuality_panel_items["sexuality_label_input"].get_text() not in (
                "", self.current_sexuality_label
                    )
                )
                or
                (
                self.acespec_panel_items["acespec_label_input"].get_text() not in (
                "", self.current_acespec_label, self.acespec_cycle
                    )
                )
                or
                (
                self.arospec_panel_items["arospec_label_input"].get_text() not in (
                "", self.current_arospec_label, self.arospec_cycle
                    )
                )
            ):
            self.new_sexuality["label_update"] = True
        else:
            if "label_update" in self.new_sexuality:
                self.new_sexuality.pop("label_update")
    
    def correct_other_labels(self, selected_label=""):
        """
        Corrects labels to match each other.
        other_label is the label that was just selected, so it has priority and stays the same.
        """
        if selected_label == "sexuality":
            if self.current_sexuality_label == "aroace":
                self.current_acespec_label = Acespec.ACE
                self.new_sexuality["acespec"] = Acespec.ACE
                self.current_arospec_label = Arospec.ARO
                self.new_sexuality["arospec"] = Arospec.ARO
            else:
                if (
                    self.current_acespec_label == Acespec.ACE and
                    self.current_arospec_label == Arospec.ARO
                ):
                    self.current_acespec_label = Acespec.ALLO
                    self.new_sexuality["acespec"] = Acespec.ALLO
        elif selected_label in ("arospec", "acespec"):
            if (
                self.current_acespec_label == Acespec.ACE and
                self.current_arospec_label == Arospec.ARO
            ):
                self.current_sexuality_label = "aroace"
                self.new_sexuality["likes_toms"] = False
                self.new_sexuality["likes_she_cats"] = False
                self.new_sexuality["acespec"] = Acespec.ACE
                self.new_sexuality["arospec"] = Arospec.ARO

