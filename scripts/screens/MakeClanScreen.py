from random import choice, randrange
import pygame_gui
import random
from .Screens import Screens
from re import sub

import pygame
import pygame_gui

from scripts.utility import get_text_box_theme, scale, generate_sprite
from scripts.housekeeping.version import get_version_info
from scripts.clan import Clan
from scripts.cat.cats import create_example_cats, Cat, Personality
from scripts.cat.skills import Skill, SkillPath
from scripts.cat.pelts import Pelt
from scripts.cat.cats import create_example_cats, create_cat, Cat
from scripts.cat.names import names
from scripts.clan import Clan
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.patrol.patrol import Patrol
from scripts.cat.skills import SkillPath
from scripts.game_structure.game_essentials import (
    game,
    screen,
    screen_x,
    screen_y,
    MANAGER,
)
from scripts.game_structure.ui_elements import UIImageButton, UISpriteButton
from scripts.patrol.patrol import Patrol
from scripts.utility import get_text_box_theme, scale
from .Screens import Screens
from ..cat.sprites import sprites
from ..game_structure.windows import SymbolFilterWindow


class MakeClanScreen(Screens):
    # UI images
    clan_frame_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/clan_name_frame.png').convert_alpha(), (432, 100))
    name_clan_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/name_clan_light.png').convert_alpha(), (1600, 1400))
    leader_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/choose cat.png').convert_alpha(), (1600, 1400))
    leader_img_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/choose cat dark.png').convert_alpha(), (1600, 1400))
    deputy_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/deputy_light.png').convert_alpha(), (1600, 1400))
    medic_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/med_light.png').convert_alpha(), (1600, 1400))
    clan_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/clan_light.png').convert_alpha(), (1600, 1400))
    bg_preview_border = pygame.transform.scale(
        pygame.image.load("resources/images/bg_preview_border.png").convert_alpha(), (466, 416))
    
    your_name_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/Your name screen.png').convert_alpha(), (1600, 1400))
    your_name_img_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/Your name screen darkmode.png').convert_alpha(), (1600, 1400))
    your_name_txt1 = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/your name text1.png').convert_alpha(), (796, 52))
    your_name_txt2 = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/your name text2.png').convert_alpha(), (536, 52))
    
    #images for the customizing screen
    sprite_preview_bg = pygame.transform.scale(pygame.image.load(
        'resources/images/sprite_preview.png').convert_alpha(), (1600, 1400))
    
    sprite_preview_bg_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/sprite_preview_dark.png').convert_alpha(), (1600, 1400))
    
    poses_bg = pygame.transform.scale(pygame.image.load(
        'resources/images/poses_bg.png').convert_alpha(), (1600, 1400))
    
    poses_bg_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/poses_bg_dark.png').convert_alpha(), (1600, 1400))
    
    choice_bg = pygame.transform.scale(pygame.image.load(
        'resources/images/custom_choice_bg.png').convert_alpha(), (1600, 1400))
    
    choice_bg_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/custom_choice_bg_dark.png').convert_alpha(), (1600, 1400))



    # This section holds all the information needed
    game_mode = 'expanded'  # To save the users selection before conformation.
    clan_name = ""  # To store the clan name before conformation
    leader = None  # To store the clan leader before conformation
    deputy = None
    med_cat = None
    members = []
    elected_camp = None
    your_cat = None

    # holds the symbol we have selected
    symbol_selected = None
    tag_list_len = 0
    # Holds biome we have selected
    biome_selected = None
    selected_camp_tab = 1
    selected_season = None
    # Camp number selected
    camp_num = "1"
    # Holds the cat we have currently selected.
    selected_cat = None
    # Hold which sub-screen we are on
    sub_screen = 'name clan'
    # Holds which ranks we are currently selecting.
    choosing_rank = None
    # To hold the images for the sections. Makes it easier to kill them
    elements = {}
    tabs = {}
    symbol_buttons = {}

    # used in symbol screen only - parent container is in element dict
    text = {}

    def __init__(self, name=None):
        super().__init__(name)
        # current page for symbol choosing
        self.current_page = 1

        self.rolls_left = -1
        self.menu_warning = None

    def screen_switches(self):
        # Reset variables
        self.game_mode = 'expanded'
        self.clan_name = ""
        self.selected_camp_tab = 1
        self.biome_selected = None
        self.selected_season = "Newleaf"
        self.symbol_selected = None
        self.leader = None  # To store the Clan leader before conformation
        self.deputy = None
        self.med_cat = None
        self.members = []
        self.clan_size = "medium"
        self.clan_age = "established"
        
        # self.selected_cat = None
        self.elements = {}
        self.pname="SingleColour"
        self.length="short"
        self.colour="WHITE"
        self.white_patches=None
        self.eye_color="BLUE"
        self.eye_colour2=None
        self.tortiebase=None
        self.tortiecolour=None
        self.pattern=None
        self.tortiepattern=None
        self.vitiligo=None
        self.points=None
        self.paralyzed=False
        self.opacity=100
        self.scars=[]
        self.tint="None"
        self.skin="BLACK"
        self.white_patches_tint="None"
        self.kitten_sprite=0
        self.reverse=False
        self.skill = "Random"
        self.accessories=[]
        self.inventory = {}
        self.sex = "male"
        self.personality = "troublesome"
        self.accessory = None
        self.permanent_condition = None
        self.preview_age = "adult"
        self.page = 0
        self.adolescent_pose = 0
        self.adult_pose = 0
        self.elder_pose = 0
        game.choose_cats = {}
        self.skills = []
        for skillpath in SkillPath:
            for skill in skillpath.value:
                self.skills.append(skill)
        # Buttons that appear on every screen.
        self.menu_warning = pygame_gui.elements.UITextBox(
            '',
            scale(pygame.Rect((50, 50), (1200, -1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            manager=MANAGER,
        )
        self.main_menu = UIImageButton(
            scale(pygame.Rect((50, 100), (306, 60))),
            "",
            object_id="#main_menu_button",
            manager=MANAGER,
        )
        create_example_cats()
        self.open_name_clan()

    def handle_event(self, event):
        if self.sub_screen == 'customize cat':
            self.handle_customize_cat_event(event)
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu:
                self.change_screen('start screen')
            if self.sub_screen == 'name clan':
                self.handle_name_clan_event(event)
            elif self.sub_screen == 'choose name':
                self.handle_choose_name_event(event)
            elif self.sub_screen == 'choose leader':
                self.handle_choose_leader_event(event)
            elif self.sub_screen == 'choose camp':
                self.handle_choose_background_event(event)
            elif self.sub_screen == "choose symbol":
                self.handle_choose_symbol_event(event)
            elif self.sub_screen == "saved screen":
                self.handle_saved_clan_event(event)
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if self.sub_screen == 'name clan':
                self.handle_name_clan_key(event)
            elif self.sub_screen == "choose camp":
                self.handle_choose_background_key(event)
            elif self.sub_screen == "saved screen" and (
                event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT
            ):
                self.change_screen("start screen")

    def handle_name_clan_event(self, event):
        if event.ui_element == self.elements["random"]:
            self.elements["name_entry"].set_text(self.random_clan_name())
        elif event.ui_element == self.elements["reset_name"]:
            self.elements["name_entry"].set_text("")
        elif event.ui_element == self.elements["next_step"]:
            new_name = sub(
                r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
            ).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()
        elif event.ui_element == self.elements["previous_step"]:
            self.clan_name = ""
            self.change_screen('start screen')
        elif event.ui_element == self.elements['small']:
            self.elements['small'].disable()
            self.elements['medium'].enable()
            self.elements['large'].enable()
            self.clan_size = "small"
        elif event.ui_element == self.elements['medium']:
            self.elements['small'].enable()
            self.elements['medium'].disable()
            self.elements['large'].enable()
            self.clan_size = "medium"
        elif event.ui_element == self.elements['large']:
            self.elements['small'].enable()
            self.elements['large'].disable()
            self.elements['medium'].enable()
            self.clan_size = "large"
        elif event.ui_element == self.elements["established"]:
            self.elements['established'].disable()
            self.elements['new'].enable()
            self.clan_age = "established"
        elif event.ui_element == self.elements["new"]:
            self.elements['established'].enable()
            self.elements['new'].disable()
            self.clan_age = "new"
    
    def random_clan_name(self):
        clan_names = names.names_dict["normal_prefixes"] + names.names_dict["clan_prefixes"]
        while True:
            chosen_name = choice(clan_names)
            if chosen_name.casefold() not in [clan.casefold() for clan in game.switches['clan_list']]:
                return chosen_name
            print("Generated clan name was already in use! Rerolling...")
    
    def handle_name_clan_key(self, event):
        if event.key == pygame.K_ESCAPE:
            self.change_screen("start screen")
        elif event.key == pygame.K_LEFT:
            if not self.elements["name_entry"].is_focused:
                self.clan_name = ""
        elif event.key == pygame.K_RIGHT:
            if not self.elements["name_entry"].is_focused:
                new_name = sub(
                    r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
                ).strip()
                if not new_name:
                    self.elements["error"].set_text("Your Clan's name cannot be empty")
                    self.elements["error"].show()
                    return
                if new_name.casefold() in [
                    clan.casefold() for clan in game.switches["clan_list"]
                ]:
                    self.elements["error"].set_text(
                        "A Clan with that name already exists."
                    )
                    self.elements["error"].show()
                    return
                self.clan_name = new_name
                self.open_choose_leader()
        elif event.key == pygame.K_RETURN:
            new_name = sub(
                r"[^A-Za-z0-9 ]+", "", self.elements["name_entry"].get_text()
            ).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()

    def handle_choose_leader_event(self, event):
        """ runs when you select a cat or reroll"""
        if event.ui_element in [
            self.elements["dice"]
        ]:
            self.elements["select_cat"].hide()
            create_example_cats()  # create new cats
            self.selected_cat = None  # Your selected cat now no longer exists. Sad. They go away.
            self.refresh_cat_images_and_info()  # Refresh all the images.
            self.rolls_left -= 1
            
            self.elements["reroll_count"].set_text(str(self.rolls_left))
            if self.rolls_left == 0:
                event.ui_element.disable()

        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 24)]:
            self.selected_cat = event.ui_element.return_cat_object()
            self.refresh_cat_images_and_info(self.selected_cat)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['select_cat']:
            self.your_cat = self.selected_cat
            self.selected_cat = None
            self.open_name_cat()
        elif event.ui_element == self.elements['previous_step']:
            self.clan_name = ""
            self.open_name_clan()
        elif event.ui_element == self.elements['customize']:
            print(self.selected_cat.name)
            self.open_customize_cat()
            print(self.selected_cat.name)
            
    def handle_choose_name_event(self, event):
        if event.ui_element == self.elements['next_step']:
            new_name = sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()).strip()
            if not new_name:
                self.elements["error"].set_text("Your cat's name cannot be empty")
                self.elements["error"].show()
                return
            self.your_cat.name.prefix = new_name
            self.open_choose_background()
        elif event.ui_element == self.elements["random"]:
            self.elements["name_entry"].set_text(choice(names.names_dict["normal_prefixes"]))
        elif event.ui_element == self.elements['previous_step']:
            self.selected_cat = None
            self.open_choose_leader()
    
    def handle_create_other_cats(self):
        """ puts all of those cats in the clan! or. the hunger games. >:3 """
        for cat in game.choose_cats.values():
            self.members.append(cat)
        self.members.append(self.your_cat)
        
    def handle_choose_background_event(self, event):
        if event.ui_element == self.elements['previous_step']:
            self.open_name_cat()
        elif event.ui_element == self.elements['forest_biome']:
            self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["mountain_biome"]:
            self.biome_selected = "Mountainous"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["plains_biome"]:
            self.biome_selected = "Plains"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["beach_biome"]:
            self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["tab1"]:
            self.selected_camp_tab = 1
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab2"]:
            self.selected_camp_tab = 2
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab3"]:
            self.selected_camp_tab = 3
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab4"]:
            self.selected_camp_tab = 4
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab5"]:
            self.selected_camp_tab = 5
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab6"]:
            self.selected_camp_tab = 6
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["newleaf_tab"]:
            self.selected_season = "Newleaf"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["greenleaf_tab"]:
            self.selected_season = "Greenleaf"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["leaffall_tab"]:
            self.selected_season = "Leaf-fall"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["leafbare_tab"]:
            self.selected_season = "Leaf-bare"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["random_background"]:
            # Select a random biome and background
            old_biome = self.biome_selected
            possible_biomes = ['Forest', 'Mountainous', 'Plains', 'Beach']
            # ensuring that the new random camp will not be the same one
            if old_biome is not None:
                possible_biomes.remove(old_biome)
            self.biome_selected = choice(possible_biomes)
            if self.biome_selected == 'Forest':
                self.selected_camp_tab = randrange(1, 7)
            elif self.biome_selected == "Mountainous":
                self.selected_camp_tab = randrange(1, 6)
            elif self.biome_selected == "Plains":
                self.selected_camp_tab = randrange(1, 6)
            else:
                self.selected_camp_tab = randrange(1, 5)
            self.refresh_selected_camp()
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["next_step"]:
            self.open_choose_symbol()

    def handle_choose_background_key(self, event):
        if event.key == pygame.K_RIGHT:
            if self.biome_selected is None:
                self.biome_selected = "Forest"
            elif self.biome_selected == "Forest":
                self.biome_selected = "Mountainous"
            elif self.biome_selected == "Mountainous":
                self.biome_selected = "Plains"
            elif self.biome_selected == "Plains":
                self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_LEFT:
            if self.biome_selected is None:
                self.biome_selected = "Beach"
            elif self.biome_selected == "Beach":
                self.biome_selected = "Plains"
            elif self.biome_selected == "Plains":
                self.biome_selected = "Mountainous"
            elif self.biome_selected == "Mountainous":
                self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_UP and self.biome_selected is not None:
            if self.selected_camp_tab > 1:
                self.selected_camp_tab -= 1
                self.refresh_selected_camp()
        elif event.key == pygame.K_DOWN and self.biome_selected is not None:
            if self.selected_camp_tab < 6:
                self.selected_camp_tab += 1
                self.refresh_selected_camp()
        elif event.key == pygame.K_RETURN:
            self.save_clan()
            self.open_clan_saved_screen()

    def handle_choose_symbol_event(self, event):
        if event.ui_element == self.elements["previous_step"]:
            self.open_choose_background()
        elif event.ui_element == self.elements["page_right"]:
            self.current_page += 1
            self.refresh_symbol_list()
        elif event.ui_element == self.elements["page_left"]:
            self.current_page -= 1
            self.refresh_symbol_list()
        elif event.ui_element == self.elements["done_button"]:
            self.save_clan()
            self.open_clan_saved_screen()
        elif event.ui_element == self.elements["random_symbol_button"]:
            if self.symbol_selected:
                if self.symbol_selected in self.symbol_buttons:
                    self.symbol_buttons[self.symbol_selected].enable()
            self.symbol_selected = choice(sprites.clan_symbols)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["filters_tab"]:
            SymbolFilterWindow()
        else:
            for symbol_id, element in self.symbol_buttons.items():
                if event.ui_element == element:
                    if self.symbol_selected:
                        if self.symbol_selected in self.symbol_buttons:
                            self.symbol_buttons[self.symbol_selected].enable()
                    self.symbol_selected = symbol_id
                    self.refresh_text_and_buttons()

    def handle_saved_clan_event(self, event):
        if event.ui_element == self.elements["continue"]:
            self.change_screen("camp screen")

    def exit_screen(self):
        self.main_menu.kill()
        self.menu_warning.kill()
        self.clear_all_page()
        self.rolls_left = -1
        return super().exit_screen()

    def on_use(self):

        # Don't allow someone to enter no name for their clan
        if self.sub_screen == "name clan":
            if self.elements["name_entry"].get_text() == "":
                self.elements["next_step"].disable()
            elif self.elements["name_entry"].get_text().startswith(" "):
                self.elements["error"].set_text("Clan names cannot start with a space.")
                self.elements["error"].show()
                self.elements["next_step"].disable()
            elif self.elements["name_entry"].get_text().casefold() in [
                clan.casefold() for clan in game.switches["clan_list"]
            ]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                self.elements["next_step"].disable()
            else:
                self.elements["error"].hide()
                self.elements['next_step'].enable()
            # Set the background for the name clan page - done here to avoid GUI layering issues
            screen.blit(pygame.transform.scale(MakeClanScreen.name_clan_img, (screen_x, screen_y)), (0,0))
            
        elif self.sub_screen == 'choose name':
            if self.elements["name_entry"].get_text() == "":
                self.elements['next_step'].disable()
            elif self.elements["name_entry"].get_text().startswith(" "):
                self.elements["error"].set_text("Your name cannot start with a space.")
                self.elements["error"].show()
                self.elements['next_step'].disable()
            else:
                self.elements["error"].hide()
                self.elements['next_step'].enable()
        elif self.sub_screen == "choose symbol":
            if len(game.switches["disallowed_symbol_tags"]) != self.tag_list_len:
                self.tag_list_len = len(game.switches["disallowed_symbol_tags"])
                self.refresh_symbol_list()

    def clear_all_page(self):
        """Clears the entire page, including layout images"""
        for image in self.elements:
            self.elements[image].kill()
        for tab in self.tabs:
            self.tabs[tab].kill()
        for button in self.symbol_buttons:
            self.symbol_buttons[button].kill()
        self.elements = {}

    def refresh_text_and_buttons(self):
        """Refreshes the button states and text boxes"""
        if self.sub_screen == "game mode":
            # Set the mode explanation text
            if self.game_mode == "classic":
                display_text = self.classic_mode_text
                display_name = "Classic Mode"
            elif self.game_mode == "expanded":
                display_text = self.expanded_mode_text
                display_name = "Expanded Mode"
            elif self.game_mode == "cruel season":
                display_text = self.cruel_mode_text
                display_name = "Cruel Season"
            else:
                display_text = ""
                display_name = "ERROR"
            self.elements["mode_details"].set_text(display_text)
            self.elements["mode_name"].set_text(display_name)

            # Update the enabled buttons for the game selection to disable the
            # buttons for the mode currently selected. Mostly for aesthetics, and it
            # make it very clear which mode is selected.
            if self.game_mode == "classic":
                self.elements["classic_mode_button"].disable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].enable()
            elif self.game_mode == "expanded":
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].disable()
                self.elements["cruel_mode_button"].enable()
            elif self.game_mode == "cruel season":
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].disable()
            else:
                self.elements["classic_mode_button"].enable()
                self.elements["expanded_mode_button"].enable()
                self.elements["cruel_mode_button"].enable()

            # Don't let the player go forwards with cruel mode, it's not done yet.
            if self.game_mode == "cruel season":
                self.elements["next_step"].disable()
            else:
                self.elements["next_step"].enable()
        # Show the error message if you try to choose a child for leader, deputy, or med cat.
        elif self.sub_screen in ['choose leader', 'choose deputy', 'choose med cat']:
            self.elements['select_cat'].show()
        # Refresh the choose-members background to match number of cat's chosen.
        elif self.sub_screen == "choose members":

            if len(self.members) == 0:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_none_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 1:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_one_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 2:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_two_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].disable()
            elif len(self.members) == 3:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_three_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].disable()
            elif 4 <= len(self.members) <= 6:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_four_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["next_step"].enable()
                # In order for the "previous step" to work properly, we must enable this button, just in case it
                # was disabled in the next step.
                self.elements["select_cat"].enable()
            elif len(self.members) == 7:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/pick_clan_screen/clan_full_light.png"
                        ).convert_alpha(),
                        (1600, 1400),
                    )
                )
                self.elements["select_cat"].disable()
                self.elements["next_step"].enable()

            # Hide the recruit cat button if no cat is selected.
            if self.selected_cat is not None:
                self.elements["select_cat"].show()
            else:
                self.elements["select_cat"].hide()

        elif self.sub_screen == "choose camp":
            # Enable/disable biome buttons
            if self.biome_selected == "Forest":
                self.elements["forest_biome"].disable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Mountainous":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].disable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Plains":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].disable()
                self.elements["beach_biome"].enable()
            elif self.biome_selected == "Beach":
                self.elements["forest_biome"].enable()
                self.elements["mountain_biome"].enable()
                self.elements["plains_biome"].enable()
                self.elements["beach_biome"].disable()

            if self.selected_season == "Newleaf":
                self.tabs["newleaf_tab"].disable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Greenleaf":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].disable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Leaf-fall":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].disable()
                self.tabs["leafbare_tab"].enable()
            elif self.selected_season == "Leaf-bare":
                self.tabs["newleaf_tab"].enable()
                self.tabs["greenleaf_tab"].enable()
                self.tabs["leaffall_tab"].enable()
                self.tabs["leafbare_tab"].disable()

            if self.biome_selected and self.selected_camp_tab:
                self.elements["next_step"].enable()

            # Deal with tab and shown camp image:
            self.refresh_selected_camp()
        elif self.sub_screen == "choose symbol":
            if self.symbol_selected:
                if self.symbol_selected in self.symbol_buttons:
                    self.symbol_buttons[self.symbol_selected].disable()
                # refresh selected symbol image
                self.elements["selected_symbol"].set_image(
                    pygame.transform.scale(
                        sprites.sprites[self.symbol_selected], (200, 200)
                    ).convert_alpha()
                )
                symbol_name = self.symbol_selected.removeprefix("symbol")
                self.text["selected"].set_text(f"Selected Symbol: {symbol_name}")
                self.elements["selected_symbol"].show()
                self.elements["done_button"].enable()

    def refresh_selected_camp(self):
        """Updates selected camp image and tabs"""
        self.tabs["tab1"].kill()
        self.tabs["tab2"].kill()
        self.tabs["tab3"].kill()
        self.tabs["tab4"].kill()
        self.tabs["tab5"].kill()
        self.tabs["tab6"].kill()

        if self.biome_selected == 'Forest':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((190, 360), (308, 60))), "", object_id="#classic_tab"
                                              , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((216, 430), (308, 60))), "", object_id="#gully_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((190, 500), (308, 60))), "", object_id="#grotto_tab"
                                              , manager=MANAGER)
            self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((170, 570), (308, 60))), "", object_id="#lakeside_tab"
                                              , manager=MANAGER)
            self.tabs["tab5"] = UIImageButton(scale(pygame.Rect((170, 640), (308, 60))), "", object_id="#pine_tab"
                                              , manager=MANAGER)
            self.tabs["tab6"] = UIImageButton(scale(pygame.Rect((170, 710), (308, 60))), "", object_id="#birch_camp_tab"
                                              , manager=MANAGER)
        elif self.biome_selected == 'Mountainous':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((222, 360), (308, 60))), "", object_id="#cliff_tab"
                                              , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((180, 430), (308, 60))), "", object_id="#cave_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((85, 500), (358, 60))), "", object_id="#crystal_tab"
                                              , manager=MANAGER)
            self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((85, 570), (308, 60))), "", object_id="#rocky_slope_tab"
                                              , manager=MANAGER)
            self.tabs["tab5"] = UIImageButton(scale(pygame.Rect((85, 640), (308, 60))), "", object_id="#quarry_tab"
                                              , manager=MANAGER)
        elif self.biome_selected == 'Plains':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((128, 360), (308, 60))), "", object_id="#grasslands_tab"
                                              , manager=MANAGER, )
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((178, 430), (308, 60))), "", object_id="#tunnel_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((128, 500), (308, 60))), "", object_id="#wasteland_tab"
                                              , manager=MANAGER)
            self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((128, 570), (308, 60))), "", object_id="#taiga_camp_tab"
                                              , manager=MANAGER)
            self.tabs["tab5"] = UIImageButton(scale(pygame.Rect((118, 640), (308, 60))), "", object_id="#desert_tab"
                                              , manager=MANAGER)
        elif self.biome_selected == 'Beach':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((152, 360), (308, 60))), "", object_id="#tidepool_tab"
                                              , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((130, 430), (308, 60))), "", object_id="#tidal_cave_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((140, 500), (308, 60))), "", object_id="#shipwreck_tab"
                                              , manager=MANAGER)
            self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((95, 570), (308, 60))), "", object_id="#tropical_island_tab"
                                              , manager=MANAGER)

        if self.selected_camp_tab == 1:
            self.tabs["tab1"].disable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 2:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].disable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 3:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].disable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 4:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].disable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 5:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].disable()
            self.tabs["tab6"].enable()
        elif self.selected_camp_tab == 6:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].disable()
        else:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
            self.tabs["tab4"].enable()
            self.tabs["tab5"].enable()
            self.tabs["tab6"].enable()

        # I have to do this for proper layering.
        if "camp_art" in self.elements:
            self.elements["camp_art"].kill()
        if self.biome_selected:
            self.elements["camp_art"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((350, 340), (900, 800))),
                pygame.transform.scale(
                    pygame.image.load(
                        self.get_camp_art_path(self.selected_camp_tab)
                    ).convert_alpha(),
                    (900, 800),
                ),
                manager=MANAGER,
            )
            self.elements["art_frame"].kill()
            self.elements["art_frame"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect(((334, 324), (932, 832)))),
                pygame.transform.scale(
                    pygame.image.load(
                        "resources/images/bg_preview_border.png"
                    ).convert_alpha(),
                    (932, 832),
                ),
                manager=MANAGER,
            )

    def refresh_selected_cat_info(self, selected=None):
        # SELECTED CAT INFO
        try:
            self.elements['cat_info'].hide()
            self.elements['cat_name'].hide()
        except:
            pass
            # im lazy
            
        if selected is not None:

            if self.sub_screen == 'choose leader':
                self.elements['cat_name'].set_text(str(selected.name))
            else:
                self.elements['cat_name'].set_text(str(selected.name))
            self.elements['cat_info'].show()
            self.elements['cat_name'].show()
            self.elements['cat_info'].set_text(selected.gender + "\n" +
                                                   str(selected.status) + "\n" +
                                                   str(selected.moons) + " moons \n" +
                                                   str(selected.personality.trait) + "\n" +
                                                   str(selected.skills.skill_string()))
            if selected.permanent_condition:

                self.elements['cat_info'].set_text(selected.gender + "\n" +
                                                   str(selected.status) + "\n" +
                                                   str(selected.moons) + " moons \n" +
                                                   str(selected.personality.trait) + "\n" +
                                                   str(selected.skills.skill_string()) + "\n" +
                                                   "permanent condition: " + list(selected.permanent_condition.keys())[0])
            self.elements['cat_info'].show()


    def refresh_cat_images_and_info(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats."""

        column_poss = [100, 200]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        for u in range(24):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((540, 390), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u])
            else:
                # put them in a circle!!
                if u == 0:
                    x_pos, y_pos = [200, 600] # LEFT OF THE CIRCLE
                elif u == 1:
                    x_pos, y_pos = [210, 475]
                elif u == 2:
                    x_pos, y_pos = [250, 360]
                elif u == 3:
                    x_pos, y_pos = [310, 250]
                elif u == 4:
                    x_pos, y_pos = [440, 150]
                elif u == 5:
                    x_pos, y_pos = [580, 110]
                elif u == 6:
                    x_pos, y_pos = [700, 100] # TOP OF THE CIRCLE
                elif u == 7:
                    x_pos, y_pos = [820, 110]
                elif u == 8:
                    x_pos, y_pos = [960, 150]
                elif u == 9:
                    x_pos, y_pos = [1090, 250]
                elif u == 10:
                    x_pos, y_pos = [1150, 360]
                elif u == 11:
                    x_pos, y_pos = [1190, 475]
                elif u == 12:
                    x_pos, y_pos = [1200, 600] # RIGHT OF THE CIRCLE
                elif u == 13:
                    x_pos, y_pos = [1190, 725]
                elif u == 14:
                    x_pos, y_pos = [1150, 840]
                elif u == 15:
                    x_pos, y_pos = [1090, 950]
                elif u == 16:
                    x_pos, y_pos = [960, 1050]
                elif u == 17:
                    x_pos, y_pos = [820, 1090]
                elif u == 18:
                    x_pos, y_pos = [700, 1100] # BOTTOM OF THE CIRCLE
                elif u == 19:
                    x_pos, y_pos = [580, 1090]
                elif u == 20:
                    x_pos, y_pos = [440, 1050]
                elif u == 21:
                    x_pos, y_pos = [310, 950]
                elif u == 22:
                    x_pos, y_pos = [250, 840]
                elif u == 23:
                    x_pos, y_pos = [210, 725]
                else:
                    x_pos, y_pos = [460, 1420]
                    
                self.elements["cat" + str(u)] = UISpriteButton(
                        scale(pygame.Rect((x_pos + 30, y_pos), (130, 130))),
                        game.choose_cats[u].sprite,
                        cat_object=game.choose_cats[u], manager=MANAGER)
                
        if self.selected_cat is not None:
            self.elements['customize'].show()
        else:
            self.elements['customize'].hide()
                
    def refresh_cat_images_and_info2(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats. """

        column_poss = [100, 200]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        # CAT IMAGES
        for u in range(6):
            if game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((620, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u])

        for u in range(6, 12):
            if game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((620, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u])
        
    def open_name_cat(self):
        """Opens the name clan screen"""
        
        self.clear_all_page()
        
        self.elements["leader_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((580, 300), (400, 400))),
                                                                    pygame.transform.scale(
                                                                        self.your_cat.sprite,
                                                                        (200, 200)), manager=MANAGER)
        if game.settings["dark mode"]:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (1600, 1400))),
                                                                    MakeClanScreen.your_name_img_dark, manager=MANAGER)
        else:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (1600, 1400))),
                                                                    MakeClanScreen.your_name_img, manager=MANAGER)

        self.elements['text1'] = pygame_gui.elements.UIImage(scale(pygame.Rect((520, 730), (796, 52))),
                                                                  MakeClanScreen.your_name_txt1, manager=MANAGER)
        self.elements['text2'] = pygame_gui.elements.UIImage(scale(pygame.Rect((520, 790), (536, 52))),
                                                                  MakeClanScreen.your_name_txt2, manager=MANAGER)
        self.elements['background'].disable()

        self.elements["version_background"] = UIImageButton(scale(pygame.Rect((1450, 1344), (1400, 55))), "", object_id="blank_button", manager=MANAGER)
        self.elements["version_background"].disable()

        if game.settings['fullscreen']:
            version_number = pygame_gui.elements.UILabel(
                pygame.Rect((1500, 1350), (-1, -1)), get_version_info().version_number[0:8],
                object_id=get_text_box_theme())
            # Adjust position
            version_number.set_position(
                (1600 - version_number.get_relative_rect()[2] - 8,
                1400 - version_number.get_relative_rect()[3]))
        else:
            version_number = pygame_gui.elements.UILabel(
                pygame.Rect((700, 650), (-1, -1)), get_version_info().version_number[0:8],
                object_id=get_text_box_theme())
            # Adjust position
            version_number.set_position(
                (800 - version_number.get_relative_rect()[2] - 8,
                700 - version_number.get_relative_rect()[3]))

        self.refresh_cat_images_and_info2()
        
        self.sub_screen = 'choose name'
        
        self.elements["random"] = UIImageButton(scale(pygame.Rect((570, 895), (68, 68))), "",
                                                object_id="#random_dice_button"
                                                , manager=MANAGER)

        self.elements["error"] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((506, 1310), (596, -1))),
                                                               manager=MANAGER,
                                                               object_id="#default_dark", visible=False)
        self.main_menu.kill()
        self.main_menu = UIImageButton(scale(pygame.Rect((100, 100), (306, 60))), "", object_id="#main_menu_button"
                                       , manager=MANAGER)

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1290), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1290), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((650, 900), (280, 58)))
                                                                          , manager=MANAGER, initial_text=self.your_cat.name.prefix)
        
        self.elements["name_entry"].set_allowed_characters(
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- "))
        self.elements["name_entry"].set_text_length_limit(11)

        # additional name entry for suffix if ur now a -paw
        if self.your_cat.age != "adolescent":
            self.elements["suffix_entry"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((950, 900), (280, 58)))
                                                                          , manager=MANAGER, initial_text=self.your_cat.name.suffix)
            self.elements["suffix_entry"].set_allowed_characters(
                list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- "))
            self.elements["suffix_entry"].set_text_length_limit(11)
        
        else:
            if game.settings['dark mode']:
                self.elements["clan"] = pygame_gui.elements.UITextBox("-paw",
                                                                scale(pygame.Rect((870, 905), (190, 70))),
                                                                object_id="#text_box_30_horizcenter_light",
                                                                manager=MANAGER)
            
            else:
                self.elements["clan"] = pygame_gui.elements.UITextBox("-paw",
                                                                scale(pygame.Rect((870, 905), (190, 70))),
                                                                object_id="#text_box_30_horizcenter",
                                                                manager=MANAGER)
        


    def open_name_clan(self):
        """Opens the name Clan screen"""
        self.clear_all_page()
        self.sub_screen = "name clan"

        # Create all the elements.
        self.elements["random"] = UIImageButton(
            scale(pygame.Rect((448, 1190), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
        )

        self.elements["error"] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((506, 1340), (596, -1))),
                                                               manager=MANAGER,
                                                               object_id="#default_dark", visible=False)

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1290), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1290), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((530, 1195), (280, 58)))
                                                                          , manager=MANAGER)
        self.elements["name_entry"].set_allowed_characters(
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- ")
        )
        self.elements["name_entry"].set_text_length_limit(11)
        self.elements["clan"] = pygame_gui.elements.UITextBox("-Clan",
                                                              scale(pygame.Rect((750, 1200), (200, 50))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        self.elements["reset_name"] = UIImageButton(scale(pygame.Rect((910, 1190), (268, 60))), "",
                                                    object_id="#reset_name_button", manager=MANAGER)
        
        if game.settings['dark mode']:
            self.elements["clan_size"] = pygame_gui.elements.UITextBox("Clan Size: ",
                                                              scale(pygame.Rect((400, 110), (200, 50))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        else:
            self.elements["clan_size"] = pygame_gui.elements.UITextBox("Clan Size: ",
                                                              scale(pygame.Rect((400, 110), (200, 50))),
                                                              object_id="#text_box_30_horizcenter",
                                                              manager=MANAGER)

        if game.settings['dark mode']:
            self.elements["clan_age"] = pygame_gui.elements.UITextBox("Clan Age: ",
                                                              scale(pygame.Rect((400, 195), (200, 60))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        else:
            self.elements["clan_age"] = pygame_gui.elements.UITextBox("Clan Age: ",
                                                              scale(pygame.Rect((400, 195), (200, 60))),
                                                              object_id="#text_box_30_horizcenter",
                                                              manager=MANAGER)
        
        self.elements["small"] = UIImageButton(scale(pygame.Rect((600,100), (192, 60))), "Small", object_id="#clan_size_small", manager=MANAGER)

        self.elements["medium"] = UIImageButton(scale(pygame.Rect((850,100), (192, 60))), "Medium", object_id="#clan_size_medium", manager=MANAGER)
        
        self.elements["large"] = UIImageButton(scale(pygame.Rect((1100,100), (192, 60))), "Large", object_id="#clan_size_large", manager=MANAGER)

        self.elements["medium"].disable()

        self.elements["established"] = UIImageButton(scale(pygame.Rect((600,200), (192, 60))), "Old", object_id="#clan_age_old", tool_tip_text="The Clan has existed for many moons and cats' backstories will reflect this.",manager=MANAGER)
        self.elements["new"] = UIImageButton(scale(pygame.Rect((850,200), (192, 60))), "New", object_id="#clan_age_new", tool_tip_text="The Clan is newly established and cats' backstories will reflect this.", manager=MANAGER)
        self.elements["established"].disable()

    def clan_name_header(self):
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((584, 20), (432, 100))),
            MakeClanScreen.clan_frame_img,
            manager=MANAGER,
        )
        self.elements["tribute_text"] = pygame_gui.elements.UITextBox(
            "The Tributes",
            scale(pygame.Rect((585, 30), (432, 100))),
            object_id="#text_box_30_horizcenter_light",
            manager=MANAGER,
        )

    def open_choose_leader(self):
        """Set up the screen for the choose leader phase."""
        self.clear_all_page()
        self.sub_screen = "choose leader"

        # if game.settings['dark mode']:
        #     self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((500, 1000), (600, 70))),
        #                                                           MakeClanScreen.leader_img_dark, manager=MANAGER)
        # else:
        #     self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((500, 1000), (600, 70))),
        #                                                           MakeClanScreen.leader_img, manager=MANAGER)

        # self.elements["background"].disable()
        self.clan_name_header()

        self.elements["choose_cat_text"] = pygame_gui.elements.UITextBox(
            "Choose your character",
            scale(pygame.Rect((600, 800), (400, 60))),
            object_id="#text_box_30_horizcenter_light",
            manager=MANAGER,
        )
        self.elements["dice"] = UIImageButton(
            scale(pygame.Rect((765, 870), (68, 68))),
            "",
            object_id="#random_dice_button",
            manager=MANAGER,
        )
        self.elements["reroll_count"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((200, 880), (100, 50))),
            str(self.rolls_left),
            object_id=get_text_box_theme(""),
            manager=MANAGER,
        )

        if self.rolls_left == 0:
            self.elements["dice"].disable()
        elif self.rolls_left == -1:
            self.elements["reroll_count"].hide()

        # info for chosen cats:
        if game.settings['dark mode']:
            self.elements['cat_info'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((880, 450), (300, 300))),
                                                                    visible=False, object_id="#text_box_22_horizleft_spacing_95_dark",
                                                                    manager=MANAGER)
        else:
            self.elements['cat_info'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((880, 450), (300, 300))),
                                                                    visible=False, object_id=get_text_box_theme("#text_box_22_horizleft_spacing_95"),
                                                                    manager=MANAGER)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((500, 350), (600, 110))),
                                                                  visible=False,
                                                                  object_id=get_text_box_theme(
                                                                      "#text_box_30_horizcenter"),
                                                                  manager=MANAGER)

        self.elements['select_cat'] = UIImageButton(scale(pygame.Rect((706, 720), (190, 60))),
                                                    "",
                                                    object_id="#recruit_button",
                                                    visible=False,
                                                    manager=MANAGER)
        

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1290), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1290), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()

        self.elements['customize'] = UIImageButton(scale(pygame.Rect((100,200),(236,60))), "", object_id="#customize_button", manager=MANAGER,  tool_tip_text = "Customize your cat")

        self.elements['customize'].hide()

        # draw cats to choose from
        self.refresh_cat_images_and_info()
    
    def randomize_custom_cat(self):
        pelts = list(Pelt.sprites_names.keys())
        pelts.remove("Tortie")
        pelts.remove("Calico")
        pelts_tortie = pelts.copy()
        pelts_tortie.remove("SingleColour")
        pelts_tortie.remove("TwoColour")
        for i in pelts_tortie.copy():
            pelts_tortie.remove(i)
            i = i.lower()
            pelts_tortie.append(i)
        # pelts_tortie.append("Single")
        permanent_conditions = ['born without a leg', 'weak leg', 'twisted leg', 'born without a tail', 'paralyzed', 'raspy lungs', 'wasting disease', 'blind', 'one bad eye', 'failing eyesight', 'partial hearing loss', 'deaf', 'constant joint pain', 'seizure prone', 'allergies', 'persistent headaches']

        white_patches = ["FULLWHITE"] + Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white
        self.selected_cat.pelt.name= random.choice(pelts) if random.randint(1,3) == 1 else "Tortie"
        self.selected_cat.pelt.length=random.choice(["short", "medium", "long"])
        self.selected_cat.pelt.colour=random.choice(Pelt.pelt_colours)
        self.selected_cat.pelt.white_patches= random.choice(white_patches) if random.randint(1,2) == 1 else None
        self.selected_cat.pelt.eye_color=choice(Pelt.eye_colours)
        self.selected_cat.pelt.eye_colour2=choice(Pelt.eye_colours) if random.randint(1,10) == 1 else None
        self.selected_cat.pelt.tortiebase=choice(Pelt.tortiebases)
        self.selected_cat.pelt.tortiecolour=choice(Pelt.pelt_colours)
        self.selected_cat.pelt.pattern=choice(Pelt.tortiepatterns)
        self.selected_cat.pelt.tortiepattern=choice(pelts_tortie)
        self.selected_cat.pelt.vitiligo=choice(Pelt.vit) if random.randint(1,5) == 1 else None
        self.selected_cat.pelt.points=choice(Pelt.point_markings) if random.randint(1,5) == 1 else None
        self.selected_cat.pelt.scars=[choice(Pelt.scars1 + Pelt.scars2 + Pelt.scars3)] if random.randint(1,10) == 1 else []
        self.selected_cat.pelt.tint=choice(["pink", "gray", "red", "orange", "black", "yellow", "purple", "blue", "warmdilute", "dilute", "cooldilute", "none"]) if random.randint(1,5) == 1 else None
        self.selected_cat.pelt.skin=choice(Pelt.skin_sprites)
        self.selected_cat.pelt.white_patches_tint=choice(["offwhite", "cream", "darkcream", "gray", "pink", "none"]) if random.randint(1,5) == 1 else None
        self.selected_cat.pelt.reverse= False if random.randint(1,2) == 1 else True
        self.skill = random.choice(self.skills)
        self.sex = random.choice(["male", "female"])
        self.personality = choice(['troublesome', 'lonesome', 'impulsive', 'bullying', 'attention-seeker', 'charming', 'daring', 'noisy', 'nervous', 'quiet', 'insecure', 'daydreamer', 'sweet', 'polite', 'know-it-all', 'bossy', 'disciplined', 'patient', 'manipulative', 'secretive', 'rebellious', 'grumpy', 'passionate', 'honest', 'leader-like', 'smug'])
        self.selected_cat.pelt.accessory = choice(Pelt.plant_accessories + Pelt.wild_accessories + Pelt.collars + Pelt.flower_accessories + Pelt.plant2_accessories + Pelt.snake_accessories + Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories + Pelt.aliveInsect_accessories + Pelt.fruit_accessories + Pelt.crafted_accessories + Pelt.tail2_accessories) if random.randint(1,5) == 1 else None
        self.permanent_condition = choice(permanent_conditions) if random.randint(1,30) == 1 else None

        self.selected_cat.age = choice(["adolescent", "adult", "senior"])

        if self.selected_cat.age == "adolescent":
            self.selected_cat.status = "apprentice"
            self.selected_cat.moons = 6
        elif self.selected_cat.age == "adult":
            self.selected_cat.status = "warrior"
            self.selected_cat.moons = 12
        else:
            self.selected_cat.status = "elder"
            self.selected_cat.moons = 120

        self.selected_cat.pelt.cat_sprites["kitten"] = random.randint(0,2)
        self.selected_cat.pelt.cat_sprites["adolescent"] = random.randint(0,2)
        self.selected_cat.pelt.cat_sprites["adult"] = random.randint(0,2)
        self.selected_cat.pelt.cat_sprites["senior"] = random.randint(0,2)

    def open_customize_cat(self):
        self.clear_all_page()
        self.sub_screen = "customize cat"
        pelt2 = Pelt(
            name=self.selected_cat.pelt.name,
            length=self.selected_cat.pelt.length,
            colour=self.selected_cat.pelt.colour,
            white_patches=self.selected_cat.pelt.white_patches,
            eye_color=self.selected_cat.pelt.eye_colour,
            eye_colour2=self.selected_cat.pelt.eye_colour2,
            tortiebase=self.selected_cat.pelt.tortiebase,
            tortiecolour=self.selected_cat.pelt.tortiecolour,
            pattern=self.selected_cat.pelt.pattern,
            tortiepattern=self.selected_cat.pelt.tortiepattern,
            vitiligo=self.selected_cat.pelt.vitiligo,
            points=self.selected_cat.pelt.points,
            accessory=self.selected_cat.pelt.accessory,
            paralyzed=self.selected_cat.pelt.paralyzed,
            scars=self.selected_cat.pelt.scars,
            tint=self.selected_cat.pelt.tint,
            skin=self.selected_cat.pelt.skin,
            white_patches_tint=self.selected_cat.pelt.white_patches_tint,
            kitten_sprite=self.selected_cat.pelt.cat_sprites["kitten"],
            adol_sprite=self.selected_cat.pelt.cat_sprites["adolescent"] if self.selected_cat.pelt.cat_sprites["adolescent"] > 2 else self.selected_cat.pelt.cat_sprites["adolescent"] + 3,
            adult_sprite=self.selected_cat.pelt.cat_sprites["adult"] if self.selected_cat.pelt.cat_sprites["adult"] > 2 else self.selected_cat.pelt.cat_sprites["adult"] + 6,
            senior_sprite=self.selected_cat.pelt.cat_sprites["senior"] if self.selected_cat.pelt.cat_sprites["senior"] > 2 else self.selected_cat.pelt.cat_sprites["senior"] + 12,
            reverse=self.selected_cat.pelt.reverse,
            accessories=[self.selected_cat.pelt.accessory] if self.selected_cat.pelt.accessory else [],
            inventory={self.selected_cat.pelt.accessory: 1} if self.selected_cat.pelt.accessory else {}
        )
        if self.selected_cat.pelt.length == 'long' and self.selected_cat.pelt.cat_sprites["adult"] < 9:
            pelt2.cat_sprites['young adult'] = self.selected_cat.pelt.cat_sprites["adult"] + 9
            pelt2.cat_sprites['adult'] = self.selected_cat.pelt.cat_sprites["adult"] + 9
            pelt2.cat_sprites['senior adult'] = self.selected_cat.pelt.cat_sprites["adult"] + 9
        
        if self.selected_cat.age in ["senior adult", "young adult"]:
            display_age = "adult"
        elif self.selected_cat.age == "senior":
            display_age = "elder"
        else:
            display_age = self.selected_cat.age

        self.preview_age = display_age if self.selected_cat is not None else "adult"

        self.elements["left"] = UIImageButton(scale(pygame.Rect((950, 990), (102, 134))), "", object_id="#arrow_right_fancy",
                                                 starting_height=2)
        
        self.elements["right"] = UIImageButton(scale(pygame.Rect((1300, 990), (102, 134))), "", object_id="#arrow_left_fancy",
                                             starting_height=2)
        if self.page == 0:
            self.elements['left'].disable()
        else:
            self.elements['left'].enable()
        
        if self.page == 2:
            self.elements['right'].disable()
        else:
            self.elements['right'].enable()

       
        
        column1_x = 150  # x-coordinate for column 1
        column2_x = 450  # x-coordinate for column 2
        column3_x = 900  # x-coordinate for column 3
        column4_x = 1200
        x_align = 340
        x_align2 = 200
        x_align3 = 250
        y_pos = [80, 215, 280, 415, 480, 615, 680, 815, 880, 1015, 1080]


        self.elements['random_customize'] = UIImageButton(scale(pygame.Rect((240, y_pos[6]), (68, 68))), "", object_id="#random_dice_button", starting_height=2)
        

        pelts = list(Pelt.sprites_names.keys())
        pelts.remove("Tortie")
        pelts.remove("Calico")
        
        pelts_tortie = pelts.copy()
        # pelts_tortie.remove("SingleColour")
        pelts_tortie.remove("TwoColour")
        for i in pelts_tortie.copy():
            pelts_tortie.remove(i)
            i = i.lower()
            pelts_tortie.append(i)
        
        permanent_conditions = ['born without a leg', 'weak leg', 'twisted leg', 'born without a tail', 'paralyzed', 'raspy lungs', 'wasting disease', 'blind', 'one bad eye', 'failing eyesight', 'partial hearing loss', 'deaf', 'constant joint pain', 'seizure prone', 'allergies', 'persistent headaches']

    # background images
    # values are ((x position, y position), (x width, y height))

        if game.settings['dark mode']:
            self.elements['spritebg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((170, 220), (500, 570))),
                                                                  MakeClanScreen.sprite_preview_bg_dark, manager=MANAGER)
        else:
            self.elements['spritebg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((170, 220), (500, 570))),
                                                                  MakeClanScreen.sprite_preview_bg, manager=MANAGER)
            
        if game.settings['dark mode']:
            self.elements['posesbg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((100, 800), (650, 400))),
                                                                  MakeClanScreen.poses_bg_dark, manager=MANAGER)
        else:
            self.elements['posesbg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((100, 800), (650, 400))),
                                                                  MakeClanScreen.poses_bg, manager=MANAGER)


        if game.settings['dark mode']:
            self.elements['choicesbg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((850, 90), (650, 1150))),
                                                                  MakeClanScreen.choice_bg_dark, manager=MANAGER)
        else:
            self.elements['choicesbg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((850, 90), (650, 1150))),
                                                                  MakeClanScreen.choice_bg, manager=MANAGER)


        self.elements['preview text'] = pygame_gui.elements.UITextBox(
                'Preview Age',
                scale(pygame.Rect((x_align, y_pos[5]),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
        self.elements['preview age'] = pygame_gui.elements.UIDropDownMenu(["kitten", "adolescent", "adult", "elder"], str(self.preview_age), scale(pygame.Rect((x_align, y_pos[6]), (260, 70))), manager=MANAGER)
        c_moons = 1
        if self.preview_age == "adolescent":
            c_moons = 6
        elif self.preview_age == "adult":
            c_moons = 12
        elif self.preview_age == "elder":
            c_moons = 121

        self.elements['preview age'].disable()
        self.selected_cat.pelt = pelt2
        self.selected_cat.sprite = generate_sprite(self.selected_cat)
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((250,280), (350, 350))),
                                   self.selected_cat.sprite,
                                   self.selected_cat.ID,
                                   starting_height=0, manager=MANAGER)
        
        self.elements['pose text'] = pygame_gui.elements.UITextBox(
                'Kitten Pose',
                scale(pygame.Rect((column1_x, y_pos[7] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
        self.elements['pose'] = pygame_gui.elements.UIDropDownMenu(["0", "1", "2"], str(self.selected_cat.pelt.cat_sprites[self.selected_cat.age]), scale(pygame.Rect((column1_x, y_pos[8]), (250, 70))), manager=MANAGER)
            
        self.elements['pose text2'] = pygame_gui.elements.UITextBox(
                'Adolescent Pose',
                scale(pygame.Rect((column2_x, y_pos[7] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
        self.elements['adolescent pose'] = pygame_gui.elements.UIDropDownMenu(["0", "1", "2"], str(self.selected_cat.pelt.cat_sprites["adolescent"]), scale(pygame.Rect((column2_x, y_pos[8]), (250, 70))), manager=MANAGER)

        self.elements['pose text3'] = pygame_gui.elements.UITextBox(
                'Adult Pose',
                scale(pygame.Rect((column1_x, y_pos[9] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
        self.elements['adult pose'] = pygame_gui.elements.UIDropDownMenu(["0", "1", "2"], str(self.selected_cat.pelt.cat_sprites["adult"]), scale(pygame.Rect((column1_x, y_pos[10]), (250, 70))), manager=MANAGER)

        self.elements['pose text4'] = pygame_gui.elements.UITextBox(
                'Elder Pose',
                scale(pygame.Rect((column2_x, y_pos[9] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
        self.elements['elder pose'] = pygame_gui.elements.UIDropDownMenu(["0", "1", "2"], str(self.selected_cat.pelt.cat_sprites["senior"]), scale(pygame.Rect((column2_x, y_pos[10]), (250, 70))), manager=MANAGER)

        # page 0
        # pose
        # pelt type 
        # pelt color
        # pelt tint
        # pelt length
        # White patches
        # White patches tint
        
        if self.page == 0:

        
            #page 1 dropdown labels

            self.elements['pelt text'] = pygame_gui.elements.UITextBox(
                'Pelt type',
                scale(pygame.Rect((column4_x, y_pos[3] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            if self.selected_cat.pelt.name == "Tortie":
                self.elements['pelt dropdown'] = pygame_gui.elements.UIDropDownMenu(pelts, "SingleColour", scale(pygame.Rect((column4_x, y_pos[4]),(250,70))), manager=MANAGER)
            else:
                self.elements['pelt dropdown'] = pygame_gui.elements.UIDropDownMenu(pelts, str(self.selected_cat.pelt.name), scale(pygame.Rect((column4_x, y_pos[4]),(250,70))), manager=MANAGER)
            if self.selected_cat.pelt.name == "Tortie":
                self.elements['pelt dropdown'].disable()
            else:
                self.elements['pelt dropdown'].enable()
            self.elements['pelt color text'] = pygame_gui.elements.UITextBox(
                'Pelt color',
                scale(pygame.Rect((column3_x, y_pos[1] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )        
            self.elements['pelt color'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_colours, str(self.selected_cat.pelt.colour), scale(pygame.Rect((column3_x, y_pos[2]),(250,70))), manager=MANAGER)
            
            self.elements['tint text'] = pygame_gui.elements.UITextBox(
                'Tint',
                scale(pygame.Rect((column4_x, y_pos[1] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            if self.selected_cat.pelt.tint:
                self.elements['tint'] = pygame_gui.elements.UIDropDownMenu(["pink", "gray", "red", "orange", "black", "yellow", "purple", "blue", "warmdilute", "dilute", "cooldilute", "none"], str(self.selected_cat.pelt.tint), scale(pygame.Rect((column4_x, y_pos[2]), (250, 70))), manager=MANAGER)
            else:
                self.elements['tint'] = pygame_gui.elements.UIDropDownMenu(["pink", "gray", "red", "orange", "black", "yellow", "purple", "blue", "warmdilute", "dilute", "cooldilute", "none"], "none", scale(pygame.Rect((column4_x, y_pos[2]), (250, 70))), manager=MANAGER)
            
            self.elements['pelt length text'] = pygame_gui.elements.UITextBox(
                'Pelt length',
                scale(pygame.Rect((column3_x, y_pos[3] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            self.elements['pelt length'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_length, str(self.selected_cat.pelt.length), scale(pygame.Rect((column3_x, y_pos[4]), (250, 70))), manager=MANAGER)

            self.elements['white patch text'] = pygame_gui.elements.UITextBox(
                'White patches',
                scale(pygame.Rect((column3_x, y_pos[5] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            if self.selected_cat.pelt.white_patches:
                self.elements['white patches'] = pygame_gui.elements.UIDropDownMenu(["None", "FULLWHITE"] + Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white, str(self.selected_cat.pelt.white_patches), scale(pygame.Rect((column3_x, y_pos[6]),(250,70))), manager=MANAGER)
            else:
                self.elements['white patches'] = pygame_gui.elements.UIDropDownMenu(["None", "FULLWHITE"] + Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white, "None", scale(pygame.Rect((column3_x, y_pos[6]),(250,70))), manager=MANAGER)
            self.elements['white patch tint text'] = pygame_gui.elements.UITextBox(
                'Patches tint',
                scale(pygame.Rect((column4_x, y_pos[5] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            if self.selected_cat.pelt.white_patches_tint:
                self.elements['white_patches_tint'] = pygame_gui.elements.UIDropDownMenu(["none"] + ["offwhite", "cream", "darkcream", "gray", "pink"], str(self.selected_cat.pelt.white_patches_tint), scale(pygame.Rect((column4_x, y_pos[6]), (250, 70))), manager=MANAGER)
            else:
                self.elements['white_patches_tint'] = pygame_gui.elements.UIDropDownMenu(["none"] + ["offwhite", "cream", "darkcream", "gray", "pink"], "none", scale(pygame.Rect((column4_x, y_pos[6]), (250, 70))), manager=MANAGER)

            self.elements['eye color text'] = pygame_gui.elements.UITextBox(
                'Eye color',
                scale(pygame.Rect((column3_x, y_pos[7] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            self.elements['eye color'] = pygame_gui.elements.UIDropDownMenu(Pelt.eye_colours, str(self.eye_color), scale(pygame.Rect((column3_x, y_pos[8]),(250,70))), manager=MANAGER)

            self.elements['eye color2 text'] = pygame_gui.elements.UITextBox(
                'Heterochromia',
                scale(pygame.Rect((column4_x, y_pos[7] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            if self.selected_cat.pelt.eye_colour2:
                self.elements['eye color2'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.eye_colours, str(self.selected_cat.pelt.eye_colour2), scale(pygame.Rect((column4_x, y_pos[8]),(250,70))), manager=MANAGER)
            else:
                self.elements['eye color2'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.eye_colours, "None", scale(pygame.Rect((column4_x, y_pos[8]),(250,70))), manager=MANAGER)

        #page 1
        #tortie
        #tortie pattern
        #tortie base
        #tortie color
        #tortie pattern2
                
        elif self.page == 1:
            self.elements['tortie text'] = pygame_gui.elements.UITextBox(
                'Tortie:',
                scale(pygame.Rect((column3_x, y_pos[2] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            self.elements['base text'] = pygame_gui.elements.UITextBox(
                'Base',
                scale(pygame.Rect((column3_x, y_pos[3] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            
            self.elements['tortie color text'] = pygame_gui.elements.UITextBox(
                'Color',
                scale(pygame.Rect((column3_x, y_pos[5] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            self.elements['pattern text'] = pygame_gui.elements.UITextBox(
                'Type',
                scale(pygame.Rect((column4_x, y_pos[5] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            self.elements['tint text2'] = pygame_gui.elements.UITextBox(
                'Pattern',
                scale(pygame.Rect((column4_x, y_pos[3] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )

            # page 1 dropdowns

            if self.selected_cat.pelt.name == "Tortie":
                self.elements['tortie'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "Yes", scale(pygame.Rect((column4_x, y_pos[2]), (250, 70))), manager=MANAGER)
            else:
                self.elements['tortie'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "No", scale(pygame.Rect((column4_x, y_pos[2]), (250, 70))), manager=MANAGER)

            if self.selected_cat.pelt.tortiebase:
                self.elements['tortiebase'] = pygame_gui.elements.UIDropDownMenu(Pelt.tortiebases, str(self.selected_cat.pelt.tortiebase), scale(pygame.Rect((column3_x, y_pos[4]), (250, 70))), manager=MANAGER)
            else:
                self.elements['tortiebase'] = pygame_gui.elements.UIDropDownMenu(Pelt.tortiebases, "single", scale(pygame.Rect((column3_x, y_pos[4]), (250, 70))), manager=MANAGER)

            if self.selected_cat.pelt.pattern:
                self.elements['pattern'] = pygame_gui.elements.UIDropDownMenu(Pelt.tortiepatterns, str(self.selected_cat.pelt.pattern), scale(pygame.Rect((column4_x, y_pos[4]), (250, 70))), manager=MANAGER)
            else:
                self.elements['pattern'] = pygame_gui.elements.UIDropDownMenu(Pelt.tortiepatterns, "ONE", scale(pygame.Rect((column4_x, y_pos[4]), (250, 70))), manager=MANAGER)
            if self.tortiecolour:
                self.elements['tortiecolor'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_colours, str(self.selected_cat.pelt.tortiecolour), scale(pygame.Rect((column3_x, y_pos[6]), (250, 70))), manager=MANAGER)
            else:
                self.elements['tortiecolor'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_colours, "GINGER", scale(pygame.Rect((column3_x, y_pos[6]), (250, 70))), manager=MANAGER)
            if self.selected_cat.pelt.tortiepattern:
                self.elements['tortiepattern'] = pygame_gui.elements.UIDropDownMenu(pelts_tortie, str(self.selected_cat.pelt.tortiepattern), scale(pygame.Rect((column4_x, y_pos[6]), (250, 70))), manager=MANAGER)
            else:
                self.elements['tortiepattern'] = pygame_gui.elements.UIDropDownMenu(pelts_tortie, "mackerel", scale(pygame.Rect((column4_x, y_pos[6]), (250, 70))), manager=MANAGER)

            if self.selected_cat.pelt.name != "Tortie":
                self.elements['pattern'].disable()
                self.elements['tortiebase'].disable()
                self.elements['tortiecolor'].disable()
                self.elements['tortiepattern'].disable()
            else:
                self.elements['pattern'].enable()
                self.elements['tortiebase'].enable()
                self.elements['tortiecolor'].enable()
                self.elements['tortiepattern'].enable()

            self.elements['vit text'] = pygame_gui.elements.UITextBox(
                'Vitiligo',
                scale(pygame.Rect((column3_x, y_pos[7] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            self.elements['point text'] = pygame_gui.elements.UITextBox(
                'Points',
                scale(pygame.Rect((column4_x, y_pos[7] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            if self.selected_cat.pelt.vitiligo:
                self.elements['vitiligo'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.vit, str(self.vitiligo), scale(pygame.Rect((column3_x, y_pos[8]), (250, 70))), manager=MANAGER)
            else:
                self.elements['vitiligo'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.vit, "None", scale(pygame.Rect((column3_x, y_pos[8]), (250, 70))), manager=MANAGER)
            
            if self.selected_cat.pelt.points:
                self.elements['points'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.point_markings, str(self.points), scale(pygame.Rect((column4_x, y_pos[8]), (250, 70))), manager=MANAGER)
            else:
                self.elements['points'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.point_markings, "None", scale(pygame.Rect((column4_x, y_pos[8]), (250, 70))), manager=MANAGER)
            

        elif self.page == 2:
            self.elements['skin text'] = pygame_gui.elements.UITextBox(
                'Skin',
                scale(pygame.Rect((column3_x, y_pos[1] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            self.elements['scar text'] = pygame_gui.elements.UITextBox(
                'Scar',
                scale(pygame.Rect((column3_x, y_pos[3] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            ) 
            self.elements['accessory text'] = pygame_gui.elements.UITextBox(
                'Accessory',
                scale(pygame.Rect((column4_x, y_pos[1] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            
            )
            self.elements['permanent condition text'] = pygame_gui.elements.UITextBox(
                'Condition',
                scale(pygame.Rect((column4_x, y_pos[3] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )

            self.elements['sex text'] = pygame_gui.elements.UITextBox(
                'Sex',
                scale(pygame.Rect((column3_x, y_pos[5] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )
            self.elements['personality text'] = pygame_gui.elements.UITextBox(
                'Kit Personality',
                scale(pygame.Rect((column4_x, y_pos[5] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER
            )

            self.elements['reverse text'] = pygame_gui.elements.UITextBox(
                'Reverse',
                scale(pygame.Rect((column3_x, y_pos[7] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER)
            
            self.elements['skills text'] = pygame_gui.elements.UITextBox(
                'Skill',
                scale(pygame.Rect((column4_x, y_pos[7] ),(1200,-1))),
                object_id=get_text_box_theme("#text_box_30_horizleft"), manager=MANAGER)
            
            # page 2 dropdowns
            
            self.elements['skin'] = pygame_gui.elements.UIDropDownMenu(Pelt.skin_sprites, str(self.selected_cat.pelt.skin), scale(pygame.Rect((column3_x, y_pos[2]), (250, 70))), manager=MANAGER)

            if self.selected_cat.pelt.scars:
                self.elements['scars'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.scars1 + Pelt.scars2 + Pelt.scars3, str(self.scars[0]), scale(pygame.Rect((column3_x, y_pos[4]), (250, 70))), manager=MANAGER)
            else:
                self.elements['scars'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.scars1 + Pelt.scars2 + Pelt.scars3, "None", scale(pygame.Rect((column3_x, y_pos[4]), (250, 70))), manager=MANAGER)

            if self.selected_cat.pelt.accessory:
                self.elements['accessory'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.plant_accessories + Pelt.wild_accessories + Pelt.collars + Pelt.flower_accessories + Pelt.plant2_accessories + Pelt.snake_accessories + Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories + Pelt.aliveInsect_accessories + Pelt.fruit_accessories + Pelt.crafted_accessories + Pelt.tail2_accessories, str(self.selected_cat.pelt.accessory), scale(pygame.Rect((1150, y_pos[2]), (300, 70))), manager=MANAGER)
            else:
                self.elements['accessory'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.plant_accessories + Pelt.wild_accessories + Pelt.collars + Pelt.flower_accessories + Pelt.plant2_accessories + Pelt.snake_accessories + Pelt.smallAnimal_accessories + Pelt.deadInsect_accessories + Pelt.aliveInsect_accessories + Pelt.fruit_accessories + Pelt.crafted_accessories + Pelt.tail2_accessories, "None", scale(pygame.Rect((1150, y_pos[2]), (300, 70))), manager=MANAGER)

            if self.permanent_condition:
                self.elements['permanent conditions'] = pygame_gui.elements.UIDropDownMenu(["None"] + permanent_conditions, str(self.permanent_condition), scale(pygame.Rect((1150, y_pos[4]), (300, 70))), manager=MANAGER)
            else:
                self.elements['permanent conditions'] = pygame_gui.elements.UIDropDownMenu(["None"] + permanent_conditions, "None", scale(pygame.Rect((1150, y_pos[4]), (300, 70))), manager=MANAGER)

            self.elements['sex'] = pygame_gui.elements.UIDropDownMenu(['male', 'female'], str(self.sex), scale(pygame.Rect((column3_x, y_pos[6]), (250, 70))), manager=MANAGER)

            self.elements['personality'] = pygame_gui.elements.UIDropDownMenu(['troublesome', 'lonesome', 'impulsive', 'bullying', 'attention-seeker', 'charming', 'daring', 'noisy', 'nervous', 'quiet', 'insecure', 'daydreamer', 'sweet', 'polite', 'know-it-all', 'bossy', 'disciplined', 'patient', 'manipulative', 'secretive', 'rebellious', 'grumpy', 'passionate', 'honest', 'leader-like', 'smug'], str(self.personality), scale(pygame.Rect((1150, y_pos[6]), (300, 70))), manager=MANAGER)

            if self.selected_cat.pelt.reverse:
                self.elements['reverse'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "Yes", scale(pygame.Rect((column3_x, y_pos[8]), (250, 70))), manager=MANAGER)
            else:
                self.elements['reverse'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "No", scale(pygame.Rect((column3_x, y_pos[8]), (250, 70))), manager=MANAGER)

            if self.skill:
                self.elements['skills'] = pygame_gui.elements.UIDropDownMenu(["Random"] + self.skills, self.skill, scale(pygame.Rect((1150, y_pos[8]), (250, 70))), manager=MANAGER)
            else:
                self.elements['skills'] = pygame_gui.elements.UIDropDownMenu(["Random"] + self.skills, "Random", scale(pygame.Rect((1150, y_pos[8]), (300, 70))), manager=MANAGER)
        
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1250), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1250), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        

                
    def handle_customize_cat_event(self, event):
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.elements['preview age']:
                self.preview_age = event.text
                self.update_sprite()
            if self.page == 0:
                if event.ui_element == self.elements['pelt dropdown']:
                    self.selected_cat.pelt.name = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['pelt color']:
                    self.selected_cat.pelt.colour = event.text
                    self.update_sprite()
                if event.ui_element == self.elements['pelt length']:
                    self.selected_cat.pelt.length = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['tint']:
                    if event.text == "none":
                        self.selected_cat.pelt.tint = None
                    else:
                        self.selected_cat.pelt.tint = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['pose']:
                    self.selected_cat.pelt.cat_sprites["kitten"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['adolescent pose']:
                    self.selected_cat.pelt.cat_sprites["adolescent"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['adult pose']:
                    if self.selected_cat.pelt.length in ['short', 'medium']:
                        self.selected_cat.pelt.cat_sprites["adult"] = int(event.text)
                    elif self.selected_cat.pelt.length == 'long':
                        self.selected_cat.pelt.cat_sprites["adult"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['elder pose']:
                    self.selected_cat.pelt.cat_sprites["senior"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['white patches']:
                    if event.text == "none":
                        self.selected_cat.pelt.white_patches = None
                    else:
                        self.selected_cat.pelt.white_patches = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['white_patches_tint']:
                    if event.text == "none":
                        self.selected_cat.pelt.white_patches_tint = None
                    else:
                        self.selected_cat.pelt.white_patches_tint = event.text
                    self.update_sprite()
            
                if event.ui_element == self.elements['eye color']:
                    self.selected_cat.pelt.eye_colour = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['eye color2']:
                    if event.text == "None":
                        self.selected_cat.pelt.eye_colour2 = None
                    else:
                        self.selected_cat.pelt.eye_colour2 = event.text
                    self.update_sprite() 
            
            elif self.page == 1:
                if event.ui_element == self.elements['tortie']:
                    if event.text == "Yes":
                        self.selected_cat.pelt.name = "Tortie"
                        # self.elements['pelt dropdown'].disable()
                        self.elements['pattern'].enable()
                        self.elements['tortiebase'].enable()
                        self.elements['tortiecolor'].enable()
                        self.elements['tortiepattern'].enable()
                        
                        self.selected_cat.pelt.pattern = "ONE"
                        self.selected_cat.pelt.tortiepattern = "bengal"
                        self.selected_cat.pelt.tortiebase = "SingleColour"
                        self.selected_cat.pelt.tortiecolour = "GINGER"
                    else:
                        self.selected_cat.pelt.name = "SingleColour"
                        self.elements['pattern'].disable()
                        self.elements['tortiebase'].disable()
                        self.elements['tortiecolor'].disable()
                        self.elements['tortiepattern'].disable()
                        self.selected_cat.pelt.pattern = None
                        self.selected_cat.pelt.tortiebase = None
                        self.selected_cat.pelt.tortiepattern = None
                        self.selected_cat.pelt.tortiecolour = None
                    self.update_sprite()
                elif event.ui_element == self.elements['tortiecolor']:
                    self.selected_cat.pelt.tortiecolour = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['pattern']:
                    self.selected_cat.pelt.pattern = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['tortiepattern']:
                    self.selected_cat.pelt.tortiepattern = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['tortiebase']:
                    self.selected_cat.pelt.tortiebase = event.text
                    self.update_sprite()
                if event.ui_element == self.elements['vitiligo']:
                    if event.text == "None":
                        self.selected_cat.pelt.vitiligo = None
                    else:
                        self.selected_cat.pelt.vitiligo = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['points']:
                    if event.text == "None":
                        self.selected_cat.pelt.points = None
                    else:
                        self.selected_cat.pelt.points = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['pose']:
                    self.selected_cat.pelt.cat_sprites["kitten"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['adolescent pose']:
                    self.selected_cat.pelt.cat_sprites["adolescent"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['adult pose']:
                    if self.selected_cat.pelt.length in ['short', 'medium']:
                        self.selected_cat.pelt.cat_sprites["adult"] = int(event.text)
                    elif self.selected_cat.pelt.length == 'long':
                        self.selected_cat.pelt.cat_sprites["adult"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['elder pose']:
                    self.selected_cat.pelt.cat_sprites["senior"] = int(event.text)
                    self.update_sprite()
             
                
            elif self.page == 2:
                
                if event.ui_element == self.elements['scars']:
                    if event.text == "None":
                        self.selected_cat.pelt.scars = []
                    else:
                        self.selected_cat.pelt.scars = []
                        self.selected_cat.pelt.scars.append(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['skin']:
                    self.selected_cat.pelt.skin = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['reverse']:
                    self.selected_cat.pelt.reverse = (event.text == "Yes")
                    self.update_sprite()
                elif event.ui_element == self.elements['accessory']:
                    if event.text == "None":
                        self.selected_cat.pelt.accessory = None
                    else:
                        self.selected_cat.pelt.accessory = event.text
                    self.update_sprite()
                elif event.ui_element == self.elements['permanent conditions']:
                    if event.text == "None":
                        self.permanent_condition = None
                        self.selected_cat.pelt.paralyzed = False
                        if "NOTAIL" in self.selected_cat.pelt.scars:
                            self.selected_cat.pelt.scars.remove("NOTAIL")
                        elif "NOPAW" in self.scars:
                            self.selected_cat.pelt.scars.remove("NOPAW")
                        self.update_sprite()
                    else:
                        self.permanent_condition = event.text
                        if event.text == 'paralyzed':
                            self.selected_cat.pelt.paralyzed = True
                            self.update_sprite()
                        else:
                            self.selected_cat.pelt.paralyzed = False
                        if event.text == 'born without a leg' and 'NOPAW' not in self.selected_cat.pelt.scars:
                            self.selected_cat.pelt.scars = []
                            self.selected_cat.pelt.scars.append('NOPAW')
                        elif event.text == "born without a tail" and "NOTAIL" not in self.selected_cat.pelt.scars:
                            self.selected_cat.pelt.scars = []
                            self.selected_cat.pelt.scars.append('NOTAIL')
                        else:
                            if "NOTAIL" in self.scars:
                                self.scars.remove("NOTAIL")
                            elif "NOPAW" in self.scars:
                                self.scars.remove("NOPAW")
                        self.update_sprite()

                elif event.ui_element == self.elements['sex']:
                    self.sex = event.text

                elif event.ui_element == self.elements['personality']:
                    self.personality = event.text
                elif event.ui_element == self.elements['pose']:
                    self.selected_cat.pelt.cat_sprites["kitten"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['adolescent pose']:
                    self.selected_cat.pelt.cat_sprites["adolescent"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['adult pose']:
                    if self.length in ['short', 'medium']:
                        self.selected_cat.pelt.cat_sprites["adult"] = int(event.text)
                    elif self.length == 'long':
                        self.selected_cat.pelt.cat_sprites["adult"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['elder pose']:
                    self.selected_cat.pelt.cat_sprites["senior"] = int(event.text)
                    self.update_sprite()
                elif event.ui_element == self.elements['skills']:
                    self.skill = event.text

        
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu:
                self.change_screen('start screen')
            elif event.ui_element == self.elements['right']:
                if self.page < 5:
                    self.page += 1
                    self.open_customize_cat()
            elif event.ui_element == self.elements['left']:
                if self.page > 0:
                    self.page -= 1
                    self.open_customize_cat()
            elif event.ui_element == self.elements['random_customize']:
                self.randomize_custom_cat()
                self.open_customize_cat()
            elif event.ui_element == self.elements['next_step']:
                
                new_cat = self.selected_cat
                new_cat.pelt = self.selected_cat.pelt
                new_cat.gender = self.sex
                new_cat.genderalign = self.sex
                self.your_cat = new_cat
                if self.permanent_condition is not None and self.permanent_condition != 'paralyzed':
                    self.your_cat.get_permanent_condition(self.permanent_condition, born_with=True)
                    self.your_cat.permanent_condition[self.permanent_condition]["moons_until"] = 1
                    self.your_cat.permanent_condition[self.permanent_condition]["moons_with"] = -1
                    self.your_cat.permanent_condition[self.permanent_condition]['born_with'] = True
                if self.paralyzed and 'paralyzed' not in self.your_cat.permanent_condition:
                    self.your_cat.get_permanent_condition('paralyzed')
                    self.your_cat.permanent_condition['paralyzed']["moons_until"] = 1
                    self.your_cat.permanent_condition['paralyzed']["moons_with"] = -1
                    self.your_cat.permanent_condition['paralyzed']['born_with'] = True
                if self.permanent_condition is not None and self.permanent_condition == "born without a tail" and "NOTAIL" not in self.your_cat.pelt.scars:
                    self.your_cat.pelt.scars.append('NOTAIL')
                    self.your_cat.permanent_condition['born without a tail']["moons_until"] = 1
                    self.your_cat.permanent_condition['born without a tail']["moons_with"] = -1
                    self.your_cat.permanent_condition['born without a tail']['born_with'] = True
                elif self.permanent_condition is not None and self.permanent_condition == "born without a leg" and "NOPAW" not in self.your_cat.pelt.scars:
                    self.your_cat.pelt.scars.append('NOPAW')
                    self.your_cat.permanent_condition['born without a leg']["moons_until"] = 1
                    self.your_cat.permanent_condition['born without a leg']["moons_with"] = -1
                    self.your_cat.permanent_condition['born without a leg']['born_with'] = True
                self.your_cat.accessories = [self.accessory]
                self.your_cat.inventory = {}
                self.your_cat.inventory.update({self.accessory: 1})
                self.your_cat.personality = Personality(trait=self.personality, kit_trait=True)
                if self.skill == "Random":
                    self.skill = random.choice(self.skills)
                self.your_cat.skills.primary = Skill.get_skill_from_string(Skill, self.skill)
                self.selected_cat = None
                self.open_name_cat()
            elif event.ui_element == self.elements['previous_step']:
                self.open_choose_leader()

    def update_sprite(self):
        pelt2 = Pelt(
            name=self.selected_cat.pelt.name,
            length=self.selected_cat.pelt.length,
            colour=self.selected_cat.pelt.colour,
            white_patches=self.selected_cat.pelt.white_patches,
            eye_color=self.selected_cat.pelt.eye_colour,
            eye_colour2=self.selected_cat.pelt.eye_colour2,
            tortiebase=self.selected_cat.pelt.tortiebase,
            tortiecolour=self.selected_cat.pelt.tortiecolour,
            pattern=self.selected_cat.pelt.pattern,
            tortiepattern=self.selected_cat.pelt.tortiepattern,
            vitiligo=self.selected_cat.pelt.vitiligo,
            points=self.selected_cat.pelt.points,
            accessory=self.selected_cat.pelt.accessory,
            paralyzed=self.selected_cat.pelt.paralyzed,
            scars=self.selected_cat.pelt.scars,
            tint=self.selected_cat.pelt.tint,
            skin=self.selected_cat.pelt.skin,
            white_patches_tint=self.selected_cat.pelt.white_patches_tint,
            kitten_sprite=self.selected_cat.pelt.cat_sprites["kitten"],
            adol_sprite=self.selected_cat.pelt.cat_sprites["adolescent"] if self.selected_cat.pelt.cat_sprites["adolescent"] > 2 else self.selected_cat.pelt.cat_sprites["adolescent"] + 3,
            adult_sprite=self.selected_cat.pelt.cat_sprites["adult"] if self.selected_cat.pelt.cat_sprites["adult"] > 2 else self.selected_cat.pelt.cat_sprites["adult"] + 6,
            senior_sprite=self.selected_cat.pelt.cat_sprites["senior"] if self.selected_cat.pelt.cat_sprites["senior"] > 2 else self.selected_cat.pelt.cat_sprites["senior"] + 12,
            reverse=self.selected_cat.pelt.reverse,
            accessories=[self.selected_cat.pelt.accessory] if self.selected_cat.pelt.accessory else [],
            inventory={self.selected_cat.pelt.accessory: 1} if self.selected_cat.pelt.accessory else {}
        )
        if self.selected_cat.pelt.length == 'long' and self.selected_cat.pelt.cat_sprites["adult"] < 9:
            pelt2.cat_sprites['young adult'] = self.selected_cat.pelt.cat_sprites["adult"] + 9
            pelt2.cat_sprites['adult'] = self.selected_cat.pelt.cat_sprites["adult"] + 9
            pelt2.cat_sprites['senior adult'] = self.selected_cat.pelt.cat_sprites["adult"] + 9
        c_moons = 1
        if self.preview_age == "adolescent":
            c_moons = 6
        elif self.preview_age == "adult":
            c_moons = 12
        elif self.preview_age == "elder":
            c_moons = 121
        # self.selected_cat = Cat(moons = c_moons, pelt=pelt2, loading_cat=True)

        self.selected_cat.pelt = pelt2

        self.selected_cat.sprite = generate_sprite(self.selected_cat)
        self.elements['sprite'].kill()
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((250,280), (350, 350))),
                                   self.selected_cat.sprite,
                                   self.selected_cat.ID,
                                   starting_height=0, manager=MANAGER)
    
    def open_choose_background(self):
        # clear screen
        self.clear_all_page()
        self.sub_screen = "choose camp"

        # Next and previous buttons
        self.elements["previous_step"] = UIImageButton(
            scale(pygame.Rect((506, 1290), (294, 60))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
        )
        self.elements["next_step"] = UIImageButton(
            scale(pygame.Rect((800, 1290), (294, 60))),
            "",
            object_id="#next_step_button",
            manager=MANAGER,
        )
        self.elements["next_step"].disable()

        # Biome buttons
        self.elements["forest_biome"] = UIImageButton(
            scale(pygame.Rect((392, 200), (200, 92))),
            "",
            object_id="#forest_biome_button",
            manager=MANAGER,
        )
        self.elements["mountain_biome"] = UIImageButton(
            scale(pygame.Rect((608, 200), (212, 92))),
            "",
            object_id="#mountain_biome_button",
            manager=MANAGER,
        )
        self.elements["plains_biome"] = UIImageButton(
            scale(pygame.Rect((848, 200), (176, 92))),
            "",
            object_id="#plains_biome_button",
            manager=MANAGER,
        )
        self.elements["beach_biome"] = UIImageButton(
            scale(pygame.Rect((1040, 200), (164, 92))),
            "",
            object_id="#beach_biome_button",
            manager=MANAGER,
        )

        # Camp Art Choosing Tabs, Dummy buttons, will be overridden.
        self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab4"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab5"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab6"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        y_pos = 550
        self.tabs["newleaf_tab"] = UIImageButton(scale(pygame.Rect((1255, y_pos), (78, 68))), "",
                                                 object_id="#newleaf_toggle_button",
                                                 manager=MANAGER,
                                                 tool_tip_text='Switch starting season to Newleaf.'
                                                 )
        y_pos += 100
        self.tabs["greenleaf_tab"] = UIImageButton(scale(pygame.Rect((1255, y_pos), (78, 68))), "",
                                                   object_id="#greenleaf_toggle_button",
                                                   manager=MANAGER,
                                                   tool_tip_text='Switch starting season to Greenleaf.'
                                                   )
        y_pos += 100
        self.tabs["leaffall_tab"] = UIImageButton(scale(pygame.Rect((1255, y_pos), (78, 68))), "",
                                                  object_id="#leaffall_toggle_button",
                                                  manager=MANAGER,
                                                  tool_tip_text='Switch starting season to Leaf-fall.'
                                                  )
        y_pos += 100
        self.tabs["leafbare_tab"] = UIImageButton(scale(pygame.Rect((1255, y_pos), (78, 68))), "",
                                                  object_id="#leafbare_toggle_button",
                                                  manager=MANAGER,
                                                  tool_tip_text='Switch starting season to Leaf-bare.'
                                                  )
        # Random background
        self.elements["random_background"] = UIImageButton(
            scale(pygame.Rect((510, 1190), (580, 60))),
            "",
            object_id="#random_background_button",
            manager=MANAGER,
        )

        # art frame
        self.elements["art_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect(((334, 324), (932, 832)))),
            pygame.transform.scale(
                pygame.image.load(
                    "resources/images/bg_preview_border.png"
                ).convert_alpha(),
                (932, 832),
            ),
            manager=MANAGER,
        )

        # camp art self.elements["camp_art"] = pygame_gui.elements.UIImage(scale(pygame.Rect((175,170),(450, 400))),
        # pygame.image.load(self.get_camp_art_path(1)).convert_alpha(), visible=False)

    def open_choose_symbol(self):
        # clear screen
        self.clear_all_page()

        # set basics
        self.sub_screen = "choose symbol"

        self.elements["previous_step"] = UIImageButton(
            scale(pygame.Rect((506, 1290), (294, 60))),
            "",
            object_id="#previous_step_button",
            manager=MANAGER,
        )
        self.elements["done_button"] = UIImageButton(
            scale(pygame.Rect((800, 1290), (294, 60))),
            "",
            object_id="#done_arrow_button",
            manager=MANAGER,
        )
        self.elements["done_button"].disable()

        # create screen specific elements
        self.elements["text_container"] = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((170, 230), (0, 0))),
            object_id="text_container",
            starting_height=1,
            manager=MANAGER,
        )
        self.text["clan_name"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 0), (-1, -1))),
            text=f"{self.clan_name}Clan",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_40"),
            manager=MANAGER,
        )
        self.text["biome"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 50), (-1, -1))),
            text=f"{self.biome_selected}",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
        )
        self.text["leader"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 90), (-1, -1))),
            text=f"Your name: {self.your_cat.name}",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
        )
        self.text["recommend"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 160), (-1, -1))),
            text=f"Recommended Symbol: N/A",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
        )
        self.text["selected"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((0, 200), (-1, -1))),
            text=f"Selected Symbol: N/A",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
        )

        self.elements["random_symbol_button"] = UIImageButton(
            scale(pygame.Rect((993, 412), (68, 68))),
            "",
            object_id="#random_dice_button",
            starting_height=1,
            tool_tip_text="Select a random symbol!",
            manager=MANAGER,
        )

        self.elements["symbol_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1081, 181), (338, 332))),
            pygame.image.load(
                f"resources/images/symbol_choice_frame.png"
            ).convert_alpha(),
            object_id="#symbol_choice_frame",
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["page_left"] = UIImageButton(
            scale(pygame.Rect((95, 829), (68, 68))),
            "",
            object_id="#arrow_left_button",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["page_right"] = UIImageButton(
            scale(pygame.Rect((1438, 829), (68, 68))),
            "",
            object_id="#arrow_right_button",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["filters_tab"] = UIImageButton(
            scale(pygame.Rect((200, 1239), (156, 60))),
            "",
            object_id="#filters_tab_button",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["symbol_list_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((152, 500), (1300, 740))),
            pygame.image.load(
                f"resources/images/symbol_list_frame.png"
            ).convert_alpha(),
            object_id="#symbol_list_frame",
            starting_height=2,
            manager=MANAGER,
        )

        if f"symbol{self.clan_name.upper()}0" in sprites.clan_symbols:
            self.text["recommend"].set_text(
                f"Recommended Symbol: {self.clan_name.upper()}0"
            )

        if not self.symbol_selected:
            if f"symbol{self.clan_name.upper()}0" in sprites.clan_symbols:
                self.symbol_selected = f"symbol{self.clan_name.upper()}0"

                self.text["selected"].set_text(
                    f"Selected Symbol: {self.clan_name.upper()}0"
                )

        if self.symbol_selected:
            symbol_name = self.symbol_selected.removeprefix("symbol")
            self.text["selected"].set_text(f"Selected Symbol: {symbol_name}")

            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1147, 254), (200, 200))),
                pygame.transform.scale(
                    sprites.sprites[self.symbol_selected], (200, 200)
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=2,
                manager=MANAGER,
            )
            self.refresh_symbol_list()
            while self.symbol_selected not in self.symbol_buttons:
                self.current_page += 1
                self.refresh_symbol_list()
            self.elements["done_button"].enable()
        else:
            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1147, 254), (200, 200))),
                pygame.transform.scale(
                    sprites.sprites["symbolADDER0"], (200, 200)
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=2,
                manager=MANAGER,
                visible=False,
            )
            self.refresh_symbol_list()
    
    def refresh_symbol_list(self):
        # get symbol list
        symbol_list = sprites.clan_symbols.copy()
        symbol_attributes = sprites.symbol_dict

        # filtering out tagged symbols
        for symbol in sprites.clan_symbols:
            index = symbol[-1]
            name = symbol.strip("symbol1234567890")
            tags = symbol_attributes[name.capitalize()][f"tags{index}"]
            for tag in tags:
                if tag in game.switches["disallowed_symbol_tags"]:
                    if symbol in symbol_list:
                        symbol_list.remove(symbol)

        # separate list into chunks for pages
        symbol_chunks = self.chunks(symbol_list, 45)

        # clamp current page to a valid page number
        self.current_page = max(1, min(self.current_page, len(symbol_chunks)))

        # handles which arrow buttons are clickable
        if len(symbol_chunks) <= 1:
            self.elements["page_left"].disable()
            self.elements["page_right"].disable()
        elif self.current_page >= len(symbol_chunks):
            self.elements["page_left"].enable()
            self.elements["page_right"].disable()
        elif self.current_page == 1 and len(symbol_chunks) > 1:
            self.elements["page_left"].disable()
            self.elements["page_right"].enable()
        else:
            self.elements["page_left"].enable()
            self.elements["page_right"].enable()

        display_symbols = []
        if symbol_chunks:
            display_symbols = symbol_chunks[self.current_page - 1]

        # Kill all currently displayed symbols
        symbol_images = [ele for ele in self.elements if ele in sprites.clan_symbols]
        for ele in symbol_images:
            self.elements[ele].kill()
            if self.symbol_buttons:
                self.symbol_buttons[ele].kill()

        x_pos = 192
        y_pos = 540
        for symbol in display_symbols:
            self.elements[f"{symbol}"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((x_pos, y_pos), (100, 100))),
                sprites.sprites[symbol],
                object_id=f"#{symbol}",
                starting_height=3,
                manager=MANAGER,
            )
            self.symbol_buttons[f"{symbol}"] = UIImageButton(
                scale(pygame.Rect((x_pos - 24, y_pos - 24), (148, 148))),
                "",
                object_id=f"#symbol_select_button",
                starting_height=4,
                manager=MANAGER,
            )
            x_pos += 140
            if x_pos >= 1431:
                x_pos = 192
                y_pos += 140

        if self.symbol_selected in self.symbol_buttons:
            self.symbol_buttons[self.symbol_selected].disable()


    def open_clan_saved_screen(self):
        self.clear_all_page()

        self.sub_screen = 'saved screen'

        self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((700, 210), (200, 200))),
            pygame.transform.scale(
                sprites.sprites[self.symbol_selected], (200, 200)
            ).convert_alpha(),
            object_id="#selected_symbol",
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["leader_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((700, 240), (200, 200))),
                                                                    pygame.transform.scale(
                                                                        self.your_cat.sprite,
                                                                        (200, 200)), manager=MANAGER)
        self.elements["continue"] = UIImageButton(scale(pygame.Rect((692, 600), (204, 60))), "",
                                                  object_id="#continue_button_small")
        self.elements["save_confirm"] = pygame_gui.elements.UITextBox(
            'May the odds be ever in your favour, ' + str(self.your_cat.name) + ".",
            scale(pygame.Rect((200, 470), (1200, 60))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER)

    def save_clan(self):
        self.handle_create_other_cats()
        game.mediated.clear()
        game.patrolled.clear()
        game.cat_to_fade.clear()
        Cat.outside_cats.clear()
        Patrol.used_patrols.clear()
        convert_camp = {1: 'camp1', 2: 'camp2', 3: 'camp3', 4: 'camp4', 5: 'camp5', 6: 'camp6'}
        self.your_cat.create_inheritance_new_cat()
        game.clan = Clan(name = self.clan_name,
                        leader = self.leader,
                        deputy = self.deputy,
                        medicine_cat = self.med_cat,
                        biome = self.biome_selected,
                        camp_bg = convert_camp[self.selected_camp_tab],
                        symbol=self.symbol_selected,
                        game_mode="expanded",
                        starting_members=self.members,
                        starting_season=self.selected_season,
                        your_cat=self.your_cat,
                        clan_age=self.clan_age)
        game.clan.create_clan()
        if self.clan_age == "established":
            game.clan.leader_lives = random.randint(1,9)
        game.cur_events_list.clear()
        game.herb_events_list.clear()
        Cat.grief_strings.clear()
        Cat.sort_cats()

    def get_camp_art_path(self, campnum):
        leaf = self.selected_season.replace("-", "")

        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = leaf.casefold()
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        biome = self.biome_selected.lower()

        if campnum:
            return f"{camp_bg_base_dir}/{biome}/{start_leave}_camp{campnum}_{light_dark}.png"
        else:
            return None

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]


make_clan_screen = MakeClanScreen()
