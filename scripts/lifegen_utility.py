import ujson
import re
from random import choice
from scripts.game_structure import game
from scripts.cat.enums import (
    CatAge,
    CatRank,
    CatGroup
)
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank, get_living_clan_cat_count
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.screens.enums import GameScreen

def get_cluster(trait):
    """
    Returns the cluster(s) for a given trait.
    """
    with open("resources/dicts/cluster_map.json", "r", encoding="utf-8") as file:
        cluster_map = ujson.load(file)

    clusters = [key for key, values in cluster_map.items() if trait in values]

    # Assign cluster and second_cluster based on the length of clusters list
    cluster = clusters[0] if clusters else "stable"
    second_cluster = clusters[1] if len(clusters) > 1 else ""

    return cluster, second_cluster



# ---------------------------------------------------------------------------- #
#                            LIFEGEN TEXT ABBREVS                              #
# ---------------------------------------------------------------------------- #


def add_to_cat_dict(abbrev, cluster, x, rel, r, abbrev_cat, text, cat_dict):
    """ Adds a cat to the dict, assigning them to their abbrev to be reused in later text. """

    if cluster and rel:
        abbrev_string = f"{r}-{abbrev}-{x}"
    elif cluster and not rel:
        abbrev_string = f"{abbrev}-{x}"
    elif rel and not cluster:
        abbrev_string = f"{r}-{abbrev}"
    else:
        abbrev_string = abbrev

    cat_dict[abbrev_string] = abbrev_cat
    text = re.sub(fr'(?<!\/){abbrev_string}(?!\/)', str(abbrev_cat.name), text)
    
    return text


def abbrev_addons(t_c, r_c, cluster, x, rel, r):
    """ Checks if cluster and relationship adodns are fulfilled.
        x = cluster
        r = relationship value
        cluster and rel are booleans for if the addons are present.
    """

    if (cluster and x not in get_cluster(r_c.personality.trait)):
        return False
    
    if (
        # CHECKMERGE
        # change these to be the rel tiers ("listens_to", "relates_to", "fancies") if i wanna be evil to the writers
            (
            rel and (
                r_c.ID not in t_c.relationships) or
                (r == "plike" and t_c.relationships[r_c.ID].like < 20) or
                (r == "plove" and t_c.relationships[r_c.ID].like < 50) or
                (r == "dislike" and t_c.relationships[r_c.ID].like > -15) or
                (r == "hate" and t_c.relationships[r_c.ID].like > -50) or
                (r == "rlike" and t_c.relationships[r_c.ID].romance < 10) or
                (r == "rlove" and t_c.relationships[r_c.ID].romance < 50) or
                (r == "jealous" and t_c.relationships[r_c.ID].respect < -20) or
                (r == "respect" and t_c.relationships[r_c.ID].respect < 20) or
                (r == "trust" and t_c.relationships[r_c.ID].trust < 20) or
                (r == "comfort" and t_c.relationships[r_c.ID].comfort < 20) or 
                (r == "neutral" and
                ( 
                    (t_c.relationships[r_c.ID].like > 20) or
                    (t_c.relationships[r_c.ID].like < -20) or
                    (t_c.relationships[r_c.ID].romance > 20) or
                    (t_c.relationships[r_c.ID].respect < -20) or
                    (t_c.relationships[r_c.ID].respect > 20) or
                    (t_c.relationships[r_c.ID].trust > 20) or
                    (t_c.relationships[r_c.ID].trust < -20) or
                    (t_c.relationships[r_c.ID].comfort > 20) or
                    (t_c.relationships[r_c.ID].comfort < -20)
                        
                    )
                )
            )
        ):
        return False

def cat_dict_check(abbrev, cluster, x, rel, r, text, cat_dict):
    """ Checks if a cat is in the dict already.
    If so, it will reuse the name in later text.
    If not, it will find a cat for the abbrev."""
    in_dict = False
    try:
        if cluster and rel:
            abbrev_string = f"{r}-{abbrev}-{x}"
        elif cluster and not rel:
            abbrev_string = f"{abbrev}-{x}"
        elif rel and not cluster:
            abbrev_string = f"{r}-{abbrev}"
        else:
            abbrev_string = abbrev
        if abbrev_string in cat_dict:
            in_dict = True
            text = re.sub(fr'(?<!\/){abbrev_string}(?!\/)', str(cat_dict[abbrev_string].name), text)
    except KeyError as e:
        text = ""
        # returning an empty string to reroll for dialogue
    return text, in_dict

