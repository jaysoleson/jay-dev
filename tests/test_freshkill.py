import os
import unittest
import ujson

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat.skills import Skill, SkillPath
from scripts.clan import Clan
from scripts.clan_resources.freshkill import FreshkillPile
from scripts.utility import get_alive_clan_queens


class FreshkillPileTest(unittest.TestCase):

    def setUp(self) -> None:
        self.prey_config = None
        with open("resources/prey_config.json", 'r') as read_file:
            self.prey_config = ujson.loads(read_file.read())
        self.amount = self.prey_config["start_amount"]
        self.prey_requirement = self.prey_config["prey_requirement"]
        self.condition_increase = self.prey_config["condition_increase"]

    def test_add_freshkill(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

        # then
        freshkill_pile.add_freshkill(1)
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.amount + 1)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

    def test_remove_freshkill(self) -> None:
        # given
        freshkill_pile1 = FreshkillPile()
        freshkill_pile1.pile["expires_in_1"] = 10
        self.assertEqual(freshkill_pile1.pile["expires_in_1"], 10)
        freshkill_pile1.remove_freshkill(5)

        freshkill_pile2 = FreshkillPile()
        freshkill_pile2.remove_freshkill(5, True)

        # then
        self.assertEqual(freshkill_pile1.pile["expires_in_4"], self.amount)
        self.assertEqual(freshkill_pile1.pile["expires_in_1"], 5)
        self.assertEqual(freshkill_pile2.total_amount, self.amount - 5)

    def test_time_skip(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

        # then
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], self.amount)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

    def test_feed_cats(self) -> None:
        # given
        test_clan = Clan(name="Test",
                         baron=None,
                         regent=None,
                         doctor=None,
                         biome='Forest',
                         camp_bg=None,
                         game_mode='expanded',
                         starting_season='Newleaf')
        test_clipper = Cat()
        test_clipper.status = "clipper"
        test_clan.add_cat(test_clipper)

        # then
        self.assertEqual(test_clan.freshkill_pile.total_amount, self.amount)
        test_clan.freshkill_pile.feed_cats([test_clipper])
        self.assertEqual(test_clan.freshkill_pile.total_amount,
                         self.amount - self.prey_requirement["clipper"])

    def test_tactic_younger_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.prey_requirement["clipper"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        youngest_clipper = Cat()
        youngest_clipper.status = "clipper"
        youngest_clipper.moons = 20
        middle_clipper = Cat()
        middle_clipper.status = "clipper"
        middle_clipper.moons = 30
        oldest_clipper = Cat()
        oldest_clipper.status = "clipper"
        oldest_clipper.moons = 40

        freshkill_pile.add_cat_to_nutrition(youngest_clipper)
        freshkill_pile.add_cat_to_nutrition(middle_clipper)
        freshkill_pile.add_cat_to_nutrition(oldest_clipper)
        self.assertEqual(
            freshkill_pile.nutrition_info[youngest_clipper.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_clipper.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[oldest_clipper.ID].percentage, 100)

        # when
        freshkill_pile.tactic_younger_first(
            [oldest_clipper, middle_clipper, youngest_clipper])

        # then
        self.assertEqual(
            freshkill_pile.nutrition_info[youngest_clipper.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_clipper.ID].percentage, 100)
        self.assertNotEqual(
            freshkill_pile.nutrition_info[oldest_clipper.ID].percentage, 100)

    def test_tactic_less_nutrition_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.prey_requirement["clipper"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        lowest_clipper = Cat()
        lowest_clipper.status = "clipper"
        lowest_clipper.moons = 20
        middle_clipper = Cat()
        middle_clipper.status = "clipper"
        middle_clipper.moons = 30
        highest_clipper = Cat()
        highest_clipper.status = "clipper"
        highest_clipper.moons = 40

        freshkill_pile.add_cat_to_nutrition(lowest_clipper)
        max_score = freshkill_pile.nutrition_info[lowest_clipper.ID].max_score
        give_score = max_score - self.prey_requirement["clipper"]
        freshkill_pile.nutrition_info[lowest_clipper.ID].current_score = give_score

        freshkill_pile.add_cat_to_nutrition(middle_clipper)
        give_score = max_score - (self.prey_requirement["clipper"] / 2)
        freshkill_pile.nutrition_info[middle_clipper.ID].current_score = give_score

        freshkill_pile.add_cat_to_nutrition(highest_clipper)
        self.assertLessEqual(
            freshkill_pile.nutrition_info[lowest_clipper.ID].percentage, 70)
        self.assertLessEqual(
            freshkill_pile.nutrition_info[middle_clipper.ID].percentage, 90)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_clipper.ID].percentage, 100)

        # when
        living_cats = [highest_clipper, middle_clipper, lowest_clipper]
        freshkill_pile.living_cats = living_cats
        freshkill_pile.tactic_less_nutrition_first(living_cats)

        # then
        self.assertEqual(freshkill_pile.total_amount, 0)
        self.assertGreaterEqual(
            freshkill_pile.nutrition_info[lowest_clipper.ID].percentage, 60)
        self.assertGreaterEqual(
            freshkill_pile.nutrition_info[middle_clipper.ID].percentage, 80)
        self.assertLess(
            freshkill_pile.nutrition_info[highest_clipper.ID].percentage, 70)

    def test_tactic_sick_injured_first(self) -> None:
        # given
        # young enough kid
        injured_cat = Cat()
        injured_cat.status = "clipper"
        injured_cat.injuries["test_injury"] = {
            "severity": "major"
        }
        sick_cat = Cat()
        sick_cat.status = "clipper"
        sick_cat.illnesses["test_illness"] = {
            "severity": "major"
        }
        healthy_cat = Cat()
        healthy_cat.status = "clipper"

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the clipper
        current_amount = self.prey_requirement["clipper"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        freshkill_pile.add_cat_to_nutrition(injured_cat)
        freshkill_pile.add_cat_to_nutrition(sick_cat)
        freshkill_pile.add_cat_to_nutrition(healthy_cat)
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 100)

        # when
        freshkill_pile.tactic_sick_injured_first([healthy_cat, sick_cat, injured_cat])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 70)

    def test_more_experience_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.prey_requirement["clipper"]
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        lowest_clipper = Cat()
        lowest_clipper.status = "clipper"
        lowest_clipper.experience = 20
        middle_clipper = Cat()
        middle_clipper.status = "clipper"
        middle_clipper.experience = 30
        highest_clipper = Cat()
        highest_clipper.status = "clipper"
        highest_clipper.experience = 40

        freshkill_pile.add_cat_to_nutrition(lowest_clipper)
        freshkill_pile.add_cat_to_nutrition(middle_clipper)
        freshkill_pile.add_cat_to_nutrition(highest_clipper)
        self.assertEqual(
            freshkill_pile.nutrition_info[lowest_clipper.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_clipper.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_clipper.ID].percentage, 100)

        # when
        freshkill_pile.tactic_more_experience_first(
            [lowest_clipper, middle_clipper, highest_clipper])

        # then
        # self.assertEqual(freshkill_pile.total_amount,0)
        self.assertLess(
            freshkill_pile.nutrition_info[lowest_clipper.ID].percentage, 70)
        self.assertLess(
            freshkill_pile.nutrition_info[middle_clipper.ID].percentage, 90)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_clipper.ID].percentage, 100)

    def test_hunter_first(self) -> None:
        # check also different ranks of hunting skill
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.prey_requirement["clipper"] + (self.prey_requirement["clipper"]/2)
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        best_hunter_clipper = Cat()
        best_hunter_clipper.status = "clipper"
        best_hunter_clipper.skills.primary = Skill(SkillPath.HUNTER, 25)
        self.assertEqual(best_hunter_clipper.skills.primary.tier, 3)
        hunter_clipper = Cat()
        hunter_clipper.status = "clipper"
        hunter_clipper.skills.primary = Skill(SkillPath.HUNTER, 0)
        self.assertEqual(hunter_clipper.skills.primary.tier, 1)
        no_hunter_clipper = Cat()
        no_hunter_clipper.status = "clipper"
        no_hunter_clipper.skills.primary = Skill(SkillPath.MEDIATOR, 0, True)

        freshkill_pile.add_cat_to_nutrition(best_hunter_clipper)
        freshkill_pile.add_cat_to_nutrition(hunter_clipper)
        freshkill_pile.add_cat_to_nutrition(no_hunter_clipper)
        self.assertEqual(freshkill_pile.nutrition_info[best_hunter_clipper.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[hunter_clipper.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[no_hunter_clipper.ID].percentage, 100)

        # when
        living_cats = [hunter_clipper, no_hunter_clipper, best_hunter_clipper]
        freshkill_pile.tactic_hunter_first(living_cats)

        # then
        # this hunter should be fed completely
        self.assertEqual(freshkill_pile.nutrition_info[best_hunter_clipper.ID].percentage, 100)
        # this hunter should be fed partially
        self.assertLess(freshkill_pile.nutrition_info[hunter_clipper.ID].percentage, 90)
        self.assertGreater(freshkill_pile.nutrition_info[hunter_clipper.ID].percentage, 70)
        # this cat should not be fed
        self.assertLess(freshkill_pile.nutrition_info[no_hunter_clipper.ID].percentage, 70)

    def test_queen_handling(self) -> None:
        # given
        # young enough kid
        mother = Cat()
        mother.gender = "female"
        mother.status = "clipper"
        father = Cat()
        father.gender = "male"
        father.status = "clipper"
        kid = Cat()
        kid.status = "kitten"
        kid.moons = 2
        kid.parent1 = father
        kid.parent2 = mother

        no_parent = Cat()
        no_parent.status = "clipper"

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the clipper
        current_amount = self.prey_requirement["queen/pregnant"] + (self.prey_requirement["clipper"] / 2)
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        freshkill_pile.add_cat_to_nutrition(mother)
        freshkill_pile.add_cat_to_nutrition(father)
        freshkill_pile.add_cat_to_nutrition(kid)
        freshkill_pile.add_cat_to_nutrition(no_parent)
        self.assertEqual(freshkill_pile.nutrition_info[kid.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[mother.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[father.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[no_parent.ID].percentage, 100)

        # when
        living_cats = [no_parent, father, kid, mother]
        self.assertEqual([mother.ID], list(get_alive_clan_queens(living_cats)[0].keys()))
        freshkill_pile.tactic_status(living_cats)

        # then
        self.assertEqual(freshkill_pile.nutrition_info[kid.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[mother.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[no_parent.ID].percentage, 90)
        self.assertGreater(freshkill_pile.nutrition_info[no_parent.ID].percentage, 70)
        self.assertLess(freshkill_pile.nutrition_info[father.ID].percentage, 70)

    def test_pregnant_handling(self) -> None:
        # given
        # young enough kid
        pregnant_cat = Cat()
        pregnant_cat.status = "clipper"
        pregnant_cat.injuries["pregnant"] = {
            "severity": "minor"
        }
        cat2 = Cat()
        cat2.status = "clipper"
        cat3 = Cat()
        cat3.status = "clipper"

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the clipper
        current_amount = self.prey_requirement["queen/pregnant"]
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        freshkill_pile.add_cat_to_nutrition(pregnant_cat)
        freshkill_pile.add_cat_to_nutrition(cat2)
        freshkill_pile.add_cat_to_nutrition(cat3)
        self.assertEqual(freshkill_pile.nutrition_info[pregnant_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[cat2.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[cat3.ID].percentage, 100)

        # when
        freshkill_pile.feed_cats([cat2, cat3, pregnant_cat])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[pregnant_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[cat2.ID].percentage, 70)
        self.assertLess(freshkill_pile.nutrition_info[cat3.ID].percentage, 70)

    def test_sick_handling(self) -> None:
        # given
        # young enough kid
        injured_cat = Cat()
        injured_cat.status = "clipper"
        injured_cat.injuries["claw-wound"] = {
            "severity": "major"
        }
        sick_cat = Cat()
        sick_cat.status = "clipper"
        sick_cat.illnesses["diarrhea"] = {
            "severity": "major"
        }
        healthy_cat = Cat()
        healthy_cat.status = "clipper"

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the clipper
        current_amount = self.prey_requirement["clipper"] * 2 
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        freshkill_pile.add_cat_to_nutrition(injured_cat)
        freshkill_pile.add_cat_to_nutrition(sick_cat)
        freshkill_pile.add_cat_to_nutrition(healthy_cat)
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 100)

        # when
        freshkill_pile.feed_cats([sick_cat, injured_cat, healthy_cat])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 70)
