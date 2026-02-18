import pygame
import re
from random import choice
from .Screens import Screens
from scripts.game_structure.audio import sound_manager

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISurfaceImageButton,
)
from scripts.screens.enums import GameScreen

from scripts.events_module.dialogue.dialogue import Dialogue

from ..game_structure.game.switches import switch_get_value, Switch
from ..game_structure.game.settings import game_setting_get
from ..cat.enums import CatGroup

import pygame_gui
from scripts.game_structure import game
# pylint: disable=consider-using-dict-items
# pylint: disable=consider-using-enumerate
from scripts.utility import (
    ui_scale,
    get_current_season,
    ui_scale_dimensions,
    generate_sprite,
    shorten_text_to_fit,
    get_current_camp,
    assign_new_bg,
    process_text,
    event_text_adjust
    )
from scripts.game_structure.screen_settings import MANAGER
from ..ui.generate_button import ButtonStyles, get_button_dict
from itertools import accumulate as _accumulate


class TalkScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.the_cat = None
        self.speaking_cat = None
        self.other_clan = None
        self.clock = pygame.time.Clock()
        self.typing_delay = 20
        self.next_frame_time = pygame.time.get_ticks() + self.typing_delay

        # STORED DIALOGUE INFO
        self.current_scene = ""
        self.current_line = ""
        self.texts = ""

        self.text_index = 0
        self.frame_index = 0
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
    
        self.chosen_text_key = ""
        self.chosen_text_value = {}
        self.chosen_text_object = {}

        # SCREEN ELEMENTS
        self.scroll_container = None
        self.dialogue_box = None
        self.textbox_graphic = None

        self.speaking_cat_elements = {}
        self.other_dict = {}
        self.cat_dict = {}

        self.back_button = None
        self.choice_buttons = {}
        self.choice_display = {}

        # BOOLS
        self.created_choice_buttons = False
        self.meow = False

        # DIALOGUE CLASS (to be instantiated later, as it's done for each new dialogue)
        self.dialogue_class = None

    def screen_switches(self):
        super().screen_switches()

        self.the_cat = Cat.all_cats.get(switch_get_value(Switch.cat))
        self.dialogue_class = Dialogue(cat=self.the_cat, you=game.clan.your_cat)
        self.speaking_cat = self.the_cat
        self.other_clan = choice(game.clan.all_other_clans)

        self.cat_dict.clear()
        self.other_dict.clear()
        self.text_index = 0
        self.frame_index = 0
        self.speaking_cat_elements = {}
        self.update_camp_bg()
        self.hide_menu_buttons()

        self.created_choice_buttons = False
        self.meow = False


        self.clan_name_bg = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((115, 438), (190, 35))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(),
                (500, 870)),
            manager=MANAGER
            )

        short_name = shorten_text_to_fit(str(self.speaking_cat.name), 320, 40)
        self.speaking_cat_elements["cat_name"] = pygame_gui.elements.UITextBox(
            short_name,
            ui_scale(pygame.Rect((115, 437), (190, 40))),
            object_id="#text_box_34_horizcenter_light",
            manager=MANAGER
            )

        self.text_type = ""

        text_options = self.dialogue_class.load_texts()

        self.chosen_text_key, self.chosen_text_value = (
            self.dialogue_class.choose_dialogue(text_options)
            )

        self.chosen_text_object = {self.chosen_text_key: self.chosen_text_value}
        self.texts = self.chosen_text_value["intro"]
        self.current_scene = "intro"
        self.current_line = self.texts[0]

        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]

        self.cat_dict = self.dialogue_class.get_cat_dict()

        talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()
        self.talk_box = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((90, 470), (624, 151))),
                talk_box_img
            )

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((250, 475), (450, 150)))
            )
        self.dialogue_box = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, 10), (450, -100))),
            object_id="#text_box_30_horizleft",
            container=self.scroll_container,
            manager=MANAGER
            )

        self.textbox_graphic = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((90, 471), (163, 150))),
                image_cache.load_image("resources/images/textbox_graphic.png").convert_alpha()
            )

        self.speaking_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((35, 450), (200, 200))),
            pygame.transform.scale(
            generate_sprite(self.speaking_cat),
            (200, 200)),
            manager=MANAGER
            )

        self.paw = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((685, 590), (15, 15))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
        self.paw.visible = False

    def adjust_text(self, text):
        """ replaces names and pronouns """
        process_text_dict = {}

        # Cat Dict looks like:
        # {
        #     "abbrev:0": CAT OBJECT#1
        # }

        # Process text dict looks like
        # {
        #     "abbrev:0": (str(cat.name), cat.pronouns)
        # }

        for abbrev in self.cat_dict:
            abbrev_cat = self.cat_dict[abbrev]
            process_text_dict[abbrev] = (str(abbrev_cat.name), choice(abbrev_cat.pronouns))

        process_text_dict["y_c"] = (str(game.clan.your_cat.name), choice(game.clan.your_cat.pronouns))
        process_text_dict["t_c"] = (str(self.the_cat.name), choice(self.the_cat.pronouns))

        processed_text = process_text(text, process_text_dict)

        # event text adjust for clan name
        final_text = event_text_adjust(
            Cat,
            text=processed_text,
            clan=game.clan,
            other_clan=self.other_clan
        )

        return final_text

    def exit_screen(self):
        self.dialogue_box.kill()
        del self.dialogue_box
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button
        self.speaking_cat_elements["cat_image"].kill()
        self.speaking_cat_elements["cat_name"].kill()
        del self.speaking_cat_elements
        self.clan_name_bg.kill()
        del self.clan_name_bg
        self.talk_box.kill()
        del self.talk_box
        self.textbox_graphic.kill()
        del self.textbox_graphic
        self.paw.kill()
        del self.paw
        for button in self.choice_buttons:
            self.choice_buttons[button].kill()
        self.choice_buttons = {}
        for option in self.choice_display:
            self.choice_display[option].kill()
        self.choice_display = {}

    def update_camp_bg(self):
        light_dark = "dark" if game_setting_get("dark mode") else "light"

        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]

        camp_bg_base_dir, camp_nr = get_current_camp()

        if camp_nr is None:
            assign_new_bg("camp1")

        available_biome = ["Forest", "Mountainous", "Plains", "Beach"]
        biome = game.clan.biome
        if biome not in available_biome:
            biome = available_biome[0]
            game.clan.biome = biome
        biome = biome.lower()

        all_backgrounds = []
        for leaf in leaves:
            platform_dir = (
                f"{camp_bg_base_dir}/{biome}/{leaf}_{camp_nr}_{light_dark}.png"
            )
            all_backgrounds.append(platform_dir)
        
        #LG
        starclan_camp = "resources/images/dead_camps/scbackground_sunsetclouds.png"
        df_camp = "resources/images/dead_camps/dfbackground_eclipse.png"
        ur_camp = "resources/images/urbg.png"

        if (
            self.the_cat.status.group == CatGroup.STARCLAN
            ):
            all_backgrounds = [
                starclan_camp,
                starclan_camp,
                starclan_camp,
                starclan_camp
            ]
        elif (
            self.the_cat.status.group == CatGroup.UNKNOWN_RESIDENCE
        ):
            all_backgrounds = [
                ur_camp,
                ur_camp,
                ur_camp,
                ur_camp
            ]
        elif (
            self.the_cat.status.group == CatGroup.DARK_FOREST
        ):
            all_backgrounds = [
                df_camp,
                df_camp,
                df_camp,
                df_camp
            ]

        self.add_bgs(
            {
                "Newleaf": pygame.transform.scale(
                    pygame.image.load(all_backgrounds[0]).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Greenleaf": pygame.transform.scale(
                    pygame.image.load(all_backgrounds[1]).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Leaf-bare": pygame.transform.scale(
                    pygame.image.load(all_backgrounds[2]).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Leaf-fall": pygame.transform.scale(
                    pygame.image.load(all_backgrounds[3]).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
            },
            {
                "Newleaf": None,
                "Greenleaf": None,
                "Leaf-bare": None,
                "Leaf-fall": None,
            },
        )

        self.set_bg(get_current_season())

    def create_choice_buttons(self):
        """
        Creates choice buttons when necessary.
        If not, it ends the dialogue.
        """
        y_pos = 0
        if f"{self.current_scene}_choices" not in self.chosen_text_value:
            self.paw.visible = True
            self.created_choice_buttons = True
            self.dialogue_class.handle_scene_effects(self.current_scene, self.chosen_text_value)
            return

        for c in self.chosen_text_value[f"{self.current_scene}_choices"]:
            
            text = self.chosen_text_value[f"{self.current_scene}_choices"][c]['text']
            scene = self.chosen_text_value[f"{self.current_scene}_choices"][c]['next_scene']

            # The clickable button
            self.choice_buttons[scene] = UIImageButton(
                ui_scale(pygame.Rect((390, 427 + y_pos), (34, 34))),
                text = "",
                object_id="#dialogue_choice_button",
                manager=MANAGER
                )

            # the background image for the text
            self.choice_display["bg" + scene] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((430, 427 + y_pos), (270, 35))),
                pygame.transform.scale(image_cache.load_image("resources/images/option_bg.png").convert_alpha(),
                (270, 35)),
                manager=MANAGER
                )

            # the text
            # use adjust_text to get r_c names and pronouns
            choice_display_text = self.adjust_text(text)
            self.choice_display["text" + scene] = pygame_gui.elements.UITextBox(
                choice_display_text,
                ui_scale(pygame.Rect((435, 428 + y_pos), (270, 35))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER
                )

            y_pos -= 40

        self.created_choice_buttons = True

    def refresh_current_scene(self):
        """
        Refreshes the current scene after a choice is made.
        """
        for btn in self.choice_buttons:
            self.choice_buttons[btn].kill()
        self.choice_buttons = {}
        for item in self.choice_display:
            self.choice_display[item].kill()
        self.choice_display = {}

        self.texts = self.chosen_text_value[self.current_scene]

        self.speaking_cat = self.the_cat
        self.text_index = 0
        self.frame_index = 0

        self.current_line = self.texts[self.text_index]

        self.created_choice_buttons = False

    def get_speaking_cat(self, text_string):
        """
        gets the current cat speaking for multi-character dialogue
        """

        cat = self.the_cat
        if "|" in text_string:
            fragments = text_string.split("|")
            if fragments[1] in self.cat_dict:
                cat = self.cat_dict[fragments[1]]
    
        return text_string, cat

    def handle_event(self, event):
        new_scene = False
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(GameScreen.PROFILE)
            for btn in self.choice_buttons:
                if event.ui_element == self.choice_buttons[btn]:
                    self.current_scene = btn
                    new_scene = True

        elif event.type == pygame.KEYDOWN and game_setting_get("keybinds"):
            if event.key == pygame.K_ESCAPE:
                self.change_screen(GameScreen.PROFILE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.text_frames:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.current_line = self.texts[self.text_index]
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1

        if new_scene:
            self.refresh_current_scene()

    def on_use(self):
        super().on_use()
        now = pygame.time.get_ticks()

        if self.texts:
            self.texts[self.text_index], speaking_cat = self.get_speaking_cat(self.current_line)

            # text isnt adjusted for names and pronouns until the very end
            # that being. now
            self.texts[self.text_index] = self.adjust_text(self.texts[self.text_index])

            # speaking cat only gets replaced if there Is one
            if speaking_cat:
                self.speaking_cat = speaking_cat

            self.speaking_cat_elements["cat_name"].kill()
            short_name = shorten_text_to_fit(str(self.speaking_cat.name), 320, 40)
            self.speaking_cat_elements["cat_name"] = pygame_gui.elements.UITextBox(
                short_name,
                ui_scale(pygame.Rect((115, 437), (190, 40))),
                object_id="#text_box_34_horizcenter_light",
                manager=MANAGER
                )

            # Redo cat_name and cat_image to account for different cats speaking.
            self.speaking_cat_elements["cat_image"].kill()
            self.speaking_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((35, 450), (200, 200))),
                pygame.transform.scale(
                generate_sprite(self.speaking_cat),
                (200, 200)),
                manager=MANAGER
                )

            # get rid of the |abbrev| if its there
            if "|" in self.texts[self.text_index]:
                self.texts[self.text_index] = self.texts[self.text_index].split("|")[-1]

            # action lines
            if self.texts[self.text_index][0] == "[" and self.texts[self.text_index][-1] == "]":
                self.speaking_cat_elements["cat_name"].hide()
                self.speaking_cat_elements["cat_image"].hide()
            else:
                self.speaking_cat_elements["cat_name"].show()
                self.speaking_cat_elements["cat_image"].show()

        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        if self.text_index < len(self.text_frames):
            if now >= self.next_frame_time and self.frame_index < len(self.text_frames[self.text_index]) - 1:
                self.frame_index += 1
                self.next_frame_time = now + self.typing_delay
                # sound_manager.play("button_press")
        # the end of the line
        if self.text_index == len(self.text_frames) - 1:
            if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                if not self.created_choice_buttons:
                    # TODO: fix the naming of this stuff so its clearer
                    self.create_choice_buttons()
                if not self.meow:
                    if "[" not in self.texts[self.text_index]:
                        sound_manager.play("meow")
                    # this plays One meow sound effect at the end of dialogue
                    self.meow = True

        # Always render the current frame
        if self.text_frames:
            self.dialogue_box.html_text = self.text_frames[self.text_index][self.frame_index]

        self.dialogue_box.rebuild()
        self.clock.tick(60)
