"""

TODO: Docs


"""

from scripts.game_structure import game
import random
from scripts.clan_resources.point_of_interest import (
get_poi_save_dict,
get_all_pois_by_tag
)
from scripts.config import get_config

# this script is only used for CREATING territories.
# actually storing and updating territories is done in territory.py
# no method from this script should ever be used anywhere else

MAP_SIZE = get_config("bellsofwar.territory_grid_size")

high_value_herbs = {
    "catmint": 4,
    "honey": 4,
    "lungwort": 3,
    "poppy": 3,
    "cobwebs": 4,
    "moss": 3
}

river_pois = [
    "terrain_waterfall",
    "terrain_fordriver",
    "terrain_sunningrocks",
]
lake_pois = [
    "gather_island",
]
ocean_pois = [
    "terrain_carrionbeach",
    "terrain_gullcliffs"
]
all_clans = []

def generate_territories():
    """
    Generate the initial territory dict upon creating a Clan.
    """
    all_clans = game.clan.all_other_clans + [game.clan]

    # this will be the final dict
    territory_dict = {}

    # get border tiles
    border_tiles = []
    all_tiles = []
    for x in range(MAP_SIZE):
        for y in range(MAP_SIZE):
            territory_dict[f"{x}-{y}"] = {
                "owner": None,
                "terrain": "land",
                "events": [],
                "history": []
                }
            if (
                x == 0 or
                y == 0 or
                x == MAP_SIZE - 1 or
                y == MAP_SIZE - 1
            ):
                border_tiles.append(f"{x}-{y}")
            all_tiles.append(f"{x}-{y}")

    all_clans = game.clan.all_other_clans + [game.clan]
    max_attempts = len(all_clans * get_config("bellsofwar.territory_expansion_modifier"))
    # this will only happen if someones fucking with the config
    if max_attempts <= 1:
        max_attempts = 1

    border_tiles_collected = distribute_tiles(
        item_list=all_clans,
        max_attempts=(
            (MAP_SIZE * 10) -
            len(all_clans * get_config("bellsofwar.territory_expansion_modifier"))
            ),
        starting_tiles=all_tiles if get_config("bellsofwar.random_territory_placement") else border_tiles,
        all_valid_tiles=all_tiles
        )

    # save border tiles to the territory dict with owner and poi info
    for clan, tile_list in border_tiles_collected.items():
        camp_option_tile_list = []
        for tile in tile_list:
            # nothing important can go on the top corner
            # as its blocked by the compass on the map screen lol
            top_corner = f"{MAP_SIZE-1}-0"
            if tile not in territory_dict:
                territory_dict[tile]["owner"] = None
            else:
                if tile == f"{round(MAP_SIZE/2)}-{round(MAP_SIZE/2)}":
                    territory_dict[tile]["poi"] = "gathering"
                else:
                    territory_dict[tile]["owner"] = clan.group_ID
                    if tile != top_corner:
                        camp_option_tile_list.append(tile)

        # find them a camp
        # first try to find a camp that is in the middle of the territory
        # not up against a border
        CAMP_ATTEMPT_LIMIT = 20
        chosen_camp_tile = None
        for i in range(CAMP_ATTEMPT_LIMIT):
            test_tile = random.choice(camp_option_tile_list)
            x = int(test_tile.split("-")[0])
            y = int(test_tile.split("-")[1])

            neighbours = [
                f"{x-1}-{y}",
                f"{x+1}-{y}",
                f"{x}-{y-1}",
                f"{x}-{y+1}"
            ]
            count = 0
            for i in neighbours:
                if i in camp_option_tile_list:
                    count += 1
            if count >= 4:
                territory_dict[test_tile].update({"camp":True})
                chosen_camp_tile = test_tile
                break

        if not chosen_camp_tile:
            print("No suitable location found for camp. Randomly choosing.")
            test_tile = random.choice(camp_option_tile_list)
            territory_dict[test_tile].update({"camp":True})
            chosen_camp_tile = test_tile

    territory_dict = _set_unclaimed_territory(
        territory_dict
        )

    for tile in territory_dict:
        if tile == f"{round(MAP_SIZE/2)}-{round(MAP_SIZE/2)}":
            territory_dict[tile]["poi"] = "gathering"

    territory_dict = _generate_terrain_info(territory_dict, border_tiles, all_tiles)
    territory_dict = _distribute_herbs(territory_dict, all_tiles)
    territory_dict = __place_pois(territory_dict)
    
    territory_dict = set_strength(territory_dict)

    return territory_dict

# ----------------------------------------------------------- #
#                STRENGTH & DISTRIBUTIONS                     #
# ----------------------------------------------------------- #

def set_strength(territory_dict, override=False):
    territory_dict = _set_herb_strength(territory_dict)
    territory_dict = _set_poi_strength(territory_dict)
    territory_dict = _set_border_strength(territory_dict)
    territory_dict = _set_general_strength(territory_dict, override=override)

    # 0 strength
    for x in range(MAP_SIZE):
        for y in range(MAP_SIZE):
            if "strength" not in territory_dict[f"{x}-{y}"]:
                if territory_dict[f"{x}-{y}"]["owner"]:
                    territory_dict[f"{x}-{y}"].update({"strength": 1})
                else:
                    territory_dict[f"{x}-{y}"].update({"strength": 0})

    territory_dict = _fill_gaps(territory_dict)

    return territory_dict

def _set_unclaimed_territory(territory_dict):
    for x in range(MAP_SIZE):
        for y in range(MAP_SIZE):
            if f"{x}-{y}" not in territory_dict:
                territory_dict[f"{x}-{y}"]["owner"] = None

    return territory_dict

