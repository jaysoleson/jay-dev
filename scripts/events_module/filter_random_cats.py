import random

from scripts.game_structure import game
from scripts.cat.enums import CatGroup
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.utility import get_cluster

# pylint: disable=consider-using-dict-items

# LIFEGEN FILE!
# this script deals with filtering the "cats" blocks used in dialogue, lg events, and lg patrols.

possible_cats_dict = {}

def choose_random_cats(
        block,
        your_cat,
        the_cat,
        cat_dict,
        key=""
        ):
    """
    Selects random cats for LG stuff! 
    """
    possible_cats = Cat.all_cats_list.copy()
    chosen_cat_dict = {}
    abbrevs = []
    skip = False

    try:
        if "cats" in block:
            skip = False
            for abbrev in block["cats"]:
                abbrevs.append(abbrev)
                # checks if there are any valid cats available
                possible_cats_dict[abbrev] = _validate_cat(abbrev, block, possible_cats, your_cat, the_cat)
                if not possible_cats_dict[abbrev]:
                    skip = True
                    break
            if skip:
                return {}

        # filter rel uses all abbrevs to make choices based on relationships
        # chosen cat dict is the selected cats! one cat object per abbrev!
        chosen_cat_dict = __filter_relationships(abbrevs, block, possible_cats_dict, your_cat, the_cat, cat_dict, key=key)
    except Exception as e:
        print("WARNING: Error with dialogue filtering for", key)
        print(e)
    return chosen_cat_dict

