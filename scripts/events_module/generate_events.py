#!/usr/bin/env python3
# -*- coding: ascii -*-
import random

import i18n
import ujson
from copy import deepcopy

from scripts.cat_relations.enums import RelType
from scripts.events_module.event_filters import (
    event_for_location,
    event_for_season,
    event_for_tags,
    event_for_reputation,
    event_for_cat,
    event_for_freshkill_supply,
    event_for_herb_supply,
    event_for_clan_relations,
    cat_for_event,
)
from scripts.events_module.ongoing.ongoing_event import OngoingEvent
from scripts.events_module.short.short_event import ShortEvent
from scripts.game_structure import constants
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource
from scripts.utility import (
    get_living_clan_cat_count,
<<<<<<< HEAD
    get_alive_status_cats,
    get_cluster
=======
>>>>>>> development
)


def get_resource_directory(fallback=False):
    return f"resources/lang/{i18n.config.get('locale') if not fallback else i18n.config.get('fallback')}/events/"


# ---------------------------------------------------------------------------- #
#                Tagging Guidelines can be found at the bottom                 #
# ---------------------------------------------------------------------------- #


class GenerateEvents:
    loaded_events = {}

    with open(
        f"resources/dicts/conditions/injuries.json", "r", encoding="utf-8"
    ) as read_file:
        INJURIES = ujson.loads(read_file.read())

    @staticmethod
    def get_short_event_dicts(file_path):
        try:
            with open(
                get_resource_directory() + file_path, "r", encoding="utf-8"
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            try:
                with open(
                    get_resource_directory(fallback=True) + file_path,
                    "r",
                    encoding="utf-8",
                ) as read_file:
                    events = ujson.loads(read_file.read())
            except:
                print(f"ERROR: Unable to load {file_path}.")
                return None

        return events

    @staticmethod
    def get_ongoing_event_dicts(file_path):
        events = None
        try:
            with open(file_path, "r", encoding="utf-8") as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"ERROR: Unable to load events from biome {file_path}.")

        return events

    @staticmethod
    def get_death_reaction_dicts(family_relation, rel_value):
        return load_lang_resource(
            f"events/death/death_reactions/{family_relation}/{family_relation}_{rel_value}.json"
        )

    @staticmethod
    def get_lead_den_event_dicts(event_type: str, success: bool):
        try:
            file_path = f"{get_resource_directory()}leader_den/{'success' if success else 'fail'}/{event_type}.json"
            with open(file_path, "r", encoding="utf-8") as read_file:
                events = ujson.loads(read_file.read())
        except:
            events = None
            print(
                f"ERROR: Unable to load lead den events for {event_type} {'success' if success else 'fail'}."
            )

        return events

    @staticmethod
    def clear_loaded_events():
        GenerateEvents.loaded_events = {}

    @staticmethod
<<<<<<< HEAD
    def generate_short_events(event_triggered, biome):
        # LG
        faith_event = False
        if event_triggered != "faith":
            file_path = f"{resource_directory}{event_triggered}/{biome}.json"
        else:
            faith_event = True
            file_path = "resources/dicts/relationship_events/faith.json"
        # ---
=======
    def generate_short_events(event_triggered, biome, frequency):
        file_path = f"{event_triggered}/{biome}.json"
        load_name = f"{file_path}_{frequency}"