def lifegen_abbrevs(Cat, text, you, cat, chosen_cat, cat_dict):
    """ Checks the requirements for each random cat abbrev.
        Returns a dict of all valid abbrevs """
    abbrevs = {}

    # heres AALLLL the conditions for certain abbrevs to be valid

    current_cat_objects = []
    for abbrev, cat_object in cat_dict.items():
        current_cat_objects.append(cat_object)
        # print("Already in cat dict:", cat_object.name)
    
    current_cat_objects.append(cat)
    current_cat_objects.append(you)

    yourcrush = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.ID in cat.mate or
        chosen_cat.ID in you.mate or
        not chosen_cat.is_dateable(you) or
        len(you.mate) > 0 or
        chosen_cat.status.is_outsider or
        chosen_cat.dead or
        chosen_cat not in you.relationships or
        (chosen_cat in you.relationships and you.relationships[chosen_cat.ID].romance < 20) or
        chosen_cat in current_cat_objects
    ) else True

    theircrush = False if (
        chosen_cat.ID == cat.ID or
        chosen_cat.ID == you.ID or
        chosen_cat.ID in cat.mate or
        chosen_cat.ID in you.mate or
        not chosen_cat.is_dateable(cat) or
        len(cat.mate) > 0 or
        chosen_cat.status.is_outsider or
        chosen_cat.dead or
        chosen_cat not in cat.relationships or
        (chosen_cat in cat.relationships and cat.relationships[chosen_cat.ID].romance < 15) or
        chosen_cat in current_cat_objects
    ) else True

    # Random statuses
    r_c = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        "r_c1" in text or
        "r_c2" in text or
        "r_c3" in text or
        "r_c4" in text or
        chosen_cat.moons < 6 or
        chosen_cat in current_cat_objects
    ) else True

    r_w = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank != CatRank.WARRIOR or
        chosen_cat in current_cat_objects
    ) else True

    r_k = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.age not in [CatAge.KITTEN, CatAge.NEWBORN] or
        chosen_cat in current_cat_objects
    ) else True

    r_a = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank != CatRank.APPRENTICE or
        chosen_cat in current_cat_objects
    ) else True

    r_m = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not chosen_cat.status.rank.is_any_medicine_rank() or
        chosen_cat in current_cat_objects
    ) else True

    r_d = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not chosen_cat.status.rank.is_any_mediator_rank() or
        chosen_cat in current_cat_objects
    ) else True

    r_q = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank not in [CatRank.QUEEN, CatRank.QUEENS_APPRENTICE] or
        chosen_cat in current_cat_objects
    ) else True

    r_e = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank != CatRank.ELDER or
        chosen_cat in current_cat_objects
    ) else True

    # Random statuses-- Shunned
    rsh_c = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not chosen_cat.status.is_shunned() or
        chosen_cat in current_cat_objects
    ) else True

    rsh_w = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank != CatRank.WARRIOR or
        not chosen_cat.status.is_shunned() or
        chosen_cat in current_cat_objects
    ) else True

    rsh_k = False if (
        not r_k or
        (r_k and not chosen_cat.status.is_shunned()) 
    ) else True

    rsh_a = False if (
        not r_a or
        (r_a and not chosen_cat.status.is_shunned()) 
    ) else True

    rsh_m = False if (
        not r_m or
        (r_m and not chosen_cat.status.is_shunned()) 
    ) else True

    rsh_d = False if (
        not r_d or
        (r_d and not chosen_cat.status.is_shunned()) 
    ) else True

    rsh_q = False if (
        not r_q or
        (r_q and not chosen_cat.status.is_shunned()) 
    ) else True

    rsh_e = False if (
        not r_e or
        (r_e and not chosen_cat.status.is_shunned()) 
    ) else True

    # Random sick cat
    r_s = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not chosen_cat.is_ill() or
        chosen_cat in current_cat_objects
    ) else True

    # Random injured cat
    r_i = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not chosen_cat.is_injured() or
        chosen_cat in current_cat_objects
    ) else True

    # Random grieving cat
    r_g = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        "grief stricken" not in chosen_cat.illnesses or
        chosen_cat in current_cat_objects
    ) else True

    # Your sibling-- any age
    y_s = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in you.inheritance.get_siblings() or
        chosen_cat in current_cat_objects
    ) else True

    # Your littermate
    y_l = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in you.inheritance.get_siblings() or
        chosen_cat.moons != you.moons or
        chosen_cat in current_cat_objects
    ) else True

    # Their sibling-- any age
    t_s = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in cat.inheritance.get_siblings() or
        chosen_cat in current_cat_objects
    ) else True

    # Their littermate
    t_l = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in cat.inheritance.get_siblings() or
        chosen_cat.moons != cat.moons or
        chosen_cat in current_cat_objects
    ) else True

    # Your apprentice
    y_a = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in you.apprentice or
        chosen_cat in current_cat_objects
    ) else True

    # Their apprentice
    t_a = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in cat.apprentice or
        chosen_cat in current_cat_objects
    ) else True

    # Your parent
    y_p = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in you.inheritance.get_parents() or
        chosen_cat in current_cat_objects
    ) else True

    # Their parent
    t_p = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in cat.inheritance.get_parents() or
        chosen_cat in current_cat_objects
    ) else True

    # Your mate
    y_m = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in you.mate or
        chosen_cat in current_cat_objects
    ) else True

    # Their mate
    t_m = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in cat.mate or
        chosen_cat in current_cat_objects
    ) else True

    # nr_1/2 -- Two cats who are potential mates
    n_r1 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        len(chosen_cat.mate) > 0 or
        chosen_cat.moons < 14 or
        "n_r2" not in text or
        chosen_cat in current_cat_objects
    ) else True

    # Gather cat object for first n_r cat
    n_r1_object = None
    for i in cat_dict.items():
        if i[0] == "n_r1":
            n_r1_object = i[1]
            break

    n_r2 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        len(chosen_cat.mate) > 0 or
        (n_r1_object and not chosen_cat.is_potential_mate(n_r1_object)) or
        n_r1_object is None or
        chosen_cat in current_cat_objects
    ) else True

    # Random cats
    
    r_c1 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat in current_cat_objects
    ) else True
    
    r_c2 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat in current_cat_objects
    ) else True
    
    r_c3 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat in current_cat_objects
    ) else True
    
    r_c4 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat in current_cat_objects
    ) else True

    # Random warriors
    r_w1 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank != CatRank.WARRIOR or
        chosen_cat in current_cat_objects
    ) else True
    
    r_w2 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank != CatRank.WARRIOR or
        chosen_cat in current_cat_objects
    ) else True
    
    r_w3 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank != CatRank.WARRIOR or
        chosen_cat in current_cat_objects
    ) else True
    
    r_w4 = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.status.rank != CatRank.WARRIOR or
        chosen_cat in current_cat_objects
    ) else True

    # Their kits
    # any age
    t_k = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in cat.inheritance.get_children() or
        chosen_cat in current_cat_objects
    ) else True

    # kit age
    t_kk = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in cat.inheritance.get_children() or
        chosen_cat.moons > 5 or
        chosen_cat in current_cat_objects
    ) else True

    # adult age
    t_ka = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in cat.inheritance.get_children() or
        chosen_cat.moons < 12 or
        chosen_cat in current_cat_objects
    ) else True
    
    # Your kits
    # any age
    y_k = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in you.inheritance.get_children() or
        chosen_cat in current_cat_objects
    ) else True

    # kit age
    y_kk = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in you.inheritance.get_children() or
        chosen_cat.moons > 5 or
        chosen_cat in current_cat_objects
    ) else True

    # adult age
    y_ka = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID not in you.inheritance.get_children() or
        chosen_cat.moons < 12 or
        chosen_cat in current_cat_objects
    ) else True

    # Mentors
    # Your DF mentor
    df_m_n = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        not chosen_cat.status.group == CatGroup.DARK_FOREST or
        chosen_cat.ID != you.df_mentor or
        chosen_cat in current_cat_objects
    ) else True

    # Their DF mentor
    t_df_mn = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        not chosen_cat.dead or
        not chosen_cat.status.group == CatGroup.DARK_FOREST or
        chosen_cat.ID != cat.df_mentor or
        chosen_cat in current_cat_objects
    ) else True

    # Your mentor
    m_n = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID != you.mentor or
        chosen_cat in current_cat_objects
    ) else True

    # Their mentor
    tm_n = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        chosen_cat.ID != cat.mentor or
        chosen_cat in current_cat_objects
    ) else True

    # Leader
    l_n = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not game.clan.leader or
        chosen_cat.ID != game.clan.leader.ID or
        chosen_cat in current_cat_objects
    ) else True

    # Deputy
    d_n = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not game.clan.deputy or
        chosen_cat.ID != game.clan.deputy.ID or
        chosen_cat in current_cat_objects
    ) else True

    # Leader-- Shunned
    sh_l = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not game.clan.leader or 
        chosen_cat.ID != game.clan.leader or
        not chosen_cat.status.is_shunned() or
        chosen_cat in current_cat_objects
    ) else True

    # Deputy-- Shunned
    sh_d = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        chosen_cat.status.is_outsider or
        not game.clan.deputy or
        chosen_cat.ID != game.clan.deputy or
        not chosen_cat.status.is_shunned() or
        chosen_cat in current_cat_objects
    ) else True

    # Dead cat of any residence
    d_c = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        not chosen_cat.dead or
        chosen_cat in current_cat_objects
    ) else True

    # Random DF cat
    rdf_c = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        not chosen_cat.dead or
        not chosen_cat.status.group == CatGroup.DARK_FOREST or
        chosen_cat in current_cat_objects
    ) else True

    # Random UR cat
    rur_c = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        not chosen_cat.dead or
        not chosen_cat.status.is_outsider or
        chosen_cat in current_cat_objects
    ) else True

    # Random SC cat
    rsc_c = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        not chosen_cat.dead or
        chosen_cat.status.group == CatGroup.DARK_FOREST or
        chosen_cat.status.is_outsider or
        chosen_cat in current_cat_objects
    ) else True

    # Lost cat
    l_c = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        not chosen_cat.status.is_lost() or
        chosen_cat in current_cat_objects
    ) else True

    # Exiled cat
    e_c = False if (
        chosen_cat.ID == you.ID or
        chosen_cat.ID == cat.ID or
        chosen_cat.dead or
        not chosen_cat.status.is_exiled(game.clan.your_cat.status.group_ID) or
        chosen_cat in current_cat_objects
    ) else True

    # Talk focus cat
    fc_c = False if (
        chosen_cat.ID != game.clan.focus_cat
    ) else True

    # grief cats
    tg_c = False if (
        "grief stricken" not in cat.illnesses or 
        "grief stricken" in cat.illnesses and "grief_cat" not in cat.illnesses["grief stricken"] or
        chosen_cat.ID != cat.illnesses["grief stricken"]["grief_cat"] or
        chosen_cat in current_cat_objects
    ) else True

    yg_c = False if (
        "grief stricken" not in you.illnesses or 
        "grief stricken" in you.illnesses and "grief_cat" not in you.illnesses["grief stricken"] or
        chosen_cat.ID != you.illnesses["grief stricken"]["grief_cat"] or
        chosen_cat in current_cat_objects
    ) else True

    v_c = False if (
        not game.clan.murdered or
        ("victim" in game.clan.murdered and chosen_cat.ID != game.clan.murdered["victim"])
    ) else True

    # now the abbrevs dict!
    # make sure to add new abbrevs here, or they won't get replaced!!!
    abbrevs = {
        "yourcrush": yourcrush,
        "theircrush": theircrush,
        "r_k": r_k,
        "r_c": r_c,
        "r_w": r_w,
        "r_a": r_a,
        "r_m": r_m,
        "r_d": r_d,
        "r_q": r_q,
        "r_e": r_e,
        "rsh_k": rsh_k,
        "rsh_c": rsh_c,
        "rsh_w": rsh_w,
        "rsh_a": rsh_a,
        "rsh_m": rsh_m,
        "rsh_d": rsh_d,
        "rsh_q": rsh_q,
        "rsh_e": rsh_e,
        "n_r1": n_r1,
        "n_r2": n_r2,
        "r_c1": r_c1,
        "r_c2": r_c2,
        "r_c3": r_c3,
        "r_c4": r_c4,
        "r_w1": r_w1,
        "r_w2": r_w2,
        "r_w3": r_w3,
        "r_w4": r_w4,
        "r_s": r_s,
        "r_i": r_i,
        "r_g": r_g,
        "y_s": y_s,
        "y_l": y_l,
        "t_s": t_s,
        "t_l": t_l,
        "y_a": y_a,
        "t_a": t_a,
        "y_p": y_p,
        "t_p": t_p,
        "y_m": y_m,
        "t_m": t_m,
        "t_k": t_k,
        "t_kk": t_kk,
        "t_ka": t_ka,
        "y_k": y_k,
        "y_kk": y_kk,
        "y_ka": y_ka,
        "df_m_n": df_m_n,
        "t_df_mn": t_df_mn,
        "m_n": m_n,
        "tm_n": tm_n,
        "l_n": l_n,
        "d_n": d_n,
        "sh_l": sh_l,
        "sh_d": sh_d,
        "d_c": d_c,
        "rdf_c": rdf_c,
        "rur_c": rur_c,
        "rsc_c": rsc_c,
        "l_c": l_c,
        "e_c": e_c,
        "fc_c": fc_c,
        "tg_c": tg_c,
        "yg_c": yg_c,
        "v_c": v_c
    }

    return abbrevs

