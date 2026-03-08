import random

from scripts.game_structure import game, constants
from scripts.special_dates import get_special_date
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure.localization import load_lang_resource
from scripts.cat.enums import CatRank, CatAge
from scripts.cat.cats import Cat

from scripts.events_module.filter_random_cats import choose_random_cats

# pylint: disable=consider-using-dict-items

class Dialogue():
    def __init__(
        self,
        cat: Cat,
        you: Cat
    ):
        self.cat = cat
        self.you = you
        self.debug = constants.CONFIG["lifegen"]["debug"]["debug_ensure_dialogue"]
        self.cat_dict = {}

        # holds a cat dict for each dialogue key
        self.dialogue_cat_dict = {}

    def load_texts(self):
        """
        Loads dialogue depending on rank, group, age
        """

        # resource_dir = "lifegen_talk"
        resource_dir = "lifegen_talk/NEW"
        possible_texts = {}

        special_date = get_special_date()

        if switch_get_value(Switch.talk_category) == "insult":
            possible_texts.update(load_lang_resource(f"{resource_dir}/insults.json"))
        elif switch_get_value(Switch.talk_category) == "flirt":
            possible_texts.update(load_lang_resource(f"{resource_dir}/flirt.json"))
        else:
            possible_texts.update(
                load_lang_resource(
                    f"{resource_dir}/{self.cat.status.rank.replace(' ', '_')}.json"
                    )
                )
            if self.cat.status.is_outsider:
                possible_texts.update(load_lang_resource(f"{resource_dir}/general_outsider.json"))
            else:
                if self.cat.status.rank != CatRank.NEWBORN:
                    # newborns will no longer participate in nuanced discussion

                    if not self.cat.status.rank.is_baby() and not self.you.status.rank.is_baby():
                        possible_texts.update(
                            load_lang_resource(
                                f"{resource_dir}/general_no_kit.json"
                                )
                            )
                    if self.cat.age != CatAge.NEWBORN and self.you.age != CatAge.NEWBORN:
                        possible_texts.update(
                            load_lang_resource(
                                f"{resource_dir}/general_no_newborn.json"
                                )
                            )
                    if not self.cat.status.rank.is_baby() and self.you.status.rank.is_baby():
                        possible_texts.update(
                            load_lang_resource(
                                f"{resource_dir}/general_you_kit.json"
                                )
                            )
                    if game.clan.focus:
                        possible_texts.update(
                            load_lang_resource(
                                f"{resource_dir}/focuses/{game.clan.focus}.json"
                                )
                            )
                    if special_date:
                        possible_texts.update(
                            load_lang_resource(
                                f"{resource_dir}/focuses/{special_date.patrol_tag}.json"
                                )
                            )
                    if constants.CONFIG['fun']['april_fools']:
                        possible_texts.update(
                            load_lang_resource(
                                f"{resource_dir}/focuses/aprilfools.json"
                                )
                            )

        # DEBUG
        # possible_texts = load_lang_resource("lifegen_talk/TEST.json")
        return possible_texts

    def filter_dialogue(self, possible_texts):
        """
        Filters possible dialogue for selection
        """

        possible_dialogue = {}
        possible_dialogue_keys = []
        for key, block in possible_texts.items():
            # print("Checking", key)
            if "season" in block:
                if (
                    block["season"] and
                    game.clan.current_season not in block["season"] and
                    game.clan.current_season.lower() not in block["season"]
                    ):
                    continue
            if "biome" in block:
                if (
                    block["biome"] and
                    game.clan.biome not in block["biome"] and
                    game.clan.biome.lower() not in block["biome"]
                    ):
                    continue
            if "camp" in block:
                if block["camp"] and game.clan.camp_bg not in block["camp"]:
                    continue

            # now this for the cats block
            chosen_cat_dict = choose_random_cats(block, self.you, self.cat, self.cat_dict, key=key)
            if not chosen_cat_dict:
                continue

            # populates the dict that holds dialogue keys
            self._populate_cat_dict(key, chosen_cat_dict)
            possible_dialogue[key] = block
            if "frequency" in block:
                count = block["frequency"]
                for other_block in block:
                    if other_block in ["season", "biome", "camp", "relationships"]:
                        count += 1
                for i in range(count):
                    possible_dialogue_keys.append(key)
            else:
                print("Warning: Dialogue", key, "has no frequency.")
                possible_dialogue_keys.append(key)


        return possible_dialogue, possible_dialogue_keys

    def get_cat_dict(self):
        """
        Returns the cat dict for use in TalkScreen
        """
        return self.cat_dict

    def choose_dialogue(self, possible_dialogue):
        """
        Makes a final selection.
        Returns the key and the dict object.
        """
        possible_dialogue, possible_dialogue_keys = self.filter_dialogue(possible_dialogue)
        if not possible_dialogue:
            possible_dialogue = load_lang_resource("lifegen_talk/general.json")
            possible_dialogue_keys = ["general"]

        debug_dict = {}
        for key in possible_dialogue_keys.copy():
            if len(possible_dialogue_keys) > 2:
                if key in game.clan.talks:
                    possible_dialogue_keys.remove(key)
            if key not in debug_dict:
                debug_dict[key] = 1
            else:
                debug_dict[key] += 1

        # debug print
        # print()
        # print("DIALOGUE WEIGHTS")
        # for key, value in debug_dict.items():
        #     print(f"{key}: {value}")

        if self.debug:
            if constants.CONFIG["lifegen"]["debug"]["debug_dialogue_override_filtering"]:
                chosen_key = self.debug
            elif self.debug in possible_dialogue:
                chosen_key = self.debug
                print(f"Debug: Dialogue set to {self.debug}")
            else:
                chosen_key = random.choice(possible_dialogue_keys)
                print(
                    f"Debugged Dialogue ID ({self.debug}) is not in possible dialogue options." +
                    " Set debug_dialogue_override_filtering to true to override filtering."
                    )
        else:
            chosen_key = random.choice(possible_dialogue_keys)

        if chosen_key != "general":
            self.cat_dict = self.dialogue_cat_dict[chosen_key]
            game.clan.talks.append(chosen_key)
        else:
            self.cat_dict = {
                "t_c": self.cat,
                "y_c": self.you
            }

        return chosen_key, possible_dialogue[chosen_key]


    # ---------------------------------------------------------------------- #
    #                                HELPERS                                 #
    # ---------------------------------------------------------------------- #

    def _populate_cat_dict(self, key, possible_cats_dict):
        self.dialogue_cat_dict[key] = possible_cats_dict

    # ---------------------------------------------------------------------- #
    #                            SCENE EFFECTS                               #
    # ---------------------------------------------------------------------- #

    def handle_scene_effects(self, current_scene, dialogue_object):
        """
        Handles scene effects such as accessories, relationship changes, and more.
        """
        # TODO: scene effects!
        if f"{current_scene}_scene_effects" in dialogue_object:
            print("Scene effects for:", current_scene)
            print(dialogue_object[f"{current_scene}_scene_effects"])