def _set_general_strength(territory_dict, override=False):
    for clan in game.clan.all_other_clans + [game.clan]:
        camp_tile = get_camp_tile(clan, territory_dict)
        strength_tiles_collected = __distribute_heatmap_tiles(
            layers=5,
            starting_tile=camp_tile,
            all_valid_tiles=_get_all_territory_tiles(clan, territory_dict, exclude_water=True)
            )
        territory_dict[camp_tile]["strength"] = 4

        territory_dict = _set_tile_strengths(
            strength_tiles_collected,
            territory_dict,
            override=override
            )
    return territory_dict

def _set_border_strength(territory_dict):
    for clan in game.clan.all_other_clans + [game.clan]:
        border_tiles = _get_all_border_tiles(clan, territory_dict=territory_dict, exclude_water=True)
        for tile in border_tiles:
            if "terrain" in territory_dict[tile] and territory_dict[tile]["terrain"] in ("lake", "ocean"):
                continue
            border_strength_tiles_collected = __distribute_heatmap_tiles(
                layers=3,
                starting_tile=tile,
                all_valid_tiles=_get_all_territory_tiles(clan, territory_dict)
                )
            if "strength" in territory_dict[tile]:
                if territory_dict[tile]["strength"] < 3:
                    territory_dict[tile]["strength"] = 3
            else:
                territory_dict[tile]["strength"] = 3
    
            territory_dict = _set_tile_strengths(
                border_strength_tiles_collected,
                territory_dict
                )
    
    return territory_dict

def _set_poi_strength(territory_dict):
    for clan in game.clan.all_other_clans + [game.clan]:
        for tile, info in territory_dict.items():
            if "poi" in info and info["owner"] == clan.group_ID:
                if "terrain" in info and info["terrain"] in ("lake", "ocean"):
                    continue
                poi_strength_tiles_collected = __distribute_heatmap_tiles(
                    layers=4,
                    starting_tile=tile,
                    all_valid_tiles=_get_all_territory_tiles(clan, territory_dict)
                    )
                if "strength" in territory_dict[tile]:
                    if territory_dict[tile]["strength"] < 3:
                        territory_dict[tile]["strength"] = 3
                    else:
                        territory_dict[tile]["strength"] = 3

                territory_dict = _set_tile_strengths(
                    poi_strength_tiles_collected,
                    territory_dict
                    )
    return territory_dict

def _distribute_herbs(territory_dict, all_tiles):
    # HERBS!
    # not all herbs get chosen, some might get chosen twice and have different patches!
    # hopefully the rng gods bless you with endless fields of catmint
    valid_tiles = []
    for tile in all_tiles:
        if "terrain" in territory_dict[tile]:
            if territory_dict[tile]["terrain"] != "land":
                continue
        valid_tiles.append(tile)

    possible_herbs = list(game.clan.herb_supply.base_herb_list.keys())
    assembled_herb_list = []
    herb_num = random.randint(22,26)

    for i in range(herb_num):
        assembled_herb_list.append(random.choice(possible_herbs))

    # CGWAR TODO: different herb lifts for different biomes
    # big patches of oak leaves would make more sense in a forest than beach yk
    herb_tiles_collected = distribute_tiles(
        item_list=assembled_herb_list,
        max_attempts=round(MAP_SIZE / 2),
        starting_tiles=valid_tiles,
        all_valid_tiles=valid_tiles
        )
    for herb, tile_list in herb_tiles_collected.items():
        for tile in tile_list:
            territory_dict[tile]["herb"] = herb

    return territory_dict

