import random

from scripts.game_structure import game
from scripts.cat.enums import CatGroup, CatRank, CatAge
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.lifegen_utility import get_cluster
from scripts.clan_package.settings import get_clan_setting
from scripts.cat.sexuality import Sexuality, Arospec, Acespec
from scripts.game_structure import game, constants


# pylint: disable=consider-using-dict-items

# LIFEGEN FILE!
# this script deals with filtering the "cats" blocks used in dialogue, lg events, and lg patrols.

possible_cats_dict = {}

debug_key = constants.CONFIG["lifegen"]["debug"]["debug_ensure_dialogue"]

def choose_random_cats(
        cats_block: dict={},
        rel_block: list=[],
        your_cat: Cat=None,
        the_cat: Cat=None,
        cat_dict={},
        key=""
        ):
    """
    Selects random cats for LG stuff!
    :param block: A dictionary containing content to be filtered. This is the "cats" block, not its parent.
    :param block: A dictionary containing relationships to be filtered for. This is the "relationships" block, not its parent.
    :param your_cat: Cat object for your cat.
    :param the_cat: Cat object for the talking cat. Outside of dialogue, this is None.
    :param cat_dict: Dict containing existing abbrevs and Cat objects as key-value pairs.
    :param key: Optional content key to pass for debugging.

    """
    possible_cats = Cat.all_cats_list.copy()
    chosen_cat_dict = {}
    abbrevs = []

    # try:
    if cats_block:
        if "y_c" not in cats_block:
            cats_block["y_c"] = {}
        for abbrev in cats_block:
            abbrevs.append(abbrev)
            # checks if there are any valid cats available
            possible_cats_dict[abbrev] = _validate_cat(
                abbrev,
                cats_block,
                possible_cats,
                your_cat,
                the_cat,
                key=key
                )
            if not possible_cats_dict[abbrev]:
                return {}

    for abbrev, cat_object in cat_dict.items():
        if abbrev not in possible_cats_dict:
            possible_cats_dict[abbrev] = [cat_object]

    # filter rel uses all abbrevs to make choices based on relationships
    # chosen cat dict is the selected cats! one cat object per abbrev!
    chosen_cat_dict = __filter_relationships(
        abbrevs,
        rel_block,
        possible_cats_dict,
        your_cat,
        the_cat,
        cat_dict
        )
    # except Exception as e:
    #     print("WARNING: Error with filtering for", key)
    #     print(e)
    return chosen_cat_dict

def _validate_cat(abbrev, cat_block, possible_cats, your_cat, the_cat, key=""):
    """
    Validates each cat block.
    Helper functions will narrow down the possible cat options.
    For r_c, a final choice is made at the end.
    For t_c and y_c, if the_cat or your_cat are not in the possible cat options,
    the dialogue is filtered out.
    """
    new_possible_cats = []

    # filtering functions!
    for cat in possible_cats:
        if not __filter_dead(cat_block[abbrev], cat):
            continue
        if not __filter_age(cat_block[abbrev], cat):
            continue
        if not __filter_rank(cat_block[abbrev], cat):
            continue

        # PG
        if not __filter_sexuality(cat_block[abbrev], cat):
            continue

        if not __filter_group(cat_block[abbrev], cat, your_cat):
            continue
        if not __filter_standing(cat_block[abbrev], cat, your_cat):
            continue

        if not __filter_skill(cat_block[abbrev], cat):
            continue
        if not __filter_cluster(cat_block[abbrev], cat):
            continue
        if not __filter_backstory(cat_block[abbrev], cat):
            continue
        if not __filter_faith(cat_block[abbrev], cat):
            continue

        if not __filter_conditions(cat_block[abbrev], cat):
            continue

        if "focus_cat" in cat_block[abbrev]:
            if cat_block[abbrev]["focus_cat"] and cat.ID != game.clan.focus_cat:
                continue
            elif not cat_block[abbrev]["focus_cat"] and cat.ID == game.clan.focus_cat:
                continue

        new_possible_cats.append(cat)

    if abbrev == "t_c" and the_cat not in new_possible_cats:
        return []
    if abbrev == "y_c" and your_cat not in new_possible_cats:
        return []

    possible_cat_dict = {}
    possible_cat_dict[abbrev] = new_possible_cats

    return new_possible_cats

    # ---------------------------------------------------------------------- #
    #                          CAT FILTERING FUNCTIONS                       #
    # ---------------------------------------------------------------------- #

