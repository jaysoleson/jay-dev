import traceback
from random import choice
from typing import TYPE_CHECKING

<<<<<<< HEAD
import ujson
from scripts.game_structure.game_essentials import game

from scripts.utility import get_cluster
=======
import i18n

from scripts.cat.enums import CatGroup
from scripts.events_module.event_filters import event_for_cat
from scripts.game_structure.localization import load_lang_resource
from scripts.utility import filter_relationship_type

if TYPE_CHECKING:
    from scripts.cat.cats import Cat
>>>>>>> development


class Thoughts:
    @staticmethod
    def thought_fulfill_rel_constraints(main_cat, random_cat, constraint) -> bool:
        """Check if the relationship fulfills the interaction relationship constraints."""
        # if the constraints are not existing, they are considered to be fulfilled
        if not random_cat:
            return False
<<<<<<< HEAD
        
        if random_cat.moons < 0:
            return False
        
=======

        constraint = constraint.copy()
>>>>>>> development
        # No current relationship-value bases tags, so this is commented out.
        relationship = False
        if (
            random_cat.ID in main_cat.relationships
            and main_cat.ID in random_cat.relationships
        ):
            relationship = True

        if "strangers" in constraint and relationship:
            return False
        elif "strangers" in constraint:
            # we remove before further filtering so that filter_relationship_type doesn't scream
            constraint.remove("strangers")

<<<<<<< HEAD
        if "littermates" in constraint and not main_cat.is_littermate(random_cat):
            return False

        if "mates" in constraint and random_cat.ID not in main_cat.mates:
            return False

        if "not_mates" in constraint and random_cat.ID in main_cat.mates:
            return False

        if "parent/child" in constraint and not main_cat.is_parent(random_cat):
            return False

        if "child/parent" in constraint and not random_cat.is_parent(main_cat):
            return False

        if "mentor/app" in constraint and random_cat not in main_cat.apprentice:
            return False

        if "app/mentor" in constraint and random_cat.ID != main_cat.mentor:
            return False

        if "strangers" in constraint and relationship and (
                relationship.platonic_like < 1 or relationship.romantic_love < 1):
=======
        if not filter_relationship_type(
            group=[main_cat, random_cat],
            filter_types=constraint,
        ):
>>>>>>> development
            return False

        return True

    @staticmethod
    def cats_fulfill_thought_constraints(
        main_cat: "Cat", random_cat: "Cat", thought, game_mode, biome, season, camp
    ) -> bool:
        """Check if the two cats fulfills the thought constraints."""

        # This is for checking biome
        if "biome" in thought:
            if biome not in thought["biome"]:
                return False

        # This is checking for season
        if "season" in thought:
            if season not in thought["season"]:
                return False

        # This is for checking camp
        if "camp" in thought:
            if camp not in thought["camp"]:
                return False

        # This is for checking the 'not_working' status
        if "not_working" in thought:
            if thought["not_working"] != main_cat.not_working():
                return False

        # This is for checking if another cat is needed and there is another cat
        r_c_in = [
            thought_str for thought_str in thought["thoughts"] if "r_c" in thought_str
        ]
        if len(r_c_in) > 0 and not random_cat:
            return False

        # This is for filtering certain relationship types between the main cat and random cat.
        if "relationship_constraint" in thought and random_cat:
            if not Thoughts.thought_fulfill_rel_constraints(
                main_cat, random_cat, thought["relationship_constraint"]
            ):
                return False

        main_info_dict = {}
        random_info_dict = {}

        # Constraints for the status of the main cat
        if "main_status_constraint" in thought:
            main_info_dict["status"] = thought["main_status_constraint"]

        # Constraints for the status of the random cat
        if "random_status_constraint" in thought and random_cat:
            random_info_dict["status"] = thought["random_status_constraint"]

        # main cat age constraint
        if "main_age_constraint" in thought:
            main_info_dict["age"] = thought["main_age_constraint"]

        if "random_age_constraint" in thought and random_cat:
            random_info_dict["age"] = thought["random_age_constraint"]

<<<<<<< HEAD
        if 'main_trait_constraint' in thought:
            if main_cat.personality.trait not in thought['main_trait_constraint']:
                return False
            
        if 'not_main_trait_constraint' in thought:
            if main_cat.personality.trait in thought['not_main_trait_constraint']:
                return False
            
        if 'random_trait_constraint' in thought and random_cat:
            if random_cat.personality.trait not in thought['random_trait_constraint']:
                return False