def _generate_terrain_info(territory_dict, border_tiles=[], all_tiles=[]):

    create_river = False
    create_lake = False
    create_ocean = False

    # road
    create_thunderpath = False

    # train track
    create_silverpath = False
    if game.clan.biome == "Plains" and game.clan.camp_bg == "camp4":
        # train camp!
        create_silverpath = True
    else:
        biome_thunderpath_chances = {
            "Plains": 2,
            "Forest": 2,
            "Mountainous": 3,
            "Beach": 10,
            "Wetlands": 20,
            "Desert": 4
        }
        if not int(random.random() * biome_thunderpath_chances[game.clan.biome]):
            create_thunderpath = True

    # river, lake, ocean
    biome_water_features = {
        "Plains": (2, 1, 0),
        "Forest": (1, 1, 0),
        "Mountainous": (1, 2, 1),
        "Beach": (1, 1, 3),
        "Wetlands": (3, 2, 0), 
        "Desert": (0, 0, 0)
    }

    river_number = biome_water_features[game.clan.biome][0]
    lake_number = biome_water_features[game.clan.biome][1]
    ocean_number = biome_water_features[game.clan.biome][2]

    lake_starting_tiles = []
    all_pois = get_poi_save_dict()
    for feature in all_pois["terrain"]:
        if feature in river_pois:
            create_river = True
        elif feature in lake_pois:
            create_lake = True
        elif feature in ocean_pois:
            create_ocean = True
    # force a lake at the center for the gathering island
    if "gather_island" in all_pois["gathering"]:
        create_lake = True
        lake_starting_tiles.append(_get_gathering_tile(territory_dict))

    if game.clan.biome == "Forest" and game.clan.camp_bg == "camp4":
        # Lakeside
        create_lake = True
        lake_starting_tiles.append(get_camp_tile(game.clan, territory_dict))

    if not create_river:
        if river_number:
            # create a river sometimes even if you dont need one!
            if not int(random.random() * 3):
                create_river = True
    if not create_lake:
        if lake_number:
            if not int(random.random() * 5):
                create_lake = True

    # beach always gets a river and an ocean!
    if game.clan.biome == "Beach":
        create_river = True
        create_ocean = True

    if not create_lake and not create_ocean and not create_river:
        # give a river if theres nothing else.. because no water features is boring
        create_river = True

    # now create them!
    if create_river:
        for i in range(river_number):
            territory_dict = __create_river(territory_dict, border_tiles, all_tiles)
    if create_ocean:
        # all mini oceans will generate on the same coast
        for i in range(ocean_number - 1):
            coast = random.choice(["north", "east", "south", "west"])
            coast_dict = {
                "north": [
                    i for i in border_tiles if int(i.split("-")[1]) == 0
                ],
                "east": [
                    i for i in border_tiles if int(i.split("-")[0]) == 0
                ],
                "south": [
                    i for i in border_tiles if int(i.split("-")[1]) == MAP_SIZE - 1
                ],
                "west": [
                    i for i in border_tiles if int(i.split("-")[0]) == MAP_SIZE - 1
                ]
            }
            for i in range(ocean_number):
                territory_dict = __create_ocean(
                    starting_tiles=coast_dict[coast],
                    all_tiles=all_tiles,
                    territory_dict=territory_dict
                )
    
    non_water_tiles = get_terrain_tiles_from_list(all_tiles, territory_dict, "land")
    if _get_gathering_tile(territory_dict) in non_water_tiles:
        non_water_tiles.remove(_get_gathering_tile(territory_dict))

    if lake_starting_tiles:
        lake_number = len(lake_starting_tiles)

    if create_lake:
        lake_tile_index = 0
        for i in range(lake_number):
            lake_source = lake_starting_tiles[lake_tile_index] if lake_tile_index < len(lake_starting_tiles) else random.choice(non_water_tiles)

            if lake_source == get_camp_tile(game.clan, territory_dict):
                # change valid tiles so its lakeSIDE, not in the middle.

                camp_x = int(lake_source.split("-")[0])
                camp_y = int(lake_source.split("-")[1])
    
                valid_directions = ["west", "east", "north", "south"]
                if camp_x == 0:
                    valid_directions.remove("west")
                if camp_x == MAP_SIZE:
                    valid_directions.remove("east")
                if camp_y == 0:
                    valid_directions.remove("north")
                if camp_y == MAP_SIZE:
                    valid_directions.remove("south")

                direction = random.choice(valid_directions)

                for nwtile in non_water_tiles.copy():
                    nw_x = int(nwtile.split("-")[0])
                    nw_y = int(nwtile.split("-")[1])

                    if direction == "north":
                        if nw_y > camp_y - 1:
                            non_water_tiles.remove(nwtile)
                            continue
                    elif direction == "east":
                        if nw_x < camp_x + 1:
                            non_water_tiles.remove(nwtile)
                            continue
                    elif direction == "south":
                        if nw_y < camp_x + 1:
                            non_water_tiles.remove(nwtile)
                            continue
                    elif direction == "west":
                        if nw_x > camp_x - 1:
                            non_water_tiles.remove(nwtile)
                            continue

            territory_dict = __create_lake(
                lake_tile=lake_source,
                all_tiles=non_water_tiles,
                territory_dict=territory_dict
            )
            lake_tile_index += 1

    if create_silverpath:
        territory_dict = __create_thunderpath(territory_dict=territory_dict, terrain_type="silverpath")
    elif create_thunderpath:
        territory_dict = __create_thunderpath(territory_dict=territory_dict)

    territory_dict = _correct_terrain(territory_dict=territory_dict)

    return territory_dict

def __create_thunderpath(territory_dict, terrain_type="thunderpath"):

    if random.randint(1,2) == 1:
        direction = "x"
    else:
        direction = "y"
    camp_tile = get_camp_tile(clan=game.clan, territory_dict=territory_dict)
    if terrain_type == "silverpath":
        # ONLY the train camp
        starting_tile = camp_tile
    else:
        invalid_x_levels = []
        invalid_y_levels = []

        unclaimed = _get_all_unclaimed_tiles(territory_dict=territory_dict)
        for tile in unclaimed.copy():
            for clan in game.clan.all_other_clans + [game.clan]:
                clan_camp = get_camp_tile(clan=clan, territory_dict=territory_dict)
                # remove tiles that could cause a thunderpath to run through camp
                if direction == "x" and clan_camp.split("-")[1] == tile.split("-")[1]:
                    invalid_x_levels.append(tile.split("-")[0])
                    invalid_y_levels.append(tile.split("-")[1])
                if direction == "y" and clan_camp.split("-")[0] == tile.split("-")[0]:
                    invalid_x_levels.append(tile.split("-")[0])
                    invalid_y_levels.append(tile.split("-")[1])
            if tile == _get_moonplace_tile(territory_dict=territory_dict):
                invalid_x_levels.append(tile.split("-")[0])
                invalid_y_levels.append(tile.split("-")[1])
            if tile == _get_gathering_tile(territory_dict=territory_dict):
                invalid_x_levels.append(tile.split("-")[0])
                invalid_y_levels.append(tile.split("-")[1])
            if "terrain" in territory_dict[tile] and territory_dict[tile]["terrain"] == "ocean":
                invalid_x_levels.append(tile.split("-")[0])
                invalid_y_levels.append(tile.split("-")[1])

            if tile.split("-")[0] in invalid_x_levels and tile in unclaimed:
                unclaimed.remove(tile)
            if tile.split("-")[1] in invalid_y_levels and tile in unclaimed:
                unclaimed.remove(tile)

        if not unclaimed:
            print("Can't make thunderpath.")
            return territory_dict
        starting_tile = random.choice(unclaimed)

    silverpath_tiles = []
    land_tiles = []

    if direction == "x":
        # y stays the same
        y_level = starting_tile.split("-")[1]
        for tile in territory_dict:
            if tile.split("-")[1] == y_level:
                silverpath_tiles.append(tile)
                land_tiles.append(f"{tile.split('-')[0]}-{int(y_level) + 1}")
                land_tiles.append(f"{tile.split('-')[0]}-{int(y_level) - 1}")
    else:
        # x stays the same
        x_level = starting_tile.split("-")[0]
        for tile in territory_dict:
            if tile.split("-")[0] == x_level:
                silverpath_tiles.append(tile)
                land_tiles.append(f"{int(x_level) + 1}-{tile.split('-')[1]}")
                land_tiles.append(f"{int(x_level) - 1}-{tile.split('-')[1]}")

    for tile in silverpath_tiles:
        territory_dict[tile]["terrain"] = terrain_type
    # for tile in land_tiles:
    #     if tile in territory_dict:
    #         # land tiles could end up being our of bounds
    #         # if the thunderpath is on a world border
    #         territory_dict[tile]["terrain"] = "land"

    return territory_dict

