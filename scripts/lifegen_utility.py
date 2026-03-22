import ujson
import re
from random import choice
from scripts.game_structure import game
from scripts.cat.enums import (
    CatAge,
    CatRank,
    CatGroup
)
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank, get_living_clan_cat_count
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.screens.enums import GameScreen

def get_cluster(trait):
    """
    Returns the cluster(s) for a given trait.
    """
    with open("resources/dicts/cluster_map.json", "r", encoding="utf-8") as file:
        cluster_map = ujson.load(file)

    clusters = [key for key, values in cluster_map.items() if trait in values]

    # Assign cluster and second_cluster based on the length of clusters list
    cluster = clusters[0] if clusters else "stable"
    second_cluster = clusters[1] if len(clusters) > 1 else ""

    return cluster, second_cluster

def check_achievements(Cat, eventspage=False):
    you = game.clan.your_cat
    achievements = set()
    murder_history = you.history.murder
    count_alive_cats = 0
    if murder_history:
        if 'is_murderer' in murder_history:
            num_victims = len(murder_history["is_murderer"])
            if num_victims >= 0:
                achievements.add("1")
            if num_victims >= 5:
                achievements.add("2")
            if num_victims >= 20:
                achievements.add("3")
            if num_victims >= 50:
                achievements.add("4")
    else:
        if you.moons >= 120:
            achievements.add("25")
        

    for cat in Cat.all_cats_list:
        if cat.moons >= 0:
            if cat.pelt.tortie_base and cat.gender == 'male':
                achievements.add("5")
            if cat.insulted:
                achievements.add("29")
            if (cat.name.prefix == "Coffee" and cat.name.suffix == "dot") or (cat.name.prefix == "Chibi" and cat.name.suffix == "Galaxies"):
                achievements.add("30")
            if cat.status.rank == CatRank.APPRENTICE and cat.name.prefix == "Pea" and cat.pelt.white_colours:
                achievements.add("33")
            if cat.status.rank == CatRank.KITTEN and cat.moons > 6:
                achievements.add("34")
            if cat.backstory == 'dfkit' or cat.backstory == 'dfkit2':
                achievements.add("35")
            ##WILDCARD check, because I've lost control of my life
            ##Actual check for wildcardness
            if cat.pelt.is_wildcard_tortie():
                achievements.add("6")

            ##code block for achievement 31
            achieve31RankList = [CatRank.MEDIATOR, CatRank.WARRIOR, CatRank.LEADER]
            achieve31UsedRanks = []
            if len(cat.mate) >= 2:
                catMateIDs = cat.mate.copy()
                if cat.status.rank in achieve31RankList:
                    achieve31UsedRanks.append(cat.status.rank)
                    for cat in Cat.all_cats_list:
                        if cat.ID in catMateIDs:
                            if (cat.status.rank in achieve31RankList) and (cat.status.rank not in achieve31UsedRanks):
                                achieve31UsedRanks.append(cat.status.rank)
                        countranks = 0
                        for i in achieve31UsedRanks:
                            if i in achieve31RankList:
                                countranks += 1
                            if countranks >= 3:
                                achievements.add("31")
            ##achievement block to check MC has a df mate for achieve 36. Not a copy of above code. Above code checks for Any cats
            mcMateIDs = you.mate 
            #for loop list is in case you have multiple mates to search through. 
            for i in mcMateIDs:
                if cat.ID in mcMateIDs and you.dead is False:
                    #Thank you Jay, for helping me figure out history stuff! 
                    if cat.history:
                        if cat.history.beginning:
                            if "encountered" in cat.history.beginning and cat.history.beginning["encountered"] is True and cat.df is True:
                                achievements.add("36")
            #code for achievement 23 + 24
            if game.clan.age >= 1:
                if get_living_clan_cat_count(Cat) == 0:
                    achievements.add('40')
                elif get_living_clan_cat_count(Cat) == 1 and you.status.alive_in_player_clan:
                    achievements.add('23')
                elif get_living_clan_cat_count(Cat) >= 100:
                    achievements.add('24')
                elif get_living_clan_cat_count(Cat) >= 400:
                    achievements.add('39')

    if you.joined_df:
        achievements.add("7")
    
    if len(you.former_apprentices) >= 1:
        achievements.add("8")
    if len(you.former_apprentices) >= 5:
        achievements.add("9")
    
    if you.inheritance.get_children():
        achievements.add("10")
    for i in you.relationships.keys():
        if you.relationships.get(i).like <= -60:
            achievements.add("11")
        if you.relationships.get(i).romance >= 60:
            achievements.add('12')
        
    if len(you.mate) >= 5:
        achievements.add('13')
    if you.status.rank == CatRank.WARRIOR:
        achievements.add('14')
    elif you.status.rank == CatRank.MEDICINE_CAT:
        achievements.add('15')
    elif you.status.rank == CatRank.MEDIATOR:
        achievements.add('16')
    elif you.status.rank == CatRank.DEPUTY:
        achievements.add('17')
    elif you.status.rank == CatRank.LEADER:
        achievements.add('18')
    elif you.status.rank == CatRank.ELDER:
        achievements.add('19')
    elif you.status.rank == CatRank.QUEEN:
        achievements.add('32')
    
    if you.moons >= 200:
        achievements.add('20')
    if you.status.is_exiled(CatGroup.PLAYER_CLAN_ID):
        achievements.add('21')
    elif you.status.is_outsider:
        achievements.add('22')
        
    if you.experience >= 100:
        achievements.add('26')
    if you.experience >= 200:
        achievements.add('27')
    if you.experience >= 300:
        achievements.add('28')

    new_achievements_list = []
    for item in achievements:
        already_earned = False
        for entry in game.clan.achievements:
            if entry[0] == item:
                already_earned = True
                break

        if not already_earned:
            game.clan.achievements.append([item, game.clan.your_cat.ID])
            if eventspage:
                new_achievements_list.append(item)
    if eventspage:
        return new_achievements_list
    
