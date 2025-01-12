from typing import Dict

import pygame.transform
import pygame_gui.elements

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import (
    game,
)
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UISpriteButton,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_personality_compatibility,
    get_text_box_theme,
    ui_scale,
    ui_scale_dimensions,
    ui_scale_offset,
    shorten_text_to_fit,
)
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import BoxStyles, get_box
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.get_arrow import get_arrow
from ..ui.icon import Icon


class ChooseQPPScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat = None
        self.previous_cat = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.the_cat = None
        self.selected_cat = None
        self.back_button = None

        self.list_frame_image = None
        
        self.toggle_qpp = None
        self.page_number = None

        self.qppscreen_button = None

        self.qpp_frame = None
        self.the_cat_frame = None
        self.info = None
        self.checkboxes = {}
        
        self.current_cat_elements = {}
        self.selected_cat_elements = {}

        self.qpps_tab_button = None
        self.offspring_tab_button = None
        self.potential_qpps_button = None
        
        # Keep track of all the cats we want to display
        self.all_qpps = []
        self.all_offspring = []
        self.all_potential_qpps = []
        
        # Keep track of the current page on all three tabs
        self.qpps_page = 0
        self.offspring_page = 0
        self.potential_qpps_page = 0
        
        self.qpps_cat_buttons = {}
        self.offspring_cat_buttons = {}
        self.potential_qpps_buttons = {}
        
        # Tab containers. 
        self.qpps_container = None
        self.offspring_container = None
        self.potential_container = None
        
        # Filter toggles
        self.kits_selected_pair = True
        self.single_only = False
        self.have_kits_only = False
        
        self.single_only_text = None
        self.have_kits_text = None
        self.with_selected_cat_text = None
        
        self.potential_page_display = None
        self.offspring_page_display = None
        self.qpp_page_display = None
        
        # Keep track of the open tab
        # Can be "potential" for the potential qpps tab, "offspring"
        # for the offspring tab, and "qpps" for the qpp tab. 
        self.open_tab = "potential" 
        self.tab_buttons = {}
        
        self.no_kits_message = None
        
        #Loading screen
        self.work_thread = None
        
    def handle_event(self, event):
        """ Handles events. """
        if game.switches["window_open"]:
            return
        
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            # Cat buttons list
            if event.ui_element == self.back_button:
                self.selected_qpp_index = 0
                self.change_screen('profile screen')
            elif event.ui_element == self.qppscreen_button:
                self.change_screen('choose mate screen')
            elif event.ui_element == self.toggle_qpp:
                
                self.work_thread = self.loading_screen_start_work(self.change_qpp)
                
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_current_cat_info()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat): 
                    game.switches["cat"] = self.next_cat
                    self.update_current_cat_info()
                else:
                    print("invalid next cat", self.next_cat)
                    
            # Checkboxes
            elif event.ui_element == self.checkboxes.get("single_only"):
                if self.single_only:
                    self.single_only = False
                else:
                    self.single_only = True
                self.update_potential_qpps_container()
            elif event.ui_element == self.checkboxes.get("have_kits_only"):
                if self.have_kits_only:
                    self.have_kits_only = False
                else:
                    self.have_kits_only = True
                self.update_potential_qpps_container()
            elif event.ui_element == self.checkboxes.get("kits_selected_pair"):
                if self.kits_selected_pair:
                    self.kits_selected_pair = False
                else:
                    self.kits_selected_pair = True
                self.update_offspring_container()
            
            # Next and last page buttons
            elif event.ui_element == self.offspring_next_page:
                self.offspring_page += 1
                self.update_offspring_container_page()
            elif event.ui_element == self.offspring_last_page:
                self.offspring_page -= 1
                self.update_offspring_container_page()
            elif event.ui_element == self.potential_next_page:
                self.potential_qpps_page += 1
                self.update_potential_qpps_container_page()
            elif event.ui_element == self.potential_last_page:
                self.potential_qpps_page -= 1
                self.update_potential_qpps_container_page()
            elif event.ui_element == self.qpps_next_page:
                self.qpps_page += 1
                self.update_qpps_container_page()
            elif event.ui_element == self.qpps_last_page:
                self.qpps_page -= 1
                self.update_qpps_container_page()
                
                
            elif event.ui_element == self.tab_buttons.get("qpps"):
                self.open_tab = "qpps"
                self.switch_tab()
            elif event.ui_element == self.tab_buttons.get("offspring"):
                self.open_tab = "offspring"
                self.switch_tab()
            elif event.ui_element == self.tab_buttons.get("potential"):
                self.open_tab = "potential"
                self.switch_tab()
            elif event.ui_element in self.qpps_cat_buttons.values() or \
                    event.ui_element in self.potential_qpps_buttons.values():
                self.selected_cat = event.ui_element.cat_object
                self.update_selected_cat()
            elif event.ui_element in self.offspring_cat_buttons.values():
                if event.ui_element.cat_object.faded:
                    return
                
                game.switches["cat"] = event.ui_element.cat_object.ID
                self.change_screen("profile screen")
            
    def screen_switches(self):
        """Sets up the elements that are always on the page"""
        self.info = pygame_gui.elements.UITextBox(
           "Cat's with queer-platonic partners will still be able to take other platonic partners"
            " and mates (unless those interactions are toggled off in their profile). "
            "Cats in QPRs will not naturally have kits with each other as if they were mates.",
            ui_scale(pygame.Rect((0, 5), (375, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95")
        )

        self.the_cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((40, 113), (266, 197))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat1_frame_mate.png"
                ).convert_alpha(),
                ui_scale_dimensions((266, 197)),
            ),
        )
        self.qpp_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((494, 113), (266, 197))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/choosing_cat2_frame_mate.png"
                ).convert_alpha(),
                ui_scale_dimensions((266, 197)),
            ),
        )
        
        self.list_frame_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 391), (650, 194))),
            get_box(BoxStyles.ROUNDED_BOX, (650, 194)),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "Next Cat " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            get_arrow(2, arrow_left=True) + " Previous Cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
    
        self.qppscreen_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((342, 142), (115, 30))),
            "mate screen",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
                                              
        # Tab containers:
        contain_rect = ui_scale(pygame.Rect((85, 400), (630, 219)))

        self.qpps_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)
        
        # All the perm elements the exist inside self.qpps_container
        self.qpps_next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((366, 179), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.qpps_container,
        )
        self.qpps_last_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((230, 179), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.qpps_container,
        )

        self.offspring_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)
        
        self.offspring_next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((366, 179), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.offspring_container,
        )
        self.offspring_last_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((230, 179), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.offspring_container,
        )
        self.offspring_separator = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((497, 0), (10, 176))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/vertical_bar.png"),
                ui_scale_dimensions((10, 176)),
            ),
            container=self.offspring_container,
        )

        self.with_selected_cat_text = pygame_gui.elements.UITextBox(
            "Offspring with selected cat",
            ui_scale(pygame.Rect((510, 12), (120, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.offspring_container,
        )

        self.potential_container = pygame_gui.core.UIContainer(contain_rect, MANAGER)

        # All the perm elements the exist inside self.potential_container
        self.potential_next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((366, 179), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.potential_container,
        )
        self.potential_last_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((230, 179), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.potential_container,
        )
        self.potential_seperator = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((497, 0), (10, 176))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/vertical_bar.png"),
                ui_scale_dimensions((10, 176)),
            ),
            container=self.potential_container,
        )

        # Checkboxes and text
        self.single_only_text = pygame_gui.elements.UITextBox(
            "No mates",
            ui_scale(pygame.Rect((517, 11), (104, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )

        self.have_kits_text = pygame_gui.elements.UITextBox(
            "Can have biological kits",
            ui_scale(pygame.Rect((517, 75), (104, -1))),
            object_id="#text_box_26_horizcenter",
            container=self.potential_container,
        )
        
        # Page numbers
        self.qpps_page = 0
        self.offspring_page = 0
        self.potential_qpps_page = 0
        

        # This may be deleted and changed later.
        self.toggle_qpp = UIImageButton(
            ui_scale(pygame.Rect((323, 310), (153, 30))),
            "",
            object_id="#confirm_mate_button",
        )

        self.open_tab = "potential"
        
        # This will set up everything else on the page. Basically everything that changed with selected or
        # current cat
        self.update_current_cat_info()

    def change_qpp(self):
        if not self.selected_cat:
            return
        
        if self.selected_cat.ID not in self.the_cat.qpp:
            self.the_cat.set_qpp(self.selected_cat)
            
        else:
            self.the_cat.unset_qpp(self.selected_cat, breakup=True)
        

    def update_both(self):
        """Updates both the current cat and selected cat info. """
        
        self.update_current_cat_info(reset_selected_cat=False) # This will also refresh tab contents
        self.update_selected_cat()

    def update_qpps_container(self):
        """Updates everything in the qpps container, including the list of current qpps,
        and the page"""
        
        self.all_qpps = self.chunks([Cat.fetch_cat(i) for i in self.the_cat.qpp], 30)
        self.update_qpps_container_page()
            
    def update_qpps_container_page(self):
        """Updates just the current page for the qpps container, does
        not refresh the list. It will also update the disable status of the 
        next and last page buttons """
        for ele in self.qpps_cat_buttons:
            self.qpps_cat_buttons[ele].kill()
        self.qpps_cat_buttons = {}
        
        
        # Different layout for a single qpp - they are just big in the center
        if len(self.all_qpps) == 1 and len(self.all_qpps[0]) == 1:
            
            #TODO disable both next and previous page buttons
            self.qpps_page = 0
            self.qpps_last_page.disable()
            self.qpps_next_page.disable()
            _qpp = self.all_qpps[0][0]
            self.mates_cat_buttons["cat"] = UISpriteButton(
                ui_scale(pygame.Rect((240, 13), (150, 150))),
                pygame.transform.scale(_qpp.sprite, ui_scale_dimensions((150, 150))),
                cat_object=_qpp,
                manager=MANAGER,
                container=self.qpps_container,
            )
            return
        
        
        total_pages = len(self.all_qpps)
        if max(1, total_pages) - 1 < self.qpps_page:
            self.qpps_page = total_pages - 1
        elif self.qpps_page < 0:
            self.qpps_page = 0
            
        if total_pages <= 1:
            self.qpps_last_page.disable()
            self.qpps_next_page.disable()
        elif self.qpps_page >= total_pages - 1:
            self.qpps_last_page.enable()
            self.qpps_next_page.disable()
        elif self.qpps_page <= 0:
            self.qpps_last_page.disable()
            self.qpps_next_page.enable()
        else:
            self.qpps_last_page.enable()
            self.qpps_next_page.enable()
        
        text = f"{self.qpps_page + 1} / {max(1, total_pages)}"
        if not self.qpp_page_display:
            self.qpp_page_display = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((264, 185), (102, 24))),
                text,
                container=self.qpps_container,
                object_id=get_text_box_theme(
                    "#text_box_26_horizcenter_vertcenter_spacing_95"
                ),
            )
        else:
            self.qpp_page_display.set_text(text)
        
        if self.all_qpps:
            display_cats = self.all_qpps[self.qpps_page]
        else:
            display_cats = []
        
        pos_x = 30
        pos_y = 0
        i = 0
        for _qpp in display_cats:
            if game.clan.clan_settings["show fav"] and _qpp.favourite != 0:
                self.fav[str(i)] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                    pygame.transform.scale(
                        pygame.image.load(
                            f"resources/images/fav_marker_{_qpp.favourite}.png").convert_alpha(),
                        (100, 100))
                )
                self.fav[str(i)].disable()
            self.mates_cat_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                _qpp.sprite,
                cat_object=_qpp,
                manager=MANAGER,
                container=self.mates_container,
            )
            pos_x += 60
            if pos_x >= 600:
                pos_x = 15
                pos_y += 60
            i += 1
        
    def update_offspring_container(self):
        """Updates everything in the qpps container, including the list of current qpps, checkboxes
        and the page"""
        self.all_offspring = [Cat.fetch_cat(i) for i in list(self.the_cat.inheritance.kits) if isinstance(Cat.fetch_cat(i), Cat)]
        if self.selected_cat and self.kits_selected_pair:
            self.all_offspring = [i for i in self.all_offspring if self.selected_cat.is_parent(i)]
        
        self.all_offspring = self.chunks(self.all_offspring, 24)

        if "kits_selected_pair" in self.checkboxes:
            self.checkboxes["kits_selected_pair"].kill()
        
        if self.kits_selected_pair:
            theme = "#checked_checkbox"
        else:
            theme = "#unchecked_checkbox"
            
        self.checkboxes["kits_selected_pair"] = UIImageButton(
            ui_scale(pygame.Rect((553, 62), (34, 34))),
            "",
            object_id=theme,
            container=self.offspring_container,
        )
        
        self.update_offspring_container_page()
    
    def update_potential_mates_container_page(self):
        """Updates just the current page for the mates container, does
        not refresh the list. It will also update the disable status of the
        next and last page buttons"""

        for ele in self.potential_qpps_buttons:
            self.potential_qpps_buttons[ele].kill()
        self.potential_qpps_buttons = {}

        total_pages = len(self.all_potential_mates)
        if max(1, total_pages) - 1 < self.potential_qpps_page:
            self.potential_qpps_page = total_pages - 1
        elif self.potential_qpps_page < 0:
            self.potential_qpps_page = 0

        if total_pages <= 1:
            self.potential_last_page.disable()
            self.potential_next_page.disable()
        elif self.potential_qpps_page >= total_pages - 1:
            self.potential_last_page.enable()
            self.potential_next_page.disable()
        elif self.potential_qpps_page <= 0:
            self.potential_last_page.disable()
            self.potential_next_page.enable()
        else:
            self.potential_last_page.enable()
            self.potential_next_page.enable()

        text = f"{self.potential_qpps_page + 1} / {max(1, total_pages)}"
        if not self.potential_page_display:
            self.potential_page_display = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((264, 185), (102, 24))),
                text,
                container=self.potential_container,
                object_id=get_text_box_theme(
                    "#text_box_26_horizcenter_vertcenter_spacing_95"
                ),
            )
        else:
            self.potential_page_display.set_text(text)

        if self.all_potential_qpps:
            display_cats = self.all_potential_qpps[self.potential_qpps_page]
        else:
            display_cats = []

        pos_x = 15
        pos_y = 0
        i = 0

        for _off in display_cats:
            self.potential_qpps_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                _off.sprite,
                cat_object=_off,
                container=self.potential_container,
            )
            pos_x += 60
            if pos_x >= 495:
                pos_x = 15
                pos_y += 60
            i += 1

    def update_potential_qpps_container(self):
        """Updates everything in the potential qpps container, including the list of current qpps, checkboxes
        and the page"""
        
        # Update checkboxes
        if "single_only" in self.checkboxes:
            self.checkboxes["single_only"].kill()

        if self.single_only:
            theme = "@checked_checkbox"
        else:
            theme = "@unchecked_checkbox"

        self.checkboxes["single_only"] = UIImageButton(
            ui_scale(pygame.Rect((553, 42), (34, 34))),
            "",
            object_id=theme,
            container=self.potential_container,
        )

        if "have_kits_only" in self.checkboxes:
            self.checkboxes["have_kits_only"].kill()

        if self.have_kits_only:
            theme = "@checked_checkbox"
        else:
            theme = "@unchecked_checkbox"

        self.checkboxes["have_kits_only"] = UIImageButton(
            ui_scale(pygame.Rect((553, 127), (34, 34))),
            "",
            object_id=theme,
            container=self.potential_container,
        )

        self.all_potential_mates = self.chunks(self.get_valid_qpps(), 24)

        # Update checkboxes
        # TODO

        self.update_potential_qpps_container_page()
    
    def update_potential_qpps_container_page(self):
        """Updates just the current page for the qpps container, does
        not refresh the list. It will also update the disable status of the  
        next and last page buttons"""
        
        for ele in self.potential_qpps_buttons:
            self.potential_qpps_buttons[ele].kill()
        self.potential_qpps_buttons = {}
        
        total_pages = len(self.all_potential_qpps)
        if max(1, total_pages) - 1 < self.potential_qpps_page:
            self.potential_qpps_page = total_pages - 1
        elif self.potential_qpps_page < 0:
            self.potential_qpps_page = 0
            
        if total_pages <= 1:
            self.potential_last_page.disable()
            self.potential_next_page.disable()
        elif self.potential_qpps_page >= total_pages - 1:
            self.potential_last_page.enable()
            self.potential_next_page.disable()
        elif self.potential_qpps_page <= 0:
            self.potential_last_page.disable()
            self.potential_next_page.enable()
        else:
            self.potential_last_page.enable()
            self.potential_next_page.enable()
        
        text = f"{self.potential_qpps_page + 1} / {max(1, total_pages)}"
        if not self.potential_page_display:
            self.potential_page_display = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((264, 185), (102, 24))),
                text,
                container=self.potential_container,
                object_id=get_text_box_theme(
                    "#text_box_26_horizcenter_vertcenter_spacing_95"
                ),
            )
        else:
            self.potential_page_display.set_text(text)
        
        if self.all_potential_qpps:
            display_cats = self.all_potential_qpps[self.potential_qpps_page]
        else:
            display_cats = []
        
        pos_x = 30
        pos_y = 0
        i = 0
        
        for _off in display_cats:
            self.potential_qpps_buttons["cat" + str(i)] = UISpriteButton(
                ui_scale(pygame.Rect((pos_x, pos_y), (50, 50))),
                _off.sprite,
                cat_object=_off,
                container=self.potential_container,
            )
            pos_x += 120
            if pos_x >= 990:
                pos_x = 30
                pos_y += 120
            i += 1
     
    def exit_screen(self):
        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}
        
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}
        
        for ele in self.tab_buttons:
            self.tab_buttons[ele].kill()
        self.tab_buttons = {}
        
        self.all_qpps = []
        self.all_potential_qpps = []
        self.all_offspring = []
        
        self.qpps_cat_buttons = {}
        self.offspring_cat_buttons = {}
        self.potential_qpps_buttons = {}
        self.checkboxes = {}
        
        self.potential_container.kill()
        self.potential_container = None
        self.offspring_container.kill()
        self.offspring_container = None
        self.qpps_container.kill()
        self.qpps_container = None
        
        self.single_only_text.kill()
        self.single_only_text = None
        self.have_kits_text.kill()
        self.have_kits_text = None
        self.with_selected_cat_text.kill()
        self.with_selected_cat_text = None
        
        self.the_cat_frame.kill()
        self.the_cat_frame = None
        self.qpp_frame.kill()
        self.qpp_frame = None
        self.info.kill()
        self.info = None
        self.back_button.kill()
        self.back_button = None
        self.qppscreen_button.kill()
        self.qppscreen_button = None
        self.previous_cat_button.kill()
        self.previous_cat_button = None
        self.next_cat_button.kill()
        self.next_cat_button = None
        self.toggle_qpp.kill()
        self.toggle_qpp = None
        
        self.potential_seperator = None
        self.offspring_seperator = None
        self.potential_last_page = None
        self.potential_next_page = None
        self.offspring_last_page = None
        self.offspring_next_page = None
        self.qpps_last_page = None
        self.qpps_next_page = None
        self.potential_page_display = None
        self.offspring_page_display = None
        self.qpp_page_display = None
        
    def update_current_cat_info(self, reset_selected_cat=True):
        """Updates all elements with the current cat, as well as the selected cat.
        Called when the screen switched, and whenever the focused cat is switched"""
        self.the_cat = Cat.all_cats[game.switches["cat"]]
        if not self.the_cat.inheritance:
            self.the_cat.create_inheritance_new_cat()

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats(exclude_status=["kitten", "medicine cat apprentice", "mediator apprentice", "apprentice"])
        self.next_cat_button.disable() if self.next_cat == 0 else self.next_cat_button.enable()
        self.previous_cat_button.disable() if self.previous_cat == 0 else self.previous_cat_button.enable()

        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        # Page numbers
        self.qpps_page = 0
        self.offspring_page = 0
        self.potential_qpps_page = 0

        heading_rect = ui_scale(pygame.Rect((0, 25), (400, -1)))
        text = "Choose a QPP for " + shorten_text_to_fit(
            str(self.the_cat.name), 500, 18
        )
        self.current_cat_elements["heading"] = pygame_gui.elements.UITextBox(
            text,
            heading_rect,
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            anchors={
                "centerx": "centerx",
            },
        )

        self.info.set_anchors(
            {"centerx": "centerx", "top_target": self.current_cat_elements["heading"]}
        )
        self.info.set_relative_position((0, 10))

        self.current_cat_elements["heading"].line_spacing = 0.95
        self.current_cat_elements["heading"].redraw_from_chunks()

        del heading_rect, text

        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 150), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
        )
        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.current_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((65, 115), (120, 30))),
            name,
            object_id="#text_box_34_horizcenter",
        )

        info = (
            str(self.the_cat.moons)
            + " moons\n"
            + self.the_cat.status
            + "\n"
            + self.the_cat.genderalign
            + "\n"
            + self.the_cat.personality.trait
            + "\n"
            + self.the_cat.sexuality
        )
        if self.the_cat.qpp:
            info += f"\n{len(self.the_cat.qpp)} "
            if len(self.the_cat.qpp) > 1:
                info += "qpps"
            else:
                info += "qpp"
        self.current_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((206, 175), (94, 100))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        if reset_selected_cat:
            self.selected_cat = None
            if self.the_cat.qpp:
                self.selected_cat = Cat.fetch_cat(self.the_cat.qpp[0])
            self.update_selected_cat()

        self.draw_tab_button()
        self.update_qpps_container()
        self.update_potential_qpps_container()
        self.update_offspring_container()
        
    def draw_tab_button(self):
        """Draw the tab buttons, and will switch the currently open tab if the button is
        not supposed to show up."""

        for x in self.tab_buttons:
            self.tab_buttons[x].kill()
        self.tab_buttons = {}

        button_rect = ui_scale(pygame.Rect((0, 0), (153, 39)))
        button_rect.bottomleft = ui_scale_offset((100, 8))
        self.tab_buttons["potential"] = UISurfaceImageButton(
            button_rect,
            "Potential Partners",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            anchors={"bottom": "bottom", "bottom_target": self.list_frame_image},
        )

        qpps_tab_shown = False
        button_rect.bottomleft = ui_scale_offset((7, 8))
        if self.the_cat.qpp:
            self.tab_buttons["qpps"] = UISurfaceImageButton(
                button_rect,
                "QPPs",
                get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
                object_id="@buttonstyles_horizontal_tab",
                starting_height=2,
                anchors={
                    "bottom": "bottom",
                    "bottom_target": self.list_frame_image,
                    "left_target": self.tab_buttons["potential"],
                },
            )
            qpps_tab_shown = True

        self.tab_buttons["offspring"] = UISurfaceImageButton(
            button_rect,
            "Offspring",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (153, 39)),
            object_id="@buttonstyles_horizontal_tab",
            starting_height=2,
            anchors={
                "bottom": "bottom",
                "bottom_target": self.list_frame_image,
                "left_target": self.tab_buttons["qpps"]
                if qpps_tab_shown
                else self.tab_buttons["potential"],
            },
        )

        if self.open_tab == "qpps" and not qpps_tab_shown:
            self.open_tab = "potential"

        self.switch_tab()
        
    def switch_tab(self):
        
        if self.open_tab == "qpps":
            self.qpps_container.show()
            self.offspring_container.hide()
            self.potential_container.hide()
            
            if "qpps" in self.tab_buttons:
                self.tab_buttons["qpps"].disable()
            self.tab_buttons["offspring"].enable()
            self.tab_buttons["potential"].enable()
        elif self.open_tab == "offspring":
            self.qpps_container.hide()
            self.offspring_container.show()
            self.potential_container.hide()
            
            if "qpps" in self.tab_buttons:
                self.tab_buttons["qpps"].enable()
            self.tab_buttons["offspring"].disable()
            self.tab_buttons["potential"].enable()
        else:
            self.qpps_container.hide()
            self.offspring_container.hide()
            self.potential_container.show()
            
            if "qpps" in self.tab_buttons:
                self.tab_buttons["qpps"].enable()
            self.tab_buttons["offspring"].enable()
            self.tab_buttons["potential"].disable()
        
    def update_selected_cat(self):
        """Updates all elements of the selected cat"""

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        if not isinstance(self.selected_cat, Cat):
            self.selected_cat = None
            self.toggle_qpp.disable()
            return

        self.draw_compatible_line_affection()

        self.selected_cat_elements["center_heart"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 188), (200, 78))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/heart_mates.png"
                    if self.selected_cat.ID in self.the_cat.qpp
                    else "resources/images/heart_breakup.png"
                    if self.selected_cat.ID in self.the_cat.previous_qpps
                    else "resources/images/heart_maybe.png"
                ).convert_alpha(),
                ui_scale_dimensions((200, 78)),
            ),
            anchors={"centerx": "centerx"},
        )

        # PrideGen
        if self.the_cat.t4t:
            self.selected_cat_elements["t4t"] = pygame_gui.elements.UITextBox(
                    f"{self.the_cat.name} is t4t!",
                    ui_scale(pygame.Rect((78, 307), (290, 30))),
                    object_id=get_text_box_theme("#text_box_22_horizleft"))
            
        if self.selected_cat.t4t:
            self.selected_cat_elements["t4t"] = pygame_gui.elements.UITextBox(
                    f"{self.selected_cat.name} is t4t!",
                    ui_scale(pygame.Rect((620, 307), (265, 32))),
                    object_id=get_text_box_theme("#text_box_22_horizleft"))
        # ---

        self.selected_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((600, 150), (150, 150))),
            pygame.transform.scale(
                self.selected_cat.sprite, ui_scale_dimensions((150, 150))
            ),
        )

        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + "..."
        self.selected_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            ui_scale(pygame.Rect((620, 115), (110, 30))),
            name,
            object_id="#text_box_34_horizcenter",
        )

        info = (
            str(self.selected_cat.moons)
            + " moons\n"
            + self.selected_cat.status
            + "\n"
            + self.selected_cat.genderalign
            + "\n"
            + self.selected_cat.personality.trait
            + "\n"
            + self.selected_cat.sexuality
        )
        if self.selected_cat.qpp:
            info += f"\n{len(self.selected_cat.qpp)} "
            if len(self.selected_cat.qpp) > 1:
                info += "QPPs"
            else:
                info += "QPP"

        self.selected_cat_elements["info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((500, 175), (94, 100))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

        if self.kits_selected_pair:
            self.update_offspring_container()

        self.toggle_qpp.kill()

        if self.selected_cat.ID in self.the_cat.qpp:
            self.toggle_qpp = UISurfaceImageButton(
                ui_scale(pygame.Rect((323, 310), (153, 30))),
                "Break It Up",
                get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
                object_id="@buttonstyles_squoval",
            )
        else:
            self.toggle_qpp = UISurfaceImageButton(
                ui_scale(pygame.Rect((323, 310), (153, 30))),
                "It's Official!",
                get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
                object_id="@buttonstyles_squoval",
            )

        if (
            not game.clan.clan_settings["same sex birth"]
            and self.the_cat.gender == self.selected_cat.gender
        ):
            warning_rect = ui_scale(pygame.Rect((0, 0), (160, 45)))
            warning_rect.bottomleft = ui_scale_offset((0, -5))
            self.selected_cat_elements[
                "no kit warning"
            ] = pygame_gui.elements.UITextBox(
                "This pair can't have biological kittens.",
                warning_rect,
                object_id=get_text_box_theme(
                    "#text_box_22_horizcenter_vertcenter_spacing_95"
                ),
                anchors={
                    "centerx": "centerx",
                    "bottom": "bottom",
                    "bottom_target": self.toggle_qpp,
                },
            )
            del warning_rect
  
    def draw_compatible_line_affection(self):
        """Draws the heart-line based on capability, and draws the hearts based on romantic love."""

        # Set the lines
        self.selected_cat_elements["compat_line"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 190), (200, 78))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/line_compatible.png"
                    if get_personality_compatibility(self.the_cat, self.selected_cat)
                    else "resources/images/line_incompatible.png"
                    if not get_personality_compatibility(
                        self.the_cat, self.selected_cat
                    )
                    else "resources/images/line_neutral.png"
                ).convert_alpha(),
                ui_scale_dimensions((200, 78)),
            ),
            anchors={"centerx": "centerx"},
        )

        # Set romantic hearts of current cat towards mate or selected cat.
        if self.the_cat.dead:
            platonic_like = 0
        else:
            if self.selected_cat.ID in self.the_cat.relationships:
                relation = self.the_cat.relationships[self.selected_cat.ID]
            else:
                relation = self.the_cat.create_one_relationship(self.selected_cat)
            platonic_like = relation.platonic_like

        if 10 <= platonic_like <= 30:
            heart_number = 1
        elif 31 <= platonic_like <= 80:
            heart_number = 2
        elif 81 <= platonic_like:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 210
        for i in range(0, heart_number):
            self.selected_cat_elements["heart1" + str(i)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_pos, 285), (22, 20))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((22, 20)),
                ),
            )
            x_pos += 27

        # Set romantic hearts of mate/selected cat towards current_cat.
        if self.selected_cat.dead:
            platonic_like = 0
        else:
            if self.the_cat.ID in self.selected_cat.relationships:
                relation = self.selected_cat.relationships[self.the_cat.ID]
            else:
                relation = self.selected_cat.create_one_relationship(self.the_cat)
            platonic_like = relation.platonic_like

        if 10 <= platonic_like <= 30:
            heart_number = 1
        elif 31 <= platonic_like <= 80:
            heart_number = 2
        elif 81 <= platonic_like:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 568
        for i in range(0, heart_number):
            self.selected_cat_elements["heart2" + str(i)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_pos, 285), (22, 20))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((22, 20)),
                ),
            )
            x_pos -= 27
    
    def on_use(self):
        super().on_use()

        self.loading_screen_on_use(self.work_thread, self.update_both)

    def get_valid_qpps(self):
        """Get a list of valid qpps for the current cat"""
        
        # Behold! The uglest list comprehension ever created! 
        valid_qpps = [
            i for i in Cat.all_cats_list if
            not i.faded
            and self.the_cat.is_potential_qpp(
                i, for_love_interest=False,
                age_restriction=False, ignore_no_qpps=True
                )
            and i.ID not in self.the_cat.qpp
            and (not self.single_only or not i.qpp)
            and (not self.have_kits_only 
                or game.clan.clan_settings["same sex birth"]
                or i.gender != self.the_cat.gender) and 
                (i.moons < self.the_cat.moons + (game.config["QPR"]["age_range"] + 1)) and
                (i.moons > self.the_cat.moons - (game.config["QPR"]["age_range"] + 1)) ]
        
        return valid_qpps

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