def get_terrain_tiles_from_list(tile_list, territory_dict={}, terrain_type="water"):
    terrain_tiles = []
    for tile in tile_list:
        if tile not in territory_dict:
            continue
        if "terrain" not in territory_dict[tile]:
            continue
        if terrain_type == "water":
            if territory_dict[tile]["terrain"] not in (
                "river", "lake", "ocean"
            ):
                continue
        elif "coast" in terrain_type:
            water = terrain_type.split(":")[1]
            if territory_dict[tile]["terrain"] != water:
                continue
            if tile not in _get_coast_tiles(water, territory_dict):
                continue
        else:
            if territory_dict[tile]["terrain"] != terrain_type:
                continue
        terrain_tiles.append(tile)
    return terrain_tiles

def _get_coast_tiles(water_type, territory_dict):
    coast_tiles = []
    for tile, info in territory_dict:
        coast_tile = False
        if info["terrain"] != water_type:
            continue
        for n in _get_immediate_neighbours(tile, territory_dict):
            if territory_dict[n]["terrain"] == "land":
                coast_tile = True
                break
        if coast_tile:
            coast_tiles.append(tile)
    return coast_tiles


def get_land_tiles_from_list(tile_list, territory_dict={}):
    land_tiles = []
    for tile in tile_list:
        if tile not in territory_dict:
            continue
        if "terrain" in territory_dict[tile]:
            if territory_dict[tile]["terrain"] in (
                "river", "lake", "ocean"
            ):
                continue
        land_tiles.append(tile)
    return land_tiles

def _correct_terrain(territory_dict):
    gather_tile = _get_gathering_tile(territory_dict)
    territory_dict[gather_tile]["terrain"] = "land"
    
    for tile in territory_dict:
        if "camp" in territory_dict[tile] and territory_dict[tile]["camp"]:
            territory_dict[tile]["terrain"] = "land"
        if "terrain" not in territory_dict[tile]:
            territory_dict[tile]["terrain"] = "land"

    return territory_dict

# ----------------------------------------------------------------------#
#                          TERRAIN FEATURES                             #
# ----------------------------------------------------------------------#

def __create_river(territory_dict={}, border_tiles=[], all_tiles=[]):
    possible_tiles = [i for i in border_tiles if "-0" in i or "0-" in i]
    starting_tile = random.choice(possible_tiles)
    river_tiles = [starting_tile]
    if "0-" in starting_tile:
        endpoint = int(river_tiles[-1].split("-")[0])
    else:
        endpoint = int(river_tiles[-1].split("-")[-1])

    valid_tiles = all_tiles.copy()
    for tile in valid_tiles.copy():
        if "camp" in territory_dict[tile] and territory_dict[tile]["camp"]:
            if tile in valid_tiles:
                valid_tiles.remove(tile)

    last_direction = ""
    direction_dict = {
        0: "west",
        1: "east",
        2: "north",
        3: "south"
    }
    RIVER_ATTEMPTS = get_config("bellsofwar.territory_grid_size") * 4
    for i in range(RIVER_ATTEMPTS):
        if endpoint >= MAP_SIZE - 1:
            break
        all_neighbours = _get_immediate_neighbours(river_tiles[-1], territory_dict=territory_dict)
        possible_choices = []
        river_neighbours = 0
        for neighbour in all_neighbours:
            if (
                "terrain" in territory_dict[neighbour] and
                territory_dict[neighbour]["terrain"] == "river" and
                neighbour != river_tiles[-1]
                ):
                # find neighbouring tiles that are already rivers
                # (excluding the tile it came from).
                # hopefully this can prevent it curling up on itself
                river_neighbours += 1
            if river_neighbours >= 1:
                continue
            if neighbour not in valid_tiles:
                continue
            if last_direction:
                if not int(random.random() * round(get_config("bellsofwar.territory_grid_size") / 5)):
                    # pass on last direction
                    if neighbour in river_tiles:
                        continue
                else:
                    if direction_dict[all_neighbours.index(neighbour)] != last_direction:
                        continue
            else:
                if neighbour in river_tiles:
                    continue
            possible_choices.append(neighbour)
        if not possible_choices:
            continue
        next_tile = random.choice(possible_choices)

        last_direction = direction_dict[all_neighbours.index(next_tile)]

        river_tiles.append(next_tile)

    for tile in river_tiles:
        territory_dict[tile]["terrain"] = "river"

    return territory_dict

