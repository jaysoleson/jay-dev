# individual tiles/ class stores all of their info


class TerritoryTile():
    def __init__(
            self,
            x: int = 0,
            y: int = 0,
            owner: str = None,
            poi: str = None,
            terrain: str = None,
            herb: str = None,
            strength: int = 1,
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
            "events": self.events
        }

    # PROPERTIES --------------------->
    @property
    def tile_string(self):
        return f"{self.x}-{self.y}"