=======
        if "main_trait_constraint" in thought:
            main_info_dict["trait"] = thought["main_trait_constraint"]

        if "random_trait_constraint" in thought and random_cat:
            random_info_dict["trait"] = thought["random_trait_constraint"]
>>>>>>> development

        if "main_skill_constraint" in thought:
            main_info_dict["skill"] = thought["main_skill_constraint"]

        if "random_skill_constraint" in thought and random_cat:
            random_info_dict["skill"] = thought["random_skill_constraint"]

        if "main_backstory_constraint" in thought:
            main_info_dict["backstory"] = thought["main_backstory_constraint"]

        if "random_backstory_constraint" in thought:
            random_info_dict["backstory"] = thought["random_backstory_constraint"]

        if not event_for_cat(main_info_dict, main_cat):
            return False

<<<<<<< HEAD
                if len(spli) != 2:
                    print("Throught constraint not properly formated", _skill)
                    continue

                if random_cat.skills.meets_skill_requirement(spli[0], spli[1]):
                    _flag = True
                    break

            if not _flag:
                return False

        if 'main_backstory_constraint' in thought:
            if main_cat.backstory not in thought['main_backstory_constraint']:
                return False

        if 'random_backstory_constraint' in thought:
            if random_cat and random_cat.backstory not in thought['random_backstory_constraint']:
                return False
            
        # LIFEGEN CONSTRAINTS
        if 'main_faith_constraint' in thought:
            if "low_sc" in thought['main_faith_constraint']:
                if (not main_cat.faith < 3 and main_cat.faith > 0):
                    return False
            elif "mid_sc" in thought['main_faith_constraint']:
                if (not main_cat.faith < 6 and main_cat.faith > 3):
                    return False
            elif "high_sc" in thought['main_faith_constraint']:
                if (not main_cat.faith < 10 and main_cat.faith > 6):
                    return False
                
            if "low_df" in thought['main_faith_constraint']:
                if (not main_cat.faith < 0 and main_cat.faith > -3):
                    return False
            elif "mid_df" in thought['main_faith_constraint']:
                if (not main_cat.faith < -3 and main_cat.faith > -6):
                    return False
            elif "high_df" in thought['main_faith_constraint']:
                if (not main_cat.faith < -6 and main_cat.faith > -10):
                    return False
                
        if 'random_faith_constraint' in thought:
            if "low_sc" in thought['random_faith_constraint']:
                if (not random_cat.faith < 3 and random_cat.faith > 0):
                    return False
            elif "mid_sc" in thought['random_faith_constraint']:
                if (not random_cat.faith < 6 and random_cat.faith > 3):
                    return False
            elif "high_sc" in thought['random_faith_constraint']:
                if (not random_cat.faith < 10 and random_cat.faith > 6):
                    return False
                
            if "low_df" in thought['random_faith_constraint']:
                if (not random_cat.faith < 0 and random_cat.faith > -3):
                    return False
            elif "mid_df" in thought['random_faith_constraint']:
                if (not random_cat.faith < -3 and random_cat.faith > -6):
                    return False
            elif "high_df" in thought['random_faith_constraint']:
                if (not random_cat.faith < -6 and random_cat.faith > -10):
                    return False
                
        if "main_cluster_constraint" in thought:
            cluster, cluster2 = get_cluster(main_cat.personality.trait)
            if cluster not in thought["main_cluster_constraint"] and (cluster2 and cluster2 not in thought["main_cluster_constraint"]):
                return False
        
        if "random_cluster_constraint" in thought and random_cat:
            cluster, cluster2 = get_cluster(random_cat.personality.trait)
            if cluster not in thought["random_cluster_constraint"] and (cluster2 and cluster2 not in thought["random_cluster_constraint"]):
                return False
                    
        
=======
        if r_c_in and not event_for_cat(random_info_dict, random_cat):
            return False
