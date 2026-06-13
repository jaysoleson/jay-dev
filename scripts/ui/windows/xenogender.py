import pygame
import pygame_gui
from scripts.game_structure.localization import load_lang_resource

from scripts.game_structure import game
from scripts.cat.cats import Cat
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.game_structure.game.switches import (
    Switch,
    switch_set_value
)
from scripts.ui.scale import ui_scale
from scripts.events_module.text_adjust import event_text_adjust

class XenogenderWindow(GameWindow):
    def __init__(self, cat):
        super().__init__(
            ui_scale(pygame.Rect((150, 150), (500, 250))),
        )
        self.set_blocking(True)
        switch_set_value(Switch.window_open, True)

        xenogender_event_data = load_lang_resource("events/xenogender_events.json")
        if cat.genderalign not in xenogender_event_data:
            self.kill()
            return
        event_text = event_text_adjust(
            Cat,
            xenogender_event_data[cat.genderalign],
            main_cat=cat,
            clan=game.clan
            )

        self.xenogender_message = UITextBoxTweaked(
            event_text,
            ui_scale(pygame.Rect((20, 60), (445, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self
        )
        self.confirm_text = UITextBoxTweaked(
            "<i>Gender successfully changed!</i>",
            ui_scale(pygame.Rect((20, 115), (445, -1))),
            line_spacing=1,
            object_id="#text_box_24_horizcenter",
            container=self
        )

        self.done_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 180), (80, 34))),
            "done",
            get_button_dict(ButtonStyles.SQUOVAL, (80, 34)),
            object_id="@buttonstyles_squoval",
            container=self,
            anchors={"centerx": "centerx"}
        )

    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                switch_set_value(Switch.window_open, False)
                self.xenogender_message.kill()
                self.confirm_text.kill()
                self.done_button.kill()
                self.kill()