def __create_lake(lake_tile, all_tiles, territory_dict={}):
    valid_tiles = all_tiles.copy()
    for tile in valid_tiles.copy():
        neighbours = _get_all_neighbours(tile, territory_dict=territory_dict)
        for n in neighbours + [tile]:
            if "camp" in territory_dict[n] and territory_dict[n]["camp"]:
                if tile in valid_tiles:
                    valid_tiles.remove(tile)
            if "terrain" in territory_dict[n] and territory_dict[n]["terrain"] in (
                "lake", "ocean"
            ):
                if tile in valid_tiles:
                    valid_tiles.remove(tile)
    if not valid_tiles:
        print("Can't create a lake with no valid tiles!")
        return territory_dict

    lake_tiles = distribute_tiles(
        item_list=[1],
        max_attempts=18,
        starting_tiles=[lake_tile],
        all_valid_tiles=all_tiles
        )
    for string, tile_list in lake_tiles.items():
        for tile in tile_list:
            if tile in territory_dict:
                territory_dict[tile]["terrain"] = "lake"
    return territory_dict

def __create_ocean(starting_tiles, all_tiles, territory_dict={}):
    valid_tiles = all_tiles.copy()
    for tile in valid_tiles:
        if "terrain" in territory_dict[tile] and territory_dict[tile]["terrain"] in (
            "ocean"
        ):
            if tile in valid_tiles:
                valid_tiles.remove(tile)
                continue
        neighbours = _get_immediate_neighbours(tile, territory_dict=territory_dict)
        for n in neighbours + [tile]:
            if "camp" in territory_dict[n] and territory_dict[n]["camp"]:
                if n in valid_tiles:
                    valid_tiles.remove(tile)

    ocean_tiles = distribute_tiles(
        item_list=[1],
        max_attempts=round(get_config("bellsofwar.territory_grid_size") * 2.5),
        starting_tiles=starting_tiles,
        all_valid_tiles=valid_tiles
        )
    for string, tile_list in ocean_tiles.items():
        for tile in tile_list:
            if tile in territory_dict:
                territory_dict[tile]["terrain"] = "ocean"
    return territory_dict

def __place_pois(territory_dict):
    # first, assemble a list of tiles and exclude camps.
    free_tiles = [
        tile for tile in list(territory_dict.keys()) if
        "camp" not in territory_dict[tile]
    ]
    # nothing important can go on the top corner
    # as its blocked by the compass on the map screen lol
    top_corner = f"{MAP_SIZE-1}-0"
    if top_corner in free_tiles:
        free_tiles.remove(top_corner)

    clan_poi_dict = get_poi_save_dict()
    for category in clan_poi_dict:
        if category == "gathering":
            # done earlier!
            continue
        elif category == "moonplace":
            moonplace_tiles = []
            for tile in free_tiles:
                # try to find a spot in unclaimed territory first
                neighbours = _get_immediate_neighbours(tile, territory_dict=territory_dict)
                for n in neighbours:
                    if not territory_dict[n]["owner"]:
                        moonplace_tiles.append(tile)
            # second attempt. if no unclaimed land spots are found,
            # just go along the edges
            if not moonplace_tiles:
                for tile in free_tiles:
                    if tile.split("-")[0] in (0, MAP_SIZE - 1):
                        moonplace_tiles.append(tile)
            for tile in moonplace_tiles.copy():
                if clan_poi_dict[category][0] != "moon_pool":
                    if "terrain" in territory_dict[tile] and territory_dict[tile]["terrain"] in (
                        "river", "lake", "ocean", "thunderpath", "silverpath"
                    ):
                        moonplace_tiles.remove(tile)
                else:
                    if "terrain" in territory_dict[tile] and territory_dict[tile]["terrain"] in (
                        "thunderpath", "silverpath"
                    ):
                        moonplace_tiles.remove(tile)
            if not moonplace_tiles:
                moonplace_tiles = free_tiles.copy()
            chosen_tile = random.choice(moonplace_tiles)
            territory_dict[chosen_tile]["poi"] = category
            territory_dict[chosen_tile]["owner"] = None
            free_tiles.remove(chosen_tile)
        else:
            # terrain features
            for feature in clan_poi_dict[category]:
                feature_tiles = []
                if feature in get_all_pois_by_tag("Twolegs:present"):
                    for tile in free_tiles:
                        if tile in territory_dict:
                            if "terrain" in territory_dict[tile]:
                                if territory_dict[tile]["terrain"] in (
                                    "river", "lake", "ocean", "silverpath", "thunderpath"
                                ):
                                    continue
                        # try to find a spot in unclaimed territory first
                        neighbours = _get_immediate_neighbours(tile, territory_dict=territory_dict)
                        for n in neighbours:
                            if (
                                not territory_dict[n]["owner"] and
                                n != f"{round(MAP_SIZE/2)}-{round(MAP_SIZE/2)}" and
                                "poi" not in territory_dict[n]
                                ):
                                feature_tiles.append(tile)
                    # same code as moonplace
                    if not feature_tiles:
                        for tile in free_tiles:
                            if tile.split("-")[0] in (0, MAP_SIZE - 1):
                                feature_tiles.append(tile)
                elif feature in (
                    "terrain_fordriver", "terrain_waterfall", "terrain_sunningrocks"
                    ):
                    for tile in free_tiles:
                        if "terrain" not in territory_dict[tile]:
                            continue
                        if territory_dict[tile]["terrain"] == "river":
                            feature_tiles.append(tile)
                elif feature in (
                    "terrain_carrionbeach", "terrain_gullcliffs"
                    ):
                    for tile in free_tiles:
                        if "terrain" not in territory_dict[tile]:
                            continue
                        if territory_dict[tile]["terrain"] in ("ocean", "lake"):
                            feature_tiles.append(tile)
                else:
                    # any other POIs are ones that should be on land
                    for tile in free_tiles:
                        if tile in get_land_tiles_from_list(free_tiles, territory_dict):
                            feature_tiles.append(tile)

                if not feature_tiles:
                    print("Didn't find tiles for", feature)
                    feature_tiles = get_land_tiles_from_list(free_tiles, territory_dict)
                chosen_tile = random.choice(feature_tiles)
                territory_dict[chosen_tile]["poi"] = feature
                if feature in get_all_pois_by_tag("Twolegs:present"):
                    territory_dict[chosen_tile]["owner"] = None

                free_tiles.remove(chosen_tile)
    return territory_dict

