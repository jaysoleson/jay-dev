import random

from scripts.cat.history import History
from scripts.conditions import get_amount_cat_for_one_medic, medical_cats_condition_fulfilled
from scripts.game_structure.game_essentials import game


# ---------------------------------------------------------------------------- #
#                              Scar Event Class                                #
# ---------------------------------------------------------------------------- #

class Scar_Events():
    """All events with a connection to conditions."""

    # scar pools
    bite_scars = [
        "CATBITE", "CATBITETWO"
    ]
    rat_scars = [
        "RATBITE", "TOE"
    ]
    beak_scars = [
        "BEAKCHEEK", "BEAKLOWER", "BEAKSIDE"
    ]
    canid_scars = [
        "LEGBITE", "NECKBITE", "TAILSCAR", "BRIGHTHEART"
    ]
    snake_scars = [
        "SNAKE", "SNAKETWO"
    ]
    claw_scars = [
        "ONE", "TWO", "SNOUT", "TAILSCAR", "CHEEK",
        "SIDE", "THROAT", "TAILBASE", "BELLY", "FACE",
        "BRIDGE", "HINDLEG", "BACK", "SCRATCHSIDE"
    ]
    leg_scars = [
        "NOPAW", "TOETRAP", "MANLEG", "FOUR"
    ]
    tail_scars = [
        "TAILSCAR", "TAILBASE", "NOTAIL", "HALFTAIL", "MANTAIL"
    ]
    ear_scars = [
        "LEFTEAR", "RIGHTEAR", 'NOLEFTEAR', 'NORIGHTEAR'
    ]
    frostbite_scars = [
        "HALFTAIL", "NOTAIL", "NOPAW", 'NOLEFTEAR', 'NORIGHTEAR', 'NOEAR',
        "FROSTFACE", "FROSTTAIL", "FROSTMITT", "FROSTSOCK",
    ]
    eye_scars = [
        "THREE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND"
    ]
    burn_scars = [
        "BRIGHTHEART", "BURNPAWS", "BURNTAIL", "BURNBELLY", "BURNRUMP"
    ]
    quill_scars = [
        "QUILLCHUNK", "QUILLSCRATCH", "QUILLSIDE"
    ]
    head_scars = [
        "SNOUT", "CHEEK", "BRIDGE", "BEAKCHEEK"
    ]
    bone_scars = [
        "MANLEG", "TOETRAP", "FOUR"
    ]
    back_scars = [
        "TWO", "TAILBASE", "BACK"
    ]
    parasitic_scars = [
        "EXPOSEDRIBS", "EYESOCKET", "ARMBONE"
    ]
    void_scars = [
        "VOIDBACK", "VOIDEYE", "VOIDTAIL", "NOPAW"
    ]
    fungal_scars = [
        "SHELFMUSHROOMS", "EYEMOSS", "PAWMOSS"
    ]
    if game.settings["infection gore"]:
        infection_scars = parasitic_scars + ear_scars + ["NOTAIL", "NOPAW", "HALFTAIL"]
    else:
        infection_scars = ear_scars + frostbite_scars + ["NOTAIL", "NOPAW", "HALFTAIL"]


    scar_allowed = {
        "bite-wound": canid_scars,
        "cat-bite": bite_scars,
        "severe burn": burn_scars,
        "rat bite": rat_scars,
        "snake bite": snake_scars,
        "mangled tail": tail_scars,
        "mangled leg": leg_scars,
        "torn ear": ear_scars,
        "frostbite": frostbite_scars,
        "torn pelt": claw_scars + beak_scars,
        "damaged eyes": eye_scars,
        "quilled by porcupine": quill_scars,
        "claw-wound": claw_scars,
        "beak bite": beak_scars,
        "broken jaw": head_scars,
        "broken back": back_scars,
        "broken bone": bone_scars,
        "withering": infection_scars,
        "void sickness": void_scars,
        "rot": fungal_scars
    }

    @staticmethod
    def handle_scars(cat, injury_name):
        """ 
        This function handles the scars
        """

        # If the injury can't give a scar, move return None, None
        if injury_name not in Scar_Events.scar_allowed:
            return None, None

        moons_with = game.clan.age - cat.injuries[injury_name]["moon_start"]
        chance = max(5 - moons_with, 1)

        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medical_cats_condition_fulfilled(game.cat_class.all_cats.values(), amount_per_med):
            chance += 2

        if injury_name in ["rot", "withering", "void sickness"]:
            chance = 8
        
        if len(cat.pelt.scars) < 4 and not int(random.random() * chance):
            
            # move potential scar text into displayed scar text
            specialty = None  # Scar to be set

            scar_pool = [i for i in Scar_Events.scar_allowed[injury_name] if i not in cat.pelt.scars]
            if 'NOPAW' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ['TOETRAP', 'RATBITE', "FROSTSOCK", "ARMBONE"]]
            if 'NOTAIL' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["HALFTAIL", "TAILBASE", "TAILSCAR", "MANTAIL", "BURNTAIL", "FROSTTAIL", "VOIDTAIL"]]
            if 'HALFTAIL' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["TAILSCAR", "MANTAIL", "FROSTTAIL"]]
            if "BRIGHTHEART" in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["RIGHTBLIND", "BOTHBLIND", "EYESOCKET", "VOIDEYE"]]
            if 'BOTHBLIND' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["THREE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND", "BRIGHTHEART", "EYESOCKET", "VOIDEYE"]]
            if 'EYESOCKET' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["THREE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND", "BRIGHTHEART", "VOIDEYE"]]
            if 'VOIDEYE' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["THREE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND", "BRIGHTHEART", "EYESOCKET"]]
            if 'EYEMOSS' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["THREE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND", "BRIGHTHEART", "EYESOCKET", "VOIDEYE"]]
            if 'NOEAR' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if
                             i not in ["LEFTEAR", "RIGHTEAR", 'NOLEFTEAR', 'NORIGHTEAR', "FROSTFACE"]]
            if 'MANTAIL' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["BURNTAIL", 'FROSTTAIL']]
            if 'BURNTAIL' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["MANTAIL", 'FROSTTAIL']]
            if 'FROSTTAIL' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ["MANTAIL", 'BURNTAIL']]
            if 'NOLEFT' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ['LEFTEAR']]
            if 'NORIGHT' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ['RIGHTEAR']]
            if 'ARMBONE' in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ['NOPAW']]
                
            # Extra check for disabling scars.
            if int(random.random() * 3):
                condition_scars = {
                    "LEGBITE", "THREE", "NOPAW", "TOETRAP", "NOTAIL", "HALFTAIL", "LEFTEAR", "RIGHTEAR",
                    "MANLEG", "BRIGHTHEART", "NOLEFTEAR", "NORIGHTEAR", "NOEAR", "LEFTBLIND",
                    "RIGHTBLIND", "BOTHBLIND", "RATBITE", "EYESOCKET", "ARMBONE", "VOIDEYE"
                }
                scar_pool = list(set(scar_pool).difference(condition_scars))
                
            # If there are not new scars to give them, return None, None.
            if not scar_pool:
                return None, None
            
            # If we've reached this point, we can move foward with giving history.
            if injury_name in ["withering", "void sickness", "rot"]:
                History.add_scar(cat,
                                  "m_c was greatly scarred by the infection.",
                                  condition=injury_name)
            else:
                History.add_scar(cat,
                                  f"m_c was scarred from an injury ({injury_name}).",
                                  condition=injury_name)

            # If we've reached this point, we can move forward with giving history.
            History.add_scar(cat,
                             f"m_c was scarred from an injury ({injury_name}).",
                             condition=injury_name)

            specialty = random.choice(scar_pool)
            if specialty in ["NOTAIL", "HALFTAIL"]:
                if cat.pelt.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                    cat.pelt.accessory = None

            # combining left/right variations into the both version
            if "NOLEFTEAR" in cat.pelt.scars and specialty == 'NORIGHTEAR':
                cat.pelt.scars.remove("NOLEFTEAR")
                specialty = 'NOEAR'
            elif "NORIGHTEAR" in cat.pelt.scars and specialty == 'NOLEFTEAR':
                cat.pelt.scars.remove("NORIGHTEAR")
                specialty = 'NOEAR'

            if 'RIGHTBLIND' in cat.pelt.scars and specialty == 'LEFTBLIND':
                cat.pelt.scars.remove("LEFTBLIND")
                specialty = 'BOTHBLIND'
            elif 'LEFTBLIND' in cat.pelt.scars and specialty == 'RIGHTBLIND':
                cat.pelt.scars.remove("RIGHTBLIND")
                specialty = 'BOTHBLIND'

            cat.pelt.scars.append(specialty)

            if injury_name == "withering":
                scar_gain_strings = [
                    f"Part of {cat.name}'s body has withered away, leaving a nasty sight.",
                    f"The infection is eating away at {cat.name}'s body."
                ]
            elif injury_name == "void sickness":
                scar_gain_strings = [
                    f"{cat.name}'s sickness has consumed part of their body.",
                    f"The infection is eating away at {cat.name}'s body."
                ]
            elif injury_name == "rot":
                scar_gain_strings = [
                    f"{cat.name}'s body is being overtaken by the infection.",
                    f"{cat.name}'s body has become a host for infectious plant life."
                ]
            else:
                scar_gain_strings = [
                    f"{cat.name}'s {injury_name} has healed, but they'll always carry evidence of the incident on their pelt.",
                    f"{cat.name} healed from their {injury_name} but will forever be marked by a scar.",
                    f"{cat.name}'s {injury_name} has healed, but the injury left them scarred.",
                ]
            return random.choice(scar_gain_strings), specialty
        else:
            return None, None
