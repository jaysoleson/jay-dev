import json
import copy


file_names = [
    "apprentice",
    "deputy",
    "elder",
    "exiled",
    "former Clancat",
    "general_no_kit",
    "general",
    "kitten",
    "kittypet",
    "leader",
    "loner",
    "mediator apprentice",
    "mediator",
    "medicine cat apprentice",
    "medicine cat",
    "queen",
    "queen's apprentice",
    "rogue",
    "warrior",
    "young elder"
]
# TODO: aauugh
file_path_convert = {
    "apprentice": {
        "file": "adolescent",
        "rank": ["apprentice"]
    },
    "deputy": {
        "file": "adult",
        "rank": ["deputy"]
    },
    "elder": {
        "file": "adult",
        "rank": ["elder"]
    },
    "exiled": {
        "file": "general",
        "standing": ["exiled"]
    },
    "former Clancat": {
        "file": "general",
        "standing": ["lost"]
    },
    "general_no_kit": {
        "file": "general_no_kit",
        "age": ["not_kitten"]
    },
    "general": {
        "file": "general"
    },
    "kitten": {
        "file": "kitten",
        "rank": ["kitten"]
    },
    "kittypet": {
        "file": "general",
        "rank": ["kittypet"]
    },
    "leader": {
        "file": "adult",
        "rank": ["leader"]
    },
    "loner": {
        "file": "general",
        "rank": ["loner"]
    },
    "mediator apprentice": {
        "file": "adolescent",
        "rank": ["mediator apprentice"]
    },
    "mediator": {
        "file": "adult",
        "rank": ["mediator"]
    },
    "medicine cat apprentice": {
        "file": "adolescent",
        "rank": ["medicine cat apprentice"]
    },
    "medicine cat": {
        "file": "adult",
        "rank": ["medicine cat"]
    },
    "queen": {
        "file": "adult",
        "rank": ["queen"]
    },
    "queen's apprentice": {
        "file": "adolescent",
        "rank": ["queen's apprentice"]
    },
    "rogue": {
        "file": "general",
        "rank": ["rogue"]
    },
    "warrior": {
        "file": "adult",
        "rank": ["warrior"]
    },
    "young elder": {
        "file": "general",
        "rank": ["elder"],
        "age": ["not_senior"]
    }
}


folder_names = [
    "events",
    "events_dead_df",
    "events_dead_sc",
    "events_dead_ur"
]

clusters = [
            "assertive",
            "stable",
            "unlawful",
            "cool",
            "brooding",
            "sweet",
            "introspective",
            "unabashed",
            "upstanding",
            "neurotic",
            "silly"
        ]
with open("scripts/events_module/dialogue/reformat_resources/abbrev_convert.json", 'r') as read_file:
    abbrev_convert = json.loads(read_file.read())

for folder in folder_names:
    for status in file_names:
        old_events = {}
        new_events = {}
        try:
            with open(f"resources/lang/en/events/lifegen_events/{folder}/{status}.json", 'r') as read_file:
                old_events = json.loads(read_file.read())
        except FileNotFoundError:
            continue

        event_count = 0
        done_events = []
        for key, event_list in old_events.items():
            for event_string in event_list:
                if event_string in done_events:
                    continue
                TYPES = []
                cluster_found = False
                cats_block = {}
                rel_block = []
                for cluster in clusters:
                    if cluster in key:
                        cluster_found = True
                        cats_block["y_c"] = {
                            "cluster": [cluster]
                        }
                if key == "df":
                    TYPES.append("df")
                elif "shunned" in key:
                    TYPES.append("shunned")
                elif "rare" in key:
                    TYPES.append("rare")
                elif key == "affair":
                    TYPES.append("affair")
                else:
                    TYPES.append("general")

                if not cluster_found:
                    cats_block["y_c"] = {}
                event_count += 1

                random_cat_count = 0
                check = copy.deepcopy(abbrev_convert)
                for abbrev, abbrev_info in check.items():
                    if abbrev in event_string:
                        # get new r_c abbrev
                        new_abbrev = f"r_c:{random_cat_count}"
                        random_cat_count += 1
                        event_string = event_string.replace(abbrev, new_abbrev)

                        if "relationship" in abbrev_info.copy():
                            for item in abbrev_info["relationship"].copy():
                                if abbrev in abbrev_info["relationship"]["cats_to"]:
                                    abbrev_info["relationship"]["cats_to"].remove(abbrev)
                                    abbrev_info["relationship"]["cats_to"].append(new_abbrev)
                                if abbrev in abbrev_info["relationship"]["cats_from"]:
                                    abbrev_info["relationship"]["cats_from"].remove(abbrev)
                                    abbrev_info["relationship"]["cats_from"].append(new_abbrev)

                            rel_block.append(abbrev_info["relationship"])
                            abbrev_info.pop("relationship")
                        cats_block[new_abbrev] = abbrev_info

                # get key and block for final writing
                new_event_key = key.split(" ")[0] + str(event_count)
                new_event_block = {
                    "cats": cats_block,
                    "relationships": rel_block,
                    "types": TYPES,
                    "event": event_string
                }
                new_events[new_event_key] = new_event_block
                done_events.append(event_string)

        
        with open(f"resources/lang/en/events/lifegen_events/NEW/{folder}/{status}.json", 'w') as json_file:
            json.dump(new_events, json_file, indent=4, separators=(',', ': '))

        