def _set_herb_strength(
        territory_dict
):
    # HERB VALUE
    for clan in game.clan.all_other_clans + [game.clan]:
        for tile, info in territory_dict.items():
            if (
                "herb" in info and
                info["herb"] in high_value_herbs and
                info["owner"] == clan.group_ID
                ):
                layers = high_value_herbs[info["herb"]]

                herb_strength_tiles_collected = __distribute_heatmap_tiles(
                    layers=layers,
                    starting_tile=tile,
                    all_valid_tiles=_get_all_territory_tiles(clan, territory_dict)
                    )
                if "strength" in territory_dict[tile]:
                    if territory_dict[tile]["strength"] < layers - 1:
                        territory_dict[tile]["strength"] = layers - 1
                    else:
                        territory_dict[tile]["strength"] = layers - 1
        
                territory_dict = _set_tile_strengths(
                    herb_strength_tiles_collected,
                    territory_dict
                    )
    return territory_dict

def _set_tile_strengths(
        
        tiles_collected,
        territory_dict,
        override=False
        ):
    """
    Updates the territory_dict with tile strength.
    If the tile already has a strength, it keeps the larger number.
    """
    for num, tile_list in tiles_collected.items():
        for tile in tile_list:
            if override:
                territory_dict[tile]["strength"] = num
            else:
                if "strength" in territory_dict[tile]:
                    if territory_dict[tile]["strength"] < num:
                        territory_dict[tile].update({"strength": num})
                else:
                    territory_dict[tile]["strength"] = num
    return territory_dict

def __distribute_heatmap_tiles(
        layers=4,
        starting_tile="",
        all_valid_tiles=[]
        ):
    # TODO CGWAR: docs

    tiles_collected = {}
    if MAP_SIZE <= 11:
        info = "bellsofwar.heatmap_mod.small_map"
    elif MAP_SIZE <= 17:
        info = "bellsofwar.heatmap_mod.medium_map"
    else:
        info = "bellsofwar.heatmap_mod.large_map"
    
    ring_expansion = {
        0: get_config(info + ".0"),
        1: get_config(info + ".1"),
        2: get_config(info + ".2"),
        3: get_config(info + ".3"),
        4: get_config(info + ".4")
    }

    for i in reversed(range(1, layers)):
        layer = i
        key = layers - layer
        tiles_collected[key] = []
        x = int(starting_tile.split("-")[0])
        y = int(starting_tile.split("-")[1])
        expand = ring_expansion[key]
        all_neighbours = [
            f"{x-layer}-{y}",
            f"{x+layer}-{y}",
            f"{x}-{y-layer}",
            f"{x}-{y+layer}",
        ]
        # corners
        if expand > 0:
            all_neighbours.extend(
                [
                    f"{x-layer}-{y-layer}",
                    f"{x-layer}-{y+layer}",
                    f"{x+layer}-{y+layer}",
                    f"{x+layer}-{y-layer}"
                ]
            )
        else:
            all_neighbours.extend(
                [
                    f"{x-layer+1}-{y-layer+1}",
                    f"{x-layer+1}-{y+layer-1}",
                    f"{x+layer-1}-{y+layer-1}",
                    f"{x+layer-1}-{y-layer+1}"
                ]
            )
        for num in range(layer):
            all_neighbours.append(f"{x-layer}-{y-num}")
            all_neighbours.append(f"{x-layer}-{y+num}")
            all_neighbours.append(f"{x+layer}-{y-num}")
            all_neighbours.append(f"{x+layer}-{y+num}")

            all_neighbours.append(f"{x-num}-{y-layer}")
            all_neighbours.append(f"{x-num}-{y+layer}")
            all_neighbours.append(f"{x+num}-{y-layer}")
            all_neighbours.append(f"{x+num}-{y+layer}")

            if expand > 0:
                expanded_tiles = []
                expanded_tiles.append(f"{x-(layer+expand)}-{y-num}")
                expanded_tiles.append(f"{x+(layer+expand)}-{y-num}")
                expanded_tiles.append(f"{x-(layer+expand)}-{y+num}")
                expanded_tiles.append(f"{x+(layer+expand)}-{y+num}")

                expanded_tiles.append(f"{x-num}-{y-(layer+expand)}")
                expanded_tiles.append(f"{x-num}-{y+(layer+expand)}")
                expanded_tiles.append(f"{x+num}-{y-(layer+expand)}")
                expanded_tiles.append(f"{x+num}-{y+(layer+expand)}")

                for t in expanded_tiles:
                    if t not in all_neighbours:
                        all_neighbours.append(t)

        expandable_tiles = []
        for tile in all_neighbours:
            if tile in all_valid_tiles:
                expandable_tiles.append(tile)

        for tile in expandable_tiles:
            if tile not in tiles_collected[key]:
                tiles_collected[key].append(tile)

    return tiles_collected

