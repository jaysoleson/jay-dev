import random

from scripts.game_structure import game, constants
from scripts.special_dates import get_special_date
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure.localization import load_lang_resource
from scripts.cat.enums import CatRank, CatGroup, CatAge
from scripts.cat.cats import Cat, BACKSTORIES

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
        possible_texts = load_lang_resource("lifegen_talk/TEST.json")
        return possible_texts

    def filter_dialogue(self, possible_texts):
        """
        Filters possible dialogue for selection
        """
        # TODO: relationships and tags n stuff! only the cat is done

        possible_dialogue = {}
        possible_cats = Cat.all_cats_list.copy()
        possible_cats_dict = {}

        abbrevs = []

        for key, block in possible_texts.items():
            chosen_cat_dict = {}
            if "cats" in block:
                skip = False
                for abbrev in block["cats"]:
                    abbrevs.append(abbrev)
                    # checks if there are any valid cats available
                    possible_cats_dict[abbrev] = self._validate_cat(abbrev, block, possible_cats)
                    if not possible_cats_dict[abbrev]:
                        skip = True
                        break
                if skip:
                    continue

            # filter rel uses all abbrevs to make choices based on relationships
            # chosen cat dict is the selected cats! one cat object per abbrev!
            chosen_cat_dict = self.__filter_relationships(abbrevs, block, possible_cats_dict)
            if not chosen_cat_dict:
                continue

            # populates the dict that holds dialogue keys
            self._populate_cat_dict(key, chosen_cat_dict)
            possible_dialogue[key] = block

        return possible_dialogue

    def __filter_relationships(self, abbrevs, block, possible_cats_dict):
        """
        Chooses final cats based on relationship constraints.
        Not a 'filter' in the same way the other filter functions are.
        """
        rel_block = block["relationships"] if "relationships" in block else []
        new_dict = {}

        for relationship in rel_block:
            from_abbrev = relationship["cats_from"][0]
            to_abbrev = relationship["cats_to"][0]
            # TODO: remove indexes later so it works for all abbrevs
            # easier said than done.....................

            to_cat_list = possible_cats_dict[to_abbrev].copy()
            from_cat_list = possible_cats_dict[from_abbrev].copy()
            random.shuffle(from_cat_list)
            # without shuffle, the same cat will always be at the top.
            # meaning theyll show up in dialogue more frequently than everyone else
            # cant have that! we are equal opportunity

            if (
                "parent/child" in relationship["relationship"] or
                "child/parent" in relationship["relationship"]
                ):
                child_found = False
                for from_cat in from_cat_list:
                    for to_cat in to_cat_list:
                        valid = self.__check_valid(
                            to_abbrev, to_cat, from_abbrev, from_cat, new_dict
                        )
                        if not valid:
                            continue

                        parent_valid = False
                        if "parent/child" in relationship["relationship"]:
                            parent_valid = from_cat.is_parent(to_cat)
                        elif "child/parent" in relationship["relationship"]:
                            parent_valid = to_cat.is_parent(from_cat)

                        if parent_valid:
                            if from_abbrev not in new_dict:
                                new_dict[from_abbrev] = from_cat
                            if to_abbrev not in new_dict:
                                new_dict[to_abbrev] = to_cat
                            child_found = True

                        if child_found:
                            break
                    if child_found:
                        break
                if not child_found:
                    return {}
            if (
                "mates" in relationship["relationship"] or
                "ex-mates" in relationship["relationship"]
                ):
                mates_found = False
                for from_cat in from_cat_list:
                    for to_cat in to_cat_list:
                        valid = self.__check_valid(
                            to_abbrev, to_cat, from_abbrev, from_cat, new_dict
                        )
                        if not valid:
                            continue

                        mates_valid = False
                        if "mates" in relationship["relationship"]:
                            mates_valid = to_cat.ID in from_cat.mate
                        elif "ex-mates" in relationship["relationship"]:
                            mates_valid = to_cat.ID in from_cat.previous_mates

                        if mates_valid:
                            if from_abbrev not in new_dict:
                                new_dict[from_abbrev] = from_cat
                            if to_abbrev not in new_dict:
                                new_dict[to_abbrev] = to_cat
                            mates_found = True

                        if mates_found:
                            break
                    if mates_found:
                        break
                if not mates_found:
                    return {}

        for abbrev in abbrevs:
            if abbrev not in new_dict:
                new_dict[abbrev] = random.choice(possible_cats_dict[abbrev])

        return new_dict


    def _populate_cat_dict(self, key, possible_cats_dict):
        self.dialogue_cat_dict[key] = possible_cats_dict


    def _validate_cat(self, abbrev, block, possible_cats):
        """
        Validates each cat block.
        Helper functions will narrow down the possible cat options.
        For r_c, a final choice is made at the end.
        For t_c and y_c, if self.cat or self.you are not in the possible cat options,
        the dialogue is filtered out.
        """
        cat_block = block["cats"]
        rel_block = block["relationships"] if "relationships" in block else []

        if not cat_block[abbrev]:
            # if the r_c is completely unconstrained,
            # manually set it to be a cat in the current group.
            # we dont go through all of that filtering with an empty dict
            possible_cats = [
                cat for cat in Cat.all_cats_list.copy() if
                cat.status.alive_in_your_cat_group
            ]
        else:
            # filtering functions!
            # filters that make the most change are done first.
            possible_cats = self.__filter_dead(cat_block[abbrev], possible_cats)
            possible_cats = self.__filter_group(cat_block[abbrev], possible_cats)
            possible_cats = self.__filter_standing(cat_block[abbrev], possible_cats)

            possible_cats = self.__filter_age(cat_block[abbrev], possible_cats)
            possible_cats = self.__filter_rank(cat_block[abbrev], possible_cats)
            possible_cats = self.__filter_skill(cat_block[abbrev], possible_cats)
            possible_cats = self.__filter_backstory(cat_block[abbrev], possible_cats)
            possible_cats = self.__filter_faith(cat_block[abbrev], possible_cats)

        # conditions are filtered either way for deaf/blind/grieving stuff
        possible_cats = self.__filter_conditions(cat_block[abbrev], possible_cats)
        
        possible_cat_dict = {}
        possible_cat_dict[abbrev] = possible_cats

        return possible_cats

    def get_cat_dict(self):
        """
        Returns the cat dict for use in TalkScreen
        """
        return self.cat_dict

    def choose_dialogue(self, possible_dialogue):
        """
        Makes a final selection.
        Returns the dict object.
        """
        possible_dialogue = self.filter_dialogue(possible_dialogue)
        if not possible_dialogue:
            possible_dialogue = load_lang_resource("lifegen_talk/general.json")

        if self.debug:
            if constants.CONFIG["lifegen"]["debug"]["debug_dialogue_override_filtering"]:
                chosen_key = self.debug
            elif self.debug in possible_dialogue:
                chosen_key = self.debug
                print(f"Debug: Dialogue set to {self.debug}")
            else:
                chosen_key = random.choice(list(possible_dialogue.keys()))
                print(
                    f"Debugged Dialogue ID ({self.debug}) is not in possible dialogue options." +
                    " Set debug_dialogue_override_filtering to true to override filtering."
                    )
        else:
            chosen_key = random.choice(list(possible_dialogue.keys()))

        if chosen_key != "general":
            self.cat_dict = self.dialogue_cat_dict[chosen_key]
        else:
            self.cat_dict = {
                "t_c": self.cat,
                "y_c": self.you
            }

        return chosen_key, possible_dialogue[chosen_key]


    # ---------------------------------------------------------------------- #
    #                          CAT FILTERING FUNCTIONS                       #
    # ---------------------------------------------------------------------- #

    def __filter_dead(self, abbrev_block, possible_cats):
        for cat in possible_cats.copy():
            if "min_max_dead_moons" in abbrev_block:
                if (
                    abbrev_block["min_max_dead_moons"][0] > cat.dead_for or
                    abbrev_block["min_max_dead_moons"][1] < cat.dead_for
                ):
                    possible_cats.remove(cat)
                    continue
            if "residence" in abbrev_block:
                if not cat.dead:
                    possible_cats.remove(cat)
                else:
                    if "any" not in abbrev_block["residence"]:
                        if (
                            "df" not in abbrev_block["residence"] and
                            cat.status.group_ID == CatGroup.DARK_FOREST_ID
                            ):
                            possible_cats.remove(cat)
                        elif (
                            "sc" not in abbrev_block["residence"] and
                            cat.status.group_ID == CatGroup.STARCLAN_ID
                            ):
                            possible_cats.remove(cat)
                        elif (
                            "ur" not in abbrev_block["residence"] and
                            cat.status.group_ID == CatGroup.UNKNOWN_RESIDENCE_ID
                            ):
                            possible_cats.remove(cat)
            else:
                if cat.dead:
                    possible_cats.remove(cat)
        return possible_cats

    def __filter_group(self, abbrev_block, possible_cats):
        for cat in possible_cats.copy():
            if "group" in abbrev_block:
                if (
                    (
                        cat.status.group and
                        cat.status.group not in abbrev_block["group"]
                    ) or
                    (
                        not cat.status.group and
                        "none" not in abbrev_block["group"]
                    ) or
                    (
                        cat.status.is_other_clancat and
                        "other_clan" not in abbrev_block["group"]
                    ) or
                    (
                        f"not_{cat.status.group}" in abbrev_block["group"]
                    )
                ):
                    possible_cats.remove(cat)
        return possible_cats

    def __filter_standing(self, abbrev_block, possible_cats):
        if "standing" not in abbrev_block:
            return possible_cats

        for cat in possible_cats.copy():
            standing_found = False
            standing_dict = {
                "lost": cat.status.is_lost(self.you.status.group_ID),
                "exiled": cat.status.is_exiled(self.you.status.group_ID),
                "shunned": cat.status.is_shunned(self.you.status.group_ID),
                "daylight": cat.status.is_daylight_warrior(self.you.status.group_ID),
                "forgiven": cat.status.is_forgiven(),
                "near": cat.status.is_near(self.you.status.group_ID),
                "outsider": cat.status.is_outsider
            }
            for tag in abbrev_block["standing"]:
                if tag in standing_dict and standing_dict[tag]:
                    standing_found = True
                    break
            if not standing_found:
                possible_cats.remove(cat)

        return possible_cats

    def __filter_age(self, abbrev_block, possible_cats):
        if "age" not in abbrev_block:
            return possible_cats

        for cat in possible_cats.copy():
            if f"not_{cat.age}" in abbrev_block["age"]:
                possible_cats.remove(cat)
                continue
            elif cat.age not in abbrev_block["age"]:
                possible_cats.remove(cat)
                continue

        return possible_cats

    def __filter_rank(self, abbrev_block, possible_cats):
        if "rank" not in abbrev_block:
            return possible_cats
        for cat in possible_cats.copy():
            if f"not_{cat.status.rank}" in abbrev_block["rank"]:
                possible_cats.remove(cat)
            elif (
                cat.status.rank not in abbrev_block["rank"] and
            cat.status.rank.replace(' ', '_') not in abbrev_block["rank"]
                ):
                possible_cats.remove(cat)
        return possible_cats

    def __filter_skill(self, abbrev_block, possible_cats):
        if "skill" not in abbrev_block:
            return possible_cats
        for cat in possible_cats.copy():
            primary_string = f"{cat.skills.primary.path.name},{cat.skills.primary.points}"
            secondary_string = ""
            if cat.skills.secondary:
                secondary_string = f"{cat.skills.secondary.path.name},{cat.skills.secondary.points}"

            if (
                f"not_{primary_string}" in abbrev_block["skill"] or
                f"not_{secondary_string}" in abbrev_block["skill"]
            ):
                possible_cats.remove(cat)
                continue
            else:
                skill_met = False
                for tag in abbrev_block["skill"]:
                    if cat.skills.meets_skill_requirement(tag.split(",")[0], int(tag.split(",")[1])):
                        skill_met = True
                        break
                if not skill_met:
                    possible_cats.remove(cat)


        return possible_cats

    def __filter_backstory(self, abbrev_block, possible_cats):

        if "backstory" not in abbrev_block:
            return possible_cats

        backstory_tag_dict = {
            "formerlyaloner": "loner_backstories",
            "formerlyarogue": "rogue_backstories",
            "formerlyakittypet": "kittypet_backstories",
            "half-Clan": "half_clan_backstories",
            "clanborn": "clanborn_backstories",
            "clanfounder": "clan_founder_backstories",
            "guide": "clan_guide_backstories",
            "formerlyanoutsider": "outsider_backstories",
            "fromanotherclan": "former_clancat_backstories",
            "orphaned": "orphaned_backstories",
            "abandoned": "abandoned_backstories",
            "dead": "dead_cat_backstories",
            "starclan": "starclan_backstories",
            "df": "df_backstories",
            "fromstarclan": "oldstarclan_backstories"
        }

        for cat in possible_cats.copy():
            backstory_found = False
            for tag in abbrev_block["backstory"]:
                if tag in backstory_tag_dict:
                    if cat.backstory in (
                        BACKSTORIES["backstory_categories"][backstory_tag_dict[tag]]
                        ):
                        backstory_found = True
                        break
                elif tag == cat.backstory:
                    backstory_found = True
                    break
            if not backstory_found:
                possible_cats.remove(cat)

        return possible_cats

    def __filter_faith(self, abbrev_block, possible_cats):
        if "min_max_faith" not in abbrev_block:
            return possible_cats
        for cat in possible_cats.copy():
            if (
                abbrev_block["min_max_faith"][0] > cat.faith or
                abbrev_block["min_max_faith"][1] < cat.faith
            ):
                possible_cats.remove(cat)
                continue
        return possible_cats

    def __filter_conditions(self, abbrev_block, possible_cats):
        for cat in possible_cats.copy():
            blind_tagged = False
            deaf_tagged = False
            grief_tagged = False

            condition_block = abbrev_block["conditions"] if "conditions" in abbrev_block else []
            for tag in condition_block:
                if isinstance(tag, list):
                    for condition in tag:
                        if (
                            condition not in cat.illnesses and
                            condition not in cat.injuries and
                            condition not in cat.permanent_condition
                        ):
                            possible_cats.remove(cat)
                            break
                elif isinstance(tag, str):
                    if ":" in tag:
                        attributes = tag.split(":")
                        condition = attributes[0]
                        born_with = attributes[1]
                        exclusive = "false"

                        if condition == "blind":
                            blind_tagged = True

                        if condition == "deaf":
                            deaf_tagged = True

                        if len(attributes) > 2:
                            exclusive = attributes[2]

                        # gen injury/illness
                        if condition == "injury" and born_with == "any":
                            if not cat.is_injured():
                                possible_cats.remove(cat)
                                break
                        if condition == "illness" and born_with == "any":
                            if not cat.is_ill():
                                possible_cats.remove(cat)
                                break

                        # now blind/deaf
                        if exclusive == "true" and condition not in cat.permanent_condition:
                            possible_cats.remove(cat)
                            break

                        if born_with == "true":
                            if not (
                                condition in cat.permanent_condition and
                                cat.permanent_condition[condition]["born_with"] is True
                            ):
                                possible_cats.remove(cat)
                                break
                        elif born_with == "false":
                            if not (
                                condition in cat.permanent_condition and
                                cat.permanent_condition[condition]["born_with"] is False
                            ):
                                possible_cats.remove(cat)
                                break
                    else:
                        if tag == "hearing":
                            if "deaf" in cat.permanent_condition:
                                possible_cats.remove(cat)
                                break
                        elif tag == "grief stricken":
                            grief_tagged = True
                        elif not (
                            tag in cat.permanent_condition or
                            tag in cat.injuries or
                            tag in cat.illnesses
                        ):
                            possible_cats.remove(cat)
                            break

            if "blind" in cat.permanent_condition and not blind_tagged and cat in possible_cats:
                possible_cats.remove(cat)
            if "deaf" in cat.permanent_condition and not deaf_tagged and cat in possible_cats:
                possible_cats.remove(cat)

            if "grief stricken" in cat.illnesses and not grief_tagged and cat in possible_cats:
                possible_cats.remove(cat)

        return possible_cats
    
    # ---------------------------------------------------------------------- #
    #                                HELPERS                                 #
    # ---------------------------------------------------------------------- #
    
    def __check_valid(self, to_abbrev, to_cat, from_abbrev, from_cat, new_dict):
        """
        Checks abbrevs and cats during filtering.
        If y_c and t_c abbrevs are constrained in relationships, they're special cases.
        Reject any cats that aren't self.you or self.cat when necessary, and don't let them become an r_c.
        """
        valid = True
        if to_abbrev == "y_c" and to_cat != self.you:
            valid = False
        if to_abbrev == "t_c" and to_cat != self.cat:
            valid = False
        if from_abbrev == "y_c" and from_cat != self.you:
            valid = False
        if from_abbrev == "t_c" and from_cat != self.cat:
            valid = False

        if to_abbrev != "y_c" and to_cat == self.you:
            valid = False
        if to_abbrev != "t_c" and to_cat == self.cat:
            valid = False
        if from_abbrev != "y_c" and from_cat == self.you:
            valid = False
        if from_abbrev != "t_c" and from_cat == self.cat:
            valid = False

        if from_abbrev in self.cat_dict:
            valid = False
        if to_abbrev in self.cat_dict:
            valid = False

        if from_abbrev in new_dict:
            valid = False
        if to_abbrev in new_dict:
            valid = False

        for key, value in new_dict.items():
            if value == from_cat:
                valid = False
                break
            if value == to_cat:
                valid = False
                break

        return valid


