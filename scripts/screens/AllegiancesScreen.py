import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    get_alive_clan_queens,
    ui_scale_offset,
)
from .Screens import Screens


class AllegiancesScreen(Screens):
    allegiance_list = []

    def __init__(self, name=None):
        super().__init__(name)
        self.names_boxes = None
        self.ranks_boxes = None
        self.scroll_container = None
        self.heading = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)
            self.mute_button_pressed(event)

    def on_use(self):
        super().on_use()

    def screen_switches(self):
        super().screen_switches()
        # Heading
        self.heading = pygame_gui.elements.UITextBox(
            "<b>The Tributes</b>",
            ui_scale(pygame.Rect((0, 115), (400, 40))),
            object_id=get_text_box_theme("#text_box_34_horizcenter_vertcenter"),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        # Set Menu Buttons.
        self.show_menu_buttons()
        self.show_mute_buttons()
        self.set_disabled_menu_buttons(["allegiances"])
        allegiance_list = self.get_allegiances_text()


        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((50, 165), (715, 470))),
            allow_scroll_x=False,
            allow_scroll_y=True,
            manager=MANAGER,
        )

        self.ranks_boxes = []
        self.names_boxes = []
        allegiances_height = 0
        for x in allegiance_list:
            self.ranks_boxes.append(
                pygame_gui.elements.UITextBox(
                    x[0],
                    ui_scale(pygame.Rect((0, 0), (150, -1))),
                    object_id=get_text_box_theme("#text_box_30_horizleft"),
                    container=self.scroll_container,
                    manager=MANAGER,
                    anchors={"top_target": self.names_boxes[-1]}
                    if len(self.names_boxes) > 0
                    else None,
                )
            )
            self.ranks_boxes[-1].disable()

            self.names_boxes.append(
                pygame_gui.elements.UITextBox(
                    x[1],
                    pygame.Rect(
                        (0, -self.ranks_boxes[-1].get_relative_rect()[3]),
                        ui_scale_offset((565, -1)),
                    ),
                    object_id=get_text_box_theme("#text_box_30_horizleft"),
                    container=self.scroll_container,
                    manager=MANAGER,
                    anchors={
                        "top_target": self.ranks_boxes[-1],
                        "left_target": self.ranks_boxes[-1],
                        "left": "left",
                        "right": "right",
                    },
                )
            )
            self.names_boxes[-1].disable()
            allegiances_height += 1
        
        self.scroll_container.set_scrollable_area_dimensions((715, 470 + allegiances_height*20))


    def exit_screen(self):
        for x in self.ranks_boxes:
            x.kill()
        del self.ranks_boxes
        for x in self.names_boxes:
            x.kill()
        del self.names_boxes
        self.scroll_container.kill()
        del self.scroll_container

        self.heading.kill()
        del self.heading

    @staticmethod
    def generate_one_entry(cat, extra_details=""):
        """Extra Details will be placed after the cat description, but before the apprentice (if they have one. )"""
        if cat.dead:
            if game.settings["dark mode"]:
                extra_details = "<font color='#FF9999' ><b>DEAD: </b></font>"
            else:
                extra_details = "<font color='#950000' ><b>DEAD: </b></font>"
        else:
            extra_details = ""

        output = f"{extra_details}{str(cat.name).upper()} - {cat.describe_cat()}"


        return output

    def get_allegiances_text(self):
        """Determine Text. Ouputs list of tuples."""

        living_cats = [i for i in Cat.all_cats.values()]
        clan1 = []
        clan2 = []
        clan3 = []
        clan4 = []
        clan5 = []
        clan6 = []
        clan7 = []
        clan8 = []
        clan9 = []
        clan10 = []
        clan11 = []
        clan12 = []
        
        for cat in living_cats:
            if cat.cat_clan == str(game.clan.all_clans[0]).replace("Clan", ""):
                clan1.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[1]).replace("Clan", ""):
                clan2.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[2]).replace("Clan", ""):
                clan3.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[3]).replace("Clan", ""):
                clan4.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[4]).replace("Clan", ""):
                clan5.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[5]).replace("Clan", ""):
                clan6.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[6]).replace("Clan", ""):
                clan7.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[7]).replace("Clan", ""):
                clan8.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[8]).replace("Clan", ""):
                clan9.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[9]).replace("Clan", ""):
                clan10.append(cat)
            if cat.cat_clan == str(game.clan.all_clans[10]).replace("Clan", ""):
                clan11.append(cat)
            if cat.cat_clan == game.clan.name:
                clan12.append(cat)

        outputs = []
        # all the clans!
        # clan 12 first because its the MC's Clan
        if clan12:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.name}Clan</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan12])
            outputs.append(_box)
        if clan1:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[0]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan1])
            outputs.append(_box)
        if clan2:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[1]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan2])
            outputs.append(_box)
        if clan3:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[2]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan3])
            outputs.append(_box)
        if clan4:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[3]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan4])
            outputs.append(_box)
        if clan5:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[4]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan5])
            outputs.append(_box)
        if clan6:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[5]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan6])
            outputs.append(_box)
        if clan7:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[6]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan7])
            outputs.append(_box)
        if clan8:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[7]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan8])
            outputs.append(_box)
        if clan9:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[8]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan9])
            outputs.append(_box)
        if clan10:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[9]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan10])
            outputs.append(_box)
        if clan11:
            _box = ["", ""]
            _box[0] = f"<b><u>{game.clan.all_clans[10]}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in clan11])
            outputs.append(_box)

        return outputs