>>>>>>> development

        # Filter for the living status of the random cat. The living status of the main cat
        # is taken into account in the thought loading process.
        if random_cat and "random_living_status" in thought:
            if random_cat:
                if random_cat.dead:
                    if random_cat.status.group == CatGroup.DARK_FOREST:
                        living_status = "darkforest"
                    else:
                        living_status = "starclan"
                else:
                    living_status = "living"
            else:
                living_status = "unknownresidence"
            if living_status and living_status not in thought["random_living_status"]:
                return False

        # this covers if living status isn't stated
        else:
            living_status = None
            if random_cat and not random_cat.dead and not random_cat.status.is_outsider:
                living_status = "living"
            if living_status and living_status != "living":
                return False
<<<<<<< HEAD
        if random_cat:
            if random_cat.moons < 0:
                return False
        if random_cat and 'random_outside_status' in thought:
            if random_cat and random_cat.outside and random_cat.status not in ["kittypet", "loner", "rogue",
                                                                               "former Clancat", "exiled"]:
                outside_status = "lost"
            elif random_cat and random_cat.outside:
                outside_status = "outside"
            else:
                outside_status = "clancat"
=======

        if random_cat and random_cat.status.is_lost():
            outside_status = "lost"
        elif random_cat and random_cat.status.is_outsider:
            outside_status = "outside"
        else:
            outside_status = "clancat"
>>>>>>> development

        if random_cat and "random_outside_status" in thought:
            if outside_status not in thought["random_outside_status"]:
                return False
        else:
            if (
                main_cat.status.is_outsider
            ):  # makes sure that outsiders can get thoughts all the time
                pass
            else:
                if outside_status and outside_status != "clancat" and len(r_c_in) > 0:
                    return False

        if "has_injuries" in thought:
            if "m_c" in thought["has_injuries"]:
                if main_cat.injuries or main_cat.illnesses:
                    injuries_and_illnesses = list(main_cat.injuries.keys()) + list(
                        main_cat.injuries.keys()
                    )
                    if (
                        not [
                            i
                            for i in injuries_and_illnesses
                            if i in thought["has_injuries"]["m_c"]
                        ]
                        and "any" not in thought["has_injuries"]["m_c"]
                    ):
                        return False
                else:
                    return False

            if "r_c" in thought["has_injuries"] and random_cat:
                if random_cat.injuries or random_cat.illnesses:
                    injuries_and_illnesses = list(random_cat.injuries.keys()) + list(
                        random_cat.injuries.keys()
                    )
                    if (
                        not [
                            i
                            for i in injuries_and_illnesses
                            if i in thought["has_injuries"]["r_c"]
                        ]
                        and "any" not in thought["has_injuries"]["r_c"]
                    ):
                        return False
                else:
                    return False

        if "perm_conditions" in thought:
            if "m_c" in thought["perm_conditions"]:
                if not main_cat.permanent_condition:
                    return False

                valid_conditions = [
                    value
                    for key, value in main_cat.permanent_condition.items()
                    if key in thought["perm_conditions"]["m_c"]
                ]

                if (
                    not valid_conditions
                    and "any" not in thought["perm_conditions"]["m_c"]
                ):
                    return False

                # find whether the status is constrained to congenital
                if (
                    congenital := thought["perm_conditions"]
                    .get("born_with", {})
                    .get("m_c")
                ):
                    # permit the event if any of the found permitted conditions matches the born_with param
                    if any(
                        condition["born_with"] == congenital
                        for condition in valid_conditions
                    ):
                        pass
                    else:
                        return False

            if "r_c" in thought["perm_conditions"] and random_cat:
                if not random_cat.permanent_condition:
                    return False

                valid_conditions = [
                    value
                    for key, value in random_cat.permanent_condition.items()
                    if key in thought["perm_conditions"]["r_c"]
                ]

                if (
                    not valid_conditions
                    and "any" not in thought["perm_conditions"]["r_c"]
                ):
                    return False

                # find whether the status is constrained to congenital
                if (
                    congenital := thought["perm_conditions"]
                    .get("born_with", {})
                    .get("r_c")
                ):
                    # permit the event if any of the given permitted conditions matches the born_with param
                    if any(
                        condition["born_with"] == congenital
                        for condition in valid_conditions
                    ):
                        pass
                    else:
                        return False

        return True

    # ---------------------------------------------------------------------------- #
    #                            BUILD MASTER DICTIONARY                           #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def create_thoughts(
        inter_list, main_cat, other_cat, game_mode, biome, season, camp
    ) -> list:
        created_list = []
        for inter in inter_list:
            if Thoughts.cats_fulfill_thought_constraints(
                main_cat, other_cat, inter, game_mode, biome, season, camp
            ):
                created_list.append(inter)
        return created_list

    @staticmethod
    def load_thoughts(main_cat, other_cat, game_mode, biome, season, camp):
        rank = main_cat.status.rank
        rank = rank.replace(" ", "_")

        if not main_cat.dead:
            life_dir = "alive"
        else:
            life_dir = "dead"

        if main_cat.dead:
            if main_cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
                spec_dir = "/unknownresidence"
            elif main_cat.status.group == CatGroup.DARK_FOREST:
                spec_dir = "/darkforest"
            else:
                spec_dir = "/starclan"
        elif main_cat.status.is_outsider:
            spec_dir = "/alive_outside"
