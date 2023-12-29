import pygame.transform
import pygame_gui.elements
from random import choice, randint
import ujson
from .Screens import Screens


from scripts.cat_relations.inheritance import Inheritance
from scripts.cat.history import History
from scripts.event_class import Single_Event
from scripts.events import events_class

from scripts.utility import get_personality_compatibility, get_text_box_theme, scale, scale_dimentions, shorten_text_to_fit
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.cat.sprites2 import Sprites2, spriteSize
from scripts.cat.pelts import Pelt
from scripts.game_structure.windows import GameOver, PickPath, DeathScreen
from scripts.game_structure.image_button import UIImageButton, UISpriteButton, UIRelationStatusBar
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER

class ChangeAccessoryScreen(Screens):
    selected_cat = None
    current_page = 1
    list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 452 / 1400 * screen_y))
    apprentice_details = {}
    selected_details = {}
    cat_list_buttons = {}
    accessory_buttons = {}
    accessories_list = []

    def __init__(self, name=None):
        super().__init__(name)
        self.list_page = None
        self.next_cat = None
        self.previous_cat = None
        self.next_page_button = None
        self.previous_page_button = None
        self.current_mentor_warning = None
        self.confirm_mentor = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.mentor_icon = None
        self.app_frame = None
        self.mentor_frame = None
        self.current_mentor_text = None
        self.info = None
        self.heading = None
        self.mentor = None
        self.the_cat = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            b_data = event.ui_element.blit_data[1]
            b_2data = []
            for b in self.accessory_buttons.values():
                b_2data.append(b.blit_data[1])
            if b_data in b_2data:
                value = b_2data.index(b_data)
                n = value
                if self.accessories_list[n] == game.clan.your_cat.pelt.accessory:
                    game.clan.your_cat.pelt.accessory = None
                if self.accessories_list[n] in game.clan.your_cat.pelt.accessories:
                    game.clan.your_cat.pelt.accessories.remove(self.accessories_list[n])
                else:
                    game.clan.your_cat.pelt.accessories.append(self.accessories_list[n])
                self.update_selected_cat()
            elif event.ui_element == self.confirm_mentor and self.selected_cat:
                game.clan.your_cat.pelt.accessories.clear()
                game.clan.your_cat.pelt.accessory =None
                self.update_selected_cat()
            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches['cat'] = self.next_cat
                    self.update_cat_list()
                    self.update_selected_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches['cat'] = self.previous_cat
                    self.update_cat_list()
                    self.update_selected_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_list()
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_list()

    def screen_switches(self):
        self.the_cat = game.clan.your_cat
        self.mentor = Cat.fetch_cat(self.the_cat.mentor)
        self.cat_list_buttons = {}
        self.accessory_buttons = {}
        self.accessories_list = []
        self.heading = pygame_gui.elements.UITextBox("Change your accessory",
                                                     scale(pygame.Rect((300, 50), (1000, 80))),
                                                     object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                     manager=MANAGER)
        self.info = pygame_gui.elements.UITextBox("The accessories you have gathered are listed below.",
                                                  scale(pygame.Rect((360, 120), (880, 200))),
                                                  object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                                                  manager=MANAGER)

        # Layout Images:
        self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((630, 226), (562, 394))),
                                                        pygame.transform.scale(
                                                            image_cache.load_image(
                                                                "resources/images/choosing_cat1_frame_ment.png").convert_alpha(),
                                                            (562, 394)), manager=MANAGER)

        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
        self.confirm_mentor = UIImageButton(scale(pygame.Rect((660, 605), (248, 70))), "",
                                            object_id="#remove_all_button")
      
        self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1160), (68, 68))), "",
                                                  object_id="#relation_list_previous", manager=MANAGER)
        self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1160), (68, 68))), "",
                                              object_id="#relation_list_next", manager=MANAGER)

        self.update_selected_cat()  # Updates the image and details of selected cat
        self.update_cat_list()

    def exit_screen(self):

        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}

        for ele in self.accessory_buttons:
            self.accessory_buttons[ele].kill()
        self.accessory_buttons = {}

        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}
        
        self.accessories_list = []


        self.heading.kill()
        del self.heading

        self.info.kill()
        del self.info

        self.mentor_frame.kill()
        del self.mentor_frame

        self.back_button.kill()
        del self.back_button
        self.confirm_mentor.kill()
        del self.confirm_mentor

        self.previous_page_button.kill()
        del self.previous_page_button
        self.next_page_button.kill()
        del self.next_page_button

    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        self.selected_cat = game.clan.your_cat
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_cat:

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((650, 300), (300, 300))),
                pygame.transform.scale(
                    self.selected_cat.sprite,
                    (300, 300)), manager=MANAGER)

            info = "Current accessories: "
            all_accessories = game.clan.your_cat.pelt.accessories
            if game.clan.your_cat.pelt.accessory and game.clan.your_cat.pelt.accessory not in all_accessories:
                all_accessories.append(game.clan.your_cat.pelt.accessory)
            if len(all_accessories) > 0:
                for i in all_accessories:
                    info += "\n" + self.accessory_display_name(i)
            else:
                info += " None"        
            
            self.selected_details["selected_info"] = pygame_gui.elements.UITextBox(info,
                                                                                   scale(pygame.Rect((980, 325),
                                                                                                     (210, 250))),
                                                                                   object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                   manager=MANAGER)

            name = str(self.selected_cat.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["mentor_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((690, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter", manager=MANAGER)
    
    def accessory_display_name(self, accessory):
        if accessory is None:
            return ''
        acc_display = accessory.lower()

        if accessory in Pelt.collars:
            collar_colors = {'crimson': 'red', 'blue': 'blue', 'yellow': 'yellow', 'cyan': 'cyan',
                            'red': 'orange', 'lime': 'lime', 'green': 'green', 'rainbow': 'rainbow',
                            'black': 'black', 'spikes': 'spiky', 'white': 'white', 'pink': 'pink',
                            'purple': 'purple', 'multi': 'multi', 'indigo': 'indigo'}
            collar_color = next((color for color in collar_colors if acc_display.startswith(color)), None)

            if collar_color:
                if acc_display.endswith('bow') and not collar_color == 'rainbow':
                    acc_display = collar_colors[collar_color] + ' bow'
                elif acc_display.endswith('bell'):
                    acc_display = collar_colors[collar_color] + ' bell collar'
                else:
                    acc_display = collar_colors[collar_color] + ' collar'

        elif accessory in Pelt.wild_accessories:
            if acc_display == 'blue feathers':
                acc_display = 'crow feathers'
            elif acc_display == 'red feathers':
                acc_display = 'cardinal feathers'

        return acc_display


    def update_cat_list(self):
        """Updates the cat sprite buttons. """
        valid_mentors = self.chunks(self.get_valid_cats(), 30)

        # If the number of pages becomes smaller than the number of our current page, set
        #   the current page to the last page
        if self.current_page > len(valid_mentors):
            self.list_page = len(valid_mentors)

        # Handle which next buttons are clickable.
        if len(valid_mentors) <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.current_page >= len(valid_mentors):
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.current_page == 1 and len(valid_mentors) > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()
        display_cats = []
        if valid_mentors:
            display_cats = valid_mentors[self.current_page - 1]

        # Kill all the currently displayed cats.
        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}


        sprites = Sprites2(spriteSize)
        
        for x in [
            'scars', 'missingscars', 'medcatherbs',
            'collars', 'bellcollars', 'bowcollars', 'nyloncollars',
            'fadestarclan', 'fadedarkforest', 'flower_accessories', 'plant2_accessories', 'snake_accessories', 'smallAnimal_accessories', 'deadInsect_accessories',
            'aliveInsect_accessories', 'fruit_accessories', 'crafted_accessories', 'tail2_accessories'

        ]:
            if 'lineart' in x and game.config['fun']['april_fools']:
                sprites.spritesheet(f"sprites/aprilfools{x}.png", x)
            else:
                sprites.spritesheet(f"sprites/{x}.png", x)


        sprites.load_scars()

        cat = game.clan.your_cat
        age = cat.age
        cat_sprite = str(cat.pelt.cat_sprites[cat.age])

        
        # setting the cat_sprite (bc this makes things much easier)
        if cat.not_working() and age != 'newborn' and game.config['cat_sprites']['sick_sprites']:
            if age in ['kitten', 'adolescent']:
                cat_sprite = str(19)
            else:
                cat_sprite = str(18)
        elif cat.pelt.paralyzed and age != 'newborn':
            if age in ['kitten', 'adolescent']:
                cat_sprite = str(17)
            else:
                if cat.pelt.length == 'long':
                    cat_sprite = str(16)
                else:
                    cat_sprite = str(15)
        else:
            if age == 'elder' and not game.config['fun']['all_cats_are_newborn']:
                age = 'senior'
            
            if game.config['fun']['all_cats_are_newborn']:
                cat_sprite = str(cat.pelt.cat_sprites['newborn'])
            else:
                cat_sprite = str(cat.pelt.cat_sprites[age])
        pos_x = 0
        pos_y = 40
        i = 0
        if game.clan.your_cat.pelt.accessory:
            if game.clan.your_cat.pelt.accessory not in game.clan.your_cat.inventory:
                game.clan.your_cat.inventory.append(game.clan.your_cat.pelt.accessory)

        for acc in game.clan.your_cat.pelt.accessories:
            if acc not in game.clan.your_cat.inventory:
                game.clan.your_cat.inventory.append(acc)
        if game.clan.your_cat.inventory:
            for accessory in game.clan.your_cat.inventory:
                if accessory in cat.pelt.plant_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_herbs' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.wild_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_wild' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.collars:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['collars' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.flower_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_flower' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.plant2_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_plant2' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.snake_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_snake' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.smallAnimal_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_smallAnimal' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.deadInsect_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_deadInsect' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.aliveInsect_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_aliveInsect' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.fruit_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_fruit' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.crafted_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_crafted' + accessory + cat_sprite], manager=MANAGER)
                elif accessory in cat.pelt.tail2_accessories:
                    self.cat_list_buttons["cat" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), sprites.sprites['acc_tail2' + accessory + cat_sprite], manager=MANAGER)
                self.accessories_list.append(accessory)
                self.accessory_buttons[str(i)] = UIImageButton(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))), "", object_id="#blank_button")

                
                pos_x += 120
                if pos_x >= 1100:
                    pos_x = 0
                    pos_y += 120
                i += 1

    def get_valid_cats(self):
        valid_mentors = []

        for accessory in game.clan.your_cat.pelt.accessories:
            valid_mentors.append(accessory)
        
        return valid_mentors

    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150 / 1600 * screen_x, 720 / 1400 * screen_y))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
    

