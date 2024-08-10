import random
from random import choice

from scripts.cat.history import History
from scripts.cat_relations.interaction import (
    SingleInteraction,
    NEUTRAL_INTERACTIONS,
    INTERACTION_MASTER_DICT,
    rel_fulfill_rel_constraints,
    cats_fulfill_single_interaction_constraints,
)
from scripts.event_class import Single_Event
from scripts.game_structure.game_essentials import game
from scripts.utility import get_personality_compatibility, process_text


# ---------------------------------------------------------------------------- #
#                           START Stats class                                  #
# ---------------------------------------------------------------------------- #


class Stats:

    def __init__(
        self,
        hunger=100,
        exposure=30,
        energy=100,
    ):
        self.chosen_interaction = None
        self.history = History()
       
        # each stat can go from 0 to 100
        self.hunger = hunger
        self.exposure = exposure
        self.energy = energy

    # ---------------------------------------------------------------------------- #
    #                                   property                                   #
    # ---------------------------------------------------------------------------- #

    @property
    def hunger(self):
        return self._hunger

    @hunger.setter
    def hunger(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._hunger = value

    @property
    def exposure(self):
        return self._exposure

    @exposure.setter
    def exposure(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._exposure = value

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._energy = value