<<<<<<< HEAD
        elif main_cat.dead and not main_cat.outside and not main_cat.df:
            spec_dir = "/starclan"
        elif main_cat.dead and main_cat.df:
            spec_dir = "/darkforest"
        elif main_cat.dead and main_cat.outside and not main_cat.df:
            spec_dir = "/unknownresidence"
=======
>>>>>>> development
        else:
            spec_dir = ""

        # newborns only pull from their status thoughts. this is done for convenience
        try:
<<<<<<< HEAD
            if main_cat.age == 'newborn':
                with open(f"{base_path}{life_dir}{spec_dir}/newborn.json", 'r') as read_file:
                    thoughts = ujson.loads(read_file.read())
                loaded_thoughts = thoughts
            elif main_cat.shunned > 0 and not main_cat.dead and not main_cat.outside:
                with open(f"{base_path}{life_dir}{spec_dir}/shunned.json", 'r') as read_file:
                    loaded_thoughts = ujson.loads(read_file.read())
=======
            if main_cat.age == "newborn":
                loaded_thoughts = load_lang_resource(
                    f"thoughts/{life_dir}{spec_dir}/newborn.json"
                )
>>>>>>> development
            else:
                thoughts = load_lang_resource(
                    f"thoughts/{life_dir}{spec_dir}/{rank}.json"
                )
                genthoughts = load_lang_resource(
                    f"thoughts/{life_dir}{spec_dir}/general.json"
                )
                loaded_thoughts = thoughts + genthoughts

            final_thoughts = Thoughts.create_thoughts(
                loaded_thoughts, main_cat, other_cat, game_mode, biome, season, camp
            )
            return final_thoughts
        except IOError:
            print("ERROR: loading thoughts")

    @staticmethod
    def get_chosen_thought(main_cat, other_cat, game_mode, biome, season, camp):
        # get possible thoughts
        try:
            # checks if the cat is Rick Astley to give the rickroll thought, otherwise proceed as usual
            if (main_cat.name.prefix + main_cat.name.suffix).replace(
                " ", ""
            ).lower() == "rickastley":
                return i18n.t("defaults.rickroll")
            else:
                chosen_thought_group = choice(
                    Thoughts.load_thoughts(
                        main_cat, other_cat, game_mode, biome, season, camp
                    )
                )
                chosen_thought = choice(chosen_thought_group["thoughts"])
        except Exception:
<<<<<<< HEAD
            chosen_thought = "Prrrp! You shouldn't see this! Report as a bug."
=======
            traceback.print_exc()
            chosen_thought = i18n.t("defaults.thought")
>>>>>>> development

        return chosen_thought

    @staticmethod
    def new_death_thought(
        main_cat, other_cat, game_mode, biome, season, camp, afterlife, lives_left
    ):
        THOUGHTS: []
        try:
            if main_cat.status.is_leader and lives_left > 0:
                loaded_thoughts = load_lang_resource(
                    f"thoughts/on_death/{afterlife}/leader_life.json"
                )
            elif main_cat.status.is_leader and lives_left == 0:
                loaded_thoughts = load_lang_resource(
                    f"thoughts/on_death/{afterlife}/leader_death.json"
                )
            else:
                loaded_thoughts = load_lang_resource(
                    f"thoughts/on_death/{afterlife}/general.json"
                )
            thought_group = choice(
                Thoughts.create_thoughts(
                    loaded_thoughts, main_cat, other_cat, game_mode, biome, season, camp
                )
            )
            chosen_thought = choice(thought_group["thoughts"])
            return chosen_thought

        except Exception:
            traceback.print_exc()
            return i18n.t("defaults.thought")
