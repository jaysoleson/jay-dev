import random
from copy import deepcopy

import ujson

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.cat.pelts import Pelt
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.utility import event_text_adjust, change_relationship_values, change_clan_relations, \
    history_text_adjust
from scripts.game_structure.game_essentials import game
from scripts.events_module.scar_events import Scar_Events
from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure.windows import RetireScreen

from scripts.conditions import (
    medical_cats_condition_fulfilled,
    get_amount_cat_for_one_medic,
)
from scripts.clan_resources.freshkill import FRESHKILL_ACTIVE, MAL_PERCENTAGE, STARV_PERCENTAGE
from scripts.event_class import Single_Event
from scripts.events_module.handle_short_events import handle_short_events
from scripts.events_module.scar_events import Scar_Events
from scripts.game_structure.game_essentials import game
from scripts.utility import (
    event_text_adjust,
    get_alive_status_cats,
    get_leader_life_notice, get_random_moon_cat
)


# ---------------------------------------------------------------------------- #
#                             Condition Event Class                            #
# ---------------------------------------------------------------------------- #


class Condition_Events:
    """All events with a connection to conditions."""

    resource_directory = "resources/dicts/conditions/"

    ILLNESSES = None
    with open(f"{resource_directory}illnesses.json", "r") as read_file:
        ILLNESSES = ujson.loads(read_file.read())

    INJURIES = None
    with open(f"{resource_directory}injuries.json", "r") as read_file:
        INJURIES = ujson.loads(read_file.read())

    PERMANENT = None
    with open(
        f"resources/dicts/conditions/permanent_conditions.json", "r"
    ) as read_file:
        PERMANENT = ujson.loads(read_file.read())
    # ---------------------------------------------------------------------------- #
    #                                    CHANCE                                    #
    # ---------------------------------------------------------------------------- #

    ILLNESSES_SEASON_LIST = None
    with open(f"resources/dicts/conditions/illnesses_seasons.json", "r") as read_file:
        ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

    INJURY_DISTRIBUTION = None
    with open(
        f"resources/dicts/conditions/event_injuries_distribution.json", "r"
    ) as read_file:
        INJURY_DISTRIBUTION = ujson.loads(read_file.read())

    # ---------------------------------------------------------------------------- #
    #                                   STRINGS                                    #
    # ---------------------------------------------------------------------------- #

    PERM_CONDITION_RISK_STRINGS = None
    with open(
        f"resources/dicts/conditions/risk_strings/permanent_condition_risk_strings.json",
        "r",
    ) as read_file:
        PERM_CONDITION_RISK_STRINGS = ujson.loads(read_file.read())

    ILLNESS_RISK_STRINGS = None
    with open(
        f"resources/dicts/conditions/risk_strings/illness_risk_strings.json", "r"
    ) as read_file:
        ILLNESS_RISK_STRINGS = ujson.loads(read_file.read())

    INJURY_RISK_STRINGS = None
    with open(
        f"resources/dicts/conditions/risk_strings/injuries_risk_strings.json", "r"
    ) as read_file:
        INJURY_RISK_STRINGS = ujson.loads(read_file.read())

    CONGENITAL_CONDITION_GOT_STRINGS = None
    with open(
        f"resources/dicts/conditions/condition_got_strings/gain_congenital_condition_strings.json",
        "r",
    ) as read_file:
        CONGENITAL_CONDITION_GOT_STRINGS = ujson.loads(read_file.read())

    PERMANENT_CONDITION_GOT_STRINGS = None
    with open(
        f"resources/dicts/conditions/condition_got_strings/gain_permanent_condition_strings.json",
        "r",
    ) as read_file:
        PERMANENT_CONDITION_GOT_STRINGS = ujson.loads(read_file.read())

    ILLNESS_GOT_STRINGS = None
    with open(f"resources/dicts/conditions/condition_got_strings/gain_illness_strings.json",
              'r') as read_file:
        ILLNESS_GOT_STRINGS = ujson.loads(read_file.read())

    ILLNESS_HEALED_STRINGS = None
    with open(
        f"resources/dicts/conditions/healed_and_death_strings/illness_healed_strings.json",
        "r",
    ) as read_file:
        ILLNESS_HEALED_STRINGS = ujson.loads(read_file.read())

    INJURY_HEALED_STRINGS = None
    with open(
        f"resources/dicts/conditions/healed_and_death_strings/injury_healed_strings.json",
        "r",
    ) as read_file:
        INJURY_HEALED_STRINGS = ujson.loads(read_file.read())

    INJURY_DEATH_STRINGS = None
    with open(
        f"resources/dicts/conditions/healed_and_death_strings/injury_death_strings.json",
        "r",
    ) as read_file:
        INJURY_DEATH_STRINGS = ujson.loads(read_file.read())
    
    INFECTION_RISK_STRINGS = None
    with open(f"resources/dicts/infection/infection_risk_strings.json", 'r') as read_file:
        INFECTION_RISK_STRINGS = ujson.loads(read_file.read())

    ILLNESS_DEATH_STRINGS = None
    with open(f"resources/dicts/conditions/healed_and_death_strings/illness_death_strings.json", 'r') as read_file:
        ILLNESS_DEATH_STRINGS = ujson.loads(read_file.read())

    @staticmethod
    def handle_nutrient(cat: Cat, nutrition_info: dict) -> None:
        """
        Handles gaining conditions or death for cats with low nutrient.
        This function should only be called if the game is in 'expanded' or 'cruel season' mode.

        Starvation and malnutrtion must be handled separately from other illnesses due to their distinct death triggers.

            Parameters
            ----------
            cat : Cat
                the cat which has to be checked and updated
            nutrition_info : dict
                dictionary of all nutrition information (can be found in the freshkill pile)
        """
        if not FRESHKILL_ACTIVE:
            return

        if cat.ID not in nutrition_info.keys():
            print(f"WARNING: Could not find cat with ID {cat.ID}({cat.name}) in the nutrition information.")
            return

        # get all events for a certain status of a cat
        cat_nutrition = nutrition_info[cat.ID]

        event = None
        illness = None
        heal = False

        # handle death first, if percentage is 0 or lower, the cat will die
        if cat_nutrition.percentage <= 0:
            text = ""
            if cat.status == "leader":
                game.clan.leader_lives -= 1
                # kill and retrieve leader life text
                text = get_leader_life_notice()

            possible_string_list = Condition_Events.ILLNESS_DEATH_STRINGS["starving"]
            event = random.choice(possible_string_list) + " " + text
            # first event in string lists is always appropriate for history formatting
            history_event = possible_string_list[0]

            event = event_text_adjust(Cat, event.strip(), main_cat=cat)

            if cat.status == 'leader':
                history_event = history_event.replace("m_c ", "")
                History.add_death(cat, condition="starving", death_text=history_event.strip())
            else:
                History.add_death(cat, condition="starving", death_text=history_event)

            cat.die()

            # if the cat is the leader and isn't full dead
            # make them malnourished and refill nutrition slightly
            if cat.status == "leader" and game.clan.leader_lives > 0:
                mal_score = nutrition_info[cat.ID].max_score / 100 * (MAL_PERCENTAGE + 1)
                nutrition_info[cat.ID].current_score = round(mal_score, 2)
                cat.get_ill("malnourished")

            types = ["birth_death"]
            game.cur_events_list.append(Single_Event(event, types, [cat.ID]))
            return

        # heal cat if percentage is high enough and cat is ill
        elif cat_nutrition.percentage > MAL_PERCENTAGE and cat.is_ill() and "malnourished" in cat.illnesses:
            illness = "malnourished"
            event = random.choice(Condition_Events.ILLNESS_HEALED_STRINGS["malnourished"])
            heal = True

        # heal cat if percentage is high enough and cat is ill
        elif cat_nutrition.percentage > STARV_PERCENTAGE and cat.is_ill() and "starving" in cat.illnesses:
            if cat_nutrition.percentage < MAL_PERCENTAGE:
                if "malnourished" not in cat.illnesses:
                    cat.get_ill("malnourished")
                illness = "starving"
                heal = True
            else:
                illness = "starving"
                heal = True

        elif MAL_PERCENTAGE >= cat_nutrition.percentage > STARV_PERCENTAGE:
            # because of the smaller 'nutrition buffer', kitten and elder should get the starving condition.
            if cat.status in ["kitten", "elder"]:
                illness = "starving"
            else:
                illness = "malnourished"

        elif cat_nutrition.percentage <= STARV_PERCENTAGE:
            illness = "starving"

        # handle the gaining/healing illness
        if heal:
            event = random.choice(Condition_Events.ILLNESS_HEALED_STRINGS[illness])
            cat.illnesses.pop(illness)
        elif not heal and illness:
            event = random.choice(Condition_Events.ILLNESS_GOT_STRINGS[illness])
            cat.get_ill(illness)

        if event:
            event_text = event_text_adjust(Cat, event, main_cat=cat)
            types = ["health"]
            game.cur_events_list.append(Single_Event(event_text, types, [cat.ID]))


    @staticmethod
    def handle_illnesses(cat, season=None):
        """
        This function handles the illnesses overall by randomly making cat ill (or not).
        It will return a bool to indicate if the cat is dead.
        """
        inftype = game.clan.infection["infection_type"]

        # return immediately if they're already dead
        triggered = False
        if cat.dead:
            if cat.dead:
                triggered = True
            return triggered

        event_string = None
        infection_events = []

        if cat.is_ill():
            event_string, infection_event = Condition_Events.handle_already_ill(cat)
            if cat.infected_for > 0 and event_string is not None:
                if not infection_event and "has reached" not in event_string:
                    # im a hack
                    # print("NOT APPENDING", event_string, "TO INFECTION EVENTS")
                    pass
                elif infection_event or "has reached" in event_string:
                    infection_events.append(event_string)

            # INFECTION
            # withering, void sickness, rot
            # so i can change the chances between them if i wanna
            if inftype == "parasitic":
                infected = False
                if "parasitic stage one" in cat.illnesses:
                    # witherchance = 3
                    witherchance = 120
                    infected = True
                elif "parasitic stage two" in cat.illnesses:
                    # witherchance = 3
                    witherchance = 80
                    infected = True
                elif "parasitic stage three" in cat.illnesses:
                    # witherchance = 3
                    witherchance = 50
                    infected = True
                elif "parasitic stage four" in cat.illnesses:
                    # witherchance = 3
                    witherchance = 15
                    infected = True
                
                if infected:
                    if random.random() < 1 / witherchance and "withering" not in cat.injuries:
                        cat.get_injured("withering")
                        event = f"The infection is beginning to destroy {cat.name}'s body."
                        game.cur_events_list.append(Single_Event(event, ["health", "infection"], cat.ID))
            elif inftype == "void":
                infected = False
                if "void stage one" in cat.illnesses:
                    witherchance = 185
                    infected = True
                elif "void stage two" in cat.illnesses:
                    witherchance = 120
                    infected = True
                elif "void stage three" in cat.illnesses:
                    witherchance = 80
                    infected = True
                elif "void stage four" in cat.illnesses:
                    witherchance = 50
                    infected = True
                
                if infected:
                    if random.random() < 1 / witherchance and "void sickness" not in cat.injuries:
                        cat.get_injured("void sickness")
                        event = f"{cat.name}'s body is slowly being consumed by the infection."
                        game.cur_events_list.append(Single_Event(event, ["health", "infection"], cat.ID))
            elif inftype == "fungal":
                infected = False
                if "fungal stage one" in cat.illnesses:
                    witherchance = 185
                    infected = True
                elif "fungal stage two" in cat.illnesses:
                    witherchance = 120
                    infected = True
                elif "fungal stage three" in cat.illnesses:
                    witherchance = 80
                    infected = True
                elif "fungal stage four" in cat.illnesses:
                    witherchance = 50
                    infected = True
                
                if infected:
                    if random.random() < 1 / witherchance and "rot" not in cat.injuries:
                        cat.get_injured("rot")
                        event = f"{cat.name}'s body is becoming very overgrown."
                        game.cur_events_list.append(Single_Event(event, ["health", "infection"], cat.ID))
        else:
            # ---------------------------------------------------------------------------- #
            #                              make cats sick                                  #
            # ---------------------------------------------------------------------------- #
            random_number = int(
                random.random()
                * game.get_config_value(
                    "condition_related", f"{game.clan.game_mode}_illness_chance"
                )
            )
            if (
                not cat.dead
                and not cat.is_ill()
                and random_number <= 10
                and not event_string
            ):

                # CLAN FOCUS!
                if game.clan.clan_settings.get("rest and recover"):
                    stopping_chance = game.config["focus"]["rest and recover"][
                        "illness_prevent"
                    ]
                    if not int(random.random() * stopping_chance):
                        return triggered
                    
                season_dict = Condition_Events.ILLNESSES_SEASON_LIST[season]
                possible_illnesses = []
                types = ["fungal", "parasitic", "void"]

                # pick up possible illnesses from the season dict
                for illness_name in season_dict:
                    if illness_name == f"{inftype} stage one":
                        if not game.clan.infection["clan_infected"]:
                            return triggered
                        else:
                            possible_illnesses += [illness_name] * (season_dict[illness_name])
                    else:
                        possible_illnesses += [illness_name] * (season_dict[illness_name] * 3)
                        # multiply by three because i cant divide stage one by three, and i want it to be less likely

                for i in types:
                    wrong_illness = f"{i} stage one"
                    while (
                        wrong_illness in possible_illnesses and
                        (game.clan.infection["infection_type"] != i or
                        cat.ID == game.clan.your_cat.ID or cat.infected_for > 0
                        or game.clan.infection["clan_infected"] is True)
                        ):
                        # no wrong type infection OR random infections for MC OR infections while the clan isnt infected
                        possible_illnesses.remove(wrong_illness)

                # pick a random illness from those possible
                random_index = int(random.random() * len(possible_illnesses))
                chosen_illness = possible_illnesses[random_index]
                # if a non-kitten got kittencough, switch it to whitecough instead
                if chosen_illness == 'kittencough' and cat.status != 'kitten':
                    chosen_illness = 'whitecough'
                # wrongtype checker
                dont = False
                types = ["fungal", "parasitic", "void"]
                for i in types:
                    if i in chosen_illness and i != game.clan.infection["infection_type"]:
                        # INFECTION failsafe-- you should never see this
                        print("Tried to give", cat.name, "a ", i, "infection?")
                        dont = True
                        break
                    
                # make em sick
                if not dont:
                    cat.get_ill(chosen_illness)
                # create event text
                if chosen_illness in ["running nose", "stomachache"]:
                    event_string = f"{cat.name} has gotten a {chosen_illness}."
                elif chosen_illness == f"{inftype} stage one":
                    insert = ""

                    infected_cats = [cat for cat in Cat.all_cats_list if not cat.outside and not cat.dead and cat.infected_for > 0]

                    if game.clan.infection["spread_by"] == "bite":
                        strings = [
                            f"{cat.name} was bitten by an infected rogue.",
                            f"{cat.name} stumbles back into camp after an outing with a fresh cat bite and a clouded look in their eyes.",
                            f"{cat.name} tries to hide their fresh wound, but the potent smell of the infection coming from them is too hard to ignore."
                        ]
                        if "spread_by_bite" not in game.clan.infection["logs"]:
                            game.clan.infection["logs"].append("spread_by_bite")
                            insert= "\nYour log has been updated."
                        cat.get_injured("cat bite")
                    elif game.clan.infection["spread_by"] == "air":
                        strings = [
                            f"{cat.name} leaves camp alone and comes back with clouded eyes that can only mean one thing.",
                            f"{cat.name} stumbles back into camp after an outing with a clouded look in their eyes.",
                            f"{cat.name} has come down with the infection."
                        ]                        
                        
                        if "spread_by_air" not in game.clan.infection["logs"]:
                            game.clan.infection["logs"].append("spread_by_air")
                            insert= "\nYour log has been updated."
                    
                    if len(infected_cats) > 5:
                        strings.append(f"The Clan is often kept awake at night by the pained wails of infected cats, but tonight, you notice that a new voice has joined their numbers. {cat.name} has been infected.")

                    event_string = random.choice(strings)
                    event_string += insert
                    infection_events.append(event_string)
                    cat.infected_for += 1
                else:
                    types = ["fungal", "void", "parasitic"]
                    for i in types:
                        if chosen_illness == f"{i} stage one" and i != inftype:
                            return
                    event_string = f"{cat.name} has gotten {chosen_illness}."

        # if an event happened, then add event to cur_event_list and save death if it happened.
        if event_string:
            types = ["health"]
            if event_string in infection_events:
                types.append("infection")
            if cat.dead:
                types.append("birth_death")
            game.cur_events_list.append(Single_Event(event_string, types, cat.ID))

        # just double-checking that trigger is only returned True if the cat is dead
        if cat.dead:
            triggered = True
        else:
            triggered = False

        return triggered

    @staticmethod
    def handle_injuries(cat, random_cat=None):
        """ 
        This function handles injuries overall by randomly injuring cat (or not).
        Returns: boolean - if an event was triggered
        """
        triggered = False
        random_number = int(
            random.random()
            * game.get_config_value(
                "condition_related", f"{game.clan.game_mode}_injury_chance"
            )
        )

        if cat.dead:
            triggered = True
            return triggered

        # handle if the current cat is already injured
        if cat.is_injured():
            for injury in cat.injuries:
                if injury == "pregnant" and cat.ID not in game.clan.pregnancy_data:
                    print(
                        f"INFO: deleted pregnancy condition of {cat.ID} due no pregnancy data in the clan."
                    )
                    del cat.injuries[injury]
                    return triggered
                elif injury == "pregnant":
                    return triggered
            triggered = Condition_Events.handle_already_injured(cat)
        else:
            # EVENTS
            if (
                not triggered
                and cat.personality.trait
                in [
                    "adventurous",
                    "bold",
                    "daring",
                    "confident",
                    "ambitious",
                    "bloodthirsty",
                    "fierce",
                    "strict",
                    "troublesome",
                    "vengeful",
                    "impulsive",
                ]
                and random_number <= 15
            ):
                triggered = True
            elif not triggered and random_number <= 5:
                triggered = True

            if triggered:
                # CLAN FOCUS!
                if game.clan.clan_settings.get("rest and recover"):
                    stopping_chance = game.config["focus"]["rest and recover"][
                        "injury_prevent"
                    ]
                    if not int(random.random() * stopping_chance):
                        return False

                handle_short_events.handle_event(event_type="health",
                                                 main_cat=cat,
                                                 random_cat=random_cat,
                                                 freshkill_pile=game.clan.freshkill_pile)


        # just double-checking that trigger is only returned True if the cat is dead
        if cat.status != "leader":
            # only checks for non-leaders, as leaders will not be dead if they are just losing a life
            if cat.dead:
                triggered = True
            else:
                triggered = False

        return triggered

    @staticmethod
    def handle_permanent_conditions(cat,
                                    condition=None,
                                    injury_name=None,
                                    illness_name=None,
                                    scar=None,
                                    born_with=False):
        """
        this function handles overall the permanent conditions of a cat.
        returns boolean if event was triggered
        """

        # dict of possible physical conditions that can be acquired from relevant scars
        scar_to_condition = {
            "LEGBITE": ["weak leg"],
            "THREE": ["one bad eye", "failing eyesight"],
            "NOPAW": ["lost a leg"],
            "TOETRAP": ["weak leg"],
            "NOTAIL": ["lost their tail"],
            "HALFTAIL": ["lost their tail"],
            "LEFTEAR": ["partial hearing loss"],
            "RIGHTEAR": ["partial hearing loss"],
            "MANLEG": ["weak leg", "twisted leg"],
            "BRIGHTHEART": ["one bad eye"],
            "NOLEFTEAR": ["partial hearing loss"],
            "NORIGHTEAR": ["partial hearing loss"],
            "NOEAR": ["partial hearing loss", "deaf"],
            "LEFTBLIND": ["one bad eye", "failing eyesight"],
            "RIGHTBLIND": ["one bad eye", "failing eyesight"],
            "BOTHBLIND": ["blind"],
            "RATBITE": ["weak leg"],
            "EYESOCKET": ["one bad eye"],
            "ARMBONE": ["weak leg"],
            "VOIDEYE": ["one bad eye"],
            "EYEMOSS": ["one bad eye"],
            "PAWMOSS": ["weak leg"]
        }
        
        scarless_conditions = [
            "weak leg",
            "paralyzed",
            "raspy lungs",
            "wasting disease",
            "blind",
            "failing eyesight",
            "one bad eye",
            "partial hearing loss",
            "deaf",
            "constant joint pain",
            "constantly dizzy",
            "recurring shock",
            "lasting grief",
            "persistent headaches",
        ]

        got_condition = False
        perm_condition = None
        possible_conditions = []

        if illness_name is not None:
            if scar is not None and scar in scar_to_condition:
                possible_conditions = scar_to_condition.get(scar)
                perm_condition = random.choice(possible_conditions)
            elif scar is None:
                try:
                    if Condition_Events.ILLNESSES[illness_name] is not None:
                        conditions = Condition_Events.ILLNESSES[illness_name]["cause_permanent"]
                        for x in conditions:
                            if x in scarless_conditions:
                                possible_conditions.append(x)
                        if len(possible_conditions) > 0 and not int(random.random() * game.config["condition_related"]["permanent_condition_chance"]):
                            perm_condition = random.choice(possible_conditions)
                        else:
                            return perm_condition
                except KeyError:
                    print(f"WARNING: {illness_name} couldn't be found in illness dict! no permanent condition was given")
                    return perm_condition

        if injury_name is not None:
            if scar is not None and scar in scar_to_condition:
                possible_conditions = scar_to_condition.get(scar)
                perm_condition = random.choice(possible_conditions)
            elif scar is None:
                try:
                    if Condition_Events.INJURIES[injury_name] is not None:
                        conditions = Condition_Events.INJURIES[injury_name][
                            "cause_permanent"
                        ]
                        for x in conditions:
                            if x in scarless_conditions:
                                possible_conditions.append(x)
                        if len(possible_conditions) > 0 and not int(
                            random.random()
                            * game.config["condition_related"][
                                "permanent_condition_chance"
                            ]
                        ):
                            perm_condition = random.choice(possible_conditions)
                        else:
                            return perm_condition
                except KeyError:
                    print(
                        f"WARNING: {injury_name} couldn't be found in injury dict! no permanent condition was given"
                    )
                    return perm_condition
            else:
                print(
                    f"WARNING: {scar} for {injury_name} is either None or is not in scar_to_condition dict."
                )

        elif condition is not None:
            perm_condition = condition

        if perm_condition is not None:
            got_condition = cat.get_permanent_condition(perm_condition, born_with)

        if got_condition is True:
            return perm_condition

    # ---------------------------------------------------------------------------- #
    #                               helper functions                               #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def handle_infection_risks(cat):
        inftype = game.clan.infection["infection_type"]
        spreadby = game.clan.infection["spread_by"]
        possible_risks = []

        # this sucks
        possible_risks.extend(["sore", "scrapes"])

        if inftype == "fungal":
            possible_risks.append("poisoned")
        elif inftype == "parasitic":
            possible_risks.append("blood loss")
        elif inftype == "void":
            possible_risks.append("shivering")

        # if f"{inftype} stage one" in cat.illnesses:
        #     if inftype == "fungal":
        #         # possible_risks.append("fleas")
        #         pass

        # elif f"{inftype} stage two" in cat.illnesses:
        #     pass

        # elif f"{inftype} stage three" in cat.illnesses:
        #     if inftype == "parasitic":
        #         possible_risks.append("lost their tail")
        #     elif inftype == "void":
        #         possible_risks.extend(["partial hearing loss", "failing eyesight", "one bad eye"])

        # elif f"{inftype} stage four" in cat.illnesses:
        #     if inftype == "parasitic":
        #         possible_risks.extend(["lost their tail", "lost their leg"])
        #     elif inftype == "void":
        #         possible_risks.extend(["partial hearing loss", "partial hearing loss", "deaf", "failing eyesight", "failing eyesight", "one bad eye", "blind"])

        # taking care of perms in withering........

        risk = random.choice(possible_risks)

        if risk in cat.illnesses:
            return

        if risk in Condition_Events.ILLNESSES:
            cat.get_ill(risk)
        elif risk in Condition_Events.INJURIES:
            cat.get_injured(risk)
        elif risk in Condition_Events.PERMANENT:
            cat.get_permanent_condition(risk, event_triggered=False)
        else:
            print("INFECTION WARNING: Risk not in any dicts.")
            return
        
        possible_string_list = Condition_Events.INFECTION_RISK_STRINGS[risk]
        
        # choose event string
        random_index = int(random.random() * len(possible_string_list))
        event = possible_string_list[random_index]
        event = event_text_adjust(Cat, event, main_cat=cat, random_cat=None)  # adjust the text
        game.cur_events_list.append(Single_Event(event, ["health", "infection"], cat.ID))

    @staticmethod
    def handle_already_ill(cat):

        inftype = game.clan.infection["infection_type"]
        starting_life_count = game.clan.leader_lives
        cat.healed_condition = False
        event_list = []
        illness_progression = {
            "running nose": "whitecough",
            "kittencough": "whitecough",
            "whitecough": "greencough",
            "greencough": "yellowcough",
            "yellowcough": "redcough",
            "an infected wound": "a festering wound",
            "heat exhaustion": "heat stroke",
            "stomachache": "diarrhea",
            "grief stricken": "lasting grief",
            f"{inftype} stage one": f"{inftype} stage two",
            f"{inftype} stage two": f"{inftype} stage three",
            f"{inftype} stage three": f"{inftype} stage four"
        }
        # ---------------------------------------------------------------------------- #
        #                         handle currently sick cats                           #
        # ---------------------------------------------------------------------------- #

        infection_event = False
        # making a copy, so we can iterate through copy and modify the real dict at the same time
        illnesses = deepcopy(cat.illnesses)
        for illness in illnesses:
            if illness in game.switches["skip_conditions"]:
                continue

            # use herbs
            Condition_Events.use_herbs(
                cat, illness, illnesses, Condition_Events.ILLNESSES
            )

            # moon skip to try and kill or heal cat
            skipped = cat.moon_skip_illness(illness)

            # if event trigger was true, events should be skipped for this illness
            if skipped is True:
                continue

            # death event text and break bc any other illnesses no longer matter
            if cat.dead or (cat.status == 'leader' and starting_life_count != game.clan.leader_lives):
                try:
                    possible_string_list = Condition_Events.ILLNESS_DEATH_STRINGS[illness]
                    event = random.choice(possible_string_list)
                    # first event in string lists is always appropriate for history formatting
                    history_event = possible_string_list[0]
                except KeyError:
                    print(f"WARNING: {illness} does not have an injury death string, placeholder used.")
                    event = "m_c was killed by their illness."
                    history_event = "m_c died to an illness."

                event = event_text_adjust(Cat, event, main_cat=cat)

                if cat.status == 'leader':
                    event = event + " " + get_leader_life_notice()
                    history_event = history_event.replace("m_c ", "")
                    History.add_death(cat, condition=illness, death_text=history_event.strip())
                else:
                    History.add_death(cat, condition=illness, death_text=history_event)

                # clear event list to get rid of any healed or risk event texts from other illnesses
                event_list.clear()
                event_list.append(event)
                game.herb_events_list.append(event)
                break

            # if the leader died, then break before handling other illnesses cus they'll be fully healed or dead dead
            if cat.status == 'leader' and starting_life_count != game.clan.leader_lives:
                break

            # heal the cat
            elif cat.healed_condition is True:
                if illness in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three",f"{inftype} stage four"]:
                    # id rather stop it from ever being true in the first place for infected cats
                    # because after a certain point, this is happening every moon
                    # but whatever. this works.
                    infection_event = True
                    continue
                else:
                    infection_event = False
                History.remove_possible_history(cat, illness)
                game.switches["skip_conditions"].append(illness)
                # gather potential event strings for healed illness
                
                # chance for a cat to become a medcat after grieving an infection victim
                infected_griefcat = False

                if illness == "grief stricken":
                    deadguy = Cat.all_cats.get(cat.illnesses['grief stricken'].get("grief_cat"))
                    if deadguy:
                        if not deadguy.history:
                            deadguy.load_history()
                        if deadguy.history:
                            if deadguy.history.died_by:
                                if deadguy.history.died_by[0]["text"]:
                                    if deadguy.history.died_by[0]["text"] == f"{deadguy.name} was killed by the infection.":
                                        infected_griefcat = True
                    if infected_griefcat:
                        if not int(random.random() * 25): # 1/25 chance
                            if cat.status not in ["newborn", "kitten", "leader", "medicine cat", "medicine cat apprentice"]:
                                event = f"Sorrow turned to determination, {cat.name} has decided to become a medicine cat to help prevent the infection from killing any more cats like it did to {deadguy.name}."
                                if cat.status in ["apprentice", "queen's apprentice", "mediator apprentice"]:
                                    cat.status = "medicine cat apprentice"
                                else:
                                    cat.status = "medicine cat"

                                game.cur_events_list.append(Single_Event(event, ["health", "infection"], cat.ID))

                try:
                    possible_string_list = Condition_Events.ILLNESS_HEALED_STRINGS[illness]
                except:
                    print("couldn't find illness")

                # choose event string
                random_index = int(random.random() * len(possible_string_list))
                event = possible_string_list[random_index]
                event = event_text_adjust(Cat, event, main_cat=cat, random_cat=None)
                event_list.append(event)
                game.herb_events_list.append(event)
                try:
                    cat.illnesses.pop(illness)
                except:
                    print("ERROR: removing illness")
                # make sure complications get reset if infection or fester were healed
                if illness in ["an infected wound", "a festering wound"]:
                    for injury in cat.injuries:
                        keys = cat.injuries[injury].keys()
                        if "complication" in keys:
                            cat.injuries[injury]["complication"] = None
                    for condition in cat.permanent_condition:
                        keys = cat.permanent_condition[condition].keys()
                        if "complication" in keys:
                            cat.permanent_condition[condition]["complication"] = None
                cat.healed_condition = False

                # move to next illness, the cat can't get a risk from an illness that has healed
                continue

            Condition_Events.give_risks(
                cat, event_list, illness, illness_progression, illnesses, cat.illnesses
            )


        # joining event list into one event string
        event_string = None
        if len(event_list) > 0:
            event_string = " ".join(event_list)
        return event_string, infection_event

    @staticmethod
    def handle_already_injured(cat):
        """
        This function handles, when the cat is already injured
        Returns: True if an event was triggered, False if nothing happened
        """
        triggered = False
        event_list = []

        injury_progression = {"poisoned": "redcough", "shock": "lingering shock"}

        # need to hold this number so that we can check if the leader has died
        starting_life_count = game.clan.leader_lives

        injuries = deepcopy(cat.injuries)
        for injury in injuries:
            if injury in game.switches["skip_conditions"]:
                continue

            Condition_Events.use_herbs(cat, injury, injuries, Condition_Events.INJURIES)

            skipped = cat.moon_skip_injury(injury)
            if skipped:
                continue

            if cat.dead or (
                cat.status == "leader" and starting_life_count != game.clan.leader_lives
            ):
                triggered = True

                try:
                    possible_string_list = Condition_Events.INJURY_DEATH_STRINGS[injury]
                    event = random.choice(possible_string_list)

                    # first string in the list is always appropriate for history text
                    history_text = possible_string_list[0]
                except KeyError:
                    print(f'WARNING: {injury} does not have an injury death string, placeholder used')

                    event = "m_c was killed by their injuries."
                    history_text = "m_c died to an injury."

                event = event_text_adjust(Cat, event, main_cat=cat)

                if cat.status == 'leader':
                    event = event + " " + get_leader_life_notice()
                    history_text = history_text.replace("m_c", " ")
                    History.add_death(cat, condition=injury, death_text=history_text.strip())

                else:
                    History.add_death(cat, condition=injury, death_text=history_text)

                # clear event list first to make sure any heal or risk events from other injuries are not shown
                event_list.clear()
                event_list.append(event)
                game.herb_events_list.append(event)
                break

            elif cat.healed_condition is True:
                game.switches["skip_conditions"].append(injury)
                triggered = True

                # Try to give a scar, and get the event text to be displayed
                event, scar_given = Scar_Events.handle_scars(cat, injury)
                # If a scar was not given, we need to grab a separate healed event
                if not scar_given:
                    try:
                        event = random.choice(
                            Condition_Events.INJURY_HEALED_STRINGS[injury]
                        )
                    except KeyError:
                        print(
                            f"WARNING: {injury} couldn't be found in the healed strings dict! placeholder string was used.")
                        event = f"m_c's injury {injury} has healed"

                event = event_text_adjust(Cat, event, main_cat=cat, random_cat=None)


                game.herb_events_list.append(event)

                History.remove_possible_history(cat, injury)
                cat.injuries.pop(injury)
                cat.healed_condition = False

                # try to give a permanent condition based on healed injury and new scar if any
                condition_got = Condition_Events.handle_permanent_conditions(
                    cat, injury_name=injury, scar=scar_given
                )

                if condition_got is not None:
                    # gather potential event strings for gotten condition
                    possible_string_list = (
                        Condition_Events.PERMANENT_CONDITION_GOT_STRINGS[injury][
                            condition_got
                        ]
                    )

                    # choose event string and ensure Clan's med cat number aligns with event text
                    random_index = random.randrange(0, len(possible_string_list))

                    med_list = get_alive_status_cats(Cat, ["medicine cat", "medicine cat apprentice"], working=True)
                    # If the cat is a med cat, don't consider them as one for the event.

                    if cat in med_list:
                        med_list.remove(cat)

                    # Choose med cat, if you can
                    if med_list:
                        med_cat = random.choice(med_list)
                    else:
                        med_cat = None

                    if not med_cat and random_index < 2 and len(possible_string_list) >= 3:
                        random_index = 2

                    event = possible_string_list[random_index]
                    event = event_text_adjust(Cat, event, main_cat=cat, random_cat=med_cat)  # adjust the text

                if event is not None:
                    event_list.append(event)
                continue

            Condition_Events.give_risks(
                cat, event_list, injury, injury_progression, injuries, cat.injuries
            )

        if len(event_list) > 0:
            event_string = " ".join(event_list)
        else:
            event_string = None

        if event_string:
            types = ["health"]
            if cat.dead:
                types.append("birth_death")
            game.cur_events_list.append(Single_Event(event_string, types, cat.ID))

        return triggered
    @staticmethod
    def handle_already_disabled(cat):
        """
        this function handles what happens if the cat already has a permanent condition.
        Returns: boolean (if something happened) and the event_string
        """
        triggered = False
        event_types = ["health"]

        event_list = []

        condition_progression = {
            "one bad eye": "failing eyesight",
            "failing eyesight": "blind",
            "partial hearing loss": "deaf",
        }

        conditions = deepcopy(cat.permanent_condition)
        for condition in conditions:

            # checking if the cat has a congenital condition to reveal and handling duration and death
            prev_lives = game.clan.leader_lives
            status = cat.moon_skip_permanent_condition(condition)

            # if cat is dead, break
            if cat.dead or game.clan.leader_lives < prev_lives:
                triggered = True
                event_types.append("birth_death")
                event = f"{cat.name} died from complications caused by {condition}."
                if cat.status == "leader" and game.clan.leader_lives >= 1:
                    event = f"{cat.name} lost a life to {condition}."
                event_list.append(event)

                if cat.status != "leader":
                    History.add_death(cat, death_text=event)
                else:
                    History.add_death(cat, death_text=f"died to {condition}")

                game.herb_events_list.append(event)
                break

            # skipping for whatever reason
            if status == "skip":
                continue

            # revealing perm condition
            if status == "reveal":
                # gather potential event strings for gotten risk
                possible_string_list = (
                    Condition_Events.CONGENITAL_CONDITION_GOT_STRINGS[condition]
                )

                # choose event string and ensure Clan's med cat number aligns with event text
                random_index = int(random.random() * len(possible_string_list))
                med_list = get_alive_status_cats(Cat, ["medicine cat", "medicine cat apprentice"], working=True, sort=True)
                med_cat = None
                has_parents = False
                if cat.parent1 is not None and cat.parent2 is not None:
                    # Check if the parent is in Cat.all_cats. If not, they are faded are dead.

                    med_parent = False  # If they have a med parent, this will be flicked to True in the next couple lines.
                    if cat.parent1 in Cat.all_cats:
                        parent1_dead = Cat.all_cats[cat.parent1].dead
                        if Cat.all_cats[cat.parent1].status == "medicine cat":
                            med_parent = True
                    else:
                        parent1_dead = True

                    if cat.parent2 in Cat.all_cats:
                        parent2_dead = Cat.all_cats[cat.parent2].dead
                        if Cat.all_cats[cat.parent2].status == "medicine cat":
                            med_parent = True
                    else:
                        parent2_dead = True

                    if not parent1_dead or not parent2_dead and not med_parent:
                        has_parents = True

                if len(med_list) == 0 or not has_parents:
                    if random_index == 0:
                        random_index = 1
                    else:
                        med_cat = None
                else:
                    med_cat = random.choice(med_list)
                    if med_cat == cat:
                        random_index = 1
                event = possible_string_list[random_index]
                event = event_text_adjust(Cat, event, main_cat=cat, random_cat=med_cat)  # adjust the text
                event_list.append(event)
                continue

            # trying herbs
            chance = 0
            if conditions[condition]["severity"] == "minor":
                chance = 10
            elif conditions[condition]["severity"] == "major":
                chance = 6
            elif conditions[condition]["severity"] == "severe":
                chance = 3
            if not int(random.random() * chance):
                Condition_Events.use_herbs(
                    cat, condition, conditions, Condition_Events.PERMANENT
                )

            # give risks
            Condition_Events.give_risks(
                cat,
                event_list,
                condition,
                condition_progression,
                conditions,
                cat.permanent_condition,
            )

        Condition_Events.determine_retirement(cat, triggered)

        if len(event_list) > 0:
            event_string = " ".join(event_list)
            game.cur_events_list.append(Single_Event(event_string, event_types, cat.ID))
        return

    @staticmethod
    def determine_retirement(cat, triggered):

        if game.clan.clan_settings["retirement"] or cat.no_retire:
            return

        if not triggered and not cat.dead and cat.status not in \
                ['leader', 'medicine cat', 'kitten', 'newborn', 'medicine cat apprentice', 'mediator',
                 'mediator apprentice', "queen", "queen's apprentice", 'elder']:
            for condition in cat.permanent_condition:
                if cat.permanent_condition[condition]["severity"] not in [
                    "major",
                    "severe",
                ]:
                    continue

                if cat.permanent_condition[condition]["severity"] == "severe":
                    # Higher changes for "severe". These are meant to be nearly 100% without
                    # being 100%
                    retire_chances = {
                        "newborn": 0,
                        "kitten": 0,
                        "adolescent": 50,  # This is high so instances where an cat retires the same moon they become an apprentice is rare
                        "young adult": 10,
                        "adult": 5,
                        "senior adult": 5,
                        "senior": 5,
                    }
                else:
                    retire_chances = {
                        "newborn": 0,
                        "kitten": 0,
                        "adolescent": 100,
                        "young adult": 80,
                        "adult": 70,
                        "senior adult": 50,
                        "senior": 10,
                    }

                chance = int(retire_chances.get(cat.age))
                if not int(random.random() * chance):
                    retire_involved = [cat.ID]
                    if cat.age == "adolescent":
                        event = (
                            f"{cat.name} decides they'd rather spend their time helping around camp and entertaining the "
                            f"kits, they're warmly welcomed into the elder's den."
                        )
                    elif game.clan.leader is not None:
                        if (
                            not game.clan.leader.dead
                            and not game.clan.leader.exiled
                            and not game.clan.leader.outside
                            and cat.moons < 120
                        ):
                            retire_involved.append(game.clan.leader.ID)
                            event = (
                                f"{game.clan.leader.name}, seeing {cat.name} struggling the last few moons "
                                f"approaches them and promises them that no one would think less of them for "
                                f"retiring early and that they would still be a valuable member of the Clan "
                                f"as an elder. {cat.name} agrees and later that day their elder ceremony "
                                f"is held."
                            )
                        else:
                            event = f"{cat.name} has decided to retire from normal Clan duty."
                    else:
                        event = (
                            f"{cat.name} has decided to retire from normal Clan duty."
                        )

                    if cat.age == 'adolescent':
                        event += f" They are given the name {cat.name.prefix}{cat.name.suffix} in honor " \
                                    f"of their contributions to {game.clan.name}Clan."
                    if cat.ID != game.clan.your_cat.ID:
                        
                        cat.retire_cat()
                        # Don't add this to the condition event list: instead make it it's own event, a ceremony. 
                        game.cur_events_list.append(
                                Single_Event(event, "ceremony", retire_involved))
                    elif not game.switches['window_open']:
                        RetireScreen('events screen')
                    elif game.switches['window_open'] and 'retire' not in game.switches['windows_dict']:
                        game.switches['windows_dict'].append('retire')

                            
    @staticmethod
    def give_risks(cat, event_list, condition, progression, conditions, dictionary):
        inftype = game.clan.infection["infection_type"]
        event_triggered = False
        if dictionary == cat.permanent_condition:
            event_triggered = True
        if "risks" not in conditions[condition]:
            return
        for risk in conditions[condition]["risks"]:
            if risk["name"] in (cat.injuries or cat.illnesses):
                continue
            if (
                risk["name"] == "an infected wound"
                and "a festering wound" in cat.illnesses
            ):
                continue
            
            # adjust chance of risk gain if Clan has enough meds
            chance = risk["chance"]
            if medical_cats_condition_fulfilled(
                Cat.all_cats.values(), get_amount_cat_for_one_medic(game.clan)
            ):
                chance += 10  # lower risk if enough meds
            if game.clan.medicine_cat is None and chance != 0:
                chance = int(
                    chance * 0.75
                )  # higher risk if no meds and risk chance wasn't 0
                if chance <= 0:  # ensure that chance is never 0
                    chance = 1
            
            infection_event = False
            if risk["name"] in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three", f"{inftype} stage four"]:
                if cat.cure_progress > 0:
                    return
                infection_event = True
                chance /= 2

            # if we hit the chance, then give the risk if the cat does not already have the risk
            if (
                chance != 0
                and not int(random.random() * chance)
                and risk["name"] not in dictionary
            ):
                # check if the new risk is a previous stage of a current illness
                skip = False
                if risk["name"] in progression:
                    if progression[risk["name"]] in dictionary:
                        skip = True
                # if it is, then break instead of giving the risk
                if skip is True:
                    break

                new_condition_name = risk["name"]

                # lower risk of getting it again if not a perm condition
                if dictionary != cat.permanent_condition:
                    saved_condition = dictionary[condition]["risks"]
                    for old_risk in saved_condition:
                        if old_risk["name"] == risk["name"]:
                            if new_condition_name in [
                                "an infected wound",
                                "a festering wound",
                            ]:
                                # if it's infection or festering, we're removing the chance completely
                                # this is both to prevent annoying infection loops
                                # and bc the illness/injury difference causes problems
                                old_risk["chance"] = 0
                            else:
                                old_risk["chance"] = risk["chance"] + 10

                med_cat = None
                removed_condition = False
                try:
                    # gather potential event strings for gotten condition
                    if dictionary == cat.illnesses:
                        possible_string_list = Condition_Events.ILLNESS_RISK_STRINGS[
                            condition
                        ][new_condition_name]
                    elif dictionary == cat.injuries:
                        possible_string_list = Condition_Events.INJURY_RISK_STRINGS[
                            condition
                        ][new_condition_name]
                    else:
                        possible_string_list = (
                            Condition_Events.PERM_CONDITION_RISK_STRINGS[condition][
                                new_condition_name
                            ]
                        )

                    # if it is a progressive condition, then remove the old condition and keep the new one
                    if (
                        condition in progression
                        and new_condition_name == progression.get(condition)
                    ):
                        removed_condition = True
                        dictionary.pop(condition)

                    # choose event string and ensure Clan's med cat number aligns with event text
                    random_index = int(random.random() * len(possible_string_list))
                    med_list = get_alive_status_cats(Cat, ["medicine cat", "medicine cat apprentice"], working=True, sort=True)
                    if len(med_list) == 0:
                        if random_index == 0:
                            random_index = 1
                        else:
                            med_cat = None
                    else:
                        med_cat = random.choice(med_list)
                        if med_cat == cat:
                            random_index = 1
                    try:
                        event = possible_string_list[random_index]
                    except:
                        print(random_index, "random index out of range. infection bug i think")
                        return
                except KeyError:
                    print(
                        f"WARNING: {condition} couldn't be found in the risk strings! placeholder string was used"
                    )
                    event = "m_c's condition has gotten worse."

                event = event_text_adjust(Cat, event, main_cat=cat, random_cat=med_cat)  # adjust the text

                event_list.append(event)

                # we add the condition to this game switch, this is so we can ensure it's skipped over for this moon
                game.switches["skip_conditions"].append(new_condition_name)
                # here we give the new condition
                if new_condition_name in Condition_Events.INJURIES:
                    cat.get_injured(new_condition_name, event_triggered=event_triggered)
                    break
                elif new_condition_name in Condition_Events.ILLNESSES:
                    cat.get_ill(new_condition_name, event_triggered=event_triggered)
                    if dictionary == cat.illnesses or removed_condition:
                        break
                    keys = dictionary[condition].keys()
                    complication = None
                    if new_condition_name == "an infected wound":
                        complication = "infected"
                    elif new_condition_name == "a festering wound":
                        complication = "festering"
                    if complication is not None:
                        if "complication" in keys:
                            dictionary[condition]["complication"] = complication
                        else:
                            dictionary[condition].update({"complication": complication})
                    break
                elif new_condition_name in Condition_Events.PERMANENT:
                    cat.get_permanent_condition(
                        new_condition_name, event_triggered=event_triggered
                    )
                    break

                # break out of risk giving loop cus we don't want to give multiple risks for one condition
                if infection_event:
                    return infection_event
                break

    @staticmethod
    def use_herbs(cat, condition, conditions, source):
        # herbs that can be used for the condition and the Clan has available
        clan_herbs = set()
        needed_herbs = set()
        clan_herbs.update(game.clan.herbs.keys())
        try:
            needed_herbs.update(source[condition]["herbs"])
        except KeyError:
            print(
                f"WARNING: {condition} does not exist in it's condition dict! if the condition is 'thorn in paw' or "
                "'splinter', disregard this! otherwise, check that your condition is in the correct dict or report "
                "this as a bug."
            )
            return
        if game.clan.game_mode == "classic":
            herb_set = needed_herbs
        else:
            herb_set = clan_herbs.intersection(needed_herbs)
        usable_herbs = list(herb_set)

        if not source[condition]["herbs"]:
            return

        if usable_herbs:
            keys = conditions[condition].keys()
            # determine the effect of the herb
            possible_effects = []
            if conditions[condition]["mortality"] != 0:
                possible_effects.append("mortality")
            if conditions[condition]["risks"]:
                possible_effects.append("risks")
            if "duration" in keys:
                if conditions[condition]["duration"] > 1:
                    possible_effects.append("duration")
            if not possible_effects:
                return

            effect = random.choice(possible_effects)

            herb_used = usable_herbs[0]
            # Failsafe, since I have no idea why we are getting 0-herb entries.

            # classic doesn't actually count herbs 
            if game.clan.game_mode != "classic":
                while game.clan.herbs[herb_used] <= 0:
                    print(
                        f"Warning: {herb_used} was chosen to use, although you currently have "
                        f"{game.clan.herbs[herb_used]}. Removing {herb_used} from herb dict, finding a new herb..."
                    )
                    game.clan.herbs.pop(herb_used)
                    usable_herbs.pop(0)
                    if usable_herbs:
                        herb_used = usable_herbs[0]
                    else:
                        print("No herbs to use for this injury")
                        return

            # deplete the herb
            amount_used = 1
            if game.clan.game_mode != "classic":
                game.clan.herbs[herb_used] -= amount_used
                if game.clan.herbs[herb_used] <= 0:
                    game.clan.herbs.pop(herb_used)

            # applying a modifier for herb priority. herbs that are better for the condition will have stronger effects
            count = 0
            for herb in source[condition]["herbs"]:
                count += 1
                if herb == herb_used:
                    break
            modifier = count
            if cat.status in ["elder", "kitten"]:
                modifier = modifier * 2

            effect_message = "this should not show up"
            if effect == "mortality":
                effect_message = "They will be less likely to die."
                conditions[condition]["mortality"] += (
                    11 - modifier + int(amount_used * 1.5)
                )
                if conditions[condition]["mortality"] < 1:
                    conditions[condition]["mortality"] = 1
            elif effect == "duration":
                effect_message = "They will heal sooner."
                conditions[condition]["duration"] -= 1
            elif effect == "risks":
                effect_message = (
                    "The risks associated with their condition are lowered."
                )
                for risk in conditions[condition]["risks"]:
                    risk["chance"] += 11 - modifier + int(amount_used * 1.5)
                    if risk["chance"] < 0:
                        risk["chance"] = 0

            text = f"{cat.name} was given {herb_used.replace('_', ' ')} as treatment for {condition}. {effect_message}"
            game.herb_events_list.append(text)
        else:
            # if they didn't get any herbs, make them more likely to die!! kill the kitties >:)
            if conditions[condition]["mortality"] > 2:
                conditions[condition]["mortality"] -= 1
            for risk in conditions[condition]["risks"]:
                if risk["chance"] > 2:
                    risk["chance"] -= 1


