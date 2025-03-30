import pygame
import pygame_gui
import random

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game
from scripts.game_structure.audio import sound_manager
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UITextBoxTweaked,
    UISurfaceImageButton,
)
from scripts.utility import get_text_box_theme, ui_scale_dimensions
from scripts.utility import ui_scale
from .Screens import Screens
from ..cat.history import History
from ..game_structure.screen_settings import MANAGER
from scripts.cat.skills import SkillPath
from ..ui.generate_button import ButtonStyles, get_button_dict
from ..ui.get_arrow import get_arrow
from scripts.game_structure import image_cache
from ..ui.generate_box import get_box, BoxStyles


class AttackScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        # UI ELEMENTS
        self.elements = {}
        self.containers = {}
        self.buttons = {}

        # LOCAL VARIABLES
        self.stage = "pre_fight"
        self.actions = []
        self.turns_taken = 0
        self.result = None
        self.taken_item = []
        self.rests = 0
        self.strategy = "attack"

    def screen_switches(self):
        """
        switches screens
        """
        super().screen_switches()
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.you = game.clan.your_cat

        if game.switches["ambush"]:
            self.stage = "fight"
            self.npc_turn()
            game.switches["ambush"] = False

        # TEXT CONTAINER
        self.containers["text"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((34, 34), (190, 420))),
            starting_height=1,
            manager=MANAGER,
        )
        # self.containers["text"] = pygame_gui.elements.UIScrollingContainer(
        #     ui_scale(pygame.Rect((34, 34), (190, 420))),
        #     object_id=("#text_box_26_horizcenter"),
        #     manager=MANAGER,
        #     allow_scroll_x=False
        #     )
        
        self.elements["text_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (190, 420))),
            get_box(
                BoxStyles.ROUNDED_BOX, (190, 420), sides=(True, True, True, True)
            ),
            container=self.containers["text"]
        )

        # ART CONTAINER
        self.containers["art"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((0, 34), (320, 420))),
            starting_height=1,
            manager=MANAGER,
            anchors={"centerx": "centerx"}
        )
        self.elements["art_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (320, 420))),
            get_box(BoxStyles.FRAME, (420, 420)),
            manager=MANAGER,
            container=self.containers["art"],
            anchors={"centerx": "centerx", "centery": "centery"}
        )
        if self.stage == "pre_fight":
            img = "gen_app_sunny"
        else:
            img = "gen_angry_cat_app"
        self.elements["art_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 100), (320, 320))),
            image_cache.load_image(f"resources/images/patrol_art/{img}.png").convert_alpha(),
            container=self.containers["art"],
            anchors={
                "centerx": "centerx"
                }
        )

        # BUTTON CONTAINER
        self.containers["buttons"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((575, 34), (190, 420))),
            starting_height=1,
            manager=MANAGER,
        )
        # self.elements["button_frame"] = pygame_gui.elements.UIImage(
        #     ui_scale(pygame.Rect((0, 0), (190, 420))),
        #     get_box(
        #         BoxStyles.FRAME, (190, 420), # sides=(True, True, True, True)
        #     ),
        #     container=self.containers["buttons"]
        # )
        width = 190
        if self.stage == "pre_fight":
            y_val = 80
            self.buttons["attack"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_val), (width, 30))),
                "attack",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (width, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"}
            )
            y_val += 50
            self.buttons["poison"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_val), (width, 30))),
                "poison",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (width, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"}
            )
            if "DEATHBERRY" in self.you.pelt.inventory.keys():
                self.buttons["poison"].enable()
            else:
                self.buttons["poison"].disable()
            y_val += 50
            self.buttons["leave"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_val), (width, 30))),
                "leave",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (width, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"}
            )
            y_val += 50
            self.buttons["help_button"] = UIImageButton(
                ui_scale(pygame.Rect((0, y_val), (34, 34))),
                "",
                object_id="#help_button",
                manager=MANAGER,
                tool_tip_text="This is the fight screen! You have several different options.\n\n" +
                "<b>Attack</b> will initiate a fight with the opponent.\n" +
                "<b>Poison</b> will allow you to attempt to poison the opponent's prey, but only if you have some poison on hand.\n" +
                "<b>Leave</b> is your last chance to leave the battle with no cost.",
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"}
            )
        elif self.stage == "fight":
            # TEXT
            compiled_string = ""
            count = 0
            for entry in reversed(self.actions):
                if count >= 6:
                    break
                if count == 0:
                    compiled_string += f"\n\n<b>{entry['text']}</b>"
                else:
                    compiled_string += f"\n\n{entry['text']}"
                count += 1

            self.elements["action_text"] = UITextBoxTweaked(
                compiled_string,
                ui_scale(pygame.Rect((0, 10), (160, 390))),
                object_id=("#text_box_26_horizcenter"),
                container=self.containers["text"],
                anchors={"centerx": "centerx"}
                )
            # BUTTONS
            y_val = 80
            self.buttons["swipe"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_val), (width, 30))),
                "swipe",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (width, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"},
                sound_id="hg_attack"
            )
            y_val += 50
            self.buttons["pin"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_val), (width, 30))),
                "pin",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (width, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"},
                sound_id="hg_attack"
            )
            y_val += 50
            self.buttons["rest"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_val), (width, 30))),
                "rest",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (width, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"}
            )
            if self.rests >= 3:
                self.buttons["rest"].disable()
            else:
                self.buttons["rest"].enable()
            y_val += 50
            self.buttons["hiss"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_val), (width, 30))),
                "hiss",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (width, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"}
            )
            y_val += 50
            self.buttons["run"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_val), (width, 30))),
                "run",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (width, 30)),
                object_id="@buttonstyles_rounded_rect",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"}
            )
            y_val += 50
            self.buttons["help_button"] = UIImageButton(
                ui_scale(pygame.Rect((0, y_val), (34, 34))),
                "",
                object_id="#help_button",
                manager=MANAGER,
                tool_tip_text="This is the fight screen! You have several different options.\n\n" +
                "<b>Swipe</b> will inflict damage on the opponent.\n" +
                "<b>Pin</b> will attempt to pin the opponent down, skipping their turn.\n" +
                "<b>Rest</b> will use your turn to recover some health. Three rests are allowed per fight.\n" + 
                "<b>Hiss</b> will startle your opponent, skipping their turn, if it succeeds. If it fails, your turn will be missed.\n" +
                "<b>Run</b> will let you escape the battle, at the cost of 10 energy and an item from your inventory.\n" +
                "Good luck!",
                container=self.containers["buttons"],
                anchors={"centerx": "centerx"}
            )
        else:
            if self.result == "flee":
                text = "You flee the fight."
                sound_manager.play("hg_attack_lose")
                if self.taken_item:
                    if self.taken_item[0] > 1:
                        item_name = self.taken_item[1].lower()
                        if item_name[-1] == "y":
                            item_name = item_name.replace(item_name[-1], "ies")
                        elif item_name[-1] == "h":
                            pass
                        else:
                            if item_name[-1] != "s":
                                item_name += "s"
                    else:
                        item_name = self.taken_item[1].lower()
                    text += f" {self.the_cat.name} takes {self.taken_item[0]} {item_name.replace('_', ' ')} from your stash."
                    self.taken_item = []
            elif self.result == "win":
                sound_manager.play("hg_attack_win")
                if self.strategy == "attack":
                    text = "<b>You won the fight!</b>"
                    if self.the_cat.pelt.inventory:
                        text += "\n\nYou have gained: "
                        text += ", ".join([(str(i[1]) + " " + i[0].lower()) for i in self.the_cat.pelt.inventory.items()])
                    History.add_murders(self.the_cat, self.you, True, "m_c killed this cat in a fight.")
                else:
                    text = f"<b>You successfully poison {self.the_cat.name}.</b>\n\n{self.the_cat.name} is alive, but very sick."
                    deathberry_num = random.randint(1, round(self.you.pelt.inventory["DEATHBERRY"]/2) + 1)
                    if deathberry_num == 1:
                        plural = "deathberry"
                    else:
                        plural = "deathberries"
                    text += f"\n\nYou have lost {deathberry_num} {plural}."
                    self.the_cat.get_injured("poisoned", inflicted_by=self.you.ID)
                    self.you.pelt.inventory["DEATHBERRY"] -= deathberry_num
                
            elif self.result == "loss":
                text = f"{self.the_cat.name} wins the fight.\n\n<b>You have died.</b>"
                sound_manager.play("hg_attack_lose")
                History.add_murders(self.you, self.the_cat, True, "m_c killed this cat in a fight.")
            else:
                text = "Mrow! What is this doing here?!"
            self.elements["action_text"] = pygame_gui.elements.UITextBox(
                text,
                ui_scale(pygame.Rect((0, 10), (170, 420))),
                object_id=("#text_box_26_horizcenter"),
                container=self.containers["text"],
                anchors={"centerx": "centerx"}
                )
        # buttons
            self.buttons["back"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, 0), (105, 30))),
                get_arrow(2) + " Back",
                get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
                object_id="@buttonstyles_squoval",
                manager=MANAGER,
                container=self.containers["buttons"],
                anchors={"centery": "centery", "centerx": "centerx"}
            )

        # STATS CONTAINER
        self.containers["stats"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((0, 470), (732, 190))),
            starting_height=1,
            manager=MANAGER,
            anchors={"centerx": "centerx"}
        )
        # frame
        self.elements["stats_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (732, 190))),
            get_box(BoxStyles.FRAME, (732, 190)),
            manager=MANAGER,
            container=self.containers["stats"],
            anchors={"centerx": "centerx", "centery": "centery"}
        )
        # stats
        # VICTIM STATS ---
        self.elements["victim_sprite"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((20, 20), (120, 120))),
                pygame.transform.scale(
                    self.the_cat.sprite, ui_scale_dimensions((120, 120))
                ),
                manager=MANAGER,
                container=self.containers["stats"],
            )
        self.elements["victim_name"] = pygame_gui.elements.UITextBox(
            str(self.the_cat.name),
            ui_scale(pygame.Rect((20, 20), (180, 40))),
            object_id=get_text_box_theme("#text_box_34_horizleft"),
            container=self.containers["stats"],
            anchors={"left_target": self.elements["victim_sprite"]}
        )
        info = (
            self.the_cat.personality.trait +
            "\n" +
            self.the_cat.skills.skill_string()
        )
        self.elements["victim_info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((20, 0), (180, 80))),
            object_id=get_text_box_theme("#text_box_26_horizleft"),
            container=self.containers["stats"],
            anchors={
                "top_target": self.elements["victim_name"],
                "left_target": self.elements["victim_sprite"]
                }
        )
        self.elements["victim_health_icon"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((20, 10), (22, 20))),
            image_cache.load_image("resources/images/heart_big.png").convert_alpha(),
            container=self.containers["stats"],
            anchors={
                "top_target": self.elements["victim_sprite"]
                }
        )

        x_val = 50
        for value in range(round(self.the_cat.stats.health / 5)):
            self.elements["victim_health_" + str(value)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_val, 10), (10, 20))),
                image_cache.load_image("resources/images/relation_bar.png").convert_alpha(),
                container=self.containers["stats"],
                anchors={
                    "top_target": self.elements["victim_sprite"]
                    })
            x_val += 11
        # ----------
        # YOU STATS ---
        self.elements["you_name"] = pygame_gui.elements.UITextBox(
            str(self.you.name),
            ui_scale(pygame.Rect((392, 20), (180, 40))),
            object_id=get_text_box_theme("#text_box_34_horizright"),
            container=self.containers["stats"]
        )
        info = (
            self.you.personality.trait +
            "\n" +
            self.you.skills.skill_string()
        )
        self.elements["you_info"] = pygame_gui.elements.UITextBox(
            info,
            ui_scale(pygame.Rect((392, 0), (180, 80))),
            object_id=get_text_box_theme("#text_box_26_horizright"),
            container=self.containers["stats"],
            anchors={
                "top_target": self.elements["you_name"]
                }
        )
        self.elements["you_sprite"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((20, 20), (120, 120))),
                pygame.transform.scale(
                    self.you.sprite, ui_scale_dimensions((120, 120))
                ),
                manager=MANAGER,
                container=self.containers["stats"],
                anchors={"left_target": self.elements["you_name"]}
            )
        self.elements["you_health_icon"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((689, 10), (22, 20))),
            image_cache.load_image("resources/images/heart_big.png").convert_alpha(),
            container=self.containers["stats"],
            anchors={
                "top_target": self.elements["you_info"]
                })

        x_val = 669
        for value in range(round(self.you.stats.health / 5)):
            self.elements["you_health_" + str(value)] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_val, 10), (10, 20))),
                image_cache.load_image("resources/images/relation_bar.png").convert_alpha(),
                container=self.containers["stats"],
                anchors={
                    "top_target": self.elements["you_info"]
                    })
            x_val -= 11
        # ----------

    def on_use(self):
        """
        on use
        """
        super().on_use()

    def handle_event(self, event):
        """
        input events
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if self.stage == "pre_fight":
                if event.ui_element == self.buttons["leave"]:
                    self.reset_variables()
                    self.change_screen("profile screen")
                elif event.ui_element == self.buttons["attack"]:
                    self.strategy = "attack"
                    self.stage = "fight"
                    attack = {
                            "action": "",
                            "turn": self.turns_taken,
                            "success": True,
                            "text": f"You prepare to attack {self.the_cat.name}."
                        }
                    self.actions.append(attack)
                    self.exit_screen()
                    self.screen_switches()
                elif event.ui_element == self.buttons["poison"]:
                    self.strategy = "poison"
                    self.stage = "fight"
                    attack = {
                            "action": "",
                            "turn": self.turns_taken,
                            "success": True,
                            "text": f"You slip some deathberries into {self.the_cat.name}'s food stash."
                        }
                    self.actions.append(attack)
                    self.npc_turn()
                    self.exit_screen()
                    self.screen_switches()
            elif self.stage == "fight":
                for action in ["swipe", "pin", "hiss", "rest", "run"]:
                    if event.ui_element == self.buttons[action]:
                        skip_success = self.get_action_result(action)

                        self.exit_screen()
                        self.screen_switches()

                        if not self.the_cat.dead and not skip_success:
                            self.npc_turn()
                            self.exit_screen()
                            self.screen_switches()
                        break
            else:
                if event.ui_element == self.buttons["back"]:
                    self.reset_variables()
                    self.change_screen("profile screen")
    
    def npc_turn(self):
        """
        npcs turn in the battle
        """

        if self.strategy == "poison":
            if random.randint(1,2) == 1:
                damage = 0
                self.stage = "post_fight"
                self.result = "win"
                return
            else:
                damage = random.randint(3, 13)
                self.stage = "fight"
                self.strategy = "attack"
                text = f"{self.the_cat.name} notices and attacks for {damage} damage!"
        else:
            damage = random.randint(3, 13)
            text = f"{self.the_cat.name} attacks for {damage} damage."
        self.you.stats.health -= damage
        attack = {
            "action": "",
            "turn": self.turns_taken,
            "success": True,
            "text": text
        }
        self.actions.append(attack)
        if self.you.stats.health <= 0:
            self.you.stats.health = 0
            self.you.die()
            self.result = "loss"
            self.stage = "post_fight"
    
    def swipe(self):
        """
        Determines damage and text for direct attacks (swipe + pin)
        """
        damage = 10
        text = ""
        if self.the_cat.sleeping:
            damage *= 2
            self.the_cat.sleeping = False
            text += f"You catch {self.the_cat.name} by surprise during a nap. "
        elif (self.the_cat.is_injured() or self.the_cat.is_ill()):
            damage *= 2

        divide = round(damage / 2)
        modifier = random.randint(-divide, divide)

        damage += modifier

        text += f"You SWIPE for {damage} damage."
        
        return damage, text

    def pin(self):
        damage = 6

        if random.randint(1,2) == 1:
            success = False
            text = "You attempt to PIN your opponent, but they're too strong."
        else:
            success = True
            text = "You pin your opponent to the ground."
        
        return damage, text, success


    def get_action_result(self, action):
        """
        Returns the result text for a player action
        """
        damage = 0
        text = ""
        skip_success = False
        if action == "swipe":
            damage, text = self.swipe()
        elif action == "pin":
            damage, text, skip_success = self.pin()
        elif action == "hiss":
            damage = 0
            text = "You hiss and startle your opponent."
            skip_success = True
        elif action == "rest":
            damage = 0
            recovered_health = random.randint(8,25)
            text = f"You REST and recover {recovered_health} health."
            self.rests += 1
            self.you.stats.health += recovered_health
            skip_success = True
        elif action == "run":
            damage = 0
            self.stage = "post_fight"
            text = "You flee the fight."
            self.result = "flee"
            self.you.stats.energy -= 10
            if self.you.stats.energy <= 0:
                self.you.stats.energy = 0
                self.you.sleeping = True

            if self.you.pelt.inventory:
                taken_item = random.choice(list(self.you.pelt.inventory.keys()))
                amount = random.randint(1, self.you.pelt.inventory[taken_item])
                self.you.pelt.inventory[taken_item] -= amount
                self.taken_item = [amount, taken_item]
                if self.you.pelt.inventory[taken_item] <= 0:
                    self.you.pelt.inventory.pop(taken_item)

                if taken_item in self.the_cat.pelt.inventory.keys():
                    self.the_cat.pelt.inventory[taken_item] += amount
                else:
                    self.the_cat.pelt.inventory[taken_item] = amount
        
        attack = {
            "action": action,
            "turn": self.turns_taken,
            "success": True,
            "text": text
        }
        self.actions.append(attack)
        self.turns_taken += 1

        if action != "run":
            self.the_cat.stats.health -= damage
            if self.the_cat.stats.health <= 0:
                self.the_cat.stats.health = 0
                self.the_cat.die()
                self.result = "win"
                self.stage = "post_fight"
        
        return skip_success
    
    def reset_variables(self):
        self.stage = "pre_fight"
        self.actions = []
        self.turns_taken = 0
        self.result = None
        self.rests = 0
        self.strategy = "attack"

    def exit_screen(self):
        """
        kills everything when exiting the screen
        """

        for ele in self.elements:
            self.elements[ele].kill()
        self.elements = {}

        for ele in self.containers:
            self.containers[ele].kill()
        self.containers = {}

        for ele in self.buttons:
            self.buttons[ele].kill()
        self.buttons = {}