other_dict = {}   
def lifegen_text_adjust(Cat, text, cat, cat_dict, r_c_allowed, o_c_allowed):
    """ Adjusts dialogue text by replacing abbreviations with cat names
    :param Cat Cat: Cat class
    :param list text: The text being processed 
    :param Cat cat: The object of the cat to whom relationship addons will apply
    :param Dict cat_dict: the dict of cat objects
    :param bool r_c_allowed: Whether or not r_c will be tried for. True for dialogue, False for patrols
    :param bool o_c_allowed: Whether or not o_c will be tried for. True for dialogue, False for patrols
    """

    COUNTER_LIM = 30
    you = game.clan.your_cat
    alive_cats = Cat.all_cats_list
    if len(alive_cats) == 0:
        return ""
    chosen_cat = choice(alive_cats)

    # this is a throwaway cat just so i can grab the abbrevs dict
    abbrevs = lifegen_abbrevs(Cat, text, you, cat, chosen_cat, cat_dict)

    for abbrev_string in abbrevs.keys():
        if abbrev_string in text:
            # dialogue-specific stuff: don't replace an abbrev if its in between | |
            if "|" in text:
                if abbrev_string in text.split("|")[1]:
                    # text = text.split("|")[-1]
                    continue
            
            # ---
            # first, go away if r_c and o_c are being disallowed for clangen reasons
            if abbrev_string == "r_c" and r_c_allowed is False:
                return ""
            if abbrev_string == "o_c" and o_c_allowed is False:
                return ""
            
            # some tomfoolery for abbrevs that might conflict with each other
            if abbrev_string == "r_c" and any(ab in text for ab in ["r_c1", "r_c2", "r_c3", "r_c4"]):
                continue
            if abbrev_string == "r_w" and any(ab in text for ab in ["r_w1", "r_w2", "r_w3", "r_w4"]):
                continue
            if abbrev_string == "t_k" and "t_ka" in text:
                continue
            if abbrev_string == "t_k" and "t_kk" in text:
                continue
            if abbrev_string == "m_n" and "tm_n" in text:
                continue

            # find cluster and rel addons if theyre there
            cluster = False
            rel = False
            match = re.search(fr'{abbrev_string}\-(\w+)', text)
            if match:
                x = match.group(1)
                cluster = True
            else:
                x = ""
            match2 = re.search(fr'(\w+)\-{abbrev_string}', text)
            if match2:
                r = match2.group(1)
                rel = True
            else:
                r = ""

            # Check if the abbrev is already in use
            text, in_dict = cat_dict_check(abbrev_string, cluster, x, rel, r, text, cat_dict)
            if in_dict is False:
                cat_choices = []

                # Grab the right selection of cats to narrow down the options before the counter starts
                if abbrev_string in ["r_w", "r_w1", "r_w2", "r_w3", "r_w4", "rsh_w"]:
                    cat_choices = find_alive_cats_with_rank(Cat, [CatRank.WARRIOR])
                elif abbrev_string in ["r_a", "rsh_a"]:
                    cat_choices = find_alive_cats_with_rank(Cat, [CatRank.APPRENTICE])
                elif abbrev_string in ["r_m", "rsh_m"]:
                    cat_choices = find_alive_cats_with_rank(Cat, [CatRank.MEDICINE_APPRENTICE, CatRank.MEDICINE_CAT])
                elif abbrev_string in ["r_d", "rsh_d"]:
                    cat_choices = find_alive_cats_with_rank(Cat, [CatRank.MEDIATOR, CatRank.MEDIATOR_APPRENTICE])
                elif abbrev_string in ["r_q", "rsh_q"]:
                    cat_choices = find_alive_cats_with_rank(Cat, [CatRank.QUEEN, CatRank.QUEENS_APPRENTICE])
                elif abbrev_string in ["r_e", "rsh_e"]:
                    cat_choices = find_alive_cats_with_rank(Cat, [CatRank.ELDER])
                elif abbrev_string in ["d_n", "sh_d"]:
                    cat_choices = find_alive_cats_with_rank(Cat, [CatRank.DEPUTY])
                elif abbrev_string in ["l_n", "sh_l"]:
                    cat_choices = find_alive_cats_with_rank(Cat, [CatRank.LEADER])
                elif abbrev_string in ["t_k", "t_kk", "t_ka"]:
                    for cat_id in cat.inheritance.get_children():
                        cat_choices.append(Cat.fetch_cat(cat_id))
                elif abbrev_string in ["y_k", "y_kk", "y_ka"]:
                    for cat_id in you.inheritance.get_children():
                        cat_choices.append(Cat.fetch_cat(cat_id))
                elif abbrev_string in ["tm_n"]:
                    cat_choices.append(Cat.fetch_cat(cat.mentor))
                elif abbrev_string in ["m_n"]:
                    cat_choices.append(Cat.fetch_cat(you.mentor))
                elif abbrev_string in ["df_m_n"]:
                    cat_choices.append(Cat.fetch_cat(you.df_mentor))
                elif abbrev_string in ["t_df_mn"]:
                    cat_choices.append(Cat.fetch_cat(cat.df_mentor))
                elif abbrev_string in ["y_a"]:
                    for cat_id in you.apprentice:
                        cat_choices.append(Cat.fetch_cat(cat_id))
                elif abbrev_string in ["t_a"]:
                    for cat_id in cat.apprentice:
                        cat_choices.append(Cat.fetch_cat(cat_id))
                elif abbrev_string in ["y_m"]:
                    for cat_id in you.mate:
                        cat_choices.append(Cat.fetch_cat(cat_id))
                elif abbrev_string in ["t_m"]:
                    for cat_id in cat.mate:
                        cat_choices.append(Cat.fetch_cat(cat_id))
                elif abbrev_string in ["rdf_c", "d_c", "rur_c", "rsc_c"]:
                    cat_choices = [i for i in Cat.all_cats_list if i.dead]
                elif abbrev_string in ["tg_c"]:
                    cat_choices = (
                        [Cat.fetch_cat(cat.illnesses['grief stricken']["grief_cat"])]
                        ) if (
                            "grief stricken" in cat.illnesses and
                            "grief_cat" in cat.illnesses['grief stricken']
                            ) else []
                elif abbrev_string in ["yg_c"]:
                    cat_choices = (
                        [Cat.fetch_cat(game.clan.your_cat.illnesses['grief stricken']["grief_cat"])]
                        ) if (
                            "grief stricken" in game.clan.your_cat.illnesses and
                            "grief_cat" in game.clan.your_cat.illnesses['grief stricken']
                            ) else []
                else:
                    if abbrev_string not in abbrevs:
                        print("Unknown LifeGen abbrev:", abbrev_string)
                    cat_choices = alive_cats

                if cat_choices is None:
                    cat_choices = [] # whatever

                try:
                    alive_cat = choice(cat_choices)
                except IndexError:
                    return ""

                if alive_cat is None:
                    return ""

                new_abbrevs = lifegen_abbrevs(Cat, text, you, cat, alive_cat, cat_dict)
                for string, value in new_abbrevs.items():
                    if string == abbrev_string:
                        new_abbrev_string = string
                        abbrev_bool = value
                        break
                    else:
                        continue

                addon_check = abbrev_addons(cat, alive_cat, cluster, x, rel, r)
                counter = 0
                while abbrev_bool is False or addon_check is False:
                    alive_cat = choice(cat_choices)
                    new_abbrevs = lifegen_abbrevs(Cat, text, you, cat, alive_cat, cat_dict)
                    for string, value in new_abbrevs.items():
                        if string == abbrev_string:
                            new_abbrev_string = string
                            abbrev_bool = value
                            break
                        else:
                            continue
                    addon_check = abbrev_addons(cat, alive_cat, cluster, x, rel, r)
                    counter += 1
                    if counter >= 30:
                        return ""
                if game.current_screen == GameScreen.PATROL and switch_get_value(Switch.patrol_category) == "date" and new_abbrev_string == "r_c":
                    continue
                else:
                    text = add_to_cat_dict(new_abbrev_string, cluster, x, rel, r, alive_cat, text, cat_dict)
    # Other Clan
    if o_c_allowed is True:
        if "o_c_n" in text:
            if "o_c_n" in other_dict:
                text = re.sub(r'(?<!\/)o_c_n(?!\/)', str(other_dict["o_c_n"].name) + "Clan", text)
            else:
                other_clan = choice(game.clan.all_other_clans)
                if not other_clan:
                    return ""
                other_dict["o_c_n"] = other_clan
                text = re.sub(r'(?<!\/)o_c_n(?!\/)', str(other_clan.name) + "Clan", text)
    # Warring Clan
    if "w_cClan" in text:
        if "at_war" in game.clan.war:
            if not game.clan.war["at_war"]:
                return ""
        else:
            return ""
        text = text.replace("w_c", str(game.clan.war["enemy"]))

    return text