def _fill_gaps(territory_dict):
    """
    A bit hacky that I need to have this, but oh well.
    Fills in gaps left by territory expansion according to its neighbours.
    """
    for tile, info in territory_dict.items():
        if info["strength"] in (3, 4):
            continue
        if not info["owner"]:
            continue
        direct_neighbours = _get_immediate_neighbours(tile, territory_dict=territory_dict)
        neighbour_strengths = []
        skip_tile = False
        for neighbour in direct_neighbours:
            if territory_dict[neighbour]["strength"] == info["strength"]:
                # its neighbours with a low strength so it can stay
                skip_tile = True
            if territory_dict[neighbour]["strength"] > 0:
                neighbour_strengths.append(territory_dict[neighbour]["strength"])
            if not neighbour_strengths:
                # this SHOULDNT actually happen
                skip_tile = True
        if skip_tile:
            continue
        info["strength"] = random.choice(neighbour_strengths)
    return territory_dict


def distribute_tiles(
        
        item_list=[],
        max_attempts=100,
        starting_tiles=[],
        all_valid_tiles=[]
        ):
    """
    Creates a distribution of tiles for borders, terrain, prey, etc.
    Returns a dict with each list item as a key. Value is its list of tiles as strings.
    :param item_list: List of items to iterate through. all_clans, herb types, etc.
    :param max_attempts: Maximum attempts for branching out. Lower numbers will lead to more unclaimed land.
    :param starting_tiles: A list of the tiles that the distribution can start from.
    """
    tiles_collected = {}
    last_indexes = {}
    # the index of the tile we're looking for neighbours for. 0 when still
    # branching off from the home point. when the home point is surrounded, we move on
    MAX_ATTEMPTS = max_attempts
    heatmap_layer = 1
    for i in range(MAX_ATTEMPTS):
        for item in item_list:
            if item not in last_indexes:
                last_indexes[item] = 0
            # find a starting tile to pick first
            if item not in tiles_collected:
                starting_tile = random.choice(starting_tiles)
                if len(starting_tiles) > 1:
                    starting_tiles.remove(starting_tile)
                tiles_collected[item] = [starting_tile]
            else:
                # branch out!
                # this sucks
                try:
                    source_tile = tiles_collected[item][last_indexes[item]]
                except Exception as e:
                    # print("Map Generation Error:", e)
                    source_tile = tiles_collected[item][0]
                x = int(source_tile.split("-")[0])
                y = int(source_tile.split("-")[1])

                north_tile = f"{x}-{y-1}" if y > 0 else None
                east_tile = f"{x+1}-{y}" if x < MAP_SIZE - 1 else None
                south_tile = f"{x}-{y+1}" if y < MAP_SIZE - 1 else None
                west_tile = f"{x-1}-{y}" if x > 0 else None

                options = []
                # set back to none if another clan has it already
                # OR if its not in possible tiles
                if north_tile:
                    for key, tile_list in tiles_collected.items():
                        if (
                            north_tile in tile_list or
                            north_tile not in all_valid_tiles
                            ):
                            north_tile = None
                            break
                if east_tile:
                    for key, tile_list in tiles_collected.items():
                        if (
                            east_tile in tile_list or
                            east_tile not in all_valid_tiles
                            ):
                            east_tile = None
                            break
                if south_tile:
                    for key, tile_list in tiles_collected.items():
                        if (
                            south_tile in tile_list or
                            south_tile not in all_valid_tiles
                            ):
                            south_tile = None
                            break
                if west_tile:
                    for key, tile_list in tiles_collected.items():
                        if (
                            west_tile in tile_list or
                            west_tile not in all_valid_tiles
                            ):
                            west_tile = None
                            break
                if (
                    not north_tile and
                    not east_tile and
                    not south_tile and
                    not west_tile
                ):
                    last_indexes[item] += 1
                    continue

                options = ["north", "east", "south", "west"]
                if not north_tile:
                    options.remove("north")
                if not east_tile:
                    options.remove("east")
                if not south_tile:
                    options.remove("south")
                if not west_tile:
                    options.remove("west")
                if not options:
                    last_indexes[item] += 1
                    continue

                move = random.choice(options)
                if move == "north":
                    tiles_collected[item].append(north_tile)
                if move == "east":
                    tiles_collected[item].append(east_tile)
                if move == "south":
                    tiles_collected[item].append(south_tile)
                if move == "west":
                    tiles_collected[item].append(west_tile)
    return tiles_collected

#-------------------------------------------------------------------#
#                           GET TILES                               #
#-------------------------------------------------------------------#

def _get_all_territory_tiles(clan, territory_dict, exclude_water=False):
    """
    Gets all territory tiles for a specified Clan.
    Returns a list of tiles as strings.
    """
    all_tiles = []
    
    for tile, info in territory_dict.items():
        if info["owner"] == clan.group_ID:
            if exclude_water:
                if "terrain" in info:
                    if info["terrain"] in ("lake", "river", "ocean"):
                        continue
            all_tiles.append(tile)
    return all_tiles

def _get_border_tiles_between_clans(clan1=None, clan2=None, territory_dict={}, exclude_water=False):
    """
    Returns two lists, each containing tiles along their border with the other Clan.
    List 1 is clan1's tiles, list 2 is clan2's tiles.
    clan2 can be set to None to get outside borders.
    """

    clan1_border_tiles = []
    clan2_border_tiles = []

    clan1_all_tiles = _get_all_territory_tiles(
        clan1,
        territory_dict=territory_dict,
        exclude_water=exclude_water
        )

    # first assemble a list of ALL of clan1's tiles.
    # check each of their neighbours. if they're neighbours with a clan2 tile,
    # add both to their lists
    if clan2:
        owner_ID = clan2.group_ID
    else:
        owner_ID = None
    for tile in clan1_all_tiles:
        neighbours = _get_immediate_neighbours(tile, territory_dict=territory_dict, exclude_water=exclude_water)
        for n in neighbours:
            if n not in territory_dict:
                if not clan2:
                    if tile not in clan1_border_tiles:
                        if tile in territory_dict and "poi" in territory_dict[tile]:
                            continue
                        clan1_border_tiles.append(tile)
                continue
            if territory_dict[n]["owner"] == owner_ID:
                if tile not in clan1_border_tiles:
                    clan1_border_tiles.append(tile)
                if n not in clan2_border_tiles:
                    clan2_border_tiles.append(n)

    return clan1_border_tiles, clan2_border_tiles