>>>>>>> development

        try:
            if load_name in GenerateEvents.loaded_events:
                return GenerateEvents.loaded_events[load_name]
            else:
                events_dict = GenerateEvents.get_short_event_dicts(file_path)

                event_list = []
                if not events_dict:
                    return event_list
                
                new_events_dict = []
                if faith_event:
                    # this sucks so bad but
                    # i have to go through the dicts with multiple interactions and seperate them here into different events
                    for faith_event in events_dict:
                        for count, text in enumerate(faith_event["interactions"], start=1):
                            new_event = deepcopy(faith_event)
                            new_event["event_text"] = [text]
                            new_event["event_id"] = f"{count}faith_{faith_event['event_id']}"
                            new_events_dict.append(new_event)

                if not new_events_dict:
                    new_events_dict = events_dict
                for event in new_events_dict:
                    event_text = event["event_text"] if "event_text" in event else None
                    event_frequency = event["frequency"] if "frequency" in event else 4
                    if not event_text:
                        event_text = (
                            event["death_text"] if "death_text" in event else None
                        )

                    if not event_text:
                        print(
                            f"WARNING: some events resources which are used in generate_events have no 'event_text'."
                        )

                    if frequency != event_frequency:
                        continue

                    event = ShortEvent(
                        event_id=event["event_id"] if "event_id" in event else "",
                        location=event["location"] if "location" in event else ["any"],
                        faith_effect=event["faith_effect"] if "faith_effect" in event else 0,
                        season=event["season"] if "season" in event else ["any"],
                        sub_type=event["sub_type"] if "sub_type" in event else [],
                        tags=event["tags"] if "tags" in event else [],
                        text=event_text,
                        new_accessory=(
                            event["new_accessory"] if "new_accessory" in event else []
                        ),
                        m_c=event["m_c"] if "m_c" in event else {},
                        r_c=event["r_c"] if "r_c" in event else {},
                        new_cat=event["new_cat"] if "new_cat" in event else [],
                        injury=event["injury"] if "injury" in event else [],
                        exclude_involved=(
                            event["exclude_involved"]
                            if "exclude_involved" in event
                            else []
                        ),
                        history=event["history"] if "history" in event else [],
                        relationships=(
                            event["relationships"] if "relationships" in event else []
                        ),
                        outsider=event["outsider"] if "outsider" in event else {},
                        other_clan=event["other_clan"] if "other_clan" in event else {},
                        supplies=event["supplies"] if "supplies" in event else [],
                        new_gender=event["new_gender"] if "new_gender" in event else [],
                        future_event=event["future_event"]
                        if "future_event" in event
                        else {},
                    )
                    event_list.append(event)

                # Add to loaded events.
                GenerateEvents.loaded_events[load_name] = event_list
                return event_list
        except:
            print(f"WARNING: {file_path} was not found, check short event generation")

    @staticmethod
    def generate_ongoing_events(event_type, biome, specific_event=None):
        file_path = f"{get_resource_directory()}/{event_type}/{biome}.json"

        if file_path in GenerateEvents.loaded_events:
            return GenerateEvents.loaded_events[file_path]
        else:
            events_dict = GenerateEvents.get_short_event_dicts(file_path)

            if not specific_event:
                event_list = []
                for event in events_dict:
                    event = OngoingEvent(
                        event=event["event"],
                        camp=event["camp"],
                        season=event["season"],
                        tags=event["tags"],
                        priority=event["priority"],
                        duration=event["duration"],
                        current_duration=0,
                        rarity=event["rarity"],
                        trigger_events=event["trigger_events"],
                        progress_events=event["progress_events"],
                        conclusion_events=event["conclusion_events"],
                        secondary_disasters=event["secondary_disasters"],
                        collateral_damage=event["collateral_damage"],
                    )
                    event_list.append(event)
                return event_list
            else:
                event = None
                for event in events_dict:
                    if event["event"] != specific_event:
                        continue
                    event = OngoingEvent(
                        event=event["event"],
                        camp=event["camp"],
                        season=event["season"],
                        tags=event["tags"],
                        priority=event["priority"],
                        duration=event["duration"],
                        current_duration=0,
                        progress_events=event["progress_events"],
                        conclusion_events=event["conclusion_events"],
                        collateral_damage=event["collateral_damage"],
                    )
                    break
                return event

    @staticmethod
    def possible_short_events(
        frequency,
        event_type=None,
    ):
        event_list = []

        # skip the rest of the loading if there is an unrecognised biome
        temp_biome = (
            game.clan.biome
            if not game.clan.override_biome
            else game.clan.override_biome
        )
        if temp_biome not in constants.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES "
                f"in clan.py?"
            )

        biome = temp_biome.lower()

        # biome specific events
        event_list.extend(
            GenerateEvents.generate_short_events(event_type, biome, frequency)
        )

        # any biome events
        event_list.extend(
            GenerateEvents.generate_short_events(event_type, "general", frequency)
        )

        return event_list

    @staticmethod
    def filter_possible_short_events(
        Cat_class,
        possible_events,
        cat,
        other_clan,
        freshkill_active,
        freshkill_trigger_factor,
        random_cat=None,
        sub_types=None,
        allowed_events=None,
        excluded_events=None,
        ignore_subtyping=False,
    ):
        final_events = []
        incorrect_format = []

        for event in possible_events:
            if event.history:
                if (
                    not isinstance(event.history, list)
                    or "cats" not in event.history[0]
                ):
                    if (
                        f"{event.event_id} history formatted incorrectly"
                        not in incorrect_format
                    ):
                        incorrect_format.append(
                            f"{event.event_id} history formatted incorrectly"
                        )
            if event.injury:
                if not isinstance(event.injury, list) or "cats" not in event.injury[0]:
                    if (
                        f"{event.event_id} injury formatted incorrectly"
                        not in incorrect_format
                    ):
                        incorrect_format.append(
                            f"{event.event_id} injury formatted incorrectly"
                        )

            # check if event is in allowed or excluded
            if allowed_events and event.event_id not in allowed_events:
                continue
            if excluded_events and event.event_id in excluded_events:
                continue

            # if requirements are overridden, allow event through
            if constants.CONFIG["event_generation"]["debug_override_requirements"]:
                final_events.append(event)
                continue

            # check for event sub_type
            if not ignore_subtyping:
                if set(event.sub_type) != set(sub_types):
                    continue

            if not event_for_location(event.location):
                continue

            if not event_for_season(event.season):
                continue

            # check tags
            if not event_for_tags(event.tags, cat, random_cat):
                continue

            # make complete leader death less likely until the leader is over 150 moons (or unless it's a murder)
            if cat.status.is_leader:
                if "all_lives" in event.tags and "murder" not in event.sub_type:
                    if int(cat.moons) < 150 and int(random.random() * 5):
                        continue

