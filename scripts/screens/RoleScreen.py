#!/usr/bin/env python3
# -*- coding: ascii -*-
import os

import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UITextBoxTweaked,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale,
    adjust_list_text,
)
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles


class RoleScreen(Screens):
    the_cat = None
    selected_cat_elements = {}
    buttons = {}
    next_cat = None
    previous_cat = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.update_selected_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_selected_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.promote_baron:
                # transfer allegiances
                for cat in Cat.all_cats_list:
                    if cat.allegiance == game.clan.baron.ID:
                        cat.allegiance = self.the_cat.ID
                
                # transfer baron accessory
                print(game.clan.baron.pelt.accessory, game.clan.colour.upper() + "BARON")
                if game.clan.colour.upper() + "BARON" in game.clan.baron.pelt.accessory:
                    game.clan.baron.pelt.accessory.remove(game.clan.colour.upper() + "BARON")
                    self.the_cat.pelt.accessory.append(game.clan.colour.upper() + "BARON")
                
                # remove the first baron
                if game.clan.baron:
                    game.clan.baron.status_change("clipper", resort=True)
                game.clan.baron = self.the_cat
                game.clan.heir = None
                self.the_cat.status_change("baron", resort=True)
                
                if game.sort_type == "rank":
                    Cat.sort_cats()
                self.update_selected_cat()
            elif event.ui_element == self.promote_regent:
                if game.clan.regent:
                    game.clan.regent.status_change("clipper", resort=True)
                game.clan.regent = self.the_cat
                self.the_cat.status_change("regent", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_clipper:
                self.the_cat.status_change("clipper", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_doctor:
                self.the_cat.status_change("doctor", resort=True)
                self.update_selected_cat()
            
            elif event.ui_element == self.promote_heir:
                if game.clan.heir:
                    game.clan.heir.status_change("clipper", resort=True)
                game.clan.heir = self.the_cat
                self.the_cat.status_change("heir", resort=True)
                self.update_selected_cat()

            elif event.ui_element == self.retire:
                self.the_cat.status_change("elder", resort=True)
                # Since you can't "unretire" a cat, apply the skill and trait change
                # here
                self.update_selected_cat()
            elif event.ui_element == self.switch_cog:
                self.the_cat.status_change("mediator", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_colt:
                self.the_cat.status_change("colt", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_apprentice_doctor:
                self.the_cat.status_change("apprentice doctor", resort=True)
                self.update_selected_cat()

        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if event.key == pygame.K_ESCAPE:
                self.change_screen("profile screen")
            elif event.key == pygame.K_RIGHT:
                game.switches["cat"] = self.next_cat
                self.update_selected_cat()
            elif event.key == pygame.K_LEFT:
                game.switches["cat"] = self.previous_cat
                self.update_selected_cat()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

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
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        # Create the buttons
        self.bar = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((48, 350), (704, 10))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/bar.png"),
                ui_scale_dimensions((704, 10)),
            ),
            manager=MANAGER,
        )

        self.blurb_background = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 195), (700, 150))),
            get_box(BoxStyles.ROUNDED_BOX, (700, 150)),
        )

        # LEADERSHIP
        self.promote_baron = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "screens.role.promote_baron",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_top",
            anchors={"top_target": self.bar},
        )
        self.promote_regent = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "screens.role.promote_regent",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.promote_baron},
        )
        self.promote_heir = UISurfaceImageButton(
            ui_scale(pygame.Rect((48, 0), (172, 36))),
            "screens.role.promote_heir",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.promote_regent},
        )

        # ADULT CAT ROLES
        self.switch_clipper = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 36))),
            "screens.role.switch_clipper",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
        )
        self.retire = UISurfaceImageButton(
            ui_scale(pygame.Rect((225, 0), (172, 36))),
            "screens.role.retire",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_clipper},
        )
        self.switch_doctor = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 36))),
            "screens.role.switch_doctor",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_cog = UISurfaceImageButton(
            ui_scale(pygame.Rect((402, 0), (172, 36))),
            "screens.role.switch_cog",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_doctor},
        )

        # In-TRAINING ROLES:
        self.switch_colt = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 36))),
            "screens.role.switch_colt",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 36)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.bar},
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )
        self.switch_apprentice_doctor = UISurfaceImageButton(
            ui_scale(pygame.Rect((579, 0), (172, 52))),
            "screens.role.switch_apprentice_doctor",
            get_button_dict(ButtonStyles.LADDER_MIDDLE, (172, 52)),
            object_id="@buttonstyles_ladder_middle",
            anchors={"top_target": self.switch_colt},
            text_is_multiline=True,
            text_layer_object_id="@buttonstyles_ladder_multiline",
        )

        self.update_selected_cat()

    def update_selected_cat(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.the_cat = Cat.fetch_cat(game.switches["cat"])
        if not self.the_cat:
            return

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((245, 40), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 150, 13)
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((387, 70), (175, -1))),
            short_name,
            object_id=get_text_box_theme("#text_box_30"),
        )

        text = [
            "<b>" + i18n.t(f"general.{self.the_cat.status}", count=1) + "</b>",
            i18n.t(f"cat.personality.{self.the_cat.personality.trait}"),
            i18n.t("general.moons_age", count=self.the_cat.moons)
            + "  |  "
            + self.the_cat.genderalign,
        ]

        if self.the_cat.mentor:
            mentor = Cat.fetch_cat(self.the_cat.mentor)
            text.append(
                i18n.t(
                    "general.mentor_label",
                    mentor=mentor.name if mentor else i18n.t("general.none"),
                )
            )

        if self.the_cat.apprentice:
            apprentices = adjust_list_text(
                [
                    str(Cat.fetch_cat(x).name)
                    for x in self.the_cat.apprentice
                    if Cat.fetch_cat(x)
                ]
            )
            text.append(
                i18n.t(
                    "general.apprentice_label",
                    count=len(self.the_cat.apprentice),
                    apprentices=apprentices,
                )
            )

        self.selected_cat_elements["cat_details"] = UITextBoxTweaked(
            "\n".join(text),
            ui_scale(pygame.Rect((395, 100), (160, 94))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            manager=MANAGER,
            line_spacing=0.95,
        )

        self.selected_cat_elements["role_blurb"] = pygame_gui.elements.UITextBox(
            self.get_role_blurb(),
            ui_scale(pygame.Rect((170, 200), (560, 135))),
            object_id="#text_box_26_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        main_dir = "resources/images/"
        paths = {
            "baron": "leader_icon.png",
            "regent": "deputy_icon.png",
            "heir": "deputy_icon.png",
            "doctor": "medic_icon.png",
            "apprentice doctor": "medic_app_icon.png",
            "cog": "mediator_icon.png",
            "clipper": "warrior_icon.png",
            "colt": "warrior_app_icon.png",
            "kitten": "kit_icon.png",
            "newborn": "kit_icon.png",
            "elder": "elder_icon.png",
        }

        if self.the_cat.status in paths:
            icon_path = os.path.join(main_dir, paths[self.the_cat.status])
        else:
            icon_path = os.path.join(main_dir, "buttonrank.png")

        self.selected_cat_elements["role_icon"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((82, 231), (78, 78))),
            pygame.transform.scale(
                image_cache.load_image(icon_path),
                ui_scale_dimensions((78, 78)),
            ),
        )

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()
        self.update_disabled_buttons()

    def update_disabled_buttons(self):

        self.update_previous_next_cat_buttons()

        if game.clan.baron:
            baron_invalid = game.clan.baron.dead or game.clan.baron.outside
        else:
            baron_invalid = True

        if game.clan.regent:
            regent_invalid = game.clan.regent.dead or game.clan.regent.outside
        else:
            regent_invalid = True

        if self.the_cat.status == "colt":
            # baronSHIP
            self.promote_baron.disable()
            self.promote_regent.disable()

            # ADULT CAT ROLES
            self.switch_clipper.disable()
            self.switch_doctor.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_cog.enable()
            self.switch_apprentice_doctor.enable()
            self.switch_colt.disable()
        elif self.the_cat.status == "clipper":
            # baronSHIP
            if baron_invalid:
                self.promote_baron.enable()
            else:
                self.promote_baron.disable()

            if regent_invalid:
                self.promote_regent.enable()
            else:
                self.promote_regent.disable()

            # ADULT CAT ROLES
            self.switch_clipper.disable()
            self.switch_doctor.enable()
            self.switch_cog.enable()
            self.retire.enable()
            self.promote_heir.enable()

            # In-TRAINING ROLES:
            self.switch_apprentice_doctor.disable()
            self.switch_colt.disable()
        elif self.the_cat.status == "regent":
            if baron_invalid:
                self.promote_baron.enable()
            else:
                self.promote_baron.disable()

            self.promote_regent.disable()

            # ADULT CAT ROLES
            self.switch_clipper.enable()
            self.switch_doctor.disable()
            self.switch_cog.enable()
            self.retire.enable()
            self.promote_heir.enable()

            # In-TRAINING ROLES:
            self.switch_apprentice_doctor.disable()
            self.switch_colt.disable()
        elif self.the_cat.status == "doctor":
            self.promote_baron.disable()
            self.promote_regent.disable()

            self.switch_clipper.enable()
            self.switch_doctor.disable()
            self.switch_cog.enable()
            self.retire.enable()
            self.promote_heir.enable()

            # In-TRAINING ROLES:
            self.switch_apprentice_doctor.disable()
            self.switch_colt.disable()
        elif self.the_cat.status == "cog":
            self.promote_baron.disable()
            self.promote_regent.disable()

            if self.the_cat.moons > 11:
                self.switch_clipper.enable()
                self.switch_doctor.enable()
                self.switch_apprentice_doctor.disable()
                self.switch_colt.disable()
            else:
                self.switch_clipper.disable()
                self.switch_doctor.disable()
                self.switch_apprentice_doctor.enable()
                self.switch_colt.enable()
            
            self.switch_cog.disable()
            self.retire.enable()
            self.promote_heir.enable()
        elif self.the_cat.status == "elder":
            if baron_invalid:
                self.promote_baron.enable()
            else:
                self.promote_baron.disable()

            if regent_invalid:
                self.promote_regent.enable()
            else:
                self.promote_regent.disable()

            # ADULT CAT ROLES
            self.switch_clipper.enable()
            self.switch_doctor.enable()
            self.switch_cog.enable()
            self.retire.disable()
            self.promote_heir.disable()

            # In-TRAINING ROLES:
            self.switch_apprentice_doctor.disable()
            self.switch_colt.disable()
        elif self.the_cat.status == "apprentice doctor":
            self.promote_baron.disable()
            self.promote_regent.disable()

            # ADULT CAT ROLES
            self.switch_clipper.disable()
            self.switch_doctor.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.promote_heir.enable()
            self.switch_cog.enable()
            self.switch_apprentice_doctor.disable()
            self.switch_colt.enable()

        elif self.the_cat.status == "baron":
            self.promote_baron.disable()
            self.promote_regent.disable()

            # ADULT CAT ROLES
            self.switch_clipper.enable()
            self.switch_doctor.enable()
            self.switch_cog.enable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_apprentice_doctor.disable()
            self.switch_colt.disable()
            self.promote_heir.disable()
        elif self.the_cat.status == "heir":
            
            if regent_invalid and self.the_cat.moons > 12:
                self.promote_regent.enable()
            else:
                self.promote_regent.disable()

            # In-TRAINING ROLES:
            if self.the_cat.moons > 12:
                self.promote_baron.enable()
                self.switch_apprentice_doctor.disable()
                self.switch_colt.disable()
                self.switch_clipper.enable()
                self.switch_doctor.enable()
                self.retire.enable()
            else:
                self.promote_baron.disable()
                self.switch_apprentice_doctor.enable()
                self.switch_colt.enable()
                self.switch_clipper.disable()
                self.switch_doctor.disable()
                self.retire.disable()
            self.promote_heir.disable()
            self.switch_cog.enable()
        else:
            self.promote_baron.disable()
            self.promote_regent.disable()

            # ADULT CAT ROLES
            self.switch_clipper.disable()
            self.switch_doctor.disable()
            self.switch_cog.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_apprentice_doctor.disable()
            self.switch_colt.disable()
            self.promote_heir.disable()

    def get_role_blurb(self):
        if self.the_cat.status == "clipper":
            output = "screens.role.blurb_clipper"
        elif self.the_cat.status == "baron":
            output = "screens.role.blurb_baron"
        elif self.the_cat.status == "regent":
            output = "screens.role.blurb_regent"
        elif self.the_cat.status == "heir":
            output = "screens.role.blurb_heir"
        elif self.the_cat.status == "doctor":
            output = "screens.role.blurb_doctor"
        elif self.the_cat.status == "cog":
            output = "screens.role.blurb_cog"
        elif self.the_cat.status == "elder":
            output = "screens.role.blurb_elder"
        elif self.the_cat.status == "colt":
            output = "screens.role.blurb_colt"
        elif self.the_cat.status == "apprentice doctor":
            output = "screens.role.blurb_apprentice_doctor"
        elif self.the_cat.status == "kitten":
            output = "screens.role.blurb_kitten"
        elif self.the_cat.status == "newborn":
            output = "screens.role.blurb_newborn"
        else:
            output = "screens.role.blurb_unknown"

        return i18n.t(output, name=self.the_cat.name, clan=game.clan.name)

    def exit_screen(self):
        self.back_button.kill()
        del self.back_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.bar.kill()
        del self.bar
        self.promote_baron.kill()
        del self.promote_baron
        self.promote_regent.kill()
        del self.promote_regent
        self.switch_clipper.kill()
        del self.switch_clipper
        self.promote_heir.kill()
        del self.promote_heir
        self.switch_doctor.kill()
        del self.switch_doctor
        self.switch_cog.kill()
        del self.switch_cog
        self.retire.kill()
        del self.retire
        self.switch_apprentice_doctor.kill()
        del self.switch_apprentice_doctor
        self.switch_colt.kill()
        del self.switch_colt
        self.blurb_background.kill()
        del self.blurb_background

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}
