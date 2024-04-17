
from copy import deepcopy
from random import choice
import random

import ujson
from scripts.game_structure.windows import QPRScreen

from scripts.cat.history import History
from scripts.utility import (
    get_highest_platonic_relation,
    event_text_adjust,
    get_personality_compatibility,
    process_text

)
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event
from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import (
    INTERACTION_MASTER_DICT,
    rel_fulfill_rel_constraints,
    cats_fulfill_single_interaction_constraints
)


class QPR_Events():
    """All events which are related to qpp's such as becoming qpps and breakups, but also for possible qpps and platonic interactions."""

    # ---------------------------------------------------------------------------- #
    #                                LOAD RESOURCES                                #
    # ---------------------------------------------------------------------------- #

    resource_directory = "resources/dicts/relationship_events/"

    QPP_DICTS = None
    with open(f"{resource_directory}qpr.json", 'r') as read_file:
        QPP_DICTS = ujson.loads(read_file.read())

    POLY_QPP_DICTS = None
    with open(f"{resource_directory}poly_qpr.json", 'r') as read_file:
        POLY_QPP_DICTS = ujson.loads(read_file.read())

    # ---------------------------------------------------------------------------- #
    #                                     qpp                                     #
    # ---------------------------------------------------------------------------- #

    # Use the overall master interaction dictionary and filter for qpp tag
    QPP_RELEVANT_INTERACTIONS = {}
    for val_type, dictionary in INTERACTION_MASTER_DICT.items():
        QPP_RELEVANT_INTERACTIONS[val_type] = {}
        QPP_RELEVANT_INTERACTIONS[val_type]["increase"] = list(
            filter(lambda inter: "qpps" in inter.relationship_constraint and "not_qpps" not in inter.relationship_constraint,
                dictionary["increase"]
            )
        )
        QPP_RELEVANT_INTERACTIONS[val_type]["decrease"] = list(
            filter(lambda inter: "qpps" in inter.relationship_constraint and "not_qpps" not in inter.relationship_constraint,
                dictionary["decrease"]
            )
        )

    # resort the first generated overview dictionary to only "positive" and "negative" interactions
    QPP_INTERACTIONS = {
        "positive": [],
        "negative": []
    }
    for val_type, dictionary in QPP_RELEVANT_INTERACTIONS.items():
        if val_type in ["jealousy", "dislike"]:
            QPP_INTERACTIONS["positive"].extend(dictionary["decrease"])
            QPP_INTERACTIONS["negative"].extend(dictionary["increase"])
        else:
            QPP_INTERACTIONS["positive"].extend(dictionary["increase"])
            QPP_INTERACTIONS["negative"].extend(dictionary["decrease"])

    # ---------------------------------------------------------------------------- #
    #                                   QPR                                   #
    # ---------------------------------------------------------------------------- #

    # Use the overall master interaction dictionary and filter for any interactions, which requires a certain amount of platonic
    PLATONIC_RELEVANT_INTERACTIONS = {}
    for val_type, dictionary in INTERACTION_MASTER_DICT.items():
        PLATONIC_RELEVANT_INTERACTIONS[val_type] = {}

        # if it's the platonic interaction type add all interactions
        if val_type == "platonic":
            PLATONIC_RELEVANT_INTERACTIONS[val_type]["increase"] = dictionary["increase"]
            PLATONIC_RELEVANT_INTERACTIONS[val_type]["decrease"] = dictionary["decrease"]
        else:
            increase = []
            for interaction in dictionary["increase"]:
                platonic = ["platonic" in tag for tag in interaction.relationship_constraint]
                if any(platonic):
                    increase.append(interaction)
            PLATONIC_RELEVANT_INTERACTIONS[val_type]["increase"] = increase

            decrease = []
            for interaction in dictionary["decrease"]:
                platonic = ["platonic" in tag for tag in interaction.relationship_constraint]
                if any(platonic):
                    decrease.append(interaction)
            PLATONIC_RELEVANT_INTERACTIONS[val_type]["decrease"] = decrease

    # resort the first generated overview dictionary to only "positive" and "negative" interactions
    PLATONIC_INTERACTIONS = {
        "positive": [],
        "negative": []
    }
    for val_type, dictionary in PLATONIC_RELEVANT_INTERACTIONS.items():
        if val_type in ["jealousy", "dislike"]:
            PLATONIC_INTERACTIONS["positive"].extend(dictionary["decrease"])
            PLATONIC_INTERACTIONS["negative"].extend(dictionary["increase"])
        else:
            PLATONIC_INTERACTIONS["positive"].extend(dictionary["increase"])
            PLATONIC_INTERACTIONS["negative"].extend(dictionary["decrease"])


    @staticmethod
    def start_interaction(cat_from, cat_to):
        """
            Filters and triggers events which are connected to romance between these two cats.
            
            Returns
            -------
            bool : if an event is triggered or not
        """
        if cat_from.ID == cat_to.ID:
            return False

        relevant_dict = deepcopy(QPR_Events.PLATONIC_INTERACTIONS)
        if cat_to.ID in cat_from.qpp and not cat_to.dead:
            relevant_dict = deepcopy(QPR_Events.QPP_INTERACTIONS)

        # check if it should be a positive or negative interaction
        relationship = cat_from.relationships[cat_to.ID]
        positive = QPR_Events.check_if_positive_interaction(relationship)

        # get the possible interaction list and filter them
        possible_interactions = relevant_dict["positive"] if positive else relevant_dict["negative"]
        filtered_interactions = []
        _season = [str(game.clan.current_season).casefold(), "Any", "any"]
        _biome = [str(game.clan.biome).casefold(), "Any", "any"]
        for interaction in possible_interactions:
            in_tags = [i for i in interaction.biome if i not in _biome]
            if len(in_tags) > 0:
                continue

            in_tags = [i for i in interaction.season if i not in _season]
            if len(in_tags) > 0:
                continue

            rel_fulfilled = rel_fulfill_rel_constraints(relationship, interaction.relationship_constraint, interaction.id)
            if not rel_fulfilled:
                continue

            cat_fulfill = cats_fulfill_single_interaction_constraints(cat_from, cat_to, interaction, game.clan.game_mode)
            if not cat_fulfill:
                continue

            filtered_interactions.append(interaction)

        if len(filtered_interactions) < 1:
            print(f"There were no platonic interactions for: {cat_from.name} to {cat_to.name}")
            return False
        
        # chose interaction
        chosen_interaction = choice(filtered_interactions)
        # check if the current interaction id is already used and us another if so
        chosen_interaction = choice(possible_interactions)
        while chosen_interaction.id in relationship.used_interaction_ids\
            and len(possible_interactions) > 2:
            possible_interactions.remove(chosen_interaction)
            chosen_interaction = choice(possible_interactions)

        # if the chosen_interaction is still in the TRIGGERED_SINGLE_INTERACTIONS, clean the list
        if chosen_interaction in relationship.used_interaction_ids:
            relationship.used_interaction_ids = []
        relationship.used_interaction_ids.append(chosen_interaction.id)

        # affect relationship - it should always be in a platonic way
        in_de_crease = "increase" if positive else "decrease"
        rel_type = "platonic"
        relationship.chosen_interaction = chosen_interaction
        relationship.interaction_affect_relationships(in_de_crease, chosen_interaction.intensity, rel_type)

        # give cats injuries if the game mode is not classic
        if len(chosen_interaction.get_injuries) > 0 and game.clan.game_mode != 'classic':
            for abbreviations, injury_dict in chosen_interaction.get_injuries.items():
                if "injury_names" not in injury_dict:
                    print(f"ERROR: there are no injury names in the chosen interaction {chosen_interaction.id}.")
                    continue

                injured_cat = cat_from
                if abbreviations != "m_c":
                    injured_cat = cat_to
                
                injuries = []
                for inj in injury_dict["injury_names"]:
                    injured_cat.get_injured(inj, True)
                    injuries.append(inj)

                possible_scar = injury_dict["scar_text"] if "scar_text" in injury_dict else None
                possible_death = injury_dict["death_text"] if "death_text" in injury_dict else None
                if injured_cat.status == "leader":
                    possible_death = injury_dict["death_leader_text"] if "death_leader_text" in injury_dict else None
                
                if possible_scar or possible_death:
                    for condition in injuries:
                        History.add_possible_history(injured_cat, condition, death_text=possible_death, scar_text=possible_scar)

        # get any possible interaction string out of this interaction
        interaction_str = choice(chosen_interaction.interactions)

        # prepare string for display
        cat_dict = {
            "m_c": (str(cat_from.name), choice(cat_from.pronouns)),
            "r_c": (str(cat_to.name), choice(cat_to.pronouns))
        }
        interaction_str = process_text(interaction_str, cat_dict)
        
        # extract intensity from the interaction
        intensity = getattr(chosen_interaction, 'intensity', 'neutral')

        effect = " (neutral effect)"
        if in_de_crease != "neutral" and positive:
            effect = f" ({intensity} positive effect)"
        if in_de_crease != "neutral" and not positive:
            effect = f" ({intensity} negative effect)"

        interaction_str = interaction_str + effect

        # send string to current moon relationship events before adding age of cats
        relevant_event_tabs = ["relation", "interaction"]
        if len(chosen_interaction.get_injuries) > 0:
            relevant_event_tabs.append("health")
        game.cur_events_list.append(Single_Event(
            interaction_str, relevant_event_tabs, [cat_to.ID, cat_from.ID]
        ))

        # now add the age of the cats before the string is sent to the cats' relationship logs
        relationship.log.append(interaction_str + f" - {cat_from.name} was {cat_from.moons} moons old")

        if not relationship.opposite_relationship and cat_from.ID != cat_to.ID:
            relationship.link_relationship()
            relationship.opposite_relationship.log.append(interaction_str + f" - {cat_to.name} was {cat_to.moons} moons old")

        #print(f"ROMANTIC! {cat_from.name} to {cat_to.name}")
        return True

    @staticmethod
    def handle_QPR_and_breakup(cat):
        """Handle events related to making new qpps, and breaking up. """
        
        if cat.no_qpps:
            return
        
        QPR_Events.handle_moving_on(cat)
        QPR_Events.handle_breakup_events(cat)
        QPR_Events.handle_new_qpp_events(cat)
        
        
    
    @staticmethod
    def handle_new_qpp_events(cat):
        """Triggers and handles any events that result in a new qpp """
        
        # First, check high love confession
        flag = QPR_Events.handle_qpr_confession(cat)
        if flag:
            return
        
        # Then, handle more random qprage
        # Choose some subset of cats that they have relationships with
        if not cat.relationships:
            return
        subset = [Cat.fetch_cat(x) for x in cat.relationships if isinstance(Cat.fetch_cat(x), Cat) and not (Cat.fetch_cat(x).dead or Cat.fetch_cat(x).outside)]
        if not subset:
            return
        
        subset = random.sample(subset, max(int(len(subset) / 3), 1))
        
        for other_cat in subset:
            relationship = cat.relationships.get(other_cat.ID)
            flag = QPR_Events.handle_new_qpps(cat, other_cat)
            if flag:
                return
        
    @staticmethod
    def handle_breakup_events(cat: Cat):
        """Triggers and handles any events that results in a breakup """
        
        for x in cat.qpp:
            qpp_ob = Cat.fetch_cat(x)
            if not isinstance(qpp_ob, Cat):
                continue
                        
            flag = QPR_Events.handle_breakup(cat, qpp_ob)
            if flag:
                return
        
         
    @staticmethod
    def handle_moving_on(cat):
        """Handles moving on from dead or outside qpps """
        for qpp_id in cat.qpp:
            if qpp_id not in Cat.all_cats:
                print(f"WARNING: Cat #{cat} has a invalid qpp. It will be removed.")
                cat.qpp.remove(qpp_id)
                continue

            cat_qpp = Cat.fetch_cat(qpp_id)
            if cat_qpp.no_qpps:
                return
            
            # Move on from dead qpps
            if cat_qpp and "grief stricken" not in cat.illnesses and ((cat_qpp.dead and cat_qpp.dead_for >= 4) or cat_qpp.outside):
                # randint is a slow function, don't call it unless we have to.
                # uh oh - jay, randint lover
                if not cat_qpp.no_qpps and random.random() > 0.5:
                    text = f'{cat.name} will always love {cat_qpp.name} but has decided to move on.'
                    game.cur_events_list.append(Single_Event(text, "relation", [cat.ID, cat_qpp.ID]))
                    cat.unset_qpp(cat_qpp)
    
    
    @staticmethod
    def handle_new_qpps(cat_from, cat_to) -> bool:
        """More in depth check if the cats will become qpps."""
        
        become_qpps, qpp_string = QPR_Events.check_if_new_qpp(cat_from, cat_to)
        not_already = cat_from not in cat_to.qpp and cat_to not in cat_from.qpp
        not_mates = cat_from not in cat_to.mate and cat_to not in cat_from.mate

        if become_qpps and qpp_string and not_already and not_mates:
            if cat_from.ID == game.clan.your_cat.ID or cat_to.ID == game.clan.your_cat.ID:
                if not game.switches['window_open']:
                    if cat_from.ID == game.clan.your_cat.ID:
                        game.switches['new_qpp'] = cat_to
                    else:
                        game.switches['new_qpp'] = cat_from
                    QPRScreen("events screen")
                else:
                    if 'qpp' not in game.switches['windows_dict']:
                        if cat_from.ID == game.clan.your_cat.ID:
                            game.switches['new_qpp'] = cat_to
                        else:
                            game.switches['new_qpp'] = cat_from
                        game.switches['windows_dict'].append('qpp')
            else:
                if cat_from not in cat_to.mate:
                    cat_from.set_qpp(cat_to)
                    game.cur_events_list.append(Single_Event(qpp_string, ["relation", "misc"], [cat_from.ID, cat_to.ID]))
                else:
                    return False
        return False

    @staticmethod
    def handle_breakup(cat_from: Cat, cat_to:Cat) -> bool:
        ''' Handles cats breaking up their relationship '''
        
        if cat_from.ID not in cat_to.qpp:
            return False
        
        if cat_from.no_qpps or cat_to.no_qpps:
            return False
        
        if cat_to.no_qpps or cat_from.no_qpps:
            return False
        
        if not QPR_Events.check_if_breakup(cat_from, cat_to):
            return False
        
        # Determine if this is a nice breakup or a fight breakup
        #TODO - make this better
        had_fight = not int(random.random() * 3)
    
        #TODO : more varied breakup text.
        cat_from.unset_qpp(cat_to, breakup=False)
        
        if cat_to.ID in cat_from.relationships:
            relationship_from = cat_from.relationships[cat_to.ID]
        else:
            relationship_from = cat_from.create_one_relationship(cat_to)
            
        if cat_from.ID in cat_to.relationships:
            relationship_to = cat_to.relationships[cat_from.ID]
        else:
            relationship_to = cat_to.create_one_relationship(cat_from)
            
        # These are large decreases - they are to prevent becoming qpps again on the same moon.
        relationship_to.romantic_love -= 15
        relationship_from.platonic_like -= 15
        relationship_to.comfortable -= 10
        relationship_from.comfortable -= 10
        if had_fight:
            relationship_to.romantic_love -= 5
            relationship_from.platonic_like -= 5
            relationship_from.platonic_like -= 10
            relationship_to.platonic_like -= 10
            relationship_from.trust -= 10
            relationship_to.trust -= 10
            relationship_to.dislike += 10
            relationship_from.dislike += 10
        
        
        if had_fight:
            text = f"{cat_from.name} and {cat_to.name} had a huge fight and broke off their platonic partnership."
        else:
            text = f"{cat_from.name} and {cat_to.name} have broken off their platonic partnership."
        game.cur_events_list.append(Single_Event(text, ["relation", "misc"], [cat_from.ID, cat_to.ID]))
        return True

    @staticmethod
    def handle_qpr_confession(cat_from) -> bool:
        """
        Check if the cat has a high love for another and qpp them if there are in the boundaries 
        :param cat: cat in question

        return: bool if event is triggered or not
        """
        # get the highest platonic love relationships
        rel_list = cat_from.relationships.values()
        highest_platonic_relation = get_highest_platonic_relation(rel_list, exclude_qpp=True)
        if not highest_platonic_relation:
            return False

        condition = game.config["QPR"]["confession"]["make_confession"]
        if not QPR_Events.relationship_fulfill_condition(highest_platonic_relation, condition):
            return False

        cat_to = highest_platonic_relation.cat_to
        if not cat_to.is_potential_qpp(cat_from) or not cat_from.is_potential_qpp(cat_to):
            return False
        
        if cat_to in cat_from.qpp:
            return False

        alive_inclan_from_qpps = [qpp for qpp in cat_from.qpp if not cat_from.fetch_cat(qpp).dead and not cat_from.fetch_cat(qpp).outside]
        alive_inclan_to_qpps = [qpp for qpp in cat_to.qpp if not cat_to.fetch_cat(qpp).dead and not cat_to.fetch_cat(qpp).outside]
        poly = len(alive_inclan_from_qpps) > 0 or len(alive_inclan_to_qpps) > 0

        if poly and not QPR_Events.current_qpps_allow_new_qpp(cat_from, cat_to):
            return False

        become_qpp = False
        condition = game.config["QPR"]["confession"]["accept_confession"]
        rel_to_check = highest_platonic_relation.opposite_relationship
        if not rel_to_check:
            highest_platonic_relation.link_relationship()
            rel_to_check = highest_platonic_relation.opposite_relationship
        
        if QPR_Events.relationship_fulfill_condition(rel_to_check, condition):
            become_qpp = True
            qpp_string = QPR_Events.get_qpp_string("high_platonic", poly, cat_from, cat_to)
        # second acceptance chance if the platonic is high enough
        elif "platonic" in condition and condition["platonic"] != 0 and\
            condition["platonic"] > 0 and rel_to_check.platonic_like >= condition["platonic"] * 1.5:
            become_qpp = True
            qpp_string = QPR_Events.get_qpp_string("high_platonic", poly, cat_from, cat_to)
        else:
            qpp_string = QPR_Events.get_qpp_string("rejected", poly, cat_from, cat_to)
            cat_from.relationships[cat_to.ID].platonic_like -= 10
            cat_to.relationships[cat_from.ID].comfortable -= 10

        not_already = cat_from not in cat_to.qpp and cat_to not in cat_from.qpp
        not_mates = cat_from not in cat_to.mate and cat_to not in cat_from.mate

        if become_qpp and not_already and not_mates:
            if cat_from.ID == game.clan.your_cat.ID or cat_to.ID == game.clan.your_cat.ID:
                if not game.switches['window_open']:
                    if cat_from.ID == game.clan.your_cat.ID:
                        game.switches['new_qpp'] = cat_to
                    else:
                        game.switches['new_qpp'] = cat_from
                    QPRScreen("events screen")
                else:
                    if 'qpp' not in game.switches['windows_dict']:
                        if cat_from.ID == game.clan.your_cat.ID:
                            game.switches['new_qpp'] = cat_to
                        else:
                            game.switches['new_qpp'] = cat_from
                        game.switches['windows_dict'].append('qpp')
            else:
                cat_from.set_qpp(cat_to)
                qpp_string = QPR_Events.prepare_relationship_string(qpp_string, cat_from, cat_to)
                game.cur_events_list.append(Single_Event(qpp_string, ["relation", "misc"], [cat_from.ID, cat_to.ID]))

        return True

    # ---------------------------------------------------------------------------- #
    #                          check if event is triggered                         #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def check_if_positive_interaction(relationship) -> bool:
        """Returns if the interaction should be a positive interaction or not."""
        # base for non-existing platonic like / dislike
        list_to_choice = [True, False]

        # take personality in count
        comp = get_personality_compatibility(relationship.cat_from, relationship.cat_to)
        if comp is not None:
            list_to_choice.append(comp)

        # further influence the partition based on the relationship
        list_to_choice += [True] * int(relationship.platonic_like/15)
        list_to_choice += [True] * int(relationship.platonic_like/15)
        list_to_choice += [False] * int(relationship.dislike/10)

        return choice(list_to_choice)

    @staticmethod
    def check_if_breakup(cat_from, cat_to):
        """ More in depth check if the cats will break up.
            Returns:
                bool (True or False)
        """
        if cat_from.ID not in cat_to.qpp:
            return False
        
        # Moving on, not breakups, occur when one qpp is dead or outside.
        if cat_from.dead or cat_from.outside or cat_to.dead or cat_to.outside:
            return False

        chance_number = QPR_Events.get_breakup_chance(cat_from, cat_to)
        if chance_number == 0:
            return False
        
        return not int(random.random() * chance_number)

    @staticmethod
    def check_if_new_qpp(cat_from, cat_to):
        """Checks if the two cats can become qpps, or not. Returns: boolean and event_string"""
        if not cat_from or not cat_to:
            return False, None

        become_qpps = False
        young_age = ['newborn', 'kitten', 'adolescent']
        if not cat_from.is_potential_qpp(cat_to):
            return False, None
        
        if cat_from.ID in cat_to.qpp:
            return False, None
        
        if cat_from.ID in cat_to.mate:
            return False, None
        
        # Gather relationships
        if cat_to.ID in cat_from.relationships:
            relationship_from = cat_from.relationships[cat_to.ID]
        else:
            relationship_from = cat_from.create_one_relationship(cat_to)
            
        if cat_from.ID in cat_to.relationships:
            relationship_to = cat_to.relationships[cat_from.ID]
        else:
            relationship_to = cat_to.create_one_relationship(cat_from)
        

        # qpp chances change based on aroace-ness! 

        qpp_string = None
        aro_qpp_chance = game.config["QPR"]["aro_chance_fulfilled_condition"]
        qpp_chance = game.config["QPR"]["chance_fulfilled_condition"]

        
        if cat_from.sexuality == 'aroace' and cat_to.sexuality == 'aroace':
            hit = int(random.random() * aro_qpp_chance - 8)
        elif cat_from.sexuality == 'aroace' and cat_to.sexuality != 'aroace' or cat_from.sexuality != 'aroace' and cat_to.sexuality == 'aroace':
            hit = int(random.random() * aro_qpp_chance - 5)
        elif cat_from.arospec == 'aromantic':
            hit = int(random.random() * aro_qpp_chance)
        else:
            hit = int(random.random() * qpp_chance)

        # has to be high because every moon this will be checked for each relationship in the game

        # friends_to_lovers = game.config["QPR"]["chance_friends_to_lovers"]
        # random_hit = int(random.random() * friends_to_lovers)

        # already return if there is 'no' hit (everything above 0), other checks are not necessary
        # if hit > 0 and random_hit > 0:
        #     return False, None

        alive_inclan_from_qpps = [qpp for qpp in cat_from.qpp if not cat_from.fetch_cat(qpp).dead and not cat_from.fetch_cat(qpp).outside]
        alive_inclan_to_qpps = [qpp for qpp in cat_to.qpp if cat_to.fetch_cat(qpp) is not None and not cat_to.fetch_cat(qpp).dead and not cat_to.fetch_cat(qpp).outside]
        poly = len(alive_inclan_from_qpps) > 0 or len(alive_inclan_to_qpps) > 0

        if poly and not QPR_Events.current_qpps_allow_new_qpp(cat_from, cat_to):
            return False, None

        if not hit and QPR_Events.relationship_fulfill_condition(relationship_from, game.config["QPR"]["qpp_condition"]) and\
            QPR_Events.relationship_fulfill_condition(relationship_to, game.config["QPR"]["qpp_condition"]):
            become_qpps = True
            qpp_string = QPR_Events.get_qpp_string("low_platonic", poly, cat_from, cat_to)

        if not become_qpps:
            return False, None

        # if poly:
        #     print("----- POLY-POLY-POLY", cat_from.name, cat_to.name)
        #     print(cat_from.qpp)
        #     print(cat_to.qpp)
        # else:
        #     print("BECOME qppS")

        qpp_string = QPR_Events.prepare_relationship_string(qpp_string, cat_from, cat_to)

        return become_qpps, qpp_string

    @staticmethod
    def relationship_fulfill_condition(relationship, condition):
        """
        Check if the relationship can fulfill the condition. 
        Example condition:
            {
            "romantic": 0,
            "platonic": 30,
            "dislike": -10,
            "admiration": 0,
            "comfortable": 20,
            "jealousy": 0,
            "trust": 0
            }

        VALUES: 
            - 0: no condition
            - positive number: value has to be higher than number
            - negative number: value has to be lower than number
        
        """
        if not relationship:
            return False
        if "platonic" in condition and condition["platonic"] != 0:
            if condition["platonic"] > 0 and relationship.platonic_like < condition["platonic"]:
                return False
            if condition["platonic"] < 0 and relationship.platonic_like > abs(condition["platonic"]):
                return False
        if "platonic" in condition and condition["platonic"] != 0:
            if condition["platonic"] > 0 and relationship.platonic_like < condition["platonic"]:
                return False
            if condition["platonic"] < 0 and relationship.platonic_like > abs(condition["platonic"]):
                return False
        if "dislike" in condition and condition["dislike"] != 0:
            if condition["dislike"] > 0 and relationship.dislike < condition["dislike"]:
                return False
            if condition["dislike"] < 0 and relationship.dislike > abs(condition["dislike"]):
                return False
        if "admiration" in condition and condition["admiration"] != 0:
            if condition["admiration"] > 0 and relationship.admiration < condition["admiration"]:
                return False
            if condition["admiration"] < 0 and relationship.admiration > abs(condition["admiration"]):
                return False
        if "comfortable" in condition and condition["comfortable"] != 0:
            if condition["comfortable"] > 0 and relationship.comfortable < condition["comfortable"]:
                return False
            if condition["comfortable"] < 0 and relationship.comfortable > abs(condition["comfortable"]):
                return False
        if "jealousy" in condition and condition["jealousy"] != 0:
            if condition["jealousy"] > 0 and relationship.jealousy < condition["jealousy"]:
                return False
            if condition["jealousy"] < 0 and relationship.jealousy > abs(condition["jealousy"]):
                return False
        if "trust" in condition and condition["trust"] != 0:
            if condition["trust"] > 0 and relationship.trust < condition["trust"]:
                return False
            if condition["trust"] < 0 and relationship.trust > abs(condition["trust"]):
                return False
        return True

    @staticmethod
    def current_qpps_allow_new_qpp(cat_from, cat_to) -> bool:
        """Check if all current qpps are fulfill the given conditions."""
        current_qpp_condition = game.config["QPR"]["poly"]["current_qpp_condition"]
        current_to_new_condition = game.config["QPR"]["poly"]["qpps_to_each_other"]

        # check relationship from current qpps from cat_from
        all_qpps_fulfill_current_qpp_condition = True
        all_qpps_fulfill_current_to_new = True
        alive_inclan_from_qpps = [qpp for qpp in cat_from.qpp if not cat_from.fetch_cat(qpp).dead and not cat_from.fetch_cat(qpp).outside]
        if len(alive_inclan_from_qpps) > 0:
            for qpp_id in alive_inclan_from_qpps:
                qpp_cat = cat_from.fetch_cat(qpp_id)
                if qpp_cat.dead:
                    continue
                if qpp_id in cat_from.relationships and cat_from.ID in qpp_cat.relationships:
                    if not QPR_Events.relationship_fulfill_condition(cat_from.relationships[qpp_id], current_qpp_condition) or\
                        not QPR_Events.relationship_fulfill_condition(qpp_cat.relationships[cat_from.ID], current_qpp_condition):
                        all_qpps_fulfill_current_qpp_condition = False
                
                if qpp_id in cat_to.relationships and cat_to.ID in qpp_cat.relationships:
                    if not QPR_Events.relationship_fulfill_condition(cat_to.relationships[qpp_id], current_to_new_condition) or\
                        not QPR_Events.relationship_fulfill_condition(qpp_cat.relationships[cat_to.ID], current_to_new_condition):
                        all_qpps_fulfill_current_to_new = False
        if not all_qpps_fulfill_current_qpp_condition or\
            not all_qpps_fulfill_current_to_new:
            return False

        # check relationship from current qpps from cat_to
        all_qpps_fulfill_current_qpp_condition = True
        all_qpps_fulfill_current_to_new = True
        alive_inclan_to_qpps = [qpp for qpp in cat_to.qpp if not cat_to.fetch_cat(qpp).dead and not cat_to.fetch_cat(qpp).outside]
        if len(alive_inclan_to_qpps) > 0:
            for qpp_id in alive_inclan_to_qpps:
                qpp_cat = cat_to.fetch_cat(qpp_id)
                if qpp_cat.dead:
                    continue
                if qpp_id in cat_to.relationships and cat_to.ID in qpp_cat.relationships:
                    if not QPR_Events.relationship_fulfill_condition(cat_to.relationships[qpp_id], current_qpp_condition) or\
                        not QPR_Events.relationship_fulfill_condition(qpp_cat.relationships[cat_to.ID], current_qpp_condition):
                        all_qpps_fulfill_current_qpp_condition = False

                if qpp_id in cat_from.relationships and cat_from.ID in qpp_cat.relationships:
                    if not QPR_Events.relationship_fulfill_condition(cat_from.relationships[qpp_id], current_to_new_condition) or\
                        not QPR_Events.relationship_fulfill_condition(qpp_cat.relationships[cat_from.ID], current_to_new_condition):
                        all_qpps_fulfill_current_to_new = False
        if not all_qpps_fulfill_current_qpp_condition or\
            not all_qpps_fulfill_current_to_new:
            return False

        return True

    @staticmethod
    def prepare_relationship_string(qpp_string, cat_from, cat_to):
        """Prepares the relationship event string for display"""
        # replace qpps with their names
        if "[m_c_qpps]" in qpp_string:
            qpp_names = [str(cat_from.fetch_cat(qpp_id).name) for qpp_id in cat_from.qpp]
            qpp_name_string = qpp_names[0]
            if len(qpp_names) == 2:
                qpp_name_string = qpp_names[0] + " and " + qpp_names[1]
            if len(qpp_names) > 2:
                qpp_name_string = ", ".join(qpp_names[:-1]) + ", and " + qpp_names[-1]
            qpp_string = qpp_string.replace("[m_c_qpps]", qpp_name_string)

        if "[r_c_qpps]" in qpp_string:
            qpp_names = [str(cat_to.fetch_cat(qpp_id).name) for qpp_id in cat_to.qpp]
            qpp_name_string = qpp_names[0]
            if len(qpp_names) == 2:
                qpp_name_string = qpp_names[0] + " and " + qpp_names[1]
            if len(qpp_names) > 2:
                qpp_name_string = ", ".join(qpp_names[:-1]) + ", and " + qpp_names[-1]
            qpp_string = qpp_string.replace("[r_c_qpps]", qpp_name_string)

        if "(m_c_qpp/qpps)" in qpp_string:
            insert = "qpp"
            if len(cat_from.qpp) > 1:
                insert = "qpps"
            qpp_string = qpp_string.replace("(m_c_qpp/qpps)", insert)

        if "(r_c_qpp/qpps)" in qpp_string:
            insert = "qpp"
            if len(cat_to.qpp) > 1:
                insert = "qpps"
            qpp_string = qpp_string.replace("(r_c_qpp/qpps)", insert)

        qpp_string = event_text_adjust(Cat, qpp_string, cat_from, cat_to)
        return qpp_string

    @staticmethod
    def get_qpp_string(key, poly, cat_from, cat_to):
        """Returns the qpp string with the certain key, cats and poly."""
        # if not poly:
        return choice(QPR_Events.QPP_DICTS[key])
        # else:
        #     poly_key = ""
        #     alive_inclan_from_qpps = [qpp for qpp in cat_from.qpp if not cat_from.fetch_cat(qpp).dead and not cat_from.fetch_cat(qpp).outside]
        #     alive_inclan_to_qpps = [qpp for qpp in cat_to.qpp if not cat_to.fetch_cat(qpp).dead and not cat_to.fetch_cat(qpp).outside]
        #     if len(alive_inclan_from_qpps) > 0 and len(alive_inclan_to_qpps) > 0:
        #         poly_key = "both_qpps"
        #     elif len(alive_inclan_from_qpps) > 0 and len(alive_inclan_to_qpps) <= 0:
        #         poly_key = "m_c_qpps"
        #     elif len(alive_inclan_from_qpps) <= 0 and len(alive_inclan_to_qpps) > 0:
        #         poly_key = "r_c_qpps"
        #     return choice(QPR_Events.POLY_QPP_DICTS[key][poly_key])

    # ---------------------------------------------------------------------------- #
    #                             get/calculate chances                            #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def get_breakup_chance(cat_from:Cat, cat_to:Cat) -> int:
        """ Looks into the current values and calculate the chance of breaking up. The lower, the more likely they will break up.
            Returns:
                integer (number)
        """
        # Gather relationships
        if cat_to.ID in cat_from.relationships:
            relationship_from = cat_from.relationships[cat_to.ID]
        else:
            relationship_from = cat_from.create_one_relationship(cat_to)
            
        if cat_from.ID in cat_to.relationships:
            relationship_to = cat_to.relationships[cat_from.ID]
        else:
            relationship_to = cat_to.create_one_relationship(cat_from)
        
        # No breakup chance if the cat is a good deal above the make-confession requirments.
        condition = game.config["QPR"]["confession"]["make_confession"].copy()
        for x in condition:
            if condition[x] > 0:
                condition[x] += 16
        if QPR_Events.relationship_fulfill_condition(relationship_from, condition):
            return 0
        if QPR_Events.relationship_fulfill_condition(relationship_to, condition):
            return 0
        
        
        chance_number = 30
        chance_number += int(relationship_from.platonic_like / 5)
        chance_number += int(relationship_to.platonic_like / 5)
        chance_number -= int(relationship_from.dislike / 15)
        chance_number -= int(relationship_from.jealousy / 15)
        chance_number -= int(relationship_to.dislike / 15)
        chance_number -= int(relationship_to.jealousy / 15)

        # change the change based on the personality
        get_along = get_personality_compatibility(cat_from, cat_to)
        if get_along is not None and get_along:
            chance_number += 5
        if get_along is not None and not get_along:
            chance_number -= 10

        # Then, at least a 1/5 chance
        chance_number = max(chance_number, 5)

        #print(f"BREAKUP CHANCE - {cat_to.name}, {cat_from.name}: {chance_number}")
        return chance_number
