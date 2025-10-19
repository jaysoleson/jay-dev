import pygame.transform
import pygame_gui.elements
from scripts.clan import HERBS

from scripts.utility import get_text_box_theme, ui_scale
from scripts.game_structure.ui_elements import UIImageButton, UISurfaceImageButton
from scripts.game_structure.game_essentials import game
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.get_arrow import get_arrow

class PriorityHerbScreen(Screens):
    herb_buttons = {}
    corners = {}
    herb_displays = {}
    back_button = None

    def __init__(self, name=None):
        super().__init__(name)

        #herb!
        self.priorityherb = None
        self.back_button = None
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
           
            if event.ui_element == self.back_button:
                self.exit_screen()
                self.change_screen('events screen')

            for herb, button in self.herb_buttons.items():

                if event.ui_element == button:
                    if herb == self.priorityherb:
                        self.priorityherb = None
                    else:
                        self.priorityherb = herb
                    self.update_herb_buttons()
                    self.update_text()

    def update_text(self):
        for ele in self.herb_displays:
            self.herb_displays[ele].kill()
        self.herb_displays = {}

        self.herb_displays["title"] = pygame_gui.elements.UITextBox(
            "<u>Priority Herb</u>",
            ui_scale(pygame.Rect((150, 36), (500, 40))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            manager=MANAGER
        )
        
        self.herb_displays["subtitle"] = pygame_gui.elements.UITextBox(
            f"{game.clan.name}Clan will focus their efforts on finding more:",
            ui_scale(pygame.Rect((150, 455), (500, 40))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER
        )

        if self.priorityherb is not None:
            if game.settings["dark mode"]:
                self.herb_displays["herbs"] = pygame_gui.elements.UITextBox(
                    f"<font color='#A2D86C'>{self.priorityherb.replace('_', ' ')}</font>",
                    ui_scale(pygame.Rect((150, 482), (500, 40))),
                    object_id=get_text_box_theme("#text_box_34_horizcenter"),
                    manager=MANAGER
                )
            else:
                self.herb_displays["herbs"] = pygame_gui.elements.UITextBox(
                    f"<font color='#136D05'>{self.priorityherb.replace('_', ' ')}</font>",
                    ui_scale(pygame.Rect((150, 482), (500, 40))),
                    object_id=get_text_box_theme("#text_box_34_horizcenter"),
                    manager=MANAGER
                )
        else:
            self.herb_displays["herbs"] = pygame_gui.elements.UITextBox(
                "None",
                ui_scale(pygame.Rect((150, 482), (500, 40))),
                object_id=get_text_box_theme("#text_box_34_horizcenter"),
                manager=MANAGER
            )

        insert = ""
        if game.settings["dark mode"]:
            insert = "_dark"

        self.herb_displays["art"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((1, 440), (820, 173))),
            pygame.image.load(f"resources/images/priority_herb_screen{insert}.png").convert_alpha(),
            starting_height=1,
            manager=MANAGER
        )

    def update_herb_buttons(self):
        """ Displays and updates herb buttons """

        for ele in self.herb_buttons:
            self.herb_buttons[ele].kill()
        self.herb_buttons = {}
        for ele in self.corners:
            self.corners[ele].kill()
        self.corners = {}

        x_start = 240
        y_start = 90
        x_spacing = 65
        y_spacing = 65
        grid_size = 2

        x_pos = x_start
        y_pos = y_start

        selected_herbs = [self.priorityherb]
        picked = 0
        for h in selected_herbs:
            if h is not None:
                picked += 1

        count = 0
        for index, herb in enumerate(HERBS):
            count += 1
            if herb in game.clan.herbs:
                stock = game.clan.herbs[herb]
            else:
                stock = 0
            if herb != self.priorityherb:
                self.herb_buttons[herb] = UIImageButton(
                    ui_scale(pygame.Rect((x_pos, y_pos), (55, 55))), 
                    "",
                    tool_tip_text=f"<b>{herb.replace('_', ' ')}</b><br>In stock: {stock}",
                    object_id=f"#{herb}",
                    manager=MANAGER
                )
            else:
                self.herb_buttons[herb] = UIImageButton(
                    ui_scale(pygame.Rect((x_pos, y_pos), (55, 55))), 
                    "",
                    tool_tip_text=f"<b>{herb.replace('_', ' ')}</b><br>In stock: {stock}",
                    object_id=f"#{herb}_selected",
                    manager=MANAGER
                )
            
            if count == 5:
                count = 0
                x_pos = x_start 
                y_pos += y_spacing
            else:
                x_pos += x_spacing 

        # these have to go after the herb buttons to avoid hover issues

        insert = ""
        if game.settings["dark mode"]:
            insert = "_dark"

        self.corners["1"] = pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((215, 70), (75, 75))),
                            pygame.image.load(f"resources/images/corner_deco{insert}.png").convert_alpha(),
                            starting_height=1,
                            manager=MANAGER
                            )
        self.corners["2"] = pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((505, 70), (75, 75))),
                            pygame.transform.flip(pygame.image.load(f"resources/images/corner_deco{insert}.png").convert_alpha(), True, False),
                            starting_height=1,
                            manager=MANAGER
                            )
        self.corners["3"] = pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((215, 360), (75, 75))),
                            pygame.transform.flip(pygame.image.load(f"resources/images/corner_deco{insert}.png").convert_alpha(), False, True),
                            starting_height=1,
                            manager=MANAGER
                            )
        self.corners["4"] = pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((505, 360), (75, 75))),
                            pygame.transform.flip(pygame.image.load(f"resources/images/corner_deco{insert}.png").convert_alpha(), True, True),
                            starting_height=1,
                            manager=MANAGER
                            )

    def screen_switches(self):
        super().screen_switches()
        
        self.priorityherb = game.clan.infection["priority_herb"]
        self.update_herb_buttons()

        self.hide_menu_buttons()

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        
        self.update_text()
    
    def on_use(self):
        super().on_use()

    def exit_screen(self):
        game.clan.infection["priority_herb"] = self.priorityherb

        for ele in self.herb_buttons:
            self.herb_buttons[ele].kill()
        self.herb_buttons = {}

        for ele in self.corners:
            self.corners[ele].kill()
        self.corners = {}

        for ele in self.herb_displays:
            self.herb_displays[ele].kill()
        self.herb_displays = {}
    
        if self.back_button:
            self.back_button.kill()
            del self.back_button