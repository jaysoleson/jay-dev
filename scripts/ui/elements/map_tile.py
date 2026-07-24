from typing import Union, Optional, Dict, Iterable, Callable

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike, Coordinate
from pygame_gui.core.interfaces import IUIManagerInterface

from scripts.game_input import INPUT_ACTION_PRESSED, Action, INPUT_ACTION_RELEASED
from scripts.game_structure import game
from scripts.game_structure.screen_settings import screen
from scripts.territory import territory_class

class MapTileButton(pygame_gui.elements.UIButton):
    """Subclass of pygame_gui's button class. This allows for auto-scaling of the
    button image."""

    def __init__(
        self,
        relative_rect: Union[RectLike, Coordinate],
        text: str,
        manager: Optional[IUIManagerInterface] = None,
        container: Optional[IContainerLikeInterface] = None,
        tool_tip_text: Union[str, None] = None,
        starting_height: int = 1,
        parent_element: UIElement = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Dict[str, Union[str, UIElement]] = None,
        allow_double_clicks: bool = False,
        generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
        visible: int = 1,
        sound_id=None,
        *,
        command: Union[Callable, Dict[int, Callable]] = None,
        tool_tip_object_id: Optional[ObjectID] = None,
        text_kwargs: Optional[Dict[str, str]] = None,
        tool_tip_text_kwargs: Optional[Dict[str, str]] = None,

        # CGW
        tile_owner = None,
        tile_string = None
    ):
        self.sound_id = sound_id
        self.tile_owner = tile_owner
        self.tile_string = tile_string
        self.selected = False

        super().__init__(
            relative_rect=relative_rect,
            text=text,
            text_kwargs=text_kwargs,
            manager=manager,
            container=container,
            tool_tip_text=tool_tip_text,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            starting_height=starting_height,
            parent_element=parent_element,
            object_id=(
                ObjectID(class_id="@image_button", object_id=object_id)
                if not isinstance(object_id, ObjectID)
                else object_id
            ),
            anchors=anchors,
            allow_double_clicks=allow_double_clicks,
            generate_click_events_from=generate_click_events_from,
            visible=visible,
            command=command,
            tool_tip_object_id=tool_tip_object_id,
        )
        self.set_colour()
        # self.create_border()
        self.rebuild()

    def set_colour(self):
        if self.tile_owner:
            self.colours["normal_bg"] = self.get_colour(self.tile_owner.colours["normal"])
            self.colours["normal_border"] = self.get_colour(self.tile_owner.colours["dark"])
            self.colours["hovered_border"] = self.get_colour(self.tile_owner.colours["dark"])
            self.colours["hovered_bg"] = self.get_colour(self.tile_owner.colours["dark"])
        else:
            self.colours["normal_border"] = self.get_colour([97, 69, 41])
            self.colours["hovered_border"] = self.get_colour([51, 31, 11])

    def get_colour(self, value_list):
        colour = pygame.Color(value_list[0], value_list[1], value_list[2])

        return colour

    def create_border(self):
        x, y = self.tile_string.split("-")
        x = int(x)
        y = int(y)
        WEST_BORDER_STRING = None
        if x > 0:
            WEST_BORDER_STRING = f"{x - 1}-{y}"
        
        if WEST_BORDER_STRING:
            if (
                game.clan.territory_tile_info[WEST_BORDER_STRING]["owner"] !=
                self.tile_owner.group_ID
                ):
                # not worky

                self.set_image(territory_class.border_tiles["west"])


    def select(self):
        if self.tile_owner:
            self.colours["normal_bg"] = self.get_colour(self.tile_owner.colours["dark"])
            self.colours["normal_border"] = self.get_colour(self.tile_owner.colours["dark"])
        else:
            self.colours["normal_border"] = self.get_colour([51, 31, 11])

        self.selected = True
        self.rebuild()
    
    def deselect(self):
        if self.tile_owner:
            self.colours["normal_bg"] = self.get_colour(self.tile_owner.colours["normal"])
            self.colours["normal_border"] = self.get_colour(self.tile_owner.colours["dark"])
        else:
            self.colours["normal_border"] = self.get_colour([97, 69, 41])

        self.selected = False
        self.rebuild()