<<<<<<< HEAD
                leader_lives = game.clan.leader_lives

                # make sure that 'some lives' and "lives_remain" events don't show up if the leader doesn't have
                # multiple lives to spare
                if "some_lives" in event.tags and leader_lives <= 3:
                    continue
                if "lives_remain" in event.tags and leader_lives < 2:
                    continue

                # check leader life count
                if "high_lives" in event.tags and leader_lives not in [7, 8, 9]:
                    continue
                elif "mid_lives" in event.tags and leader_lives not in [4, 5, 6]:
                    continue
                elif "low_lives" in event.tags and leader_lives not in [1, 2, 3]:
                    continue

            discard = False
            for rank in Cat_class.rank_sort_order:
                if f"clan:{rank}" in event.tags:
                    if rank in ["leader", "deputy"] and not get_alive_status_cats(
                        Cat_class, [rank]
                    ):
                        discard = True
                    elif not len(get_alive_status_cats(Cat_class, [rank])) >= 2:
                        discard = True
            if discard:
                continue

            if "clan_apps" in event.tags and not get_alive_status_cats(
                    Cat_class,
                    ["apprentice", "medicine cat apprentice", "mediator apprentice", "queen's apprentice"],
            ):
                continue

            # If the cat or any of their mates have "no kits" toggled, forgo the adoption event.
            if "adoption" in event.tags:
                if cat.no_kits:
                    continue
                if cat.moons <= 14 + cat.age_moons["kitten"][1]:
                    continue
                if any(Cat_class.fetch_cat(i).no_kits for i in cat.mates):
                    continue

