import random

from scripts.game_structure import game, constants
from scripts.special_dates import get_special_date
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure.localization import load_lang_resource
from scripts.cat.enums import CatRank, CatGroup, CatAge
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.utility import get_cluster

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
            # print("Checking", key)
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

    def _validate_cat(self, abbrev, block, possible_cats):
        """
        Validates each cat block.
        Helper functions will narrow down the possible cat options.
        For r_c, a final choice is made at the end.
        For t_c and y_c, if self.cat or self.you are not in the possible cat options,
        the dialogue is filtered out.
        """
        cat_block = block["cats"]

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
            possible_cats = self.__filter_dead(cat_block[abbrev], possible_cats.copy())
            possible_cats = self.__filter_group(cat_block[abbrev], possible_cats.copy())
            possible_cats = self.__filter_standing(cat_block[abbrev], possible_cats.copy())

            possible_cats = self.__filter_age(cat_block[abbrev], possible_cats.copy())
            possible_cats = self.__filter_rank(cat_block[abbrev], possible_cats.copy())
            possible_cats = self.__filter_skill(cat_block[abbrev], possible_cats.copy())
            possible_cats = self.__filter_cluster(cat_block[abbrev], possible_cats.copy())
            possible_cats = self.__filter_backstory(cat_block[abbrev], possible_cats.copy())
            possible_cats = self.__filter_faith(cat_block[abbrev], possible_cats.copy())

        # conditions are filtered either way for deaf/blind/grieving stuff
        possible_cats = self.__filter_conditions(cat_block[abbrev], possible_cats.copy())

        if abbrev == "t_c" and self.cat not in possible_cats:
            return []
        if abbrev == "y_c" and self.you not in possible_cats:
            return []
        
        possible_cat_dict = {}
        possible_cat_dict[abbrev] = possible_cats.copy()

        return possible_cats

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
            if (
                f"not_{cat.status.rank}" in abbrev_block["rank"] or
                f"not_{cat.status.rank.replace(' ', '_')}" in abbrev_block["rank"]
                ):
                possible_cats.remove(cat)
            elif (
                "df_trainee" in abbrev_block["rank"] and
                    not (cat.joined_df)
                ): possible_cats.remove(cat)
            elif (
                "not_df_trainee" in abbrev_block["rank"] and
                    (cat.joined_df)
                ): possible_cats.remove(cat)
            elif (
                "guide" in abbrev_block["rank"] and
                    cat not in (game.clan.instructor, game.clan.demon)
                ): possible_cats.remove(cat)
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
            skill_met = False
            # if the skill tag is negative (tier is -1), the cat cant have Any of the negative skills.
            # they'll only need one of the positive skills to get the dialogue
            # negative and positive skill tags can be combined!
            # so like ["LORE,1", "OMEN,-1"] is possible, for example.
            neg_skills_met = 0
            neg_skills = 0
            for tag in abbrev_block["skill"]:
                tier = int(tag.split(",")[1])
                if tier == -1:
                    neg_skills += 1
                if cat.skills.meets_skill_requirement(tag.split(",")[0], tier):
                    if tier == -1:
                        neg_skills_met += 1
                    else:
                        skill_met = True

            if (
                not skill_met or
                (neg_skills > 0 and neg_skills != neg_skills_met)
                ):
                possible_cats.remove(cat)


        return possible_cats
    
    def __filter_cluster(self, abbrev_block, possible_cats):
        if "cluster" not in abbrev_block:
            return possible_cats
        for cat in possible_cats.copy():
            cluster1, cluster2 = get_cluster(cat.personality.trait)
            if (
                cluster1 not in abbrev_block["cluster"] and
                cluster2 not in abbrev_block["cluster"] and
                cat.personality.trait not in abbrev_block["cluster"]
            ):
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
                        if condition == "injury" and born_with == "none":
                            if cat.is_injured():
                                possible_cats.remove(cat)
                                break
                        if condition == "illness" and born_with == "none":
                            if cat.is_ill():
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
                                deaf_tagged = False
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
            if (
                (
                    "deaf" in cat.permanent_condition and
                    cat.permanent_condition["deaf"]["born_with"] is True
                )
                and not deaf_tagged
                and cat in possible_cats
                ):
                possible_cats.remove(cat)

            if "grief stricken" in cat.illnesses and not grief_tagged and cat in possible_cats:
                possible_cats.remove(cat)

        return possible_cats
    
    def __filter_relationships(self, abbrevs, block, possible_cats_dict):
        """
        Chooses final cats based on relationship constraints.
        Not a 'filter' in the same way the other filter functions are. More of a selection tool.
        """
        # TODO: fix??? this is SO nested it pisses me off. idk if theres much i can do though
        rel_block = block["relationships"] if "relationships" in block else []
        new_dict = {
            "y_c": self.you,
            "t_c": self.cat
        }

        for relationship in rel_block:
            for rel_tag in relationship["relationship"]:

                # substitute for a "rel_found" bool, as, with multiple relationships,
                # you cant depend on a true or false.
                # check how many relationships are valid vs. how many we need to be.
                # if these arent the same number at the end, the dialogue will be filtered out.
                valid_rels = 0
                rels_to_check = 0

                # get our initial count before we start looping
                for FROM in relationship["cats_from"]:
                    for TO in relationship["cats_to"]:
                        if TO != FROM:
                            rels_to_check += 1

                # begin 500 nested for loops!
                for FROM in relationship["cats_from"]:
                    if valid_rels == rels_to_check:
                        continue
                    for TO in relationship["cats_to"]:
                        if valid_rels == rels_to_check:
                            continue
                        if TO == FROM:
                            continue
                        
                        # Grab our possible cats depending on the abbrev
                        to_cat_list = possible_cats_dict[TO].copy()
                        from_cat_list = possible_cats_dict[FROM].copy()
                        
                        # shuffle so the same cat isnt always on top
                        random.shuffle(to_cat_list)
                        random.shuffle(from_cat_list)

                        # if the cat is already here, don't replace them
                        if FROM in new_dict:
                            from_cat_list = [new_dict[FROM]]
                        if TO in new_dict:
                            to_cat_list = [new_dict[TO]]

                        # now begin finding cats
                        match_found = False
                        for from_cat in from_cat_list:
                            if valid_rels == rels_to_check:
                                continue
                            if match_found:
                                continue
                            for to_cat in to_cat_list:
                                if valid_rels == rels_to_check:
                                    continue
                                if match_found:
                                    continue
                                rel_valid = False
                                # this will check is the abbrev and cat are valid.
                                # ensures r_c's are never self.you or self.cat and similar checks.
                                valid = self.__check_valid(
                                    TO, to_cat, FROM, from_cat, new_dict
                                )

                                # special logic for the different types of relationship
                                if valid:
                                    if rel_tag == "mates":
                                        rel_valid = to_cat.ID in from_cat.mate
                                    elif rel_tag == "non-mates":
                                        rel_valid = to_cat.ID not in from_cat.mate
                                    elif rel_tag == "ex-mates":
                                        rel_valid = to_cat.ID in from_cat.previous_mates

                                    elif rel_tag == "parent/child":
                                        rel_valid = (
                                            from_cat.is_parent(to_cat) or
                                            from_cat.ID in to_cat.adoptive_parents
                                            )
                                    elif rel_tag == "child/parent":
                                        rel_valid = (
                                            to_cat.is_parent(from_cat) or
                                            to_cat.ID in from_cat.adoptive_parents
                                            )
                                    elif rel_tag == "birth parent/birth child":
                                        rel_valid = from_cat.is_parent(to_cat)
                                    elif rel_tag == "birth child/birth parent":
                                        rel_valid = to_cat.is_parent(from_cat)
                                    elif rel_tag == "adoptive parent/adoptive child":
                                        rel_valid = from_cat.ID in to_cat.adoptive_parents
                                    elif rel_tag == "adoptive child/adoptive parent":
                                        rel_valid = to_cat.ID in from_cat.adoptive_parents
                                    # TODO: all other rels in all_resources rel tags

                                    elif rel_tag == "app/mentor":
                                        rel_valid = from_cat.ID in to_cat.apprentice
                                    elif rel_tag == "mentor/app":
                                        rel_valid = to_cat.ID in from_cat.apprentice
                                    elif rel_tag == "df app/df mentor":
                                        rel_valid = from_cat.ID in to_cat.df_apprentices
                                    elif rel_tag == "df mentor/df app":
                                        rel_valid = to_cat.ID in from_cat.df_apprentices
                                    else:
                                        # now check rel value tags
                                        rel_valid = True
                                        try:
                                            attributes = rel_tag.split("_")
                                        except:
                                            print(f"WARNING: Invalid relationship tag ({rel_tag})")
                                            rel_valid = False
                                        if to_cat.ID not in from_cat.relationships:
                                            rel_valid = False
                                        else:
                                            if "min" in rel_tag:
                                                if attributes[1] == "like":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].like <
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                elif attributes[1] == "romance":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].romance <
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                elif attributes[1] == "respect":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].respect <
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                elif attributes[1] == "trust":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].trust <
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                elif attributes[1] == "comfort":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].comfort <
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                else:
                                                    print(f"WARNING: Invalid relationship tag ({rel_tag})")
                                                    rel_valid = False
                                            elif "max" in rel_tag:
                                                if attributes[1] == "like":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].like >
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                elif attributes[1] == "romance":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].romance >
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                elif attributes[1] == "respect":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].respect >
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                elif attributes[1] == "trust":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].trust >
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                elif attributes[1] == "comfort":
                                                    if (
                                                        from_cat.relationships[to_cat.ID].comfort >
                                                        int(attributes[2])
                                                        ):
                                                        rel_valid = False
                                                else:
                                                    print(f"WARNING: Invalid relationship tag ({rel_tag})")
                                                    rel_valid = False

                                    if rel_valid:
                                        valid_rels += 1
                                        if FROM not in new_dict:
                                            new_dict[FROM] = from_cat
                                            match_found = True
                                        if TO not in new_dict:
                                            new_dict[TO] = to_cat
                                            match_found = True

                if valid_rels != rels_to_check:
                    return {}

        for abbrev in abbrevs:
            if abbrev not in new_dict and abbrev not in ("t_c", "y_c"):
                options = possible_cats_dict[abbrev]
                for existing_cat in new_dict:
                    if new_dict[existing_cat] in options:
                        options.remove(new_dict[existing_cat])
                if not options:
                    return {}
                chosen_cat = random.choice(options)
                new_dict[abbrev] = chosen_cat

        return new_dict
    
    # ---------------------------------------------------------------------- #
    #                                HELPERS                                 #
    # ---------------------------------------------------------------------- #
    
    def __check_valid(self, to_abbrev, to_cat, from_abbrev, from_cat, new_dict):
        """
        Checks abbrevs and cats during filtering.
        If y_c and t_c abbrevs are constrained in relationships, they're special cases.
        Reject any cats that aren't self.you or self.cat when necessary,
        and don't let them become an r_c.
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

        for key, value in new_dict.items():
            if value == from_cat and key != from_abbrev:
                valid = False
                break
            if value == to_cat and key != to_abbrev:
                valid = False
                break

        return valid

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
