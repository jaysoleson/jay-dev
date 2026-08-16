# individual tiles/ class stores all of their info
from scripts.game_structure import game
from scripts.config import get_config
from scripts.events_module.text_adjust import event_text_adjust, adjust_list_text
from scripts.cat.cats import Cat
from scripts.territory import territory_class

class TerritoryTile():
    MAP_SIZE = get_config("bellsofwar.territory_grid_size")
    high_value_herbs = {
            "catmint": 4,
            "honey": 4,
            "lungwort": 3,
            "poppy": 3,
            "cobwebs": 4,
            "moss": 3
        }

    def __init__(
            self,
            x: int = 0,
            y: int = 0,
            owner: str = None,
            poi: str = None,
            terrain: str = None,
            herb: str = None,
            strength: int = 0,
            camp: bool = False,
            events: list = []
    ):
        """
        Class object of a single territory tile.

        Args -------->
            x (int): the tile's x value.
            y (int): the tile's y value.

            owner (Clan, OtherClan, None): The tile's owner. Saved to JSON as the group_ID.
                default value: None
            poi (str): A string representing the POI located on this territory tile.
                default value: None
            terrain (str): The terrain of the tile.
                default value: "land"
            herb (str): The tile's most prevalent herb.
                default value: None
            strength (int): The territory's security level on a scale from 1-5.
                default value: 1
            # CAMP
            events (list): A list of all events within a specified time period that occurred on this tile.
                default value: []

        ------------->
         
        """
        self.x = x
        self.y = y
    
        self.owner = owner
        self.terrain = terrain
        self.poi = poi
        self.herb = herb
        self.strength = strength
        self.camp = camp
        self.events = events

    def get_save_dict(self):
        """
        Sets returns the save dict for the Tile.
        """
        return {
            "owner": self.owner.group_ID if self.owner else None,
            "terrain": self.terrain,
            "herb": self.herb,
            "poi": self.poi,
            "strength": self.strength,
            "camp": self.camp,
            "events": self.events
        }

    # PROPERTIES --------------------->
    @property
    def tile_string(self):
        return f"{self.x}-{self.y}"

    def in_dispute(self):
        for war in game.clan.war:
            if war.demand == self:
                return [war.get_offense_object().name, war.get_defense_object().name]
        return None

    # TEXT DISPLAY FUNCTIONS
    def name_string(self):
        """
        Returns the NAME of the tile. Biome, POI, or camp name.
        E.G. "The Twolegplace", "Forest", "GemClan Camp".
        """

        name = f"<b>{game.clan.biome}</b>" if game.clan.biome != "Mountainous" else "<b>Mountains</b>"
        if self.poi:
            if "terrain" in self.poi:
                name = "<b>" + event_text_adjust(Cat, text="{POI/name/" + self.poi + "}").title() + "</b>"
            else:
                name = "<b>" + event_text_adjust(Cat, text="{POI/category/" + self.poi + "}").title() + "</b>"
        elif self.camp:
            name = "<b>" + str(self.owner.name) + " Camp</b>"
        elif self.in_dispute():
            name = "<b>Disputed Territory</b>"
        else:
            if self.terrain != "land":
                name = f"<b>{self.terrain.capitalize()}</b>"

        return name

    def owner_string(self):
        """
        Returns the string describing who owns the tile.
        E.G. "GemClan Territory", "Unclaimed Land".
        """
        if self.in_dispute():
            return "Fought over by <b>" + self.in_dispute()[0] + " </b>and<b> " + self.in_dispute()[1] + "."
        if self.owner:
            return f"<b>{self.owner.name}'s Territory</b>"
        return "<b>Unclaimed Land</b>"

    def security_string(self):
        """
        Returns the string describing the tile's security.
        E.G. "Unguarded", "Patrolled regularly".
        """
        if self.in_dispute():
            return ""

        strength_dict = {
            0: "Unguarded",
            1: "Rarely visited",
            2: "Patrolled infrequently",
            3: "Patrolled regularly",
            4: "Effectively guarded"
        }
        return strength_dict[self.strength]

    def herb_string(self):
        if not self.herb:
            return ""
        return "Effective source of <br><b>" + self.herb.replace("_", " ") + "</b>"

    # OTHER HELPERS
    def desirability(self):
        desirability = 0
        if self.terrain in ("river", "lake"):
            desirability += 2
        if self.herb:
            if self.herb in self.high_value_herbs:
                desirability += self.high_value_herbs[self.herb]
        
        return desirability
    
    def get_immediate_neighbours(self):
        neighbour_strings = [
            f"{self.x - 1}-{self.y}",
            f"{self.x + 1}-{self.y}",
            f"{self.x}-{self.y - 1}",
            f"{self.x}-{self.y + 1}"
        ]
        return [territory_class.get_tile_from_string(t) for t in neighbour_strings]

    def is_bordering(self, border_type):
        """
        Returns True if the tile is bordering the specified feature.
        border_type can be None to get unclaimed border, an OtherClan or Clan object,
        or a terrain type.
        """
        for n in self.get_immediate_neighbours():
            if not n:
                continue
            if isinstance(border_type, str):
                # it's terrain!
                if border_type == "water":
                    if n.terrain in territory_class.water_types:
                        return True
                else:
                    if n.terrain == border_type:
                        return True
            else:
                if n.owner == border_type:
                    return True
        return False

    def __repr__(self):
        return f"#TILE: {self.tile_string}"

tile_class = TerritoryTile()
