from scripts.game_structure import game
from scripts.territory import territory_class
import random
from scripts.events_module.text_adjust import (
    adjust_list_text
)

class War():
    # INDIVIDUAL wars
    # maybe move events and stuff here
    """
    offense is the GROUP ID
    SO IS DEFENSE
    """
    def __init__(
            self,
            offense="",
            defense="",
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
            "demand": self.demand if isinstance(self.demand, str) else self.demand.tile_string,
            "duration": self.duration,
            "progress": self.progress
        }
    
    def is_in_war(self, clan, other_clan=None):
        """
        Return True if the specifed Clan(s) are a part of this war.
        """
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
        for other_clan in [game.clan] + game.clan.all_other_clans:
            if other_clan.group_ID == opponent_ID:
                opponent_object = other_clan
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
        Or all Clans if there are multiple.
        The Clan passed as an argument will come first in the sentence.
        """
        found_wars = []
        for war in game.clan.war:
            if clan.group_ID in [war.offense, war.defense]:
                found_wars.append(war)

        opponents = []
        for war in found_wars:
            opponents.append(war.get_opponent_object(clan).name)

        if len(opponents) == 1:
            opponent = self.get_opponent_object(clan)
            demand = self.demand if isinstance(self.demand, str) else "territory"
            return f"<b>{clan.name}</b> is at war with <b>{opponent.name}</b> over <b>{demand}</b>."
        return f"<b>{clan.name}</b> is at war with <b>{adjust_list_text(opponents)}</b>."
    
    def get_offense_object(self):
        """
        Returns the Clan or OtherClan object of the offensive Clan.
        """
        offense_object = None
        for clan in [game.clan] + game.clan.all_other_clans:
            if clan.group_ID == self.offense:
                offense_object = clan
                break
        return offense_object

    def get_defense_object(self):
        """
        Returns the Clan or OtherClan object of the defensive Clan.
        """
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
        # TODO: determine demand tile based on desirablility. herbs, water, POIs.
        # and maybe find a way to involve this in the event text
        demand_tiles = territory_class.get_tiles(
            ["other_clan_inner_border"],
            clan=self.get_offense_object(),
            other_clan=self.get_defense_object()
            )
        if demand_tiles and random.randint(1,4) != 1:
            demand = random.choice(demand_tiles)
        else:
            demand = random.choice(["herbs", "prey"])

        print("DEMAND:", demand)
        self.demand = demand

    def win_war(self, winner):
        """
        Handles prizes for winning wars.
        """
        # TODO: maybe winning extra tiles (neighbours of demand tile)
        # TODO: prey and herbs
        if self.demand:
            print(winner.name, "wins the war! They win:", self.demand)
            if not isinstance(self.demand, str):
                if self.demand.owner != winner:
                    self.demand.change_owner(winner)
            else:
                # prey or herbs
                pass

    def end_war(self):
        game.clan.war.remove(self)
    
    def __repr__(self):
        return f"{self.get_offense_object().name} vs. {self.get_defense_object().name} | {self.duration} moons | Demands: {self.demand}"

war_class = War()
