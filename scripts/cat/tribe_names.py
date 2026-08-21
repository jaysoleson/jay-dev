"""
Welcome to the Tribe Name Generation script by johann!

!! YOU WILL NEED TO RUN FROM SOURCE FOR THIS TO WORK !!

This script can generate a random Tribe name from the provided JSON.
Feel free to integrate this script into your mod/game to generate Tribe names for your Cats,
or just run it on its own to come up with some character names!

This is a Python script that was written outside of a Clangen branch,
so no Cat or Clan objects are present.
Any filtering or other logic you'd like to apply that uses those object types
will need to be written yourself into the `valid_for_filters()` function.
You can do it!

RECOMMENDED STEPS TO INTEGRATE INTO YOUR GAME:
- Add this script to your scripts folder.
- Add the provided JSON to resources/lang/en
- Import the `generate_tribe_name()` function into scripts where it's necessary.
    This can vary based on how you want to implement the new names.
    Will all cats get Tribe names, just Clan cats, just random outsiders?
- Call the function to assign a full tribe name to a cat's prefix.
    cat.name.prefix = generate_tribe_name(cat)
    cat.name.suffix = ""
"""
# pylint:disable=line-too-long
# pylint:disable=consider-using-dict-items
import random
import re
from itertools import product
import ujson
from scripts.game_structure import game

# CONSTS ------------------------>
JSON_FILE_PATH = "resources/lang/en/tribe_names.json"
# ------------------------------->

# Load Name Data ---------------->
NAME_DATA = {}
with open(
    JSON_FILE_PATH,
    "r",
    encoding="utf-8",
) as read_file:
    NAME_DATA = ujson.loads(read_file.read())

NAMES = NAME_DATA["names"]

REPLACEMENT_DICT = {
    "SMALL_BIRD": NAME_DATA["small_birds"],
    "LARGE_BIRD": NAME_DATA["large_birds"],
    "ANY_BIRD": NAME_DATA["small_birds"] + NAME_DATA["large_birds"],
    "RODENT": NAME_DATA["rodents"],
    "LARGE_ANIMAL": NAME_DATA["large_animals"],
    "TERRAIN_FEATURE": NAME_DATA["terrain_features"],
    "RUSHING_WATER": NAME_DATA["rushing_water"],
    "STILL_WATER": NAME_DATA["still_water"]
}
# ------------------------------->

# HELPERS ----------------------->
def get_name_option_list(string):
    """
    Breaks up strings with option inserts (e.g. Cry of {Bird,Dog,River})
    and returns all options (e.g. [Cry of Bird, Cry of Dog, Cry of River]).
    """
    groups = re.findall(r'\{([^{}]*)\}', string)
    options = [group.split(',') for group in groups]

    for combination in product(*options):
        result = string
        for replacement in combination:
            result = re.sub(r'\{[^{}]*\}', replacement, result, count=1)
        yield result

def get_options_for_pref(prefix, cat=None):
    """
    Returns all name options that follow the specified prefix.
    Does not split up prefixes with multiple options for weighting purposes.
    """
    # get filters
    biome = game.clan.biome
    return_names = []
    pref_list = []
    if "," in prefix:
        pref_list = prefix.split(",")
    if prefix in REPLACEMENT_DICT:
        pref_list = REPLACEMENT_DICT[prefix]
    if not pref_list:
        pref_list = [prefix]
    for p in pref_list:
        if "filters" in NAMES[prefix]:
            if not valid_for_filters(
                NAMES[prefix]["filters"],
                cat=cat,
                biome=biome
                ):
                continue
        for m in NAMES[prefix]["names"]:
            for e in NAMES[prefix]["names"][m]:
                for x in get_name_option_list(e):
                    key_in_repl = False
                    for r_key in REPLACEMENT_DICT:
                        if r_key in x:
                            key_in_repl = True
                            for item in REPLACEMENT_DICT[r_key]:
                                return_names.append(p + " " + m + " " + x.replace(r_key, item))
                    if not key_in_repl:
                        return_names.append(p + " " + m + " " + x)
    return return_names
# ------------------------------->

# FILTERING --------------------->
def valid_for_filters(
        filter_list,
        cat=None,
        biome="Forest"
        ) -> bool:
    """
    Filters names by given parameters
    Such as biome, season, anything else you'd like to add!

    As this script was written outside of a Clangen mod, this Cat logic
    doesn't actually do anything.
    Try seeing if it works for your mod and expand on it if you please!
    You'll just need to pass a Cat object into this function (the Cat that you're generating a name for).
    """
    for filter_type, filter_info in filter_list.items():
        if (
            filter_type == "biome" and
            biome not in filter_info
            ):
            return False
        if filter_type == "cat" and cat:
            # Add your logic for filtering based on Cat Pelt, Personality, or anything else!
            pass
    return True
# ------------------------------->

def populate_name_dict(cat=None):
    """
    Creates a dictionary where key = prefix and value = all name options.
    """
    all_p = []
    all_w = []
    all_names_prefix_dict = {}
    for pref in NAMES:
        all_names_prefix_dict[pref] = get_options_for_pref(pref, cat=cat)

    all_p = list(all_names_prefix_dict.keys())
    for n in all_p:
        # Get Weights
        # Prefixes are already weighted by the amount of options they have,
        # But they can be further affected by specifying frequency in the JSON.
        if "frequency" in NAMES[n]:
            weight = len(all_names_prefix_dict[n]) * NAMES[n]["frequency"]
        else:
            weight = len(all_names_prefix_dict[n])
        all_w.append(weight)

    return all_p, all_w, all_names_prefix_dict

    # name options are weighted by prefix key
    # the keys arent split up before doing this
    # SO. LARGE_BIRD isnt three times as likely to be chosen as "Frog"
    # just because theres so many large birds.
    # without this weighting, everyone has a damn bird name
# ------------------------------->

# ACTUAL NAME GENERATION -------->
def generate_tribe_name(
    cat=None
):
    """
    Generates a Tribe name and returns it!
    This is the only function that needs to be called to create a Tribe name.
    """

    # Now Get Name Information
    ALL_PREFIXES, ALL_WEIGHTS, all_names_prefix_dict = populate_name_dict(cat)

    # Randomly choose prefix + following information.
    chosen_prefix = random.choices(ALL_PREFIXES, weights=ALL_WEIGHTS, k=1)[0]
    full_name = random.choice(all_names_prefix_dict[chosen_prefix])

    # Replace any presets from the replacement dict
    # (LARGE_BIRD, RODENT, TERRAIN_FEATURE, etc.)
    # with a random option under that category.
    for key, name_list in REPLACEMENT_DICT.items():
        if key in full_name:
            full_name = full_name.replace(key, random.choice(name_list))

    # print("Generating Tribe Name...")
    # print(f"The Clan has encountered {full_name}.")
    # print()

    return full_name