def check_achievements(Cat, eventspage=False):
    you = game.clan.your_cat
    achievements = set()
    murder_history = you.history.murder
    count_alive_cats = 0
    if murder_history:
        if 'is_murderer' in murder_history:
            num_victims = len(murder_history["is_murderer"])
            if num_victims >= 0:
                achievements.add("1")
            if num_victims >= 5:
                achievements.add("2")
            if num_victims >= 20:
                achievements.add("3")
            if num_victims >= 50:
                achievements.add("4")
    else:
        if you.moons >= 120:
            achievements.add("25")
        

    for cat in Cat.all_cats_list:
        if cat.moons >= 0:
            if cat.pelt.tortie_base and cat.gender == 'male':
                achievements.add("5")
            if cat.insulted:
                achievements.add("29")
            if (cat.name.prefix == "Coffee" and cat.name.suffix == "dot") or (cat.name.prefix == "Chibi" and cat.name.suffix == "Galaxies"):
                achievements.add("30")
            if cat.status.rank == CatRank.APPRENTICE and cat.name.prefix == "Pea" and cat.pelt.white_colours:
                achievements.add("33")
            if cat.status.rank == CatRank.KITTEN and cat.moons > 6:
                achievements.add("34")
            if cat.backstory == 'dfkit' or cat.backstory == 'dfkit2':
                achievements.add("35")
            ##WILDCARD check, because I've lost control of my life
            ##Actual check for wildcardness
            if cat.pelt.is_wildcard_tortie():
                achievements.add("6")

            ##code block for achievement 31
            achieve31RankList = [CatRank.MEDIATOR, CatRank.WARRIOR, CatRank.LEADER]
            achieve31UsedRanks = []
            if len(cat.mate) >= 2:
                catMateIDs = cat.mate.copy()
                if cat.status.rank in achieve31RankList:
                    achieve31UsedRanks.append(cat.status.rank)
                    for cat in Cat.all_cats_list:
                        if cat.ID in catMateIDs:
                            if (cat.status.rank in achieve31RankList) and (cat.status.rank not in achieve31UsedRanks):
                                achieve31UsedRanks.append(cat.status.rank)
                        countranks = 0
                        for i in achieve31UsedRanks:
                            if i in achieve31RankList:
                                countranks += 1
                            if countranks >= 3:
                                achievements.add("31")
            ##achievement block to check MC has a df mate for achieve 36. Not a copy of above code. Above code checks for Any cats
            mcMateIDs = you.mate 
            #for loop list is in case you have multiple mates to search through. 
            for i in mcMateIDs:
                if cat.ID in mcMateIDs and you.dead is False:
                    #Thank you Jay, for helping me figure out history stuff! 
                    if cat.history:
                        if cat.history.beginning:
                            if "encountered" in cat.history.beginning and cat.history.beginning["encountered"] is True and cat.df is True:
                                achievements.add("36")
            #code for achievement 23 + 24
            if game.clan.age >= 1:
                if get_living_clan_cat_count(Cat) == 0:
                    achievements.add('40')
                elif get_living_clan_cat_count(Cat) == 1 and you.status.alive_in_player_clan:
                    achievements.add('23')
                elif get_living_clan_cat_count(Cat) >= 100:
                    achievements.add('24')
                elif get_living_clan_cat_count(Cat) >= 400:
                    achievements.add('39')

    if you.joined_df:
        achievements.add("7")
    
    if len(you.former_apprentices) >= 1:
        achievements.add("8")
    if len(you.former_apprentices) >= 5:
        achievements.add("9")
    
    if you.inheritance.get_children():
        achievements.add("10")
    for i in you.relationships.keys():
        if you.relationships.get(i).like <= -60:
            achievements.add("11")
        if you.relationships.get(i).romance >= 60:
            achievements.add('12')
        
    if len(you.mate) >= 5:
        achievements.add('13')
    if you.status.rank == CatRank.WARRIOR:
        achievements.add('14')
    elif you.status.rank == CatRank.MEDICINE_CAT:
        achievements.add('15')
    elif you.status.rank == CatRank.MEDIATOR:
        achievements.add('16')
    elif you.status.rank == CatRank.DEPUTY:
        achievements.add('17')
    elif you.status.rank == CatRank.LEADER:
        achievements.add('18')
    elif you.status.rank == CatRank.ELDER:
        achievements.add('19')
    elif you.status.rank == CatRank.QUEEN:
        achievements.add('32')
    
    if you.moons >= 200:
        achievements.add('20')
    if you.status.is_exiled(CatGroup.PLAYER_CLAN_ID):
        achievements.add('21')
    elif you.status.is_outsider:
        achievements.add('22')
        
    if you.experience >= 100:
        achievements.add('26')
    if you.experience >= 200:
        achievements.add('27')
    if you.experience >= 300:
        achievements.add('28')

    new_achievements_list = []
    for item in achievements:
        already_earned = False
        for entry in game.clan.achievements:
            if entry[0] == item:
                already_earned = True
                break

        if not already_earned:
            game.clan.achievements.append([item, game.clan.your_cat.ID])
            if eventspage:
                new_achievements_list.append(item)
    if eventspage:
        return new_achievements_list
    
