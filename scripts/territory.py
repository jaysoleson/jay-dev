import pygame
from scripts.game_structure import game
import random
from scripts.cat.enums import CatRank, CatGroup, CatSocial
from scripts.clan_resources.point_of_interest import (
    load_pois,
    get_poi_save_dict,
    generate_and_add_new_poi,
    PoiType,
    get_poi_names_set,
    clear_pois,
)


class Territory():
    MAP_WIDTH = 11
    MAP_HEIGHT = 11

    def __init__(self):
        self.border_tiles = {}

    def generate_territories(self):
        """
        Generate the initial territory dict upon creating a Clan
        """
        all_clans = game.clan.all_other_clans + [game.clan]
        border_tiles = []
        territory_dict = {}
        # get border tiles
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                if (
                    x == 0 or
                    y == 0 or
                    x == 10 or
                    y == 10
                ):
                    border_tiles.append(f"{x}-{y}")
        
        # now assign territory
        tiles_collected = {}
        last_indexes = {}
        # the index of the tile we're looking for neighbours for. 0 when still
        # branching off from the home point. when the home point is surrounded, we move on
        MAX_ATTEMPTS = 100 - len(all_clans * 10)
        for i in range(MAX_ATTEMPTS):
            for clan in all_clans:
                if clan.group_ID not in last_indexes:
                    last_indexes[clan.group_ID] = 0
                # find a border tile to pick first
                if clan.group_ID not in tiles_collected:
                    starting_tile = random.choice(border_tiles)
                    border_tiles.remove(starting_tile)
                    tiles_collected[clan.group_ID] = [starting_tile]
                else:
                    # branch out!
                    # this sucks
                    try:
                        source_tile = tiles_collected[clan.group_ID][last_indexes[clan.group_ID]]
                    except Exception as e:
                        # print("Map Generation Error:", e)
                        source_tile = tiles_collected[clan.group_ID][0]
                    x = int(source_tile.split("-")[0])
                    y = int(source_tile.split("-")[1])

                    north_tile = f"{x}-{y-1}" if y > 0 else None
                    east_tile = f"{x+1}-{y}" if x < 10 else None
                    south_tile = f"{x}-{y+1}" if y < 10 else None
                    west_tile = f"{x-1}-{y}" if x > 0 else None

                    options = []
                    # set back to none if another clan has it already
                    if north_tile:
                        for clan_ID, tile_list in tiles_collected.items():
                            if north_tile in tile_list:
                                north_tile = None
                                break
                    if east_tile:
                        for clan_ID, tile_list in tiles_collected.items():
                            if east_tile in tile_list:
                                east_tile = None
                                break
                    if south_tile:
                        for clan_ID, tile_list in tiles_collected.items():
                            if south_tile in tile_list:
                                south_tile = None
                                break
                    if west_tile:
                        for clan_ID, tile_list in tiles_collected.items():
                            if west_tile in tile_list:
                                west_tile = None
                                break
                    if (
                        not north_tile and
                        not east_tile and
                        not south_tile and
                        not west_tile
                    ):
                        last_indexes[clan.group_ID] += 1
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
                        last_indexes[clan.group_ID] += 1
                        continue

                    move = random.choice(options)
                    if move == "north":
                        tiles_collected[clan.group_ID].append(north_tile)
                    if move == "east":
                        tiles_collected[clan.group_ID].append(east_tile)
                    if move == "south":
                        tiles_collected[clan.group_ID].append(south_tile)
                    if move == "west":
                        tiles_collected[clan.group_ID].append(west_tile)

        all_pois = get_poi_save_dict()
        poi_tiles = {}

        for terrain_poi in all_pois["terrain"]:
            if "twoleg" in terrain_poi:
                random_tile = random.choice(border_tiles)
            else:
                random_tile = str(random.randint(0,10)) + "-" + str(random.randint(0,10))
            poi_tiles.update({random_tile: terrain_poi})

        moonplace_tile = random.choice(["10-0", "0-0", "0-10", "10-10"])

        for clan_ID, tile_list in tiles_collected.items():
            new_tile_list = []
            for tile in tile_list:
                if tile == "5-5":
                    territory_dict[tile] = {"owner": None, "poi": "gathering"}
                elif tile == moonplace_tile:
                    territory_dict[tile] = {"owner": None, "poi": "moonplace"}
                elif tile in poi_tiles:
                    if "twoleg" in poi_tiles[tile]:
                        territory_dict[tile] = {"owner": None, "poi": poi_tiles[tile]}
                    else:
                        territory_dict[tile] = {"owner": clan_ID, "poi": poi_tiles[tile]}
                else:
                    territory_dict[tile] = {"owner": clan_ID}
                    new_tile_list.append(tile)
        
            # find them a camp
            # first try to find a camp that is in the middle of the territory
            # not up against a border
            CAMP_ATTEMPT_LIMIT = 20
            camp_found = False
            for i in range(CAMP_ATTEMPT_LIMIT):
                test_tile = random.choice(new_tile_list)
                if test_tile in [moonplace_tile, poi_tiles, "5-5"]:
                    continue
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
                    if i in new_tile_list:
                        count += 1
                if count >= 4:
                    camp_found = True
                    territory_dict[test_tile].update({"camp":True})
                    break

            if not camp_found:
                print("No suitable location found. Randomly choosing.")
                test_tile = random.choice(new_tile_list)
                territory_dict[test_tile].update({"camp":True})
        
        # now unclaimed territory
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                if f"{x}-{y}" not in territory_dict:
                    if f"{x}-{y}" == "5-5":
                        territory_dict[f"{x}-{y}"] = {"owner": None, "poi": "gathering"}
                    elif f"{x}-{y}" == moonplace_tile:
                        territory_dict[f"{x}-{y}"] = {"owner": None, "poi": "moonplace"}
                    elif f"{x}-{y}" in poi_tiles:
                        territory_dict[f"{x}-{y}"] = {"owner": None, "poi": poi_tiles[f"{x}-{y}"]}
                    else:
                        territory_dict[f"{x}-{y}"] = {"owner": None}

        return territory_dict

    def get_tile_owner(self, tile_string):

        owner_ID = game.clan.territory_tile_info[tile_string]["owner"]
        if not owner_ID:
            return None
        tile_owner_group = game.used_group_IDs[game.clan.territory_tile_info[tile_string]["owner"]]
        tile_owner = None

        if tile_owner_group == CatGroup.OTHER_CLAN:
            for clan in game.clan.all_other_clans:
                if clan.group_ID == game.clan.territory_tile_info[tile_string]["owner"]:
                    tile_owner = clan
        elif tile_owner_group == CatGroup.PLAYER_CLAN:
            tile_owner = game.clan

        return tile_owner

territory_class = Territory()
