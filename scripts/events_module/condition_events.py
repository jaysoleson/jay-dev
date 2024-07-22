import ujson
import random
from copy import deepcopy

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.cat.pelts import Pelt
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.utility import event_text_adjust, get_med_cats, change_relationship_values, change_clan_relations, \
    history_text_adjust
from scripts.game_structure.game_essentials import game
from scripts.events_module.scar_events import Scar_Events
from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure.windows import RetireScreen

from scripts.event_class import Single_Event


# ---------------------------------------------------------------------------- #
#                             Condition Event Class                            #
# ---------------------------------------------------------------------------- #

class Condition_Events():
    """All events with a connection to conditions."""

    resource_directory = "resources/dicts/conditions/"

    ILLNESSES = None
    with open(f"{resource_directory}illnesses.json", 'r') as read_file:
        ILLNESSES = ujson.loads(read_file.read())

    INJURIES = None
    with open(f"{resource_directory}injuries.json", 'r') as read_file:
        INJURIES = ujson.loads(read_file.read())

    PERMANENT = None
    with open(f"resources/dicts/conditions/permanent_conditions.json", 'r') as read_file:
        PERMANENT = ujson.loads(read_file.read())
    # ---------------------------------------------------------------------------- #
    #                                    CHANCE                                    #
    # ---------------------------------------------------------------------------- #

    ILLNESSES_SEASON_LIST = None
    with open(f"resources/dicts/conditions/illnesses_seasons.json", 'r') as read_file:
        ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

    INJURY_DISTRIBUTION = None
    with open(f"resources/dicts/conditions/event_injuries_distribution.json", 'r') as read_file:
        INJURY_DISTRIBUTION = ujson.loads(read_file.read())

    # ---------------------------------------------------------------------------- #
    #                                   STRINGS                                    #
    # ---------------------------------------------------------------------------- #

    PERM_CONDITION_RISK_STRINGS = None
    with open(f"resources/dicts/conditions/risk_strings/permanent_condition_risk_strings.json", 'r') as read_file:
        PERM_CONDITION_RISK_STRINGS = ujson.loads(read_file.read())

    ILLNESS_RISK_STRINGS = None
    with open(f"resources/dicts/conditions/risk_strings/illness_risk_strings.json", 'r') as read_file:
        ILLNESS_RISK_STRINGS = ujson.loads(read_file.read())

    INJURY_RISK_STRINGS = None
    with open(f"resources/dicts/conditions/risk_strings/injuries_risk_strings.json", 'r') as read_file:
        INJURY_RISK_STRINGS = ujson.loads(read_file.read())

    CONGENITAL_CONDITION_GOT_STRINGS = None
    with open(f"resources/dicts/conditions/condition_got_strings/gain_congenital_condition_strings.json", 'r') as read_file:
        CONGENITAL_CONDITION_GOT_STRINGS = ujson.loads(read_file.read())

    PERMANENT_CONDITION_GOT_STRINGS = None
    with open(f"resources/dicts/conditions/condition_got_strings/gain_permanent_condition_strings.json", 'r') as read_file:
        PERMANENT_CONDITION_GOT_STRINGS = ujson.loads(read_file.read())

    ILLNESS_HEALED_STRINGS = None
    with open(f"resources/dicts/conditions/healed_and_death_strings/illness_healed_strings.json", 'r') as read_file:
        ILLNESS_HEALED_STRINGS = ujson.loads(read_file.read())

    INJURY_HEALED_STRINGS = None
    with open(f"resources/dicts/conditions/healed_and_death_strings/injury_healed_strings.json", 'r') as read_file:
        INJURY_HEALED_STRINGS = ujson.loads(read_file.read())

    INJURY_DEATH_STRINGS = None
    with open(f"resources/dicts/conditions/healed_and_death_strings/injury_death_strings.json", 'r') as read_file:
        INJURY_DEATH_STRINGS = ujson.loads(read_file.read())
    
    INFECTION_RISK_STRINGS = None
    with open(f"resources/dicts/infection/infection_risk_strings.json", 'r') as read_file:
        INFECTION_RISK_STRINGS = ujson.loads(read_file.read())

    @staticmethod
    def handle_illnesses(cat, season=None):
        """ 
        This function handles overall the illnesses in 'expanded' (or 'cruel season') game mode.
        It will return a bool to indicate if the cat is dead.
        """
        inftype = game.clan.infection["infection_type"]

        # return immediately if they're already dead or in the wrong game-mode
        triggered = False
        if cat.dead or game.clan.game_mode == "classic":
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
            if inftype == "parasitic":
                infected = False
                if "parasitic stage one" in cat.illnesses:
                    witherchance = 85
                    infected = True
                elif "parasitic stage two" in cat.illnesses:
                    witherchance = 70
                    infected = True
                elif "parasitic stage three" in cat.illnesses:
                    witherchance = 40
                    infected = True
                elif "parasitic stage four" in cat.illnesses:
                    witherchance = 30
                    infected = True
                
                if infected:
                    if random.random() < 1 / witherchance and "withering" not in cat.injuries:
                        cat.get_injured("withering")
                        print(cat.name, "is withering")
                        event = f"The infection is beginning to destroy {cat.name}'s body."
                        game.cur_events_list.append(Single_Event(event, ["health", "infection"], cat.ID))
        else:
            # ---------------------------------------------------------------------------- #
            #                              make cats sick                                  #
            # ---------------------------------------------------------------------------- #
            random_number = int(
                random.random() * game.get_config_value("condition_related", f"{game.clan.game_mode}_illness_chance"))
            if not cat.dead and not cat.is_ill() and random_number <= 10 and not event_string:

                # CLAN FOCUS!
                if game.clan.clan_settings.get("rest and recover"):
                    stopping_chance = game.config["focus"]["rest and recover"]["illness_prevent"]
                    if not int(random.random() * stopping_chance):
                        # print(f"rest and recover - illness prevented for {cat.name}")
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
                    while wrong_illness in possible_illnesses and game.clan.infection["infection_type"] != i:
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
                        # failsafe-- you should never see this
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
                    if game.clan.infection["spread_by"] == "bite":
                        strings = [
                            f"{cat.name} was bitten by an infected rogue.",
                            f"{cat.name} stumbles back into camp after an outing with a fresh cat bite and a clouded look in their eyes.",
                            f"{cat.name} tries to hide their fresh wound, but the potent smell of the infection coming from them is too hard to ignore."
                        ]
                        event_string = random.choice(strings)
                        if "spread_by_bite" not in game.clan.infection["logs"]:
                            game.clan.infection["logs"].append("spread_by_bite")
                            event_string += "\nYour log has been updated."
                        cat.get_injured("cat bite")
                    elif game.clan.infection["spread_by"] == "air":
                        strings = [
                            f"{cat.name} leaves camp alone and comes back with clouded eyes that can only mean one thing.",
                            f"{cat.name} stumbles back into camp after an outing with a clouded look in their eyes.",
                            f"{cat.name} has come down with the infection."
                        ]                        
                        event_string = random.choice(strings)
                        if "spread_by_air" not in game.clan.infection["logs"]:
                            game.clan.infection["logs"].append("spread_by_air")
                            event_string += "\nYour log has been updated."

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
            # game.health_events_list.append(event_string)

        # just double-checking that trigger is only returned True if the cat is dead
        if cat.dead:
            triggered = True
        else:
            triggered = False

        return triggered

    @staticmethod
    def handle_injuries(cat, other_cat=None, alive_kits=None, war=None, enemy_clan=None, season=None):
        """ 
        This function handles overall the injuries in 'expanded' (or 'cruel season') game mode.
        Returns: boolean - if an event was triggered
        """
        has_other_clan = False
        triggered = False
        text = None
        random_number = int(random.random() * game.get_config_value("condition_related", f"{game.clan.game_mode}_injury_chance"))

        if cat.dead:
            triggered = True
            return triggered

        involved_cats = [cat.ID]
        injury_event = None
        # handle if the current cat is already injured
        if cat.is_injured() and game.clan.game_mode != 'classic':
            for injury in cat.injuries:
                if injury == "pregnant" and cat.ID not in game.clan.pregnancy_data:
                    print(f"INFO: deleted pregnancy condition of {cat.ID} due no pregnancy data in the clan.")
                    del cat.injuries[injury]
                    return triggered
                elif injury == 'pregnant':
                    return triggered
            triggered, event_string = Condition_Events.handle_already_injured(cat)
            text = event_string
        else:
            # EVENTS
            if not triggered and \
                    cat.personality.trait in ["adventurous",
                                            "bold",
                                            "daring",
                                            "confident",
                                            "ambitious",
                                            "bloodthirsty",
                                            "fierce",
                                            "strict",
                                            "troublesome",
                                            "vengeful",
                                            "impulsive"] and \
                    random_number <= 15:
                triggered = True
            elif not triggered and random_number <= 5:
                triggered = True

            if triggered:
                # CLAN FOCUS!
                if game.clan.clan_settings.get("rest and recover"):
                    stopping_chance = game.config["focus"]["rest and recover"]["injury_prevent"]
                    if not int(random.random() * stopping_chance):
                        # print(f"rest and recover - injury prevented for {cat.name}")
                        return False

                if war:
                    other_clan = enemy_clan
                else:
                    other_clan = random.choice(game.clan.all_clans)
                if other_clan:
                    other_clan_name = f'{other_clan.name}Clan'

                if other_clan_name == 'None':
                    other_clan = game.clan.all_clans[0]
                    other_clan_name = f'{other_clan.name}Clan'

                possible_events = GenerateEvents.possible_short_events(cat.status, cat.age, "injury")
                final_events = GenerateEvents.filter_possible_short_events(possible_events, cat, other_cat, war,
                                                                           enemy_clan, other_clan, alive_kits)

                if len(final_events) > 0:
                    injury_event = random.choice(final_events)

                    if "other_clan" in injury_event.tags or "war" in injury_event.tags:
                        has_other_clan = True

                    if "rel_up" in injury_event.tags:
                        change_clan_relations(other_clan, difference=1)
                    elif "rel_down" in injury_event.tags:
                        change_clan_relations(other_clan, difference=-1)

                    # let's change some relationship values \o/ check if another cat is mentioned
                    if "other_cat" in injury_event.tags:
                        involved_cats.append(other_cat.ID)
                        Condition_Events.handle_relationship_changes(cat, injury_event, other_cat)

                    #print(injury_event.event_text)
                    text = event_text_adjust(Cat, injury_event.event_text, cat, other_cat, other_clan_name)

                    if game.clan.game_mode == "classic":
                        if "scar" in injury_event.tags and len(cat.pelt.scars) < 4:
                            # add tagged scar
                            for scar in Pelt.scars1 + Pelt.scars2 + Pelt.scars3:
                                if scar in injury_event.tags:
                                    cat.pelt.scars.append(scar)

                            # add scar history
                            if injury_event.history_text:
                                if "scar" in injury_event.history_text:
                                    history_text = history_text_adjust(injury_event.history_text['scar'],
                                                                              other_clan_name, game.clan)
                                    History.add_scar(cat, history_text, other_cat=other_cat)
                    else:
                        # record proper history text possibilities
                        if injury_event.history_text:
                            possible_scar = None
                            possible_death = None
                            if "scar" in injury_event.history_text:
                                possible_scar = history_text_adjust(injury_event.history_text['scar'],
                                                                   other_clan_name, game.clan, other_cat_rc = other_cat)
                            if cat.status == 'leader' and 'lead_death' in injury_event.history_text:
                                possible_death = history_text_adjust(injury_event.history_text['lead_death'],
                                                                    other_clan_name, game.clan, other_cat_rc = other_cat)
                            elif cat.status != 'leader' and 'reg_death' in injury_event.history_text:
                                possible_death = history_text_adjust(injury_event.history_text['reg_death'],
                                                                    other_clan_name, game.clan, other_cat_rc = other_cat)

                            if possible_scar or possible_death:
                                History.add_possible_history(cat, injury_event.injury, scar_text=possible_scar, 
                                                             death_text=possible_death, other_cat=other_cat)
                            
                        cat.get_injured(injury_event.injury)

        # just double-checking that trigger is only returned True if the cat is dead
        if cat.status != "leader":
            # only checks for non-leaders, as leaders will not be dead if they are just losing a life
            if cat.dead:
                triggered = True
            else:
                triggered = False

        if text is not None:
            types = ["health"]
            if cat.dead:
                types.append("birth_death")
            if has_other_clan:
                types.append("other_clans")
            # Add event text to the relationship log if two cats are involved
            if other_cat:
                pos_rel_event = ["romantic", "platonic", "neg_dislike", "respect", "comfort", "neg_jealousy", "trust"]
                neg_rel_event = ["neg_romantic", "neg_platonic", "dislike", "neg_respect", "neg_comfort", "jealousy", "neg_trust"]
                effect = ""
                if injury_event:
                    if any(tag in injury_event.tags for tag in pos_rel_event):
                        effect = " (positive effect)"
                    elif any(tag in injury_event.tags for tag in neg_rel_event):
                        effect = " (negative effect)"

                log_text = text + effect

                if cat.moons == 1:
                    cat.relationships[other_cat.ID].log.append(log_text + f" - {cat.name} was {cat.moons} moon old")
                else:
                    cat.relationships[other_cat.ID].log.append(log_text + f" - {cat.name} was {cat.moons} moons old")
            game.cur_events_list.append(Single_Event(text, types, involved_cats))

        return triggered

    @staticmethod
    def handle_relationship_changes(cat, injury_event, other_cat):
        cat_to = None
        cat_from = None
        n = game.config["relationship"]["influence_condition_events"]
        romantic = 0
        platonic = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0
        if "rc_to_mc" in injury_event.tags:
            cat_to = [cat.ID]
            cat_from = [other_cat]
        elif "mc_to_rc" in injury_event.tags:
            cat_to = [other_cat.ID]
            cat_from = [cat]
        elif "to_both" in injury_event.tags:
            cat_to = [cat.ID, other_cat.ID]
            cat_from = [other_cat, cat]
        if "romantic" in injury_event.tags:
            romantic = n
        elif "neg_romantic" in injury_event.tags:
            romantic = -n
        if "platonic" in injury_event.tags:
            platonic = n
        elif "neg_platonic" in injury_event.tags:
            platonic = -n
        if "dislike" in injury_event.tags:
            dislike = n
        elif "neg_dislike" in injury_event.tags:
            dislike = -n
        if "respect" in injury_event.tags:
            admiration = n
        elif "neg_respect" in injury_event.tags:
            admiration = -n
        if "comfort" in injury_event.tags:
            comfortable = n
        elif "neg_comfort" in injury_event.tags:
            comfortable = -n
        if "jealousy" in injury_event.tags:
            jealousy = n
        elif "neg_jealousy" in injury_event.tags:
            jealousy = -n
        if "trust" in injury_event.tags:
            trust = n
        elif "neg_trust" in injury_event.tags:
            trust = -n
        change_relationship_values(
            cat_to,
            cat_from,
            romantic,
            platonic,
            dislike,
            admiration,
            comfortable,
            jealousy,
            trust)

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
            "ARMBONE": ["weak leg"]
        }
        
        scarless_conditions = [
            "weak leg", "paralyzed", "raspy lungs", "wasting disease", "blind", "failing eyesight", "one bad eye",
            "partial hearing loss", "deaf", "constant joint pain", "constantly dizzy", "recurring shock",
            "lasting grief", "persistent headaches"
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
                        conditions = Condition_Events.INJURIES[injury_name]["cause_permanent"]
                        for x in conditions:
                            if x in scarless_conditions:
                                possible_conditions.append(x)
                        if len(possible_conditions) > 0 and not int(random.random() * game.config["condition_related"]["permanent_condition_chance"]):
                            perm_condition = random.choice(possible_conditions)
                        else:
                            return perm_condition
                except KeyError:
                    print(f"WARNING: {injury_name} couldn't be found in injury dict! no permanent condition was given")
                    return perm_condition
            # else:
            #     print(f"WARNING: {scar} for {injury_name} is either None or is not in scar_to_condition dict.")

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
        event = event_text_adjust(Cat, event, cat, other_cat=None)  # adjust the text
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
            if illness in game.switches['skip_conditions']:
                continue

            # use herbs
            Condition_Events.use_herbs(cat, illness, illnesses, Condition_Events.ILLNESSES)

            # moon skip to try and kill or heal cat
            skipped = cat.moon_skip_illness(illness)

            # if event trigger was true, events should be skipped for this illness
            if skipped is True:
                continue

            # death event text and break bc any other illnesses no longer matter
            if cat.dead and cat.status != 'leader':
                if illness not in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three", f"{inftype} stage four"]:
                    event = f"{cat.name} died of {illness}."
                else:
                    event = f"{cat.name} was killed by the infection."
                    infection_event = True
                # clear event list to get rid of any healed or risk event texts from other illnesses
                event_list.clear()
                event_list.append(event)
                History.add_death(cat, event)
                game.herb_events_list.append(event)
                break

            # if the leader died, then break before handling other illnesses cus they'll be fully healed or dead dead
            elif cat.status == 'leader' and starting_life_count != game.clan.leader_lives:
                if illness not in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three", f"{inftype} stage four"]:
                    History.add_death(cat, f"died to {illness}")
                else:
                    History.add_death(cat, "died to the infection") 
                    infection_event = True
                break

            # heal the cat
            elif cat.healed_condition is True:
                if illness in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three",f"{inftype} stage four"]:
                    # id rather stop it from ever being true in the first place for infected cats
                    # because after a certain point, this is happening every moon
                    # but whatever. this works.
                    infection_event = True
                    continue
                History.remove_possible_history(cat, illness)
                game.switches['skip_conditions'].append(illness)
                # gather potential event strings for healed illness
                try:
                    possible_string_list = Condition_Events.ILLNESS_HEALED_STRINGS[illness]
                except:
                    print("couldn't find illness")

                # choose event string
                random_index = int(random.random() * len(possible_string_list))
                event = possible_string_list[random_index]
                event = event_text_adjust(Cat, event, cat, other_cat=None)
                event_list.append(event)
                game.herb_events_list.append(event)
                try:
                    cat.illnesses.pop(illness)
                except:
                    print("ERROR: removing illness")
                # make sure complications get reset if infection or fester were healed
                if illness in ['an infected wound', 'a festering wound']:
                    for injury in cat.injuries:
                        keys = cat.injuries[injury].keys()
                        if 'complication' in keys:
                            cat.injuries[injury]['complication'] = None
                    for condition in cat.permanent_condition:
                        keys = cat.permanent_condition[condition].keys()
                        if 'complication' in keys:
                            cat.permanent_condition[condition]['complication'] = None
                cat.healed_condition = False

                # move to next illness, the cat can't get a risk from an illness that has healed
                continue

            Condition_Events.give_risks(cat, event_list, illness, illness_progression, illnesses, cat.illnesses)
            if infection_event:
                infec = Condition_Events.give_risks(cat, event_list, illness, illness_progression, illnesses, cat.illnesses)
                print("INFEC:", infec)


        # joining event list into one event string
        event_string = None
        if len(event_list) > 0:
            event_string = ' '.join(event_list)
        return event_string, infection_event

    @staticmethod
    def handle_already_injured(cat):
        """
        This function handles, when the cat is already injured
        Returns: boolean (if something happened) and the event_string
        """
        triggered = False
        event_list = []

        injury_progression = {
            "poisoned": "redcough",
            "shock": "lingering shock"
        }

        # need to hold this number so that we can check if the leader has died
        starting_life_count = game.clan.leader_lives

        if game.clan.game_mode == "classic":
            return triggered

        injuries = deepcopy(cat.injuries)
        for injury in injuries:
            if injury in game.switches['skip_conditions']:
                continue

            Condition_Events.use_herbs(cat, injury, injuries, Condition_Events.INJURIES)

            skipped = cat.moon_skip_injury(injury)
            if skipped:
                continue

            if cat.dead or (cat.status == 'leader' and starting_life_count != game.clan.leader_lives):
                triggered = True

                try:
                    possible_string_list = Condition_Events.INJURY_DEATH_STRINGS[injury]
                    event = random.choice(possible_string_list)
                except:
                    print(f'WARNING: {injury} does not have an injury death string, placeholder used')
                    event = "m_c was killed by their injuries."

                event = event_text_adjust(Cat, event, cat)

                if cat.status == 'leader':
                    history_text = event.replace(str(cat.name), " ")
                    History.add_death(cat, condition=injury, death_text=history_text.strip())
                    if not cat.dead:
                        event = event.replace('.', ', losing a life.')
                else:
                    History.add_death(cat, condition=injury, death_text=event)

                # clear event list first to make sure any heal or risk events from other injuries are not shown
                event_list.clear()
                event_list.append(event)
                game.herb_events_list.append(event)
                break
            elif cat.healed_condition is True:
                game.switches['skip_conditions'].append(injury)
                triggered = True
                scar_given = None

                # Try to give a scar, and get the event text to be displayed
                event, scar_given = Scar_Events.handle_scars(cat, injury)
                # If a scar was not given, we need to grab a seperate healed event
                if not scar_given:
                    try:
                        event = random.choice(Condition_Events.INJURY_HEALED_STRINGS[injury])
                    except KeyError:
                        print(f"WARNING: {injury} couldn't be found in the healed strings dict! placeholder string was used.")
                        event = f"m_c's injury {injury} has healed"
                event = event_text_adjust(Cat, event, cat, other_cat=None)
                
                game.herb_events_list.append(event)
                    
                History.remove_possible_history(cat, injury)
                cat.injuries.pop(injury)
                cat.healed_condition = False

                # try to give a permanent condition based on healed injury and new scar if any
                condition_got = Condition_Events.handle_permanent_conditions(cat, injury_name=injury, illness_name=None, scar=scar_given)

                if condition_got is not None:
                    # gather potential event strings for gotten condition
                    possible_string_list = Condition_Events.PERMANENT_CONDITION_GOT_STRINGS[injury][condition_got]

                    # choose event string and ensure Clan's med cat number aligns with event text
                    random_index = random.randrange(0, len(possible_string_list))
                    
                    med_list = get_med_cats(Cat)
                    #If the cat is a med cat, don't conister them as one for the event. 
                    if cat in med_list:
                        med_list.remove(cat)
                    
                    #Choose med cat, if you can
                    if med_list:
                        med_cat = random.choice(med_list)
                    else:
                        med_cat = None
                    
                    if not med_cat and random_index < 2 and len(possible_string_list) >= 3:
                        random_index = 2
        
                    event = possible_string_list[random_index]
                    event = event_text_adjust(Cat, event, cat, other_cat=med_cat)  # adjust the text
                if event is not None:
                    event_list.append(event)
                continue

            Condition_Events.give_risks(cat, event_list, injury, injury_progression, injuries, cat.injuries)

        if len(event_list) > 0:
            event_string = ' '.join(event_list)
        else:
            event_string = None
        return triggered, event_string

    @staticmethod
    def handle_already_disabled(cat):
        """
        this function handles what happens if the cat already has a permanent condition.
        Returns: boolean (if something happened) and the event_string
        """
        triggered = False
        event_types = ["health"]

        if game.clan.game_mode == "classic":
            return triggered

        event_list = []

        condition_progression = {
            "one bad eye": "failing eyesight",
            "failing eyesight": "blind",
            "partial hearing loss": "deaf"
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

                if cat.status != 'leader':
                    History.add_death(cat, death_text=event)
                else:
                    History.add_death(cat, death_text=f"died to {condition}")

                game.herb_events_list.append(event)
                break

            # skipping for whatever reason
            if status == 'skip':
                continue

            # revealing perm condition
            if status == 'reveal':
                # gather potential event strings for gotten risk
                possible_string_list = Condition_Events.CONGENITAL_CONDITION_GOT_STRINGS[condition]

                # choose event string and ensure Clan's med cat number aligns with event text
                random_index = int(random.random() * len(possible_string_list))
                med_list = get_med_cats(Cat)
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
                event = event_text_adjust(Cat, event, cat, other_cat=med_cat)  # adjust the text
                event_list.append(event)
                continue

            # trying herbs
            chance = 0
            if conditions[condition]["severity"] == 'minor':
                chance = 10
            elif conditions[condition]["severity"] == 'major':
                chance = 6
            elif conditions[condition]["severity"] == 'severe':
                chance = 3
            if not int(random.random() * chance):
                Condition_Events.use_herbs(cat, condition, conditions, Condition_Events.PERMANENT)

            # give risks
            Condition_Events.give_risks(cat, event_list, condition, condition_progression, conditions, cat.permanent_condition)

        Condition_Events.determine_retirement(cat, triggered)

        if len(event_list) > 0:
            event_string = ' '.join(event_list)
            game.cur_events_list.append(Single_Event(event_string, event_types, cat.ID))
        return

    @staticmethod
    def determine_retirement(cat, triggered):
        
        if game.clan.clan_settings['retirement'] or cat.no_retire:
            return

        if not triggered and not cat.dead and cat.status not in \
                ['leader', 'medicine cat', 'kitten', 'newborn', 'medicine cat apprentice', 'mediator',
                 'mediator apprentice', "queen", "queen's apprentice", 'elder']:
            for condition in cat.permanent_condition:
                if cat.permanent_condition[condition]['severity'] not in ['major', 'severe']:
                    continue
                    
                if cat.permanent_condition[condition]['severity'] == "severe":
                    # Higher changes for "severe". These are meant to be nearly 100% without
                    # being 100%
                    retire_chances = {
                        'newborn': 0,
                        'kitten': 0,
                        'adolescent': 50,  # This is high so instances where an cat retires the same moon they become an apprentice is rare
                        'young adult': 10,
                        'adult': 5,
                        'senior adult': 5,
                        'senior': 5
                    }
                else:
                    retire_chances = {
                        'newborn': 0,
                        'kitten': 0,
                        'adolescent': 100,
                        'young adult': 80,
                        'adult': 70,
                        'senior adult': 50,
                        'senior': 10
                    }
                
                chance = int(retire_chances.get(cat.age))
                if not int(random.random() * chance):
                    retire_involved = [cat.ID]
                    if cat.age == 'adolescent':
                        event = f"{cat.name} decides they'd rather spend their time helping around camp and entertaining the " \
                                f"kits, they're warmly welcomed into the elder's den."
                    elif game.clan.leader is not None:
                        if not game.clan.leader.dead and not game.clan.leader.exiled and \
                                not game.clan.leader.outside and cat.moons < 120:
                            retire_involved.append(game.clan.leader.ID)
                            event = f"{game.clan.leader.name}, seeing {cat.name} struggling the last few moons " \
                                    f"approaches them and promises them that no one would think less of them for " \
                                    f"retiring early and that they would still be a valuable member of the Clan " \
                                    f"as an elder. {cat.name} agrees and later that day their elder ceremony " \
                                    f"is held."
                        else:
                            event = f'{cat.name} has decided to retire from normal Clan duty.'
                    else:
                        event = f'{cat.name} has decided to retire from normal Clan duty.'

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
            if risk["name"] == 'an infected wound' and 'a festering wound' in cat.illnesses:
                continue
            infection_event = False
            if risk["name"] in [f"{inftype} stage one", f"{inftype} stage two", f"{inftype} stage three", f"{inftype} stage four"]:
                infection_event = True

            # adjust chance of risk gain if Clan has enough meds
            chance = risk["chance"]
            if medical_cats_condition_fulfilled(Cat.all_cats.values(),
                                                get_amount_cat_for_one_medic(game.clan)):
                chance += 10  # lower risk if enough meds
            if game.clan.medicine_cat is None and chance != 0:
                chance = int(chance * .75)  # higher risk if no meds and risk chance wasn't 0
                if chance <= 0:  # ensure that chance is never 0
                    chance = 1

            # if we hit the chance, then give the risk if the cat does not already have the risk
            if chance != 0 and not int(random.random() * chance) and risk['name'] not in dictionary:
                # check if the new risk is a previous stage of a current illness
                skip = False
                if risk['name'] in progression:
                    if progression[risk['name']] in dictionary:
                        skip = True
                # if it is, then break instead of giving the risk
                if skip is True:
                    break

                new_condition_name = risk['name']

                # lower risk of getting it again if not a perm condition
                if dictionary != cat.permanent_condition:
                    saved_condition = dictionary[condition]["risks"]
                    for old_risk in saved_condition:
                        if old_risk['name'] == risk['name']:
                            if new_condition_name in ['an infected wound', 'a festering wound']:
                                # if it's infection or festering, we're removing the chance completely
                                # this is both to prevent annoying infection loops
                                # and bc the illness/injury difference causes problems
                                old_risk["chance"] = 0
                            else:
                                old_risk['chance'] = risk["chance"] + 10

                med_cat = None
                removed_condition = False
                try:
                    # gather potential event strings for gotten condition
                    if dictionary == cat.illnesses:
                        possible_string_list = Condition_Events.ILLNESS_RISK_STRINGS[condition][new_condition_name]
                    elif dictionary == cat.injuries:
                        possible_string_list = Condition_Events.INJURY_RISK_STRINGS[condition][new_condition_name]
                    else:
                        possible_string_list = Condition_Events.PERM_CONDITION_RISK_STRINGS[condition][new_condition_name]

                    # if it is a progressive condition, then remove the old condition and keep the new one
                    if condition in progression and new_condition_name == progression.get(condition):
                        removed_condition = True
                        dictionary.pop(condition)

                    # choose event string and ensure Clan's med cat number aligns with event text
                    random_index = int(random.random() * len(possible_string_list))
                    med_list = get_med_cats(Cat)
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
                    print(f"WARNING: {condition} couldn't be found in the risk strings! placeholder string was used")
                    event = "m_c's condition has gotten worse."

                event = event_text_adjust(Cat, event, cat, other_cat=med_cat)  # adjust the text
                event_list.append(event)

                # we add the condition to this game switch, this is so we can ensure it's skipped over for this moon
                game.switches['skip_conditions'].append(new_condition_name)
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
                    if new_condition_name == 'an infected wound':
                        complication = 'infected'
                    elif new_condition_name == 'a festering wound':
                        complication = 'festering'
                    if complication is not None:
                        if 'complication' in keys:
                            dictionary[condition]['complication'] = complication
                        else:
                            dictionary[condition].update({'complication': complication})
                    break
                elif new_condition_name in Condition_Events.PERMANENT:
                    cat.get_permanent_condition(new_condition_name, event_triggered=event_triggered)
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
            print(f"WARNING: {condition} does not exist in it's condition dict! if the condition is 'thorn in paw' or "
                  "'splinter', disregard this! otherwise, check that your condition is in the correct dict or report "
                  "this as a bug.")
            return
        herb_set = clan_herbs.intersection(needed_herbs)
        usable_herbs = list(herb_set)

        if not source[condition]["herbs"]:
            return

        if usable_herbs:
            keys = conditions[condition].keys()
            # determine the effect of the herb
            possible_effects = []
            if conditions[condition]['mortality'] != 0:
                possible_effects.append('mortality')
            if conditions[condition]["risks"]:
                possible_effects.append('risks')
            if 'duration' in keys:
                if conditions[condition]['duration'] > 1:
                    possible_effects.append('duration')
            if not possible_effects:
                return

            effect = random.choice(possible_effects)

            herb_used = usable_herbs[0]
            # Failsafe, since I have no idea why we are getting 0-herb entries.
            while game.clan.herbs[herb_used] <= 0:
                print(f"Warning: {herb_used} was chosen to use, although you currently have "
                      f"{game.clan.herbs[herb_used]}. Removing {herb_used} from herb dict, finding a new herb...")
                game.clan.herbs.pop(herb_used)
                usable_herbs.pop(0)
                if usable_herbs:
                    herb_used = usable_herbs[0]
                else:
                    print("No herbs to use for this injury")
                    return
                print(f"New herb found: {herb_used}")

            # deplete the herb
            amount_used = 1
            game.clan.herbs[herb_used] -= amount_used
            if game.clan.herbs[herb_used] <= 0:
                game.clan.herbs.pop(herb_used)

            # applying a modifier for herb priority. herbs that are better for the condition will have stronger effects
            count = 0
            for herb in source[condition]['herbs']:
                count += 1
                if herb == herb_used:
                    break
            modifier = count
            if cat.status in ['elder', 'kitten']:
                modifier = modifier * 2

            effect_message = 'this should not show up'
            if effect == 'mortality':
                effect_message = 'They will be less likely to die.'
                conditions[condition]["mortality"] += 11 - modifier + int(amount_used * 1.5)
                if conditions[condition]["mortality"] < 1:
                    conditions[condition]["mortality"] = 1
            elif effect == 'duration':
                effect_message = 'They will heal sooner.'
                conditions[condition]["duration"] -= 1
            elif effect == 'risks':
                effect_message = 'The risks associated with their condition are lowered.'
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
                if risk['chance'] > 2:
                    risk['chance'] -= 1


# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #


