from scripts.game_structure import game
from scripts.territory import territory_class
import random

class War():
    # INDIVIDUAL wars
    # maybe move events and stuff here
    def __init__(
            self,
            offense=[],
            defense=[],
            demand="",
            duration=0,
            progress=0
            ):
        self.offense = offense
        self.defense = defense
        self.demand = demand
        self.duration = duration
        self.progress = progress
        # PROGRESS is an int -1, 0, or 1. it represents whether the war is going
        # negatively, neutrally, or positively.

    def get_war_dict(self):
        return {
            "offense": self.offense,
            "defense": self.defense,
            "demand": self.demand,
            "duration": self.duration,
            "progrss": self.progress
        }
    
    def is_in_war(self, clan, other_clan=None):
        if not other_clan:
            if clan.group_ID == self.offense:
                return True
            if clan.group_ID == self.defense:
                return True
        else:
            if (
                clan.group_ID == self.offense and
                other_clan.group_ID == self.defense
            ):
                return True
            if (
                clan.group_ID == self.defense and
                other_clan.group_ID == self.offense
            ):
                return True
        return False
    
    def is_offense(self, clan):
        return clan.group_ID == self.offense
    
    def is_defense(self, clan):
        return clan.group_ID == self.offense
    
    def get_opponent_ID(self, clan):
        """
        Returns the string ID of the specified Clan's current opponent.
        """
        if clan.group_ID == self.offense:
            return self.defense
        return self.offense
    
    def get_opponent_object(self, clan):
        """
        Returns the Clan or OtherClan object of the specified Clan's current opponent.
        """
        opponent_object = None
        opponent_ID = self.get_opponent_ID(clan)
        for clan in [game.clan] + game.clan.all_other_clans:
            if clan.group_ID == opponent_ID:
                opponent_object = clan
                break
        return opponent_object
    
    def get_opposition_string(self, clan):
        """
        Returns an "at war with" string, only mentioning the opponent by name.
        """
        opponent = self.get_opponent_object(clan)

        return f"At war with <b>{opponent.name}</b>"

    def get_full_opposition_string(self, clan):
        """
        Returns an "at war with" string, mentioning both Clans.
        The Clan passed as an argument will come first in the sentence.
        """
        opponent = self.get_opponent_object(clan)
        return f"<b>{clan.name}</b> is at war with <b>{opponent.name}</b>"
    
    def get_offense_object(self):
        offense_object = None
        for clan in [game.clan] + game.clan.all_other_clans:
            if clan.group_ID == self.offense:
                offense_object = clan
                break
        return offense_object

    def get_defense_object(self):
        defense_object = None
        for clan in [game.clan] + game.clan.all_other_clans:
            if clan.group_ID == self.defense:
                defense_object = clan
                break
        return defense_object
    
    def get_demand(self):
        """
        Determines the demand for a war.
        """
        # TODO: depends on herbs and borders, border strength
        # TODO: use this to change demands in the middle of wars!
        demand_tiles = territory_class.get_tiles(
            "other_clan_inner_border",
            clan=self.get_offense_object(),
            other_clan=self.get_defense_object(),
            exclude_water=True
            )[0]
        if demand_tiles:
            demand = random.choice(demand_tiles)
        else:
            demand = random.choice(["herbs", "prey"])
        self.demand = demand

    def win_war(self, winner):
        if self.demand:
            print(winner.name, "wins the war! They win:", self.demand)
            if self.demand in game.clan.territory_tile_info:
                territory_class.update_tile_info(self.demand, "owner", winner.group_ID)
    
    def __repr__(self):
        return f"{self.get_offense_object().name} vs. {self.get_defense_object().name} | {self.duration} moons | Demands: {self.demand}"

war_class = War()