def __filter_dead(abbrev_block, cat):
    if "min_max_dead_moons" in abbrev_block:
        if (
            abbrev_block["min_max_dead_moons"][0] > cat.dead_for or
            abbrev_block["min_max_dead_moons"][1] < cat.dead_for
        ):
            return False
    if "residence" in abbrev_block:
        if not cat.dead:
            return False
        else:
            if "any" not in abbrev_block["residence"]:
                if (
                    "df" not in abbrev_block["residence"] and
                    cat.status.group_ID == CatGroup.DARK_FOREST_ID
                    ):
                    return False
                elif (
                    "sc" not in abbrev_block["residence"] and
                    cat.status.group_ID == CatGroup.STARCLAN_ID
                    ):
                    return False
                elif (
                    "ur" not in abbrev_block["residence"] and
                    cat.status.group_ID == CatGroup.UNKNOWN_RESIDENCE_ID
                    ):
                    return False
    else:
        if cat.dead:
            return False
    return True

def __filter_group(abbrev_block, cat, your_cat):
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
            ) or 
            (
                f"-{cat.status.group}" in abbrev_block["group"]
            ) or 
            (
                "your_group" in abbrev_block["group"] and
                not cat.status.group == your_cat.status.group
            )
        ):
            return False
    else:
        if "residence" not in abbrev_block and cat.status.group != your_cat.status.group:
            return False
    return True

def __filter_standing(abbrev_block, cat, your_cat):
    if "standing" not in abbrev_block:
        if cat.status.is_shunned() and random.randint(1,4) != 1:
            # hack
            return False
        return True

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
        return False

    return True

def __filter_age(abbrev_block, cat):
    if "age" not in abbrev_block:
        return True

    if f"not_{cat.age}" in abbrev_block["age"]:
        return False
    if "not_kitten" in abbrev_block["age"] and cat.age == CatAge.NEWBORN:
        return False
    if f"-{cat.age}" in abbrev_block["age"]:
        return False
    if cat.age not in abbrev_block["age"]:
        return False
    if any(age in abbrev_block for age in (
        CatAge.NEWBORN, CatAge.KITTEN, CatAge.ADOLESCENT,
        CatAge.YOUNG_ADULT, CatAge.ADULT, CatAge.SENIOR_ADULT, CatAge.SENIOR
    )):
        if cat.age not in abbrev_block["age"]:
            return False

    return True

def __filter_rank(abbrev_block, cat):
    if "rank" not in abbrev_block:
        return True
    if (
        f"not_{cat.status.rank}" in abbrev_block["rank"] or
        f"not_{cat.status.rank.replace(' ', '_')}" in abbrev_block["rank"] or
        f"-{cat.status.rank.replace}" in abbrev_block["rank"]
        ):
        return False
    elif (
        "df_trainee" in abbrev_block["rank"]
        ):
        if not cat.joined_df:
            return False
    elif (
        "not_df_trainee" in abbrev_block["rank"]
        ):
        if cat.joined_df:
            return False
    elif (
        "guide" in abbrev_block["rank"]
        ):
        if cat not in (game.clan.instructor, game.clan.demon):
            return False
    elif abbrev_block['rank']:
        if (
            cat.status.rank not in abbrev_block["rank"] and
            cat.status.rank.replace(' ', '_') not in abbrev_block["rank"]
            ):
            return False
    return True

