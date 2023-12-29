import os
from random import choice, randint, choices

import pygame

from ..cat.history import History
from ..housekeeping.datadir import get_save_dir
from ..game_structure.windows import ChangeCatName, SpecifyCatGender, KillCat, SaveAsImage

import ujson

from scripts.utility import event_text_adjust, scale, ACC_DISPLAY, process_text, chunks

from .Screens import Screens

from scripts.utility import get_text_box_theme, scale_dimentions, generate_sprite, shorten_text_to_fit, get_cluster, get_alive_kits, get_alive_cats, get_alive_apps, get_alive_meds, get_alive_mediators, get_alive_queens, get_alive_elders, get_alive_warriors, get_med_cats
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.game_structure import image_cache
import pygame_gui
from re import sub
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER, screen
from scripts.cat.names import names, Name
from scripts.clan_resources.freshkill import FRESHKILL_ACTIVE

class TalkScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.resource_dir = "resources/dicts/lifegen_talk/"
        self.texts = ""
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]

        self.scroll_container = None
        self.life_text = None
        self.header = None
        self.the_cat = None
        self.text_index = 0
        self.frame_index = 0
        self.typing_delay = 20
        self.next_frame_time = pygame.time.get_ticks() + self.typing_delay
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.text = None
        self.profile_elements = {}
        self.talk_box_img = None


    def screen_switches(self):
        self.update_camp_bg()
        self.hide_menu_buttons()
        self.text_index = 0
        self.frame_index = 0
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.profile_elements = {}
        self.clan_name_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((450, 875), (380, 70))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/clan_name_bg.png").convert_alpha(),
                (500, 870)),
            manager=MANAGER)
        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(str(self.the_cat.name),
                                                                          scale(pygame.Rect((500, 870), (-1, 80))),
                                                                          object_id="#text_box_34_horizcenter_light",
                                                                          manager=MANAGER)
        self.texts = self.get_possible_text(self.the_cat)
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        self.talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()

        self.talk_box = pygame_gui.elements.UIImage(
                scale(pygame.Rect((178, 942), (1248, 302))),
                self.talk_box_img
            )
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                        object_id="#back_button", manager=MANAGER)
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((500, 970), (900, 300))))
        self.text = pygame_gui.elements.UITextBox("", 
                                                  scale(pygame.Rect((0, 0), (900, -100))),
                                                  object_id="#text_box_30_horizleft",
                                                  container=self.scroll_container, manager=MANAGER)
        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((70, 900), (400, 400))),

                                                                         pygame.transform.scale(
                                                                             generate_sprite(self.the_cat),
                                                                             (400, 400)), manager=MANAGER)
        self.paw = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1370, 1180), (30, 30))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
        self.paw.visible = False


    def exit_screen(self):
        self.text.kill()
        del self.text
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button
        self.profile_elements["cat_image"].kill()
        self.profile_elements["cat_name"].kill()
        del self.profile_elements
        self.clan_name_bg.kill()
        del self.clan_name_bg
        self.talk_box.kill()
        del self.talk_box
        self.paw.kill()
        del self.paw

    def update_camp_bg(self):
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        camp_bg_base_dir = 'resources/images/camp_bg/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        camp_nr = game.clan.camp_bg

        if camp_nr is None:
            camp_nr = 'camp1'
            game.clan.camp_bg = camp_nr

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome
        if biome not in available_biome:
            biome = available_biome[0]
            game.clan.biome = biome
        biome = biome.lower()

        all_backgrounds = []
        for leaf in leaves:
            platform_dir = f'{camp_bg_base_dir}/{biome}/{leaf}_{camp_nr}_{light_dark}.png'
            all_backgrounds.append(platform_dir)

        self.newleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[0]).convert(), (screen_x, screen_y))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (screen_x, screen_y))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (screen_x, screen_y))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (screen_x, screen_y))
    
    def on_use(self):
        if game.clan.clan_settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_bg, (0, 0))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_bg, (0, 0))    
        now = pygame.time.get_ticks()
        if self.text_index < len(self.text_frames):
            if now >= self.next_frame_time and self.frame_index < len(self.text_frames[self.text_index]) - 1:
                self.frame_index += 1
                self.next_frame_time = now + self.typing_delay

        if self.text_index == len(self.text_frames) - 1:
            if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                self.paw.visible = True
        # Always render the current frame
        self.text.html_text = self.text_frames[self.text_index][self.frame_index]
        self.text.rebuild()
        self.clock.tick(60)

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('profile screen')
        elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1  # Go to the last frame
        return
    
    def get_cluster_list(self):
        return ["assertive", "brooding", "cool", "upstanding", "introspective", "neurotic", "silly", "stable", "sweet", "unabashed", "unlawful"]
    
    def get_cluster_list_you(self):
        return ["you_assertive", "you_brooding", "you_cool", "you_upstanding", "you_introspective", "you_neurotic", "you_silly", "you_stable", "you_sweet", "you_unabashed", "you_unlawful"]
    
    
    def relationship_check(self, talk, cat_relationship):
        relationship_conditions = {
            'hate': 50,
            'romantic_like': 30,
            'platonic_like': 30,
            'jealousy': 30,
            'dislike': 30,
            'comfort': 30,
            'respect': 30,
            'trust': 30
        }
        
        for key, value in relationship_conditions.items():
            if key in talk[0] and cat_relationship < value:
                return True
        return False
    
    def handle_random_cat(self, cat):
        random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
        counter = 0
        while random_cat.outside or random_cat.dead or random_cat.ID in [game.clan.your_cat.ID, cat.ID]:
            counter += 1
            if counter == 15:
                break
            random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
        return random_cat
        
    def get_possible_text(self, cat):
        text = ""
        texts_list = {}
        you = game.clan.your_cat

        resource_dir = "resources/dicts/lifegen_talk/"
        possible_texts = {}
        with open(f"{resource_dir}{cat.status}.json", 'r') as read_file:
            possible_texts = ujson.loads(read_file.read())
            
        if cat.status not in ['kitten', "newborn"] and you.status not in ['kitten', 'newborn']:
            with open(f"{resource_dir}general_no_kit.json", 'r') as read_file:
                possible_texts2 = ujson.loads(read_file.read())
                possible_texts.update(possible_texts2)
        
        if cat.status not in ['kitten', "newborn"] and you.status in ['kitten', 'newborn']:
            with open(f"{resource_dir}general_you_kit.json", 'r') as read_file:
                possible_texts3 = ujson.loads(read_file.read())
                possible_texts.update(possible_texts3)

        if cat.status not in ['kitten', 'newborn'] and you.status not in ['kitten', 'newborn']:
            with open(f"{resource_dir}crush.json", 'r') as read_file:
                possible_texts3 = ujson.loads(read_file.read())
                possible_texts.update(possible_texts3)
        
        cluster1, cluster2 = get_cluster(cat.personality.trait)
        cluster3, cluster4 = get_cluster(you.personality.trait)
        
        their_trait_list = ['troublesome', 'fierce', 'bold', 'daring', 'confident', 'adventurous', 'arrogant', 'competitive', 'rebellious', 'bloodthirsty', 'cold', 'strict', 'vengeful', 'grumpy', 'charismatic', 'sneaky', 'cunning', 'arrogant', 'righteous', 'ambitious', 'strict', 'competitive', 'responsible', 'lonesome', 'righteous', 'calm', 'gloomy', 'wise', 'thoughtful', 'nervous', 'insecure', 'lonesome', 'troublesome', 'childish', 'playful', 'strange', 'loyal', 'responsible', 'wise', 'faithful', 'compassionate', 'faithful', 'loving', 'oblivious', 'sincere', 'childish', 'confident', 'bold', 'shameless', 'strange', 'oblivious', 'flamboyant', 'troublesome', 'bloodthirsty', 'sneaky', 'rebellious']
        you_trait_list = ['you_troublesome', 'you_fierce', 'you_bold', 'you_daring', 'you_confident', 'you_adventurous', 'you_arrogant', 'you_competitive', 'you_rebellious', 'you_bloodthirsty', 'you_cold', 'you_strict', 'you_vengeful', 'you_grumpy', 'you_charismatic', 'you_sneaky', 'you_cunning', 'you_arrogant', 'you_righteous', 'you_ambitious', 'you_strict', 'you_competitive', 'you_responsible', 'you_lonesome', 'you_righteous', 'you_calm', 'you_gloomy', 'you_wise', 'you_thoughtful', 'you_nervous', 'you_insecure', 'you_lonesome', 'you_troublesome', 'you_childish', 'you_playful', 'you_strange', 'you_loyal', 'you_responsible', 'you_wise', 'you_faithful', 'you_compassionate', 'you_faithful', 'you_loving', 'you_oblivious', 'you_sincere', 'you_childish', 'you_confident', 'you_bold', 'you_shameless', 'you_strange', 'you_oblivious', 'you_flamboyant', 'you_troublesome', 'you_bloodthirsty', 'you_sneaky', 'you_rebellious']
        you_backstory_list = [
            "you_clanfounder",
            "you_clanborn",
            "you_outsiderroots",
            "you_half-Clan",
            "you_formerlyloner",
            "you_formerlyrogue",
            "you_formerlykittypet",
            "you_formerlyoutsider",
            "you_originallyanotherclan",
            "you_orphaned",
            "you_abandoned"
        ]
        they_backstory_list = ["they_clanfounder",
            "they_clanborn",
            "they_outsiderroots",
            "they_half-Clan",
            "they_formerlyloner",
            "they_formerlyrogue",
            "they_formerlykittypet",
            "they_formerlyoutsider",
            "they_originallyanotherclan",
            "they_orphaned",
            "they_abandoned"
        ]
        skill_list = ['teacher', 'hunter', 'fighter', 'runner', 'climber', 'swimmer', 'speaker', 'mediator1', 'clever', 'insightful', 'sense', 'kit', 'story', 'lore', 'camp', 'healer', 'star', 'omen', 'dream', 'clairvoyant', 'prophet', 'ghost', 'explorer', 'tracker', 'artistan', 'guardian', 'tunneler', 'navigator', 'song', 'grace', 'clean', 'innovator', 'comforter', 'matchmaker', 'thinker', 'cooperative', 'scholar', 'time', 'treasure', 'fisher', 'language', 'sleeper']
        you_skill_list = ['you_teacher', 'you_hunter', 'you_fighter', 'you_runner', 'you_climber', 'you_swimmer', 'you_speaker', 'you_mediator1', 'you_clever', 'you_insightful', 'you_sense', 'you_kit', 'you_story', 'you_lore', 'you_camp', 'you_healer', 'you_star', 'you_omen', 'you_dream', 'you_clairvoyant', 'you_prophet', 'you_ghost', 'you_explorer', 'you_tracker', 'you_artistan', 'you_guardian', 'you_tunneler', 'you_navigator', 'you_song', 'you_grace', 'you_clean', 'you_innovator', 'you_comforter', 'you_matchmaker', 'you_thinker', 'you_cooperative', 'you_scholar', 'you_time', 'you_treasure', 'you_fisher', 'you_language', 'you_sleeper']
        for talk_key, talk in possible_texts.items():
            tags = talk[0]
            for i in range(len(tags)):
                tags[i] = tags[i].lower()
                
            if "insult" in tags:
                continue

            if you.moons == 0 and "newborn" not in tags:
                continue

            # Status tags
            if you.status not in tags and "any" not in tags and "young elder" not in tags and "no_kit" not in tags and "newborn" not in tags:
                continue
            elif "young elder" in tags and cat.status == 'elder' and cat.moons >= 100:
                continue
            elif "no_kit" in tags and you.status in ['kitten', 'newborn']:
                continue
            elif "newborn" in tags and you.moons != 0:
                continue

            if "they_adult" in tags and cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"]:
                continue
            if "they_app" in tags and cat.status not in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"]:
                continue
            
            if "they_grieving" not in tags and "grief stricken" in cat.illnesses:
                continue
            if "they_grieving" in tags and "grief stricken" not in cat.illnesses:
                continue
            
            # Cluster tags
            if any(i in self.get_cluster_list() for i in tags):
                if cluster1 not in tags and cluster2 not in tags:
                    continue
            if any(i in self.get_cluster_list_you() for i in tags):
                if ("you_"+cluster3) not in tags and ("you_"+cluster4) not in tags:
                    continue
            
            # Trait tags
            if any(i in you_trait_list for i in tags):
                ts = you_trait_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                if you.personality.trait not in ts:
                    continue
            if any(i in their_trait_list for i in tags):
                if cat.personality.trait not in tags:
                    continue
                
            # Backstory tags
            if any(i in you_backstory_list for i in tags):
                ts = you_backstory_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                if you.backstory not in ts:
                    continue
            if any(i in they_backstory_list for i in tags):
                ts = they_backstory_list
                for j in range(len(ts)):
                    ts[j] = ts[j][4:]
                if cat.backstory not in ts:
                    continue
                
            # Skill tags
            if any(i in you_skill_list for i in tags):
                ts = you_skill_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                    ts[j] = ''.join([q for q in ts[j] if not q.isdigit()])
                if (you.skills.primary.path not in ts) or (you.skills.secondary.path not in ts):
                    continue
            if any(i in skill_list for i in tags):
                ts = skill_list
                for j in range(len(ts)):
                    ts[j] = ''.join([q for q in ts[j] if not q.isdigit()])
                if (cat.skills.primary.path not in ts) or (cat.skills.secondary.path not in ts):
                    continue
                
            # Season tags
            if ('leafbare' in talk[0] and game.clan.current_season != 'Leaf-bare') or ('newleaf' in talk[0] and game.clan.current_season != 'Newleaf') or ('leaffall' in talk[0] and game.clan.current_season != 'Leaf-fall') or ('greenleaf' in talk[0] and game.clan.current_season != 'Greenleaf'):
                continue
            
            # Biome tags
            if any(i in ['beach', 'forest', 'plains', 'mountainous', 'wetlands', 'desert'] for i in talk[0]):
                if game.clan.biome.lower() not in talk[0]:
                    continue
                
            # Injuries, grieving and illnesses tags
            
            if "you_pregnant" in tags and "pregnant" not in you.injuries:
                continue
            if "they_pregnant" in tags and "pregnant" not in cat.injuries:
                continue
            
            if "grief stricken" not in you.illnesses and "you_grieving" in tags:
                continue
                
            if "starving" not in you.illnesses and "you_starving" in tags:
                continue
            if "starving" not in cat.illnesses and "they_starving" in tags:
                continue
            
            if any(i in ["you_ill", "you_injured"] for i in tags):
                ill_injured = False

                if you.is_ill() and "you_ill" in tags and "grief stricken" not in you.illnesses:
                    for illness in you.illnesses:
                        if you.illnesses[illness]['severity'] != 'minor':
                            ill_injured = True
                if you.is_injured() and "you_injured" in tags and "pregnant" not in you.injuries and "recovering from birth" not in you.injuries and "sprain" not in you.injuries:
                    for injury in you.injuries:
                        if you.injuries[injury]['severity'] != 'minor':
                            ill_injured = True            
                if not ill_injured:
                    continue 
            
            if any(i in ["they_ill", "they_injured"] for i in tags):
                ill_injured = False
                
                if cat.is_ill() and "they_ill" in tags and "grief stricken" not in cat.illnesses:
                    for illness in cat.illnesses:
                        if cat.illnesses[illness]['severity'] != 'minor':
                            ill_injured = True
                if cat.is_injured() and "they_injured" in tags and "pregnant" not in cat.injuries and "recovering from birth" not in cat.injuries and "sprain" not in cat.injuries:
                    for injury in cat.injuries:
                        if cat.injuries[injury]['severity'] != 'minor':
                            ill_injured = True

                if not ill_injured:
                    continue 
            
            # Relationships
            # Family tags:
            if any(i in ["from_your_parent", "from_adopted_parent", "adopted_parent", "half sibling", "littermate", "siblings_mate", "cousin", "adopted_sibling", "parents_siblings", "from_mentor", "from_your_kit", "from_your_apprentice", "from_mate", "from_parent", "adopted_parent", "from_kit", "sibling", "from_adopted_kit"] for i in tags):
                
                fam = False
                if "from_mentor" in tags:
                    if you.mentor == cat.ID:
                        fam = True
                if "from_your_apprentice" in tags:
                    if cat.mentor == you.ID:
                        fam = True
                if "from_mate" in tags:
                    if cat.ID in you.mate:
                        fam = True   
                if "from_parent" in tags or "from_your_parent" in tags:
                    if you.parent1:
                        if you.parent1 == cat.ID:
                            fam = True
                    if you.parent2:
                        if you.parent2 == cat.ID:
                            fam = True
                if "adopted_parent" in tags or "from adopted_parent" in tags or "from_adopted_parent" in tags:
                    if cat.ID in you.inheritance.get_no_blood_parents():
                        fam = True
                if "from_kit" in tags or "from_your_kit" in tags:
                    if cat.ID in you.inheritance.get_blood_kits():
                        fam = True
                if "from_adopted_kit" in tags:
                    if cat.ID in you.inheritance.get_not_blood_kits():
                        fam = True
                if "littermate" in tags:
                    if cat.ID in you.inheritance.get_siblings() and cat.moons == you.moons:
                        fam = True
                if "sibling" in tags:
                    if cat.ID in you.inheritance.get_siblings():
                        fam = True
                if "half sibling" in tags:
                    c_p1 = cat.parent1
                    if not c_p1:
                        c_p1 = "no_parent1_cat"
                    c_p2 = cat.parent2
                    if not c_p2:
                        c_p2 = "no_parent2_cat"
                    y_p1 = you.parent1
                    if not y_p1:
                        y_p1 = "no_parent1_you"
                    y_p2 = you.parent2
                    if not y_p2:
                        y_p2 = "no_parent2_you"
                    if ((c_p1 == y_p1 or c_p1 == y_p2) or (c_p2 == y_p1 or c_p2 == y_p2)) and not (c_p1 == y_p1 and c_p2 == y_p2) and not (c_p2 == y_p1 and c_p1 == y_p2) and not (c_p1 == y_p2 and c_p2 == y_p1):
                        fam = True
                if "adopted_sibling" in tags:
                    if cat.ID in you.inheritance.get_no_blood_siblings():
                        fam = True
                if "parents_siblings" in tags:
                    if cat.ID in you.inheritance.get_parents_siblings():
                        fam = True
                if "cousin" in tags:
                    if cat.ID in you.inheritance.get_cousins():
                        fam = True
                if "siblings_mate" in tags:
                    if cat.ID in you.inheritance.get_siblings_mates():
                        fam = True
                if not fam:
                    continue
                

            if "non-related" in tags:
                if cat.ID in you.inheritance.all_inheritances:
                    continue
                
            # If you have murdered someone and have been revealed
            if "murder" in talk[0]:
                if game.clan.your_cat.revealed:
                    if game.clan.your_cat.history:
                        if "is_murderer" in game.clan.your_cat.history.murder:
                            if len(game.clan.your_cat.history.murder["is_murderer"]) == 0:
                                continue
                            if 'accomplices' in game.switches:
                                if cat.ID in game.switches['accomplices']:
                                    continue
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
            
            if "war" in tags:
                if game.clan.war.get("at_war", False):
                    continue
                    
            if "non-mates" in tags:
                if you.ID in cat.mate:
                    continue

            if "they_older" in tags:
                if you.age != cat.age and cat.moons < you.moons:
                    continue
            
            if "they_sameage" in tags:
                if you.age != cat.age:
                    continue
            
            if "they_younger" in tags:
                if you.age != cat.age and cat.moons > you.moons:
                    continue
            
            # Relationship conditions
            if you.ID in cat.relationships:
                if cat.relationships[you.ID].dislike < 30 and 'hate' in tags:
                    continue
                if cat.relationships[you.ID].romantic_love < 20 and 'romantic_like' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 20 and 'platonic_like' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 50 and 'platonic_love' in tags:
                    continue
                if cat.relationships[you.ID].jealousy < 5 and 'jealousy' in tags:
                    continue
                if cat.relationships[you.ID].dislike < 20 and 'dislike' in tags:
                    continue
                if cat.relationships[you.ID].comfortable < 5 and 'comfort' in tags:
                    continue
                if cat.relationships[you.ID].admiration < 5 and 'respect' in tags:
                    continue      
                if cat.relationships[you.ID].trust < 5 and 'trust' in tags:
                    continue
                if (cat.relationships[you.ID].platonic_like > 10 or cat.relationships[you.ID].dislike > 10) and "neutral" in tags:
                    continue
            else:
                if any(i in ["hate","romantic_like","platonic_like","jealousy","dislike","comfort","respect","trust"] for i in tags):
                    continue

            texts_list[talk_key] = talk
        
        if not texts_list:
            resource_dir = "resources/dicts/lifegen_talk/"
            possible_texts = None
            with open(f"{resource_dir}general.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())
                clusters_1 = f"{cluster1} "
                if cluster2:
                    clusters_1 += f"and {cluster2}"
                clusters_2 = f"{cluster3} "
                if cluster4:
                    clusters_2 += f"and {cluster4}"
                try:
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("c_1", clusters_1)
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("c_2", clusters_2)
                    if game.clan.your_cat.moons == 0:
                        possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("r_1", "newborn")
                    else:
                        possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("r_1", game.clan.your_cat.status)
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("r_2", cat.status)
                except Exception as e:
                    print(e)
            texts_list['general'] = possible_texts['general']
    
        max_retries = 30
        counter = 0
        if len(game.clan.talks) > 50:
            game.clan.talks.clear()
        
        weights = []
        for item in texts_list.values():
            tags = item[0]
            weights.append(len(tags))

        while counter < max_retries:
            # Select a key randomly, weighted by the number of tags
            # text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
            text_chosen_key = choice(list(texts_list.keys()))
            text = texts_list[text_chosen_key][1]
            new_text = self.get_adjusted_txt(text, cat)

            if text_chosen_key not in game.clan.talks and new_text:
                game.clan.talks.append(text_chosen_key)
                return new_text

            counter += 1

        text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
        text = texts_list[text_chosen_key][1]
        new_text = self.get_adjusted_txt(text, cat)
        counter = 0
        while not new_text:
            text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
            text = texts_list[text_chosen_key][1]
            new_text = self.get_adjusted_txt(text, cat)
            counter +=1
            if counter == 30:
                possible_texts = None
                with open(f"{resource_dir}general.json", 'r') as read_file:
                    possible_texts = ujson.loads(read_file.read())
                    clusters_1 = f"{cluster1} "
                    if cluster2:
                        clusters_1 += f"and {cluster2}"
                    clusters_2 = f"{cluster3} "
                    if cluster4:
                        clusters_2 += f"and {cluster4}"
                    try:
                        possible_texts['general'][1][0].replace("c_1", clusters_1)
                        possible_texts['general'][1][0].replace("c_2", clusters_2)
                        possible_texts['general'][1][0].replace("r_1", game.clan.your_cat.status)
                        possible_texts['general'][1][0].replace("r_2", cat.status)
                    except Exception as e:
                        print(e)
                
                return possible_texts['general'][1]
        return new_text

    def get_adjusted_txt(self, text, cat):
        you = game.clan.your_cat
       
        text = [t1.replace("c_n", game.clan.name) for t1 in text]
        text = [t1.replace("y_c", str(you.name)) for t1 in text]
        text = [t1.replace("t_c", str(cat.name)) for t1 in text]
        
        for i in range(len(text)):
            text[i] = self.adjust_txt(text[i], cat)
            if text[i] == "":
                return ""

        r_c_found = False
        for i in range(len(text)):
            if "r_c" in text[i]:
                r_c_found = True
        if r_c_found:
            alive_cats = self.get_living_cats()
            alive_cat = choice(alive_cats)
            while alive_cat.ID == game.clan.your_cat.ID or alive_cat.ID == cat.ID:
                alive_cat = choice(alive_cats)
            text = [t1.replace("r_c", str(alive_cat.name)) for t1 in text]

        if "grief stricken" in cat.illnesses:
            try:
                dead_cat = Cat.all_cats.get(cat.illnesses['grief stricken'].get("grief_cat"))
                text = [t1.replace("d_c", str(dead_cat.name)) for t1 in text]  
            except:
                dead_cat = str(Cat.all_cats.get(game.clan.starclan_cats[-1]).name)
                text = [t1.replace("d_c", dead_cat) for t1 in text]
        elif "grief stricken" in you.illnesses:
            try:
                dead_cat = Cat.all_cats.get(you.illnesses['grief stricken'].get("grief_cat"))
                text = [t1.replace("d_c", str(dead_cat.name)) for t1 in text]  
            except:
                dead_cat = str(Cat.all_cats.get(game.clan.starclan_cats[-1]).name)
                text = [t1.replace("d_c", dead_cat) for t1 in text]
        d_c_found = False
        for t in text:
            if "d_c" in t:
                d_c_found = True
        if d_c_found:
            dead_cat = str(Cat.all_cats.get(game.clan.starclan_cats[-1]).name)
            text = [t1.replace("d_c", dead_cat) for t1 in text]
        return text

    def get_living_cats(self):
        living_cats = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and not the_cat.outside:
                living_cats.append(the_cat)
        return living_cats
        
    def adjust_txt(self, text, cat):
        try:
            if "your_crush" in text:
                if len(game.clan.your_cat.mate) > 0 or game.clan.your_cat.no_mates:
                    return ""
                crush = None
                for c in self.get_living_cats():
                    if c.ID == game.clan.your_cat.ID or c.ID == cat.ID:
                        continue
                    relations = game.clan.your_cat.relationships.get(c.ID)
                    if not relations:
                        continue
                    if relations.romantic_love > 10:
                        crush = c
                        break
                if crush:
                    text = text.replace("your_crush", str(crush.name))
                else:
                    return ""
            if "their_crush" in text:
                if len(cat.mate) > 0 or cat.no_mates:
                    return ""
                crush = None
                for c in self.get_living_cats():
                    if c.ID == game.clan.your_cat.ID or c.ID == cat.ID:
                        continue
                    relations = cat.relationships.get(c.ID)
                    if not relations:
                        continue
                    if relations.romantic_love > 10:
                        crush = c
                        break
                if crush:
                    text = text.replace("their_crush", str(crush.name))
                else:
                    return ""
            
            
            if "r_c1" in text:
                alive_apps = self.get_living_cats()
                if len(alive_apps) <= 2:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    alive_app = choice(alive_apps)
                alive_apps.remove(alive_app)
                text = text.replace("r_c1", str(alive_app.name))
                if "r_c2" in text:
                    alive_app2 = choice(alive_apps)
                    while alive_app2.ID == game.clan.your_cat.ID or alive_app2.ID == cat.ID:
                        alive_app2 = choice(alive_apps)
                    text = text.replace("r_c2", str(alive_app2.name))
                if "r_c3" in text:
                    alive_app3 = choice(alive_apps)
                    while alive_app3.ID == game.clan.your_cat.ID or alive_app3.ID == cat.ID:
                        alive_app3 = choice(alive_apps)
                    text = text.replace("r_c3", str(alive_app3.name))
            if "r_k" in text:
                alive_kits = get_alive_kits(Cat)
                if len(alive_kits) <= 1:
                    return ""
                alive_kit = choice(alive_kits)
                while alive_kit.ID == game.clan.your_cat.ID or alive_kit.ID == cat.ID:
                    alive_kit = choice(alive_kits)
                text = text.replace("r_k", str(alive_kit.name))
            if "r_a" in text:
                alive_apps = get_alive_apps(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    alive_app = choice(alive_apps)
                text = text.replace("r_a", str(alive_app.name))
            if "r_w" in text:
                alive_apps = get_alive_warriors(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    alive_app = choice(alive_apps)
                text = text.replace("r_w", str(alive_app.name))
            if "r_m" in text:
                alive_apps = get_alive_meds(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    alive_app = choice(alive_apps)
                text = text.replace("r_m", str(alive_app.name))
            if "r_d" in text:
                alive_apps = get_alive_mediators(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    alive_app = choice(alive_apps)
                text = text.replace("r_d", str(alive_app.name))
            if "r_q" in text:
                alive_apps = get_alive_queens(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    alive_app = choice(alive_apps)
                text = text.replace("r_q", str(alive_app.name))
            if "r_e" in text:
                alive_apps = get_alive_elders(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    alive_app = choice(alive_apps)
                text = text.replace("r_e", str(alive_app.name))
            if "r_s" in text:
                alive_apps = get_alive_cats(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.is_ill():
                    alive_app = choice(alive_apps)
                text = text.replace("r_s", str(alive_app.name))
            if "r_i" in text:
                alive_apps = get_alive_cats(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.is_injured():
                    alive_app = choice(alive_apps)
                text = text.replace("r_i", str(alive_app.name))
            if "l_n" in text:
                if game.clan.leader is None:
                    return ""
                if game.clan.leader.dead or game.clan.leader.outside or game.clan.leader.ID == game.clan.your_cat.ID or game.clan.leader.ID == cat.ID:
                    return ""
                text = text.replace("l_n", str(game.clan.leader.name))
            if "d_n" in text:
                if game.clan.deputy is None:
                    return ""
                if game.clan.deputy.dead or game.clan.deputy.outside or game.clan.deputy.ID == game.clan.your_cat.ID or game.clan.deputy.ID == cat.ID:
                    return ""
                text = text.replace("d_n", str(game.clan.deputy.name))
            if "y_s" in text:
                if len(game.clan.your_cat.inheritance.get_siblings()) == 0:
                    return ""
                sibling = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_siblings()))
                if sibling.outside or sibling.dead or sibling.ID == cat.ID:
                    return ""
                text = text.replace("y_s", str(sibling.name))
            if "t_s" in text:
                if len(cat.inheritance.get_siblings()) == 0:
                    return ""
                sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
                if sibling.outside or sibling.dead or sibling.ID == game.clan.your_cat.ID:
                    return ""
                text = text.replace("t_s", str(sibling.name))
            if "y_a" in text:
                if len(game.clan.your_cat.apprentice) == 0:
                    return ""
                text = text.replace("y_a", str(Cat.fetch_cat(choice(game.clan.your_cat.apprentice)).name))
            if "y_l" in text:
                if len(game.clan.your_cat.inheritance.get_siblings()) == 0:
                    return ""
                sibling = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_siblings()))
                counter = 0
                while sibling.moons != game.clan.your_cat.moons or sibling.outside or sibling.dead:
                    sibling = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_siblings()))
                    counter+=1
                    if counter == 15:
                        return ""
                text = text.replace("y_l", str(sibling.name))
            if "t_l" in text:
                if len(cat.inheritance.get_siblings()) == 0:
                    return ""
                sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
                counter = 0
                while sibling.moons != cat.moons or sibling.outside or sibling.dead:
                    sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
                    counter+=1
                    if counter == 15:
                        return ""
                text = text.replace("t_l", str(sibling.name))
            if "y_p" in text:
                if len(game.clan.your_cat.inheritance.get_parents()) == 0:
                    return ""
                parent = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_parents()))
                if parent.outside or parent.dead or parent.ID==cat.ID:
                    return ""
                text = text.replace("y_p", str(parent.name))
            if "t_p" in text:
                if len(cat.inheritance.get_parents()) == 0:
                    return ""
                parent = Cat.fetch_cat(choice(cat.inheritance.get_parents()))
                if parent.outside or parent.dead or parent.ID==game.clan.your_cat.ID:
                    return ""
                text = text.replace("t_p", str(parent.name))
            if "y_m" in text:
                if game.clan.your_cat.mate is None or len(game.clan.your_cat.mate) == 0 or cat.ID in game.clan.your_cat.mate:
                    return ""
                text = text.replace("y_m", str(Cat.fetch_cat(choice(game.clan.your_cat.mate)).name))
            if "t_mn" in text:
                if cat.mentor is None:
                    return ""
                text = text.replace("t_mn", str(Cat.fetch_cat(cat.mentor).name))
            if "tm_n" in text:
                if cat.mentor is None:
                    return ""
                text = text.replace("tm_n", str(Cat.fetch_cat(cat.mentor).name))
            if "m_n" in text:
                if game.clan.your_cat.mentor is None:
                    return ""
                text = text.replace("m_n", str(Cat.fetch_cat(game.clan.your_cat.mentor).name))
            if "o_c" in text:
                other_clan = choice(game.clan.all_clans)
                if not other_clan:
                    return ""
                text = text.replace("o_c", str(other_clan.name))
            if "t_m" in text:
                if cat.mate is None or len(cat.mate) == 0 or cat.ID in game.clan.your_cat.mate:
                    return ""
                text = text.replace("t_m", str(Cat.fetch_cat(choice(cat.mate)).name))
            if "t_k" in text:
                if cat.inheritance.get_children() is None or len(cat.inheritance.get_children()) == 0:
                    return ""
                text = text.replace("t_k", str(choice(cat.inheritance.get_children()).name))
            if "y_k" in text:
                if game.clan.your_cat.inheritance.get_children() is None or len(game.clan.your_cat.inheritance.get_children()) == 0:
                    return ""
                text = text.replace("y_k", str(choice(game.clan.your_cat.inheritance.get_children()).name))
            if "n_r1" in text:
                if "n_r2" not in text:
                    return ""
                random_cat1 = choice(self.get_living_cats())
                random_cat2 = choice(self.get_living_cats())
                counter = 0
                while not random_cat1.is_potential_mate(random_cat2) or random_cat2.age != random_cat1.age:
                    random_cat1 = choice(self.get_living_cats())
                    random_cat2 = choice(self.get_living_cats())
                    counter +=1
                    if counter > 40:
                        return ""
                text = text.replace("n_r1", str(random_cat1.name))
                text = text.replace("n_r2", str(random_cat2.name))
            if "_" in text:
                print(f"_ found in {text}")
                return ""
             
        except Exception as e:
            print(e)
            print("ERROR: could not replace abbrv.")
            return text


        return text