import pygame
from scripts.game_structure import game
import random
from scripts.cat.enums import CatGroup
from scripts.clan_resources.point_of_interest import (
    get_poi_save_dict,
)
from scripts.config import get_config



class Territory():
    MAP_WIDTH = get_config("bellsofwar.territory_grid_size")
    MAP_HEIGHT = get_config("bellsofwar.territory_grid_size")

    high_value_herbs = {
        "catmint": 4,
        "honey": 4,
        "lungwort": 3,
        "poppy": 3,
        "cobwebs": 4,
        "moss": 3
    }
    def __init__(self):
        self.border_tiles = {}
        self.all_clans = []

    def generate_territories(self):
        """
        Generate the initial territory dict upon creating a Clan.
        """
        self.all_clans = game.clan.all_other_clans + [game.clan]

        # this will be the final dict
        territory_dict = {}
        
        # get border tiles
        border_tiles = []
        all_tiles = []
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                territory_dict[f"{x}-{y}"] = {"owner": None}
                if (
                    x == 0 or
                    y == 0 or
                    x == self.MAP_WIDTH - 1 or
                    y == self.MAP_HEIGHT - 1
                ):
                    border_tiles.append(f"{x}-{y}")
                all_tiles.append(f"{x}-{y}")


        max_attempts = len(self.all_clans * get_config("bellsofwar.territory_expansion_modifier"))
        # this will only happen if someones fucking with the config
        if max_attempts <= 1:
            max_attempts = 1

        border_tiles_collected = self.distribute_tiles(
            item_list=self.all_clans,
            max_attempts=(
                (self.MAP_WIDTH * 10) -
                len(self.all_clans * get_config("bellsofwar.territory_expansion_modifier"))
                ),
            starting_tiles=all_tiles if get_config("bellsofwar.random_territory_placement") else border_tiles,
            all_valid_tiles=all_tiles
            )

        # Now POI tiles
        all_pois = get_poi_save_dict()
        poi_tiles = {}

        for terrain_poi in all_pois["terrain"]:
            if "twoleg" in terrain_poi:
                random_tile = random.choice(border_tiles)
            else:
                random_tile = str(random.randint(0, self.MAP_WIDTH - 1)) + "-" + str(random.randint(0,self.MAP_HEIGHT - 1))
            poi_tiles.update({random_tile: terrain_poi})

        moonplace_tiles = [
                f"{self.MAP_WIDTH - 1}-0", "0-0", f"0-{self.MAP_HEIGHT - 1}", f"{self.MAP_WIDTH - 1}-{self.MAP_HEIGHT - 1}"
                ]
        for tile in poi_tiles:
            if tile in moonplace_tiles:
                moonplace_tiles.remove(tile)
        
        moonplace_tile = random.choice(moonplace_tiles)
        gathering_tile = f"{round((self.MAP_WIDTH - 1) / 2)}-{round((self.MAP_HEIGHT - 1) / 2)}"

        # save border tiles to the territory dict with owner and poi info
        for clan, tile_list in border_tiles_collected.items():
            new_tile_list = []
            for tile in tile_list:
                if tile not in territory_dict:
                    territory_dict[tile]["owner"] = None
                if tile == gathering_tile:
                    territory_dict[tile]["owner"] = None
                    territory_dict[tile]["poi"] = "gathering"
                elif tile == moonplace_tile:
                    territory_dict[tile]["owner"] = None
                    territory_dict[tile]["poi"] = "moonplace"
                elif tile in poi_tiles:
                    if "twoleg" in poi_tiles[tile]:
                        territory_dict[tile]["owner"] = None
                    else:
                        territory_dict[tile]["owner"] = clan.group_ID
                    territory_dict[tile]["poi"] = poi_tiles[tile]
                else:
                    territory_dict[tile]["owner"] = clan.group_ID
                    new_tile_list.append(tile)
        
            # find them a camp
            # first try to find a camp that is in the middle of the territory
            # not up against a border
            CAMP_ATTEMPT_LIMIT = 20
            chosen_camp_tile = None
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
                    territory_dict[test_tile].update({"camp":True})
                    chosen_camp_tile = test_tile
                    break

            if not chosen_camp_tile:
                print("No suitable location found. Randomly choosing.")
                test_tile = random.choice(new_tile_list)
                territory_dict[test_tile].update({"camp":True})
                chosen_camp_tile = test_tile

        territory_dict = self._distribute_herbs(territory_dict, all_tiles)
        territory_dict = self._set_unclaimed_territory(
            territory_dict,
            poi_tiles,
            gathering_tile,
            moonplace_tile
            )
        territory_dict = self.__set_strength(territory_dict)

        return territory_dict

    # ----------------------------------------------------------- #
    #                STRENGTH & DISTRIBUTIONS                     #
    # ----------------------------------------------------------- #

    def __set_strength(self, territory_dict, override=False):
        new_dict = self._set_herb_strength(territory_dict)
        new_dict = self._set_poi_strength(territory_dict)
        new_dict = self._set_general_strength(territory_dict, override=override)
        new_dict = self._set_border_strength(territory_dict)

        # 0 strength
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                if "strength" not in new_dict[f"{x}-{y}"]:
                    if new_dict[f"{x}-{y}"]["owner"]:
                        new_dict[f"{x}-{y}"].update({"strength": 1})
                    else:
                        new_dict[f"{x}-{y}"].update({"strength": 0})

        new_dict = self._fill_gaps(new_dict)

        return new_dict

    def _set_unclaimed_territory(self, territory_dict, poi_tiles, gathering_tile, moonplace_tile):
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                if f"{x}-{y}" not in territory_dict:
                    territory_dict[f"{x}-{y}"]["owner"] = None
                    if f"{x}-{y}" == gathering_tile:
                        territory_dict[f"{x}-{y}"]["poi"] = "gathering"
                    elif f"{x}-{y}" == moonplace_tile:
                        territory_dict[f"{x}-{y}"]["poi"] = "moonplace"
                    elif f"{x}-{y}" in poi_tiles:
                        territory_dict[f"{x}-{y}"]["poi"] = poi_tiles[f"{x}-{y}"]
        return territory_dict
    
    def _set_general_strength(self, territory_dict, override=False):
        if not self.all_clans:
            self.all_clans = game.clan.all_other_clans + [game.clan]
        for clan in self.all_clans:
            chosen_camp_tile = None
            for tile in territory_dict:
                if territory_dict[tile]["owner"] == clan.group_ID:
                    if "camp" in territory_dict[tile] and territory_dict[tile]["camp"]:
                        chosen_camp_tile = tile
                        break
            if not chosen_camp_tile:
                print("Can't find camp!")
                return
            strength_tiles_collected = self.__distribute_heatmap_tiles(
                layers=5,
                starting_tile=chosen_camp_tile,
                all_valid_tiles=self.get_all_territory_tiles(clan, territory_dict)
                )
            # print(clan.name, ":", strength_tiles_collected)
            territory_dict[chosen_camp_tile]["strength"] = 4

            territory_dict = self._set_tile_strengths(
                strength_tiles_collected,
                territory_dict,
                override=override
                )
        return territory_dict
    
    def _set_border_strength(self, territory_dict):
        for clan in self.all_clans:
            all_neighbours = self.get_neighbouring_clans(clan, territory_dict)
            for neighbour in all_neighbours:
                border_tiles = self.get_border_tiles_between_clans(clan, neighbour, territory_dict)[0]
                for tile in border_tiles:
                    border_strength_tiles_collected = self.__distribute_heatmap_tiles(
                        layers=3,
                        starting_tile=tile,
                        all_valid_tiles=self.get_all_territory_tiles(clan, territory_dict)
                        )
                    if "strength" in territory_dict[tile]:
                        if territory_dict[tile]["strength"] < 3:
                            territory_dict[tile]["strength"] = 3
                    else:
                        territory_dict[tile]["strength"] = 3
            
                    territory_dict = self._set_tile_strengths(
                        border_strength_tiles_collected,
                        territory_dict
                        )
        
        return territory_dict

    def _set_poi_strength(self, territory_dict):
        for clan in self.all_clans:
            for tile, info in territory_dict.items():
                if "poi" in info and info["owner"] == clan.group_ID:
                    poi_strength_tiles_collected = self.__distribute_heatmap_tiles(
                        layers=4,
                        starting_tile=tile,
                        all_valid_tiles=self.get_all_territory_tiles(clan, territory_dict)
                        )
                    if "strength" in territory_dict[tile]:
                        if territory_dict[tile]["strength"] < 3:
                            territory_dict[tile]["strength"] = 3
                        else:
                            territory_dict[tile]["strength"] = 3

                    territory_dict = self._set_tile_strengths(
                        poi_strength_tiles_collected,
                        territory_dict
                        )
        return territory_dict

    def _distribute_herbs(self, territory_dict, all_tiles):
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
            max_attempts=round(self.MAP_WIDTH / 2),
            starting_tiles=all_tiles,
            all_valid_tiles=all_tiles
            )
        for herb, tile_list in herb_tiles_collected.items():
            for tile in tile_list:
                territory_dict[tile]["herb"] = herb

        return territory_dict

    def _set_herb_strength(
            self,
            territory_dict
    ):
        # HERB VALUE
        for clan in self.all_clans:
            for tile, info in territory_dict.items():
                if (
                    "herb" in info and
                    info["herb"] in self.high_value_herbs and
                    info["owner"] == clan.group_ID
                    ):
                    layers = self.high_value_herbs[info["herb"]]

                    herb_strength_tiles_collected = self.__distribute_heatmap_tiles(
                        layers=layers,
                        starting_tile=tile,
                        all_valid_tiles=self.get_all_territory_tiles(clan, territory_dict)
                        )
                    if "strength" in territory_dict[tile]:
                        if territory_dict[tile]["strength"] < layers - 1:
                            territory_dict[tile]["strength"] = layers - 1
                        else:
                            territory_dict[tile]["strength"] = layers - 1
            
                    territory_dict = self._set_tile_strengths(
                        herb_strength_tiles_collected,
                        territory_dict
                        )
        return territory_dict

    def _set_tile_strengths(
            self,
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
            self,
            layers=4,
            starting_tile=None,
            all_valid_tiles=[]
            ):
        # TODO CGWAR: docs

        tiles_collected = {}
        if self.MAP_WIDTH <= 11:
            info = "bellsofwar.heatmap_mod.small_map"
        elif self.MAP_WIDTH <= 17:
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

        # print(tiles_collected)
        return tiles_collected
    
    def _fill_gaps(self, territory_dict):
        """
        A bit hacky that I need to have this, but oh well.
        Fills in gaps left by territory expansion according to its neighbours.
        """
        for tile, info in territory_dict.items():
            if info["strength"] in (3, 4):
                continue
            if not info["owner"]:
                continue
            direct_neighbours = self.get_immediate_neighbours(tile)
            neighbour_strengths = []
            skip_tile = False
            for neighbour in direct_neighbours:
                if neighbour not in territory_dict:
                    # if its in the negatives bc the source is a border
                    continue
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
            self,
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
                    east_tile = f"{x+1}-{y}" if x < self.MAP_WIDTH - 1 else None
                    south_tile = f"{x}-{y+1}" if y < self.MAP_HEIGHT - 1 else None
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
    
    def get_all_territory_tiles(self, clan, territory_dict={}):
        """
        Gets all territory tiles for a specified Clan.
        Returns a list of tiles as strings.
        """
        all_tiles = []
        if not territory_dict:
            territory_dict = game.clan.territory_tile_info
        
        for tile, info in territory_dict.items():
            if info["owner"] == clan.group_ID:
                all_tiles.append(tile)
        return all_tiles
    
    def get_border_tiles_between_clans(self, clan1=None, clan2=None, territory_dict={}):
        """
        Returns two lists, each containing tiles along their border with the other Clan.
        List 1 is clan1's tiles, list 2 is clan2's tiles.
        """
        if not territory_dict:
            territory_dict = game.clan.territory_tile_info

        clan1_border_tiles = []
        clan2_border_tiles = []

        clan1_all_tiles = self.get_all_territory_tiles(clan1, territory_dict=territory_dict)

        # first assemble a list of ALL of clan1's tiles.
        # check each of their neighbours. if they're neighbours with a clan2 tile,
        # add both to their lists
        for tile in clan1_all_tiles:
            neighbours = self.get_immediate_neighbours(tile)
            for n in neighbours:
                if n not in territory_dict:
                    continue
                if territory_dict[n]["owner"] == clan2.group_ID:
                    if tile not in clan1_border_tiles:
                        clan1_border_tiles.append(tile)
                    if n not in clan2_border_tiles:
                        clan2_border_tiles.append(n)
        
        return clan1_border_tiles, clan2_border_tiles
    
    def get_neighbouring_clans(self, clan, territory_dict={}):
        """
        Returns a list of Clan/OtherClan objects that border the specified Clan
        """
        if not territory_dict:
            territory_dict = game.clan.territory_tile_info

        oc_dict = {}
        for other_clan in game.clan.all_other_clans:
            oc_dict[other_clan.group_ID] = other_clan

        neighbouring_clans = []
        clan_tiles = self.get_all_territory_tiles(clan, territory_dict=territory_dict)
        for tile in clan_tiles:
            neighbours = self.get_immediate_neighbours(tile)
            for n in neighbours:
                if n in territory_dict:
                    if territory_dict[n]["owner"]:
                        owner_ID = territory_dict[n]["owner"]
                        if owner_ID == clan.group_ID:
                            continue
                        if owner_ID in oc_dict:
                            if oc_dict[owner_ID] not in neighbouring_clans:
                                neighbouring_clans.append(oc_dict[owner_ID])
                        if owner_ID == game.clan.group_ID:
                            if game.clan not in neighbouring_clans:
                                neighbouring_clans.append(game.clan)
        return neighbouring_clans
    
    def get_immediate_neighbours(self, tile_string, layer=1):
        x = int(tile_string.split("-")[0])
        y = int(tile_string.split("-")[1])
        return [
                f"{x-layer}-{y}",
                f"{x+layer}-{y}",
                f"{x}-{y-layer}",
                f"{x}-{y+layer}",
            ]
    
    def update_tile_info(self, tile, key, value):
        if key == "owner":
            print(tile, "OLD:", game.clan.territory_tile_info[tile])
            game.clan.territory_tile_info[tile][key] = value
            self.remap_strength()
            print(tile, "NEW:", game.clan.territory_tile_info[tile])

    def remap_strength(self):
        game.clan.territory_tile_info = self.__set_strength(
            game.clan.territory_tile_info.copy(),
            override=True
            )

territory_class = Territory()