def _validate_cat(abbrev, block, possible_cats, your_cat, the_cat):
    """
    Validates each cat block.
    Helper functions will narrow down the possible cat options.
    For r_c, a final choice is made at the end.
    For t_c and y_c, if the_cat or your_cat are not in the possible cat options,
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
        possible_cats = __filter_dead(cat_block[abbrev], possible_cats.copy())
        possible_cats = __filter_group(cat_block[abbrev], possible_cats.copy())
        possible_cats = __filter_standing(cat_block[abbrev], possible_cats.copy(), your_cat)

        possible_cats = __filter_age(cat_block[abbrev], possible_cats.copy())
        possible_cats = __filter_rank(cat_block[abbrev], possible_cats.copy())
        possible_cats = __filter_skill(cat_block[abbrev], possible_cats.copy())
        possible_cats = __filter_cluster(cat_block[abbrev], possible_cats.copy())
        possible_cats = __filter_backstory(cat_block[abbrev], possible_cats.copy())
        possible_cats = __filter_faith(cat_block[abbrev], possible_cats.copy())

    # conditions are filtered either way for deaf/blind/grieving stuff
    # possible_cats = __filter_conditions(cat_block[abbrev], possible_cats.copy())

    if abbrev == "t_c" and the_cat not in possible_cats:
        return []
    if abbrev == "y_c" and your_cat not in possible_cats:
        return []
    
    possible_cat_dict = {}
    possible_cat_dict[abbrev] = possible_cats.copy()

    return possible_cats

    # ---------------------------------------------------------------------- #
    #                          CAT FILTERING FUNCTIONS                       #
    # ---------------------------------------------------------------------- #

def __filter_dead(abbrev_block, possible_cats):
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

def __filter_group(abbrev_block, possible_cats):
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

def __filter_standing(abbrev_block, possible_cats, your_cat):
    if "standing" not in abbrev_block:
        return possible_cats

    for cat in possible_cats.copy():
        standing_found = False
        standing_dict = {
            "lost": cat.status.is_lost(your_cat.status.group_ID),
            "exiled": cat.status.is_exiled(your_cat.status.group_ID),
            "shunned": cat.status.is_shunned(your_cat.status.group_ID),
            "daylight": cat.status.is_daylight_warrior(your_cat.status.group_ID),
            "forgiven": cat.status.is_forgiven(),
            "near": cat.status.is_near(your_cat.status.group_ID),
            "outsider": cat.status.is_outsider
        }
        for tag in abbrev_block["standing"]:
            if tag in standing_dict and standing_dict[tag]:
                standing_found = True
                break
        if not standing_found:
            possible_cats.remove(cat)

    return possible_cats

def __filter_age(abbrev_block, possible_cats):
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

def __filter_rank(abbrev_block, possible_cats):
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

def __filter_skill(abbrev_block, possible_cats):
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

def __filter_cluster(abbrev_block, possible_cats):
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

def __filter_backstory(abbrev_block, possible_cats):

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

def __filter_faith(abbrev_block, possible_cats):
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

def __filter_conditions(abbrev_block, possible_cats):
    for cat in possible_cats.copy():
        blind_tagged = False
        deaf_tagged = False

        condition_true = False
        reg_tagged = False

        exclusive_conditions = ["pregnant", "grief stricken"]

        condition_block = abbrev_block["condition"] if "condition" in abbrev_block else []
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

                    # exclusionary
                    if condition == "not" and (
                        born_with in cat.illnesses or
                        born_with in cat.injuries or
                        born_with in cat.permanent_condition
                    ):
                        possible_cats.remove(cat)
                        break

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
                    elif tag in exclusive_conditions:
                        if not (
                            tag in cat.permanent_condition or
                            tag in cat.injuries or
                            tag in cat.illnesses
                        ):
                            possible_cats.remove(cat)
                            break
                    else:
                        reg_tagged = True
                        if (
                            tag in cat.permanent_condition or
                            tag in cat.injuries or
                            tag in cat.illnesses
                        ):
                            condition_true = True
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
    
        if reg_tagged:
            if cat in possible_cats and not condition_true:
                possible_cats.remove(cat)

    return possible_cats

def __filter_relationships(all_abbrevs, block, dict_possible_cats, your_cat, the_cat, cat_dict, key=""):
    """
    Chooses final cats based on relationship constraints.
    Not a 'filter' in the same way the other filter functions are. More of a selection tool.
    """
    rel_block = block["relationships"] if "relationships" in block else []
    new_dict = {
        "y_c": your_cat,
        "t_c": the_cat
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
                    to_cat_list = dict_possible_cats[TO].copy()
                    from_cat_list = dict_possible_cats[FROM].copy()
                    
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
                            # ensures r_c's are never your_cat or the_cat and similar checks.
                            valid = __check_valid(
                                TO, to_cat, FROM, from_cat, new_dict, your_cat, the_cat, cat_dict
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
                                elif rel_tag == "sibling's mate/mate's sibling":
                                    rel_valid = to_cat.ID in from_cat.inheritance.get_siblings_mates()
                                elif rel_tag == "mate's sibling/sibling's mate":
                                    rel_valid = from_cat.ID in to_cat.inheritance.get_siblings_mates()
                                elif rel_tag == "cousins":
                                    rel_valid = from_cat.ID in to_cat.inheritance.get_cousins()
                                elif rel_tag == "adopted siblings":
                                    rel_valid = from_cat.ID in to_cat.inheritance.get_no_blood_siblings()
                                elif rel_tag == "parent's sibling/sibling's kit":
                                    rel_valid = from_cat.ID in to_cat.inheritance.get_parents_siblings()
                                elif rel_tag == "strangers":
                                    if from_cat.ID in to_cat.relationships:
                                        rel_valid = False
                                elif rel_tag == "siblings":
                                    rel_valid = from_cat.ID in to_cat.inheritance.get_siblings()
                                elif rel_tag == "littermates":
                                    rel_valid = from_cat.ID in to_cat.inheritance.get_siblings() and from_cat.moons == to_cat.moons
                                elif rel_tag == "grandparent/grandchild":
                                    rel_valid = from_cat.is_grandparent(to_cat)
                                elif rel_tag == "grandchild/grandparent":
                                    rel_valid = to_cat.is_grandparent(from_cat)
                                
                                elif rel_tag == "dead/grieving":
                                    if "grief stricken" not in to_cat.illnesses:
                                        rel_valid = False
                                    elif "grief cat" not in to_cat.illnesses["grief stricken"]:
                                        rel_valid = False
                                    elif to_cat.illnesses["grief stricken"]["grief cat"] != from_cat.ID:
                                        rel_valid = False
                                    else:
                                        rel_valid = True
                                elif rel_tag == "grieving/dead":
                                    if "grief stricken" not in from_cat.illnesses:
                                        rel_valid = False
                                    elif "grief cat" not in from_cat.illnesses["grief stricken"]:
                                        rel_valid = False
                                    elif from_cat.illnesses["grief stricken"]["grief cat"] != to_cat.ID:
                                        rel_valid = False
                                    else:
                                        rel_valid = True
                                
                                elif rel_tag == "victim/murderer":
                                    if not to_cat.history.murder:
                                        rel_valid = False
                                    elif "is_murderer" not in to_cat.history.murder:
                                        rel_valid = False
                                    else:
                                        rel_valid = False
                                        for murder in to_cat.history.murder["is_murderer"]:
                                            if "victim" == from_cat.ID:
                                                rel_valid = True
                                                break
                                
                                elif rel_tag == "murderer/victim":
                                    if not from_cat.history.murder:
                                        rel_valid = False
                                    elif "is_murderer" not in from_cat.history.murder:
                                        rel_valid = False
                                    else:
                                        rel_valid = False
                                        for murder in from_cat.history.murder["is_murderer"]:
                                            if "victim" == to_cat.ID:
                                                rel_valid = True
                                                break
                                elif rel_tag == "non-related":
                                    rel_valid = from_cat.ID in to_cat.get_relatives()

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

    for abbrev in all_abbrevs:

        if abbrev not in new_dict and abbrev not in ("t_c", "y_c"):
            options = dict_possible_cats[abbrev]
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

def __check_valid(to_abbrev, to_cat, from_abbrev, from_cat, new_dict, your_cat, the_cat, cat_dict):
    """
    Checks abbrevs and cats during filtering.
    If y_c and t_c abbrevs are constrained in relationships, they're special cases.
    Reject any cats that aren't you or the_catcat when necessary,
    and don't let them become an r_c.
    """
    valid = True
    if to_abbrev == "y_c" and to_cat != your_cat:
        valid = False
    if to_abbrev == "t_c" and to_cat != the_cat:
        valid = False
    if from_abbrev == "y_c" and from_cat != your_cat:
        valid = False
    if from_abbrev == "t_c" and from_cat != the_cat:
        valid = False

    if to_abbrev != "y_c" and to_cat == your_cat:
        valid = False
    if to_abbrev != "t_c" and to_cat == the_cat:
        valid = False
    if from_abbrev != "y_c" and from_cat == your_cat:
        valid = False
    if from_abbrev != "t_c" and from_cat == the_cat:
        valid = False

    if from_abbrev in cat_dict:
        valid = False
    if to_abbrev in cat_dict:
        valid = False

    for key, value in new_dict.items():
        if value == from_cat and key != from_abbrev:
            valid = False
            break
        if value == to_cat and key != to_abbrev:
            valid = False
            break

    return valid