# PG
def __filter_sexuality(abbrev_block, cat):
    gender_block = abbrev_block["gender"] if "gender" in abbrev_block else []
    sexuality_block = abbrev_block["sexuality"] if "sexuality" in abbrev_block else []

    if not sexuality_block and not gender_block:
        return True
    
    vanilla_tags = [
        "likes_she_cats",
        "not:likes_she_cats",
        "likes_toms",
        "not:likes_toms",
        "likes_any",
        Acespec.ALLO,
        Acespec.DEMI,
        Acespec.GREY,
        Acespec.ACE,
        Arospec.ALLO,
        Arospec.DEMI,
        Arospec.GREY,
        Arospec.ARO,
        "cisgender",
        "transgender",
        "nonbinary",
        "binary",
        "male",
        "female",
        "not:male",
        "not:female"
    ]
    
    # sexuality
    if "likes_she_cats" in sexuality_block and not cat.sexuality.likes_she_cats:
        return False
    if "not:likes_she_cats" in sexuality_block and cat.sexuality.likes_she_cats:
        return False
    
    if "likes_toms" in sexuality_block and not cat.sexuality.likes_toms:
        return False
    if "not:likes_toms" in sexuality_block and cat.sexuality.likes_toms:
        return False
    
    if "likes_any" in sexuality_block and not (cat.sexuality.likes_toms or cat.sexuality.likes_she_cats):
        return False
    
    if any(tag in sexuality_block for tag in [
        Acespec.ALLO,
        Acespec.DEMI,
        Acespec.GREY,
        Acespec.ACE
    ]):
        if cat.sexuality.acespec not in sexuality_block:
            return False
    if any(tag in sexuality_block for tag in [
        Arospec.ALLO,
        Arospec.DEMI,
        Arospec.GREY,
        Arospec.ARO
    ]):
        if cat.sexuality.arospec not in sexuality_block:
            return False
    
    # gender
    if "cisgender" in gender_block and cat.gender != cat.genderalign:
        return False
    if "transgender" in gender_block and cat.gender == cat.genderalign:
        return False
    if "nonbinary" in gender_block and cat.genderalign in (Sexuality.male_genders + Sexuality.female_genders):
        return False
    if "binary" in gender_block and cat.genderalign not in (Sexuality.male_genders + Sexuality.female_genders):
        return False
    if "female" in gender_block and cat.genderalign not in Sexuality.female_genders:
        return False
    if "male" in gender_block and cat.genderalign not in Sexuality.male_genders:
        return False
    if "not:female" in gender_block and cat.genderalign in Sexuality.female_genders:
        return False
    if "not:male" in gender_block and cat.genderalign in Sexuality.male_genders:
        return False
    
    # other tags
    if not any(tag in sexuality_block + gender_block for tag in vanilla_tags):
        if not (
            cat.sexuality.sexuality_label or
            cat.sexuality.acespec_label or
            cat.sexuality.arospec_label or
            cat.genderalign
        ) in sexuality_block + gender_block:
            return False
    return True

def __filter_skill(abbrev_block, cat):
    if "skill" not in abbrev_block:
        return True
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
        return False
    return True

def __filter_cluster(abbrev_block, cat):
    if "cluster" not in abbrev_block:
        return True
    cluster1, cluster2 = get_cluster(cat.personality.trait)
    if (
        cluster1 not in abbrev_block["cluster"] and
        cluster2 not in abbrev_block["cluster"] and
        cat.personality.trait not in abbrev_block["cluster"]
    ):
        return False

    return True

def __filter_backstory(abbrev_block, cat):

    if "backstory" not in abbrev_block:
        return True

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

    backstory_found = False
    for tag in abbrev_block["backstory"]:
        if tag in backstory_tag_dict:
            if cat.backstory in (
                BACKSTORIES["backstory_categories"][backstory_tag_dict[tag]]
                ):
                backstory_found = True
                break
            if f"-{cat.backstory}" in (
                BACKSTORIES["backstory_categories"][backstory_tag_dict[tag]]
                ):
                break
        elif tag == cat.backstory:
            backstory_found = True
            break
    if not backstory_found:
        return False

    return True

def __filter_faith(abbrev_block, cat):
    if "min_max_faith" not in abbrev_block:
        return True
    if (
        abbrev_block["min_max_faith"][0] > cat.faith or
        abbrev_block["min_max_faith"][1] < cat.faith
    ):
        return False
    return True