def get_current_camp():
    """ LG """
    if game.clan.your_cat:
        if game.clan.your_cat.status.group in [CatGroup.PLAYER_CLAN, CatGroup.OTHER_CLAN]:
            camp_nr = game.clan.camp_bg
            camp_bg_base_dir = "resources/images/camp_bg/clancat"
        elif game.clan.your_cat.status.group == CatGroup.ROGUE_GROUP:
            camp_nr = game.clan.rogue_group_bg
            camp_bg_base_dir = "resources/images/camp_bg/rogue"
        elif game.clan.your_cat.status.group == CatGroup.LONER_GROUP:
            camp_nr = game.clan.loner_group_bg
            camp_bg_base_dir = "resources/images/camp_bg/loner"
        elif game.clan.your_cat.status.group == CatGroup.HOUSEHOLD:
            camp_nr = game.clan.household_bg
            camp_bg_base_dir = "resources/images/camp_bg/kittypet"
        else:
            camp_nr = game.clan.no_group_bg
            camp_bg_base_dir = "resources/images/camp_bg/none"
    else:
        camp_nr = game.clan.camp_bg
        camp_bg_base_dir = "resources/images/camp_bg/clancat"

    return camp_bg_base_dir, camp_nr

def assign_new_bg(camp):
    """ LG """
    if game.clan.your_cat:
        if game.clan.your_cat.status.group in [CatGroup.PLAYER_CLAN, CatGroup.OTHER_CLAN]:
            game.clan.camp_bg = camp
        elif game.clan.your_cat.status.group == CatGroup.ROGUE_GROUP:
            game.clan.rogue_group_bg = camp
        elif game.clan.your_cat.status.group == CatGroup.LONER_GROUP:
            game.clan.loner_group_bg = camp
        elif game.clan.your_cat.status.group == CatGroup.HOUSEHOLD:
            game.clan.household_bg = camp
        else:
            game.clan.no_group_bg = camp
    else:
        game.clan.camp_bg = camp

# LG
def get_your_cat_group_count(Cat):
    count = 0
    for the_cat in Cat.all_cats.values():
        if not the_cat.status.alive_in_your_cat_group:
            continue
        count += 1
    return count
