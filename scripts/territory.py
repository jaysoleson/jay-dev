import pygame
from scripts.game_structure import game
import random
from scripts.cat.enums import CatGroup
from scripts.clan_resources.point_of_interest import (
    get_poi_save_dict,
)
from scripts.config import get_config



class Territory():
    MAP_WIDTH = 11
    MAP_HEIGHT = 11

    def __init__(self):
        self.border_tiles = {}

    def generate_territories(self):
        """
        Generate the initial territory dict upon creating a Clan
        """

        # this will be the final dict
        territory_dict = {}
        
        # get border tiles
        border_tiles = []
        all_tiles = []
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                if (
                    x == 0 or
                    y == 0 or
                    x == 10 or
                    y == 10
                ):
                    border_tiles.append(f"{x}-{y}")
                all_tiles.append(f"{x}-{y}")


        all_clans = game.clan.all_other_clans + [game.clan]
        max_attempts = len(all_clans * get_config("bellsofwar.territory_size"))
        # this will only happen if someones fucking with the config
        if max_attempts <= 1:
            max_attempts = 1

        border_tiles_collected = self.distribute_tiles(
            item_list=all_clans,
            max_attempts=100 - len(all_clans * get_config("bellsofwar.territory_size")),
            starting_tiles=all_tiles if get_config("bellsofwar.random_territory_placement") else border_tiles
            )

        # Now POI tiles
        all_pois = get_poi_save_dict()
        poi_tiles = {}

        for terrain_poi in all_pois["terrain"]:
            if "twoleg" in terrain_poi:
                random_tile = random.choice(border_tiles)
            else:
                random_tile = str(random.randint(0,10)) + "-" + str(random.randint(0,10))
            poi_tiles.update({random_tile: terrain_poi})

        moonplace_tile = random.choice(["10-0", "0-0", "0-10", "10-10"])

        # save border tiles to the territory dict with owner and poi info
        for clan, tile_list in border_tiles_collected.items():
            clan_ID = clan.group_ID
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
        
        # now that the territory dict is full, we can do more distributions.

        # HERBS!
        # not all herbs get chosen, some might get chosen twice and have different patches!
        # hopefully the rng gods bless you with endless fields of catmint
        possible_herbs = list(game.clan.herb_supply.base_herb_list.keys())
        assembled_herb_list = []
        herb_num = random.randint(18,25)

        for i in range(herb_num):
            assembled_herb_list.append(random.choice(possible_herbs))

        # CGWAR TODO: different herb lifts for different biomes
        # big patches of oak leaves would make more sense in a forest than beach yk
        herb_tiles_collected = self.distribute_tiles(
            item_list=assembled_herb_list,
            max_attempts=5,
            starting_tiles=all_tiles
            )
        for herb, tile_list in herb_tiles_collected.items():
            for tile in tile_list:
                territory_dict[tile]["herb"] = herb

        return territory_dict
    
    def distribute_tiles(self, item_list=[], max_attempts=100, starting_tiles=[]):
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
        for i in range(MAX_ATTEMPTS):
            for item in item_list:
                if item not in last_indexes:
                    last_indexes[item] = 0
                # find a border tile to pick first
                if item not in tiles_collected:
                    starting_tile = random.choice(starting_tiles)
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
                    east_tile = f"{x+1}-{y}" if x < 10 else None
                    south_tile = f"{x}-{y+1}" if y < 10 else None
                    west_tile = f"{x-1}-{y}" if x > 0 else None

                    options = []
                    # set back to none if another clan has it already
                    if north_tile:
                        for key, tile_list in tiles_collected.items():
                            if north_tile in tile_list:
                                north_tile = None
                                break
                    if east_tile:
                        for key, tile_list in tiles_collected.items():
                            if east_tile in tile_list:
                                east_tile = None
                                break
                    if south_tile:
                        for key, tile_list in tiles_collected.items():
                            if south_tile in tile_list:
                                south_tile = None
                                break
                    if west_tile:
                        for key, tile_list in tiles_collected.items():
                            if west_tile in tile_list:
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