def __filter_conditions(abbrev_block, cat):
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
                    return False
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
                    return False

                # gen injury/illness
                if condition == "injury" and born_with == "any":
                    if not cat.is_injured():
                        return False
                if condition == "illness" and born_with == "any":
                    if not cat.is_ill():
                        return False
                if condition == "injury" and born_with == "none":
                    if cat.is_injured():
                        return False
                if condition == "illness" and born_with == "none":
                    if cat.is_ill():
                        return False

                # now blind/deaf
                if exclusive == "true" and condition not in cat.permanent_condition:
                    return False

                if born_with == "true":
                    if not (
                        condition in cat.permanent_condition and
                        cat.permanent_condition[condition]["born_with"] is True
                    ):
                        return False
                elif born_with == "false":
                    if not (
                        condition in cat.permanent_condition and
                        cat.permanent_condition[condition]["born_with"] is False
                    ):
                        return False
            else:
                if tag == "hearing":
                    if "deaf" in cat.permanent_condition:
                        deaf_tagged = False
                        return False
                elif tag in exclusive_conditions:
                    if not (
                        tag in cat.permanent_condition or
                        tag in cat.injuries or
                        tag in cat.illnesses
                    ):
                        return False
                else:
                    reg_tagged = True
                    if (
                        tag in cat.permanent_condition or
                        tag in cat.injuries or
                        tag in cat.illnesses
                    ):
                        condition_true = True
                        break

    if "blind" in cat.permanent_condition and not blind_tagged:
        return False
    if (
            (
                "deaf" in cat.permanent_condition and
                cat.permanent_condition["deaf"]["born_with"] is True
            )
            and not deaf_tagged
        ):
        return False

    if reg_tagged and not condition_true:
        return False

    return True

def __filter_relationships(all_abbrevs, rel_block, dict_possible_cats, your_cat, the_cat, cat_dict):
    """
    Chooses final cats based on relationship constraints.
    Not a 'filter' in the same way the other filter functions are. More of a selection tool.
    """
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
                    to_cat_list = dict_possible_cats[TO].copy() if TO in dict_possible_cats else Cat.all_cats_list.copy()
                    from_cat_list = dict_possible_cats[FROM].copy() if FROM in dict_possible_cats else Cat.all_cats_list.copy()

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
                            if not to_cat:
                                print("to_cat in list is None! Report to Jay!")
                                print(to_cat_list)
                                print(rel_block)
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
                                # PG
                                elif rel_tag == "qpps":
                                    rel_valid = to_cat.ID in from_cat.qpp
                                elif rel_tag == "non-qpps":
                                    rel_valid = to_cat.ID not in from_cat.qpp
                                # ---
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
                                    rel_valid = from_cat.is_cousin(to_cat)
                                elif rel_tag == "adopted siblings":
                                    rel_valid = from_cat.ID in to_cat.inheritance.get_no_blood_siblings()
                                elif rel_tag == "parent's sibling/sibling's kit":
                                    rel_valid = from_cat.is_uncle_aunt(to_cat)
                                elif rel_tag == "strangers":
                                    if from_cat.ID in to_cat.relationships:
                                        rel_valid = False
                                elif rel_tag == "siblings":
                                    rel_valid = from_cat.is_sibling(to_cat)
                                elif rel_tag == "littermates":
                                    rel_valid = from_cat.is_littermate(to_cat)
                                elif rel_tag == "grandparent/grandchild":
                                    rel_valid = from_cat.is_grandparent(to_cat)
                                elif rel_tag == "grandchild/grandparent":
                                    rel_valid = to_cat.is_grandparent(from_cat)
                                elif rel_tag == "half-siblings":
                                    rel_valid = to_cat.is_half_sibling(from_cat)
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
                                elif rel_tag == "related":
                                    rel_valid = from_cat.is_related(to_cat, get_clan_setting("first cousin mates"))
                                elif rel_tag == "non-related":
                                    rel_valid = not from_cat.is_related(to_cat, get_clan_setting("first cousin mates"))

                                elif rel_tag == "victim/murderer":
                                    if not to_cat.history.murder:
                                        rel_valid = False
                                    elif "is_murderer" not in to_cat.history.murder:
                                        rel_valid = False
                                    else:
                                        rel_valid = False
                                        for murder in to_cat.history.murder["is_murderer"]:
                                            if murder["victim"] == from_cat.ID:
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
                                            if murder["victim"] == to_cat.ID:
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