def get_current_camp():
    """ LG """
    if game.clan.your_cat:
        if game.clan.your_cat.status.group in [CatGroup.PLAYER_CLAN, CatGroup.OTHER_CLAN]:
            camp_nr = game.clan.camp_bg
            camp_bg_base_dir = "resources/images/camp_bg/clancat"
        elif game.clan.your_cat.status.group == CatGroup.ROGUE_GROUP:
            camp_nr = game.clan.rogue_group_bg
            camp_bg_base_dir = "resources/images/camp_bg/rogue"
        elif game.clan.your_cat.status.group == CatGroup.LONER_GROUP:
            camp_nr = game.clan.loner_group_bg
            camp_bg_base_dir = "resources/images/camp_bg/loner"
        elif game.clan.your_cat.status.group == CatGroup.HOUSEHOLD:
            camp_nr = game.clan.household_bg
            camp_bg_base_dir = "resources/images/camp_bg/kittypet"
        else:
            camp_nr = game.clan.no_group_bg
            camp_bg_base_dir = "resources/images/camp_bg/none"
    else:
        camp_nr = game.clan.camp_bg
        camp_bg_base_dir = "resources/images/camp_bg/clancat"

    return camp_bg_base_dir, camp_nr

def assign_new_bg(camp):
    """ LG """
    if game.clan.your_cat:
        if game.clan.your_cat.status.group in [CatGroup.PLAYER_CLAN, CatGroup.OTHER_CLAN]:
            game.clan.camp_bg = camp
        elif game.clan.your_cat.status.group == CatGroup.ROGUE_GROUP:
            game.clan.rogue_group_bg = camp
        elif game.clan.your_cat.status.group == CatGroup.LONER_GROUP:
            game.clan.loner_group_bg = camp
        elif game.clan.your_cat.status.group == CatGroup.HOUSEHOLD:
            game.clan.household_bg = camp
        else:
            game.clan.no_group_bg = camp
    else:
        game.clan.camp_bg = camp

# LG
def get_your_cat_group_count(Cat):
    count = 0
    for the_cat in Cat.all_cats.values():
        if not the_cat.status.alive_in_your_cat_group:
            continue
        count += 1
    return count