=======
>>>>>>> development
            # check for old age
            if (
                "old_age" in event.sub_type
                and cat.moons < constants.CONFIG["death_related"]["old_age_death_start"]
            ):
                continue
            # remove some non-old age events to encourage elders to die of old age more often
            if (
                "old_age" not in event.sub_type
                and cat.moons > constants.CONFIG["death_related"]["old_age_death_start"]
                and int(random.random() * 3)
            ):
                continue

            # check if already trans
            if "transition" in event.sub_type and cat.gender != cat.genderalign:
                continue

<<<<<<< HEAD
            if event.m_c:
                if cat.age not in event.m_c["age"] and "any" not in event.m_c["age"]:
                    continue
                if (
                    cat.status not in event.m_c["status"]
                    and "any" not in event.m_c["status"]
                ):
                    continue
                if event.m_c["relationship_status"]:
                    if not filter_relationship_type(
                        group=[cat, random_cat],
                        filter_types=event.m_c["relationship_status"],
                        event_id=event.event_id,
                    ):
                        continue

                # FAITH EVENT STUFF
                if "min_max_faith" in event.m_c:
                    if cat.faith < event.m_c["min_max_faith"][0]:
                        continue
                    if cat.faith > event.m_c["min_max_faith"][1]:
                        continue
                if event.r_c and random_cat and "min_max_faith" in event.r_c:
                    if random_cat.faith < event.r_c["min_max_faith"][0]:
                        continue
                    if random_cat.faith > event.r_c["min_max_faith"][1]:
                        continue

                # residence
                if "residence" in event.m_c:
                    if not cat.dead:
                        continue
                    if "ur" in event.m_c["residence"]:
                        if not cat.outside:
                            continue
                    if "df" in event.m_c["residence"]:
                        if not cat.df:
                            continue
                    if "sc" in event.m_c["residence"]:
                        if cat.outside or cat.df:
                            continue
                if "shunned" in event.m_c:
                    if event.m_c["shunned"] is True and cat.shunned == 0:
                        continue
                    elif event.m_c["shunned"] is False and cat.shunned != 0:
                        continue

                # check cat trait and skill
                if (
                    int(random.random() * trait_skill_bypass) or prevent_bypass
                ):  # small chance to bypass
                    has_trait = False
                    if event.m_c["trait"]:
                        if cat.personality.trait in event.m_c["trait"]:
                            has_trait = True
                    
                    # LG
                    has_cluster = False
                    if "cluster" in event.m_c and event.m_c["cluster"]:
                        cluster1, cluster2 = get_cluster(cat.personality.trait)
                        if (
                            cluster1 in event.m_c["cluster"] or
                            cluster2 in event.m_c["cluster"]
                            ):
                            has_cluster = True
                    
                    if "df_status" in event.m_c and event.m_c["df_status"]:
                        if cat.joined_df is False:
                            continue
                        else:
                            if cat.graduated_df and "warrior" not in event.m_c["df_status"]:
                                continue
                            if not cat.graduated_df and "apprentice" not in event.m_c["df_status"]:
                                continue
                    #  ---

                    has_skill = False
                    if event.m_c["skill"]:
                        for _skill in event.m_c["skill"]:
                            split = _skill.split(",")

                            if len(split) < 2:
                                print("Cat skill incorrectly formatted", _skill)
                                continue

                            if cat.skills.meets_skill_requirement(
                                split[0], int(split[1])
                            ):
                                has_skill = True
                                break

                    if event.m_c["trait"] and event.m_c["skill"]:
                        if not has_trait or has_skill:
                            continue
                    elif event.m_c["trait"]:
                        if not has_trait:
                            continue
                    elif event.m_c["skill"]:
                        if not has_skill:
                            continue

                    if "cluster" in event.m_c and event.m_c["cluster"]:
                        if not has_cluster:
                            continue

                    # check cat negate trait and skill
                    has_trait = False
                    if event.m_c["not_trait"]:
                        if cat.personality.trait in event.m_c["not_trait"]:
                            has_trait = True

                    has_skill = False
                    if event.m_c["not_skill"]:
                        for _skill in event.m_c["not_skill"]:
                            split = _skill.split(",")

                            if len(split) < 2:
                                print("Cat skill incorrectly formatted", _skill)
                                continue

                            if cat.skills.meets_skill_requirement(
                                split[0], int(split[1])
                            ):
                                has_skill = True
                                break

                    if has_trait or has_skill:
                        continue

                # check backstory
                if event.m_c["backstory"]:
                    if cat.backstory not in event.m_c["backstory"]:
                        continue

                # check gender for transition events
                if event.m_c["gender"]:
                    if (
                        cat.gender not in event.m_c["gender"]
                        and "any" not in event.m_c["gender"]
                    ):
                        continue


            # check that a random_cat is available to use for r_c
            if event.r_c and random_cat:
                if (
                    random_cat.age not in event.r_c["age"]
                    and "any" not in event.r_c["age"]
                ):
                    continue
                if (
                    random_cat.status not in event.r_c["status"]
                    and "any" not in event.r_c["status"]
                ):
                    continue
                if event.r_c["relationship_status"]:
                    if not filter_relationship_type(
                        group=[cat, random_cat],
                        filter_types=event.r_c["relationship_status"],
                        event_id=event.event_id,
                    ):
                        continue

                # residence
                if "residence" in event.r_c:
                    if not random_cat.dead:
                        continue
                    if "ur" in event.r_c["residence"]:
                        if not random_cat.outside:
                            continue
                    if "df" in event.r_c["residence"]:
                        if not random_cat.df:
                            continue
                    if "sc" in event.r_c["residence"]:
                        if random_cat.outside or random_cat.df:
                            continue

                if "shunned" in event.r_c:
                    if event.r_c["shunned"] is True and cat.shunned == 0:
                        continue
                    elif event.r_c["shunned"] is False and cat.shunned != 0:
                        continue

                # check cat trait and skill
                if (
                    int(random.random() * trait_skill_bypass) or prevent_bypass
                ):  # small chance to bypass
                    has_trait = False
                    if event.r_c["trait"]:
                        if random_cat.personality.trait in event.r_c["trait"]:
                            has_trait = True

                    # LG
                    has_cluster = False
                    if  "cluster" in event.r_c and event.r_c["cluster"]:
                        cluster1, cluster2 = get_cluster(random_cat.personality.trait)
                        if (
                            cluster1 in event.r_c["cluster"] or
                            cluster2 in event.r_c["cluster"]
                            ):
                            has_cluster = True
                    if "df_status" in event.r_c and event.r_c["df_status"]:
                        if random_cat.joined_df is False:
                            continue
                        else:
                            if random_cat.graduated_df and "warrior" not in event.r_c["df_status"]:
                                continue
                            if not random_cat.graduated_df and "apprentice" not in event.r_c["df_status"]:
                                continue
                    #  ---

                    has_skill = False
                    if event.r_c["skill"]:
                        for _skill in event.r_c["skill"]:
                            split = _skill.split(",")

                            if len(split) < 2:
                                print("random_cat skill incorrectly formatted", _skill)
                                continue

                            if random_cat.skills.meets_skill_requirement(
                                split[0], int(split[1])
                            ):
                                has_skill = True
                                break

                    if event.r_c["trait"] and event.r_c["skill"]:
                        if not has_trait or has_skill:
                            continue
                    elif event.r_c["trait"]:
                        if not has_trait:
                            continue
                    elif event.r_c["skill"]:
                        if not has_skill:
                            continue
                    
                    if "cluster" in event.r_c and event.r_c["cluster"]:
                        if not has_cluster:
                            continue

                    # check cat negate trait and skill
                    has_trait = False
                    if event.r_c["not_trait"]:
                        if random_cat.personality.trait in event.r_c["not_trait"]:
                            has_trait = True

                    has_skill = False
                    if event.r_c["not_skill"]:
                        for _skill in event.r_c["not_skill"]:
                            split = _skill.split(",")

                            if len(split) < 2:
                                print("random_cat skill incorrectly formatted", _skill)
                                continue

                            if random_cat.skills.meets_skill_requirement(
                                split[0], int(split[1])
                            ):
                                has_skill = True
                                break

                    if has_trait or has_skill:
                        continue

                # check backstory
                if event.r_c["backstory"]:
                    if random_cat.backstory not in event.r_c["backstory"]:
                        continue

            # check that injury is possible
            if event.injury:
                # determine which injury severity list will be used
                allowed_severity = None
                discard = False
                if cat.status in GenerateEvents.INJURY_DISTRIBUTION:
                    minor_chance = GenerateEvents.INJURY_DISTRIBUTION[cat.status][
                        "minor"
                    ]
                    major_chance = GenerateEvents.INJURY_DISTRIBUTION[cat.status][
                        "major"
                    ]
                    severe_chance = GenerateEvents.INJURY_DISTRIBUTION[cat.status][
                        "severe"
                    ]
                    severity_chosen = random.choices(
                        ["minor", "major", "severe"],
                        [minor_chance, major_chance, severe_chance],
                        k=1,
                    )
                    if severity_chosen[0] == "minor":
                        allowed_severity = "minor"
                    elif severity_chosen[0] == "major":
                        allowed_severity = "major"
                    else:
                        allowed_severity = "severe"

                for block in event.injury:
                    for injury in block["injuries"]:
                        if injury in GenerateEvents.INJURIES:
                            if (
                                GenerateEvents.INJURIES[injury]["severity"]
                                != allowed_severity
                            ):
                                discard = True
                                break

                            if "m_c" in block["cats"]:
                                if injury == "mangled tail" and (
                                    "NOTAIL" in cat.pelt.scars
                                    or "HALFTAIL" in cat.pelt.scars
                                ):
                                    continue

                                if injury == "torn ear" and "NOEAR" in cat.pelt.scars:
                                    continue
                            if "r_c" in block["cats"]:
                                if injury == "mangled tail" and (
                                    "NOTAIL" in random_cat.pelt.scars
                                    or "HALFTAIL" in random_cat.pelt.scars
                                ):
                                    continue

                                if (
                                    injury == "torn ear"
                                    and "NOEAR" in random_cat.pelt.scars
                                ):
                                    continue

