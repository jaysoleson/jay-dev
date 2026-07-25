from typing import Union, Optional, Dict, Iterable, Callable

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.gui_type_hints import RectLike, Coordinate
from pygame_gui.core.interfaces import IUIManagerInterface

from scripts.game_structure import game
from scripts.game_structure.screen_settings import screen
from scripts.territory import territory_class
from scripts.clan import COLOURS

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
        tile_string = None,
        view_colours = False,
        view_icons = False,
        icon_tile = False,
        opacity = 255,
        herb=None,
        current_view="borders"
    ):
        self.sound_id = sound_id

        # Clan object for the owner of the tile.
        # Nonetype if no owner
        self.tile_owner = tile_owner

        # string. "x-y"
        self.tile_string = tile_string

        # bool
        self.selected = False

        # int: opacity (alpha). 0 (transparent) to 255 (opaque)
        self.opacity = opacity

        # bools: are colours and icons visible
        self.view_colour = view_colours
        self.view_icons = view_icons

        # bool: is it a tile with an icon on it
        self.icon_tile = icon_tile

        # the tile's main herb if it has one
        self.herb = herb
        self.current_view = current_view

        self.colour_dict = {}

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
        self.border_width = 1

        self.set_colour_dict()

        self.set_colour()
        self.rebuild()
    
    def set_colour_dict(self):
        self.colour_dict = self.get_colour_dict()

    def get_colour_dict(self):
        """
        Returns a dict of light, normal, and dark colours based on the base (normal)
        """
        opacity = self.opacity
        if self.selected:
            opacity = 255

        colour = None
        if self.current_view == "borders":
            if self.tile_owner:
                colour = COLOURS[self.tile_owner.colour]
        elif self.current_view == "herbs":
            if self.herb:
                colour_object = game.clan.herb_supply.herb[self.herb].colour
                colour = [colour_object.r, colour_object.g, colour_object.b]
        if not colour:
            colour = COLOURS["default"]

        # deconstruct and reassemble edited versions of the colours            
        hover_colour_list = [
            round(colour[0] - colour[0] / 3),
            round(colour[1] - colour[1] / 3),
            round(colour[2] - colour[2] / 3)
            ]
        light_colour_list = [colour[0] + 15, colour[1] + 15, colour[2] + 15]

        normal_colour = pygame.Color(colour[0], colour[1], colour[2], opacity)
        light_colour = pygame.Color(light_colour_list[0], light_colour_list[1], light_colour_list[2], opacity)
        hover_colour = pygame.Color(hover_colour_list[0], hover_colour_list[1], hover_colour_list[2], opacity)

        return {
            "light": light_colour,
            "normal": normal_colour,
            "dark": hover_colour,
        }

    def set_colour(self):
        # HERB VIEW
        if self.current_view == "herbs":
            if self.view_colour:
                if self.herb:
                    if self.selected:
                        self.colours["normal_bg"] = self.colour_dict["dark"]
                    else:
                        self.colours["normal_bg"] = self.colour_dict["normal"]
                    self.colours["hovered_bg"] = self.colour_dict["dark"]
                    self.colours["normal_border"] = self.colour_dict["dark"]
                else:
                    self.colours["normal_border"] = self.colour_dict["normal"]
                self.colours["hovered_border"] = self.colour_dict["dark"]
            else:
                self.colours["hovered_border"] = self.colour_dict["dark"]
                if self.selected:
                    self.colours["normal_border"] = self.colour_dict["dark"]
                else:
                    # transparent
                    self.colours["normal_border"] = pygame.Color(0, 0, 0, 0)
        # BORDER VIEW
        else:
            if self.view_colour:
                if self.tile_owner:
                    # someones territory: set BG for selected
                    if self.selected:
                        self.colours["normal_bg"] = self.colour_dict["dark"]
                    else:
                        self.colours["normal_bg"] = self.colour_dict["normal"]
                    self.colours["hovered_bg"] = self.colour_dict["dark"]
                    self.colours["normal_border"] = self.colour_dict["dark"]
                else:
                    if self.selected:
                        self.colours["normal_border"] = self.colour_dict["dark"]
                    else:
                        self.colours["normal_border"] = self.colour_dict["normal"]
                self.colours["hovered_border"] = self.colour_dict["dark"]
                    
                # icon tiles get bgs no matter who owns them.
                if self.icon_tile:
                    self.colours["normal_bg"] = self.colour_dict["normal"]
                    self.colours["hovered_bg"] = self.colour_dict["dark"]
            else:
                self.colours["hovered_border"] = self.colour_dict["dark"]
                if self.selected:
                    self.colours["normal_border"] = self.colour_dict["dark"]
                else:
                    # transparent
                    self.colours["normal_border"] = pygame.Color(0, 0, 0, 0)
        
        if self.view_icons:
            if self.icon_tile:
                if self.selected:
                    self.colours["normal_bg"] = self.colour_dict["dark"]
                else:
                    self.colours["normal_bg"] = self.colour_dict["normal"]
                self.colours["hovered_bg"] = self.colour_dict["dark"]
        
        self.colours["active_bg"] = self.colours["hovered_bg"]
        self.colours["active_border"] = self.colours["hovered_border"]

        self.set_colour_dict()

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
        self.border_width = 2
        self.selected = True
        self.set_colour()
        self.rebuild()
    
    def deselect(self):
        self.border_width = 1
        self.selected = False
        self.set_colour()
        self.rebuild()
