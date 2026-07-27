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
        view_water = False,
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
        self.view_water = view_water

        self.current_view = current_view

        # bool: is it a tile with an icon on it
        self.icon_tile = icon_tile

        # the tile's main herb if it has one
        self.herb = herb

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

        self._set_colour_dict()

        self._set_colour()
        self.rebuild()
    
    def _set_colour_dict(self):
        self.colour_dict = self._get_colour_dict()

    def _get_colour_dict(self):
        """
        Returns a dict of light, normal, and dark colours based on the base (normal)
        """
        opacity = self.opacity
        # if self.selected:
        #     opacity = 255

        colour = None
        tile_info = game.clan.territory_tile_info[self.tile_string]
        if self.current_view == "borders":
            if self.tile_owner:
                if self.view_colour:
                    colour = COLOURS[self.tile_owner.colour]
                else:
                    colour = COLOURS["default"]
        elif self.current_view == "herbs":
            if self.herb:
                colour_object = game.clan.herb_supply.herb[self.herb].colour
                if self.view_colour:
                    colour = [colour_object.r, colour_object.g, colour_object.b]
                else:
                    colour = COLOURS["default"]
        elif self.current_view == "strength":
            map_colours = {
                0: "default",
                1: "dust",
                2: "yellow",
                3: "orange",
                4: "red"
            }
            if "strength" in tile_info:
                if self.view_colour:
                    colour = COLOURS[map_colours[tile_info["strength"]]]
                else:
                    colour = COLOURS["default"]
        elif self.current_view == "terrain":
            map_colours = {
                "river": "blue",
                "lake": "blue",
                "ocean": "blue"
            }
            if "terrain" in tile_info:
                if self.view_colour:
                    colour = COLOURS[map_colours[tile_info["terrain"]]]
                else:
                    colour = COLOURS["default"]
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

        if self.view_water and self.view_colour:
            if "terrain" in tile_info and tile_info["terrain"] in (
                "river", "lake", "ocean"
            ) and self.current_view != "terrain":
                colour_list = [normal_colour, light_colour, hover_colour]
                new_colour_list = []
                darken_by = [45, 22, 5]
                for colour in colour_list:
                    r = int(colour.r) - darken_by[0]
                    if r < 0:
                        r = 0
                    g = int(colour.g) - darken_by[1]
                    if g < 0:
                        g = 0
                    b = int(colour.b) - darken_by[2]
                    if b < 0:
                        b = 0

                    new_colour_list.append(pygame.Color(r, g, b, 240))
                if new_colour_list:
                    normal_colour = new_colour_list[0]
                    light_colour = new_colour_list[1]
                    hover_colour = new_colour_list[2]
        return {
            "light": light_colour,
            "normal": normal_colour,
            "dark": hover_colour,
        }

    def _set_colour(self):
        populated = False
        if self.current_view == "borders":
            populated = self.tile_owner
        elif self.current_view == "herbs":
            populated = self.herb
        elif self.current_view == "strength":
            populated = game.clan.territory_tile_info[self.tile_string]["strength"] > 0
        elif self.current_view == "terrain":
            populated = "terrain" in game.clan.territory_tile_info[self.tile_string]
        
        if self.view_water:
            if "terrain" in game.clan.territory_tile_info[self.tile_string]:
                if game.clan.territory_tile_info[self.tile_string]["terrain"] in (
                    "river", "lake", "ocean"
                ):
                    populated = True
        
        if self.icon_tile:
            populated = True

        if self.view_colour:
            if populated:
                if self.selected:
                    self.colours["normal_bg"] = self.colour_dict["dark"]
                else:
                    self.colours["normal_bg"] = self.colour_dict["normal"]
                    if self.tile_owner:
                        self.colours["normal_border"] = self.colour_dict["dark"]
                    else:
                        self.colours["normal_border"] = self.colour_dict["normal"]
                        if self.herb and not self.tile_owner:
                            self.colours["normal_border"] = self.colour_dict["dark"]
                self.colours["hovered_bg"] = self.colour_dict["dark"]
            else:
                self.colours["normal_bg"] = pygame.Color(0, 0, 0, 0)
                self.colours["hovered_bg"] = pygame.Color(0, 0, 0, 0)
                self.colours["normal_border"] = self.colour_dict["normal"]
            
            self.colours["hovered_border"] = self.colour_dict["dark"]
        else:
            if self.icon_tile:
                if self.selected:
                    self.colours["normal_bg"] = self.colour_dict["dark"]
                else:
                    self.colours["normal_bg"] = self.colour_dict["normal"]
                self.colours["hovered_bg"] = self.colour_dict["dark"]
                self.colours["normal_border"] = self.colour_dict["dark"]
            else:
                self.colours["normal_bg"] = pygame.Color(0, 0, 0, 0)
                self.colours["hovered_bg"] = pygame.Color(0, 0, 0, 0)
                self.colours["normal_border"] = pygame.Color(0, 0, 0, 0)
                self.colours["hovered_border"] = self.colour_dict["dark"]

            if self.selected:
                self.colours["normal_border"] = self.colour_dict["dark"]

            self.colours["hovered_border"] = self.colour_dict["dark"]

        self.colours["active_bg"] = self.colours["hovered_bg"]
        self.colours["active_border"] = self.colours["hovered_border"]

        self._set_colour_dict()

    def select(self):
        self.border_width = 2
        self.selected = True
        self._set_colour()
        self.rebuild()
    
    def deselect(self):
        self.border_width = 1
        self.selected = False
        self._set_colour()
        self.rebuild()