=======
            m_c_injuries = []
            r_c_injuries = []
            discard = False
            for block in event.injury:
                for injury in block["injuries"]:
                    if "m_c" in block["cats"]:
                        m_c_injuries.append(injury)
                    if "r_c" in block["cats"]:
                        r_c_injuries.append(injury)
>>>>>>> development
                if discard:
                    continue

            # check if m_c is allowed this event
            if event.m_c:
                if not event_for_cat(
                    cat_info=event.m_c,
                    cat=cat,
                    cat_group=[cat, random_cat] if random_cat else None,
                    event_id=event.event_id,
                    injuries=m_c_injuries,
                ):
                    continue
            # if a random cat was pre-chosen, then we check if the event will be suitable for them
            if random_cat:
                if not event_for_cat(
                    cat_info=event.r_c,
                    cat=random_cat,
                    cat_group=[random_cat, cat],
                    event_id=event.event_id,
                    injuries=r_c_injuries,
                ):
                    continue

            # check if outsider event is allowed
            if event.outsider:
                if not event_for_reputation(event.outsider["current_rep"]):
                    continue

            # other Clan related checks
            if event.other_clan:
                if not other_clan:
                    continue

                if not event_for_clan_relations(
                    event.other_clan["current_rep"], other_clan
                ):
                    continue

                # during a war we want to encourage the clans to have positive events
                # when the overall war notice was positive
                if "war" in event.sub_type:
                    rel_change_type = switch_get_value(Switch.war_rel_change_type)
                    if (
                        event.other_clan["changed"] < 0
                        and rel_change_type != "rel_down"
                    ):
                        continue

            # clans below a certain age can't have their supplies messed with
            if game.clan.age < 5 and event.supplies:
                continue

            elif event.supplies:
                clan_size = get_living_clan_cat_count(Cat_class)
                discard = False
                for supply in event.supplies:
                    trigger = supply["trigger"]
                    supply_type = supply["type"]
                    if supply_type == "freshkill":
                        if not freshkill_active:
                            continue

                        if not event_for_freshkill_supply(
                            game.clan.freshkill_pile,
                            trigger,
                            freshkill_trigger_factor,
                            clan_size,
                        ):
                            discard = True
                            break
                        else:
                            discard = False

                    else:  # if supply type wasn't freshkill, then it must be a herb type
                        if not event_for_herb_supply(trigger, supply_type, clan_size):
                            discard = True
                            break
                        else:
                            discard = False

                if discard:
                    continue

            # LG
            # Slightly changing the event weight based on the cats current faiths
            if event.faith_effect:
                if event.faith_effect > 0:
                    if event.m_c:
                        if "affected" in event.m_c and event.m_c["affected"] is True:
                            if cat.faith < 0:
                                event.weight -= round(event.weight / 3)
                    if event.r_c:
                        if "affected" in event.m_c and event.m_c["affected"] is True:
                            if random_cat.faith < 0:
                                event.weight -= round(event.weight / 3)
                elif event.faith_effect < 0:
                    if event.m_c:
                        if "affected" in event.m_c and event.m_c["affected"] is True:
                            if cat.faith > 0:
                                event.weight -= round(event.weight / 3)
                    if event.r_c:
                        if "affected" in event.m_c and event.m_c["affected"] is True:
                            if random_cat.faith > 0:
                                event.weight -= round(event.weight / 3)
                elif event.faith_effect == 0:
                    if event.m_c:
                        if "affected" in event.m_c and event.m_c["affected"] is True:
                            if (
                                cat.faith > 2 or
                                cat.faith < 2
                                ):
                                event.weight -= round(event.weight / 3)
                    if event.r_c:
                        if "affected" in event.m_c and event.m_c["affected"] is True:
                            if (
                                random_cat.faith > 2 or
                                random_cat.faith < 2
                                ):
                                event.weight -= round(event.weight / 3)
            # ------


            final_events.extend([event] * event.weight)
        if not final_events:
            return None, None

        cat_list = [
            c for c in Cat_class.all_cats.values() if c.status.alive_in_player_clan
        ]
        chosen_cat = None
        chosen_event = None

        if random_cat:
            chosen_cat = random_cat
            # if we've got our random cat already, then check if we have to find an ensured event
            if constants.CONFIG["event_generation"]["debug_ensure_event_id"]:
                for event in final_events:
                    if (
                        event.event_id
                        == constants.CONFIG["event_generation"]["debug_ensure_event_id"]
                    ):
                        chosen_event = event
                        break
            # else, pick a random one from the available events
            elif not chosen_event:
                chosen_event = random.choice(final_events)

        failed_ids = []
        while final_events and not chosen_cat and not chosen_event:
            chosen_event = random.choice(final_events)
            if chosen_event.event_id in failed_ids:
                final_events.remove(chosen_event)
                chosen_event = None
                continue

            # if we have an ensured id, only allow that event past
            if (
                constants.CONFIG["event_generation"]["debug_ensure_event_id"]
                and constants.CONFIG["event_generation"]["debug_ensure_event_id"]
                != chosen_event.event_id
            ):
                final_events.remove(chosen_event)
                chosen_event = None
                continue

            if not chosen_event.r_c:
                break

            # if we're overriding requirements, don't bother looking for an appropriate cat
            if constants.CONFIG["event_generation"]["debug_override_requirements"]:
                chosen_cat = random.choice(cat_list)
                continue

            # gotta gather injuries so we can check if the cat can get them
            r_c_injuries = []
            for block in chosen_event.injury:
                r_c_injuries.extend(block["injuries"] if "r_c" in block["cats"] else [])

            chosen_cat = cat_for_event(
                constraint_dict=chosen_event.r_c,
                possible_cats=cat_list,
                comparison_cat=cat,
                comparison_cat_rel_status=chosen_event.m_c.get(
                    "relationship_status", []
                ).copy(),
                injuries=r_c_injuries,
                return_id=False,
            )

            if not chosen_cat:
                failed_ids.append(chosen_event.event_id)
                final_events.remove(chosen_event)
                chosen_event = None
            else:
                break

        for notice in incorrect_format:
            print(notice)

        return chosen_event, chosen_cat

    @staticmethod
    def possible_ongoing_events(event_type=None, specific_event=None):
        event_list = []

        if game.clan.biome not in constants.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES in clan.py?"
            )

        else:
            biome = game.clan.biome.lower()
            if not specific_event:
                event_list.extend(
                    GenerateEvents.generate_ongoing_events(event_type, biome)
                )
                """event_list.extend(
                    GenerateEvents.generate_ongoing_events(event_type, "general", specific_event)
                )"""
                return event_list
            else:
                event = GenerateEvents.generate_ongoing_events(
                    event_type, biome, specific_event
                )
                return event

    @staticmethod
    def possible_death_reactions(family_relation, rel_value, trait, body_status):
        possible_events = []
        # grab general events first, since they'll always exist
        events = GenerateEvents.get_death_reaction_dicts("general", rel_value)
        possible_events.extend(events["general"][body_status])
        if trait in events and body_status in events[trait]:
            possible_events.extend(events[trait][body_status])

        # grab family events if they're needed. Family events should not be romantic.
        if family_relation != "general" and rel_value != RelType.ROMANCE:
            events = GenerateEvents.get_death_reaction_dicts(family_relation, rel_value)
            possible_events.extend(events["general"][body_status])
            if trait in events and body_status in events[trait]:
                possible_events.extend(events[trait][body_status])

        return possible_events

    def possible_lead_den_events(
        self,
        cat,
        event_type: str,
        interaction_type: str,
        success: bool,
        other_clan_temper=None,
        player_clan_temper=None,
    ) -> list:
        """
        finds and generates a list of possible leader den events
        :param cat: the cat object of the cat attending the Gathering
        :param other_clan_temper: the temperament of the other clan
        :param player_clan_temper: the temperament of the player clan
        :param event_type: other_clan or outsider
        :param interaction_type: str retrieved from object_ID of selected interaction button
        :param success: True if the interaction was a success, False if it was a failure
        """
        possible_events = []

        events = GenerateEvents.get_lead_den_event_dicts(event_type, success)
        for event in events:
            if event["interaction_type"] != interaction_type:
                continue

            if "other_clan_temper" in event or "player_clan_temper" in event:
                if (
                    other_clan_temper not in event["other_clan_temper"]
                    and "any" not in event["other_clan_temper"]
                ):
                    continue
                if (
                    player_clan_temper not in event["player_clan_temper"]
                    and "any" not in event["player_clan_temper"]
                ):
                    continue

            elif "reputation" in event:
                if not event_for_reputation(event["reputation"]):
                    continue

            cat_info = event["m_c"]
            if not event_for_cat(cat_info=cat_info, cat=cat):
                continue

            possible_events.append(event)

        return possible_events


generate_events = GenerateEvents()