def get_camp_tile(clan, territory_dict):
    """ Returns the tile string for the specified Clan's camp."""

    camp = None
    for tile in territory_dict:
        if territory_dict[tile]["owner"] == clan.group_ID:
            if "camp" in territory_dict[tile] and territory_dict[tile]["camp"]:
                camp = tile
                break
    if not camp:
        print("Couldn't find camp for", clan.name, "?")
        camp = "0-0"
    return camp

def _get_all_border_tiles(clan, territory_dict, exclude_water=False):
    """ 
    Returns a list of ALL border tiles for the specified Clan.
    Includes Clan borders and outside borders.
    """

    all_border_tiles = _get_outside_borders(
        clan,
        territory_dict=territory_dict,
        exclude_water=exclude_water
        )
    for other_clan in game.clan.all_other_clans + [game.clan]:
        if other_clan == clan:
            continue
        border_tiles = _get_border_tiles_between_clans(
            clan,
            other_clan,
            territory_dict=territory_dict,
            exclude_water=exclude_water
            )[0]
        for tile in border_tiles:
            if tile not in all_border_tiles:
                all_border_tiles.append(tile)

    return all_border_tiles

def _get_outside_borders(clan, territory_dict={}, exclude_water=False):
    """ Returns a list of tile strings that border Unclaimed land or the edge of the map."""
    border_tiles = _get_border_tiles_between_clans(
        clan1=clan,
        clan2=None,
        territory_dict=territory_dict,
        exclude_water=exclude_water
        )
    return border_tiles[0]

def _get_all_unclaimed_tiles(territory_dict, exclude_water=False):
    unclaimed_tiles = []
    for tile in territory_dict:
        if not territory_dict[tile]["owner"]:
            if "poi" in territory_dict[tile]:
                continue
            if exclude_water:
                if territory_dict[tile]["terrain"] in (
                    "lake", "ocean"
                ):
                    continue
            unclaimed_tiles.append(tile)
    return unclaimed_tiles

##################################################################

def _get_immediate_neighbours(
        
        tile_string,
        layer=1,
        territory_dict={},
        exclude_water=False,
        only_water=False
        ):
    """
    Gets the neighbours of a specified tile. Returns a list of strings.
    :param tile_string: The string representing the specified tile. E.G. "0-0"
    :param layer: An integer representing the layer of neighbour. Default to 1.
    :param territory_dict: The current territory dict. If nothing is passed, it will disregard and include neighbouring tiles that are invalid. E.G. "-1--1"
    :param exclude_water: Set to true to exclude water tiles from the neighbour list.
    :param only_water: Set to true to exclude land tiles from the neighbour list.
    """
    x = int(tile_string.split("-")[0])
    y = int(tile_string.split("-")[1])

    neighbour_list = [
            f"{x-layer}-{y}",
            f"{x+layer}-{y}",
            f"{x}-{y-layer}",
            f"{x}-{y+layer}",
        ]
    valid_neighbour_list = []
    for n in neighbour_list:
        if territory_dict:
            if n not in territory_dict:
                continue
        if exclude_water:
            if territory_dict and n in territory_dict:
                if "terrain" in territory_dict[n]:
                    if territory_dict[n]["terrain"] in ("river", "lake", "ocean"):
                        continue

        if only_water:
            if territory_dict and n in territory_dict:
                if "terrain" in territory_dict[n]:
                    if territory_dict[n]["terrain"] not in ("river", "lake", "ocean"):
                        continue
                else:
                    continue
        valid_neighbour_list.append(n)

    return valid_neighbour_list

def _get_all_neighbours(
        tile_string,
        layer=1,
        territory_dict={},
        exclude_water=False,
        only_water=False
    ):

    immediate_neighbours = _get_immediate_neighbours(
        tile_string,
        layer,
        territory_dict,
        exclude_water,
        only_water
        )

    x = int(tile_string.split("-")[0])
    y = int(tile_string.split("-")[1])
    corners = [
        f"{x-1}-{y-1}",
        f"{x+1}-{y-1}",
        f"{x-1}-{y+1}",
        f"{x+1}-{y+1}"
    ]
    for n in corners:
        if territory_dict:
            if n not in territory_dict:
                continue
        if exclude_water:
            if territory_dict and n in territory_dict:
                if "terrain" in territory_dict[n]:
                    if territory_dict[n]["terrain"] in ("river", "lake", "ocean"):
                        continue

        if only_water:
            if territory_dict and n in territory_dict:
                if "terrain" in territory_dict[n]:
                    if territory_dict[n]["terrain"] not in ("river", "lake", "ocean"):
                        continue
                else:
                    continue
        immediate_neighbours.append(n)
    return immediate_neighbours

def _get_gathering_tile(territory_dict):
    for tile in territory_dict:
        if "poi" not in territory_dict[tile]:
            continue
        if territory_dict[tile]["poi"] == "gathering":
            return tile
    return None

def _get_moonplace_tile(territory_dict):
    for tile in territory_dict:
        if "poi" not in territory_dict[tile]:
            continue
        if territory_dict[tile]["poi"] == "moonplace":
            return tile
    return None
