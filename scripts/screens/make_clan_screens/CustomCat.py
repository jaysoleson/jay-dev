import pygame
import pygame_gui
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.screens.enums import GameScreen
import copy

from scripts.game_structure.game import Switch, switch_get_value
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.sprite_button import UISpriteButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme
from scripts.cat.cats import Cat, create_cat
from scripts.cat.enums import CatRank, CatAge
from scripts.cat.pelts import Pelt

class CustomCatScreen(MakeClanScreenBase):
    def __init__(self, name="custom_cat_screen"):
        super().__init__(name)
        # your edited cat
        self.custom_cat = None
        # the cat you started with
        self.starting_cat = None

    def screen_switches(self):
        super().screen_switches()
        self.starting_cat = Cat.all_cats.get(switch_get_value(Switch.cat))
        if not self.starting_cat:
            self.starting_cat = switch_get_value(Switch.possible_cats)[0]

        self.custom_cat = create_cat(CatRank.KITTEN)
        # self.custom_cat.pelt = copy.deepcopy(self.starting_cat.pelt)

        self.elements["previous_step"].hide()
        self.elements["next_step"].hide()

        self.elements["back"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 500), (110, 34))),
            "back",
            get_button_dict(ButtonStyles.SQUOVAL, (110, 34)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"centerx": "centerx"}
        )
        self.elements["done"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 600), (110, 34))),
            "done",
            get_button_dict(ButtonStyles.SQUOVAL, (110, 34)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"centerx": "centerx"}
        )

        self.elements["your_cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, -50), (160, 160))),
            pygame.transform.scale(self.custom_cat.sprite, ui_scale_dimensions((200, 200))),
            starting_height=1,
            manager=MANAGER,
            anchors={"centerx": "centerx", "centery": "centery"}
        )


    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["back"]:
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_CATS)
            if event.ui_element == self.elements["done"]:
                self._assign_cat()
                self.change_screen(GameScreen.MAKE_CLAN_YOUR_NAME)
        
        return super().handle_event(event)
    
    def _assign_cat(self):
        self.clan_info.your_cat = self.custom_cat

    def exit_screen(self):
        super().exit_screen()