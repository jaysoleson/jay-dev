"""

TODO: Docs


"""
from scripts.game_structure import game
from scripts.config import get_config
from scripts.clan_resources.point_of_interest import (
get_poi_categories_set,
get_poi_names_set
)

class Territory():
    """
    Class containing territory information!
    Does not store or create tiles.
    """
    MAP_SIZE = get_config("bellsofwar.territory_grid_size")

    def __init__(self):
        self.all_clans = []

        self.terrain_types = [
            "land", "river", "lake", "ocean",
            "thunderpath", "silverpath"
        ]
        self.water_types = [
            "river", "lake", "ocean"
        ]

    def get_owned_tiles(self, clan):
        """
        Returns all tiles owned by the specified Clan.
        """
        owned_tiles = []
        for tile in game.clan.territory_tiles:
            if tile.owner == clan:
                owned_tiles.append(tile)
        return owned_tiles

    def get_clan_territory_dict(self):
        """
        Returns a dict where key = Clan and value = list[TerritoryTile]
        """
        return_dict = {}
        for clan in self.all_clans:
            return_dict[clan] = []

        for tile in game.clan.territory_tiles:
            if tile.owner:
                return_dict[tile.owner].append(tile)
        return return_dict

    def get_neighbouring_clans(self, clan):
        """
        Returns a list of Clan/OtherClan objects that border the specified Clan
        """
        clans = []
        for other_clan in game.clan.all_other_clans + [game.clan]:
            if other_clan == clan:
                continue
            for tile in self.get_tiles(["any"], clan=other_clan):
                if tile.is_bordering(clan):
                    clans.append(other_clan)
                    break
        return clans

    def get_tile_from_string(self, string):
        """
        Takes a tile string and returns the TerritoryTile it belongs to.
        """
        for tile in game.clan.territory_tiles:
            if tile.tile_string == string:
                return tile
        return None

    def get_tiles(
            self,
            tile_types,
            clan=None,
            other_clan=None
            ):
        """
        Takes a list of tile_types and returns a list of tiles
        that adhere to all of those parameters.
        """
        all_tiles = game.clan.territory_tiles
        if not isinstance(tile_types, list):
            print("Tile types is not a list!", tile_types)
            tile_types = [tile_types]

        for tile_type in tile_types:
            if tile_type == "other_clan_border":
                all_tiles = [
                    t for t in all_tiles.copy()
                    if t.owner == clan and
                    t.is_bordering(other_clan)
                ]
            elif tile_type == "other_clan_inner_border":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == other_clan and
                    t.is_bordering(clan)
                ]
            elif tile_type == "unclaimed_border":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == clan and
                    t.is_bordering(None) and
                    t.poi not in ("gathering", "moonplace")
                ]
            elif tile_type == "unclaimed":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner is None and
                    t.poi not in ("gathering", "moonplace")
                ]
            elif "coast" in tile_type:
                water = tile_type.split(":")[1]
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == clan and
                    t.terrain == "land" and
                    t.is_bordering(water)
                ]
            elif tile_type in self.terrain_types:
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == clan and
                    t.terrain == tile_type
                ]
            elif tile_type == "water":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.terrain in self.water_types
                ]
            elif tile_type == "herb":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.herb
                ]
            elif tile_type == "camp":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == clan and
                    t.camp is True
                ]
            elif tile_type == "other_clan_camp":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == other_clan and
                    t.camp is True
                ]
            elif tile_type == "outside_camp":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == clan and
                    not t.camp and
                    t.terrain == "land"
                ]
            elif tile_type == "territory":
                border_tiles = self._get_all_border_tiles(clan)
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == clan and
                    t.terrain == "land" and
                    t not in border_tiles
                ]
            elif tile_type == "border":
                border_tiles = self._get_all_border_tiles(clan)
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == clan and
                    t in border_tiles
                ]
            elif tile_type == "outside":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner != clan
                ]
            elif tile_type == "not_other_clan_territory":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    (t.owner == clan or
                    t.owner is None)
                ]
            elif tile_type == "any":
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.owner == clan
                ]
            elif tile_type in list(game.clan.herb_supply.base_herb_list.keys()):
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.herb == tile_type
                ]
            elif tile_type in get_poi_names_set():
                if "gather" in tile_type:
                    all_tiles = [
                        t for t in all_tiles.copy() if
                        t.poi == "gathering"
                    ]
                elif "moon" in tile_type:
                    all_tiles = [
                        t for t in all_tiles.copy() if
                        t.poi == "moonplace"
                    ]
                else:
                    all_tiles = [
                        t for t in all_tiles.copy() if
                        t.poi == tile_type
                    ]
            elif tile_type in get_poi_categories_set():
                all_tiles = [
                    t for t in all_tiles.copy() if
                    t.poi == tile_type
                ]
                print(tile_type, all_tiles)
            else:
                # shouldnt need this
                for tile in all_tiles:
                    if tile.terrain == tile_type:
                        all_tiles = [tile]
                        break
                print("No logic for tile type", tile_type)
        # print("GET TILES:", tile_types)
        return all_tiles

    def _get_all_border_tiles(self, clan):
        """
        Returns a list of all border tiles of a specified Clan's territory.
        """
        border_tiles = []
        all_tiles = [t for t in game.clan.territory_tiles if t.owner == clan]

        for tile in all_tiles:
            if tile.is_bordering("any"):
                border_tiles.append(tile)
        return border_tiles

territory_class = Territory()
