from strenum import StrEnum
import random

from scripts.cat.pelts import Pelt
from scripts.events_module.text_adjust import adjust_list_text

class Acespec(StrEnum):
    ALLO = "allosexual"
    DEMI = "demisexual"
    GREY = "greyasexual"
    ACE = "asexual"

class Arospec(StrEnum):
    ALLO = "alloromantic"
    DEMI = "demiromantic"
    GREY = "greyaromantic"
    ARO = "aromantic"

class Sexuality():
    male_genders = [
        "male", "trans male", "demiboy", "boy", "man", "tom", "genderfaun"
    ]
    female_genders = [
        "female", "trans female", "demigirl", "girl", "woman", "molly", "genderdoe"
    ]
    def __init__(
            self,

            sexuality_label="",
            likes_toms=False,
            likes_she_cats=False,
            likes_enbies=False,

            arospec_label="",
            acespec_label="",
            acespec=Acespec.ALLO,
            arospec=Arospec.ALLO,

            t4t=False
            ):
        self.sexuality_label = sexuality_label
        self.likes_toms = likes_toms
        self.likes_she_cats = likes_she_cats
        self.likes_enbies = likes_enbies

        self.acespec_label = acespec_label
        self.arospec_label = arospec_label
        self.acespec = acespec
        self.arospec = arospec

        self.t4t = t4t

    # CAT GENERATION
    def generate_sexuality_label(self, genderalign):
        """
        Generates the sexuality string based on gender.
        """
        if genderalign in self.male_genders:
            label_dict = {
                (True, False, False): "gay",
                (True, False, True): "gay",
                (False, True, False): "straight",
                (False, True, True): "straight",
                (True, True, False): random.choice(["biXX", "panXX"]),
                (True, True, True): random.choice(["biXX", "panXX"]),
                (False, False, False): "aroace"
            }
        elif genderalign in self.female_genders:
            label_dict = {
                (True, False, False): "straight",
                (True, False, True): "straight",
                (False, True, False): "lesbian",
                (False, True, True): "lesbian",
                (True, True, False): random.choice(["biXX", "panXX"]),
                (True, True, True): random.choice(["biXX", "panXX"]),
                (False, False, False): "aroace"
            }
        else:
            label_dict = {
                (True, False, False): "androXX",
                (True, False, True): "androXX",
                (False, True, False): "gynoXX",
                (False, True, True): "gynoXX",
                (True, True, False): random.choice(["biXX", "panXX"]),
                (True, True, True): random.choice(["biXX", "panXX"]),
                (False, False, False): "aroace"
            }

        cat_arospec = False
        cat_acespec = False

        first_label = label_dict[(self.likes_toms, self.likes_she_cats, self.likes_enbies)]
        if self.acespec != Acespec.ALLO and first_label != "aroace":
            cat_acespec = True
        if self.arospec != Arospec.ALLO and first_label != "aroace":
            cat_arospec = True
        
        # labels like bi will change to "bisexual" or "biromantic" depending on the cats
        # ace/arospec orientations
        if cat_acespec and not cat_arospec:
            first_label = first_label.replace("XX", "romantic")
        elif cat_arospec and not cat_acespec:
            first_label = first_label.replace("XX", "sexual")
        elif not cat_arospec and not cat_acespec:
            first_label = first_label.replace("XX", "sexual")
        else:
            first_label = first_label.replace("XX", "")

        return first_label

    def correct_aroace(self):
        """
        Corrects the sexuality parameters so aro/ace and likes_XYZ values line up.
        """

        if (
            not self.likes_toms and
            not self.likes_she_cats and
            not self.likes_enbies
        ):
            self.arospec = Arospec.ARO
            self.acespec = Acespec.ACE
            return

        if (
            self.arospec == Arospec.ARO and
            self.acespec == Acespec.ACE
        ):
            self.likes_toms = False
            self.likes_she_cats = False
            self.likes_enbies = False
        


    def init_random_sexuality(self, gender):
        """
        Randomises a new cat's sexuality.
        """
        self.sexuality_label = "TEMP"
        if gender in self.male_genders:
            self.likes_toms = random.choice([True, False])
            self.likes_she_cats = random.choice([True, False, True])
        elif gender in self.female_genders:
            self.likes_toms = random.choice([True, False, True])
            self.likes_she_cats = random.choice([True, False])
        else:
            self.likes_toms = random.choice([True, False])
            self.likes_she_cats = random.choice([True, False])


        # likes enbies cant be true if the other two are false. no enby chasers sorry
        self.likes_enbies = random.choice([True, False]) if self.likes_toms or self.likes_she_cats else False

        acespec_chance = 20
        arospec_chance = 20

        if not int(random.random() * acespec_chance):
            self.acespec = random.choice(
                [
                    Acespec.DEMI,
                    Acespec.GREY,
                    Acespec.ACE,
                    Acespec.ACE,
                    Acespec.ACE,
                ]
            )
        else:
            self.acespec = Acespec.ALLO

        if not int(random.random() * arospec_chance):
            self.arospec = random.choice(
                [
                    Arospec.DEMI,
                    Arospec.GREY,
                    Arospec.ARO,
                    Arospec.ARO,
                    Arospec.ARO,
                ]
            )
        else:
            self.arospec = Arospec.ALLO

        self.correct_aroace()

        # Labels!
        self.acespec_label = self.acespec
        self.arospec_label = self.arospec
        self.sexuality_label = self.generate_sexuality_label(gender)

        self.t4t = False

    def get_sexuality_dict(self):
        """
        Returns the sexuality dict for the save file.
        """
        return {
            "sexuality_label": self.sexuality_label,
            "likes_toms": self.likes_toms,
            "likes_she_cats": self.likes_she_cats,
            "likes_enbies": self.likes_enbies,
            "arospec_label": self.arospec_label,
            "acespec_label": self.acespec_label,
            "arospec": self.arospec,
            "acespec": self.acespec,
            "t4t": self.t4t
        }
    
    # BOOL RETURNERS
    def is_aroace(self):
        if self.arospec == Arospec.ARO and self.acespec == Acespec.ACE:
            return True
        return False
    
    # PROFILE DISPLAY
    def get_sexuality_profile_display(self, kitten=False):
        """
        Fetches sexuality information and puts it together to display on the profile.
        """
        if kitten:
            return "???"

        all_labels = []
        first_label = self.sexuality_label
        all_labels.append(first_label)

        if self.acespec != Acespec.ALLO and first_label != "aroace":
            all_labels.append(self.acespec)
        if self.arospec != Arospec.ALLO and first_label != "aroace":
            all_labels.append(self.arospec)

        return adjust_list_text(all_labels)
    

    # FLAGS
    def find_valid_flags(self, cat):
        valid_flags = []
        if cat.gender != cat.genderalign:
            valid_flags.append("TRANS")

        if cat.genderalign.upper() in Pelt.all_pridegen_accessories:
            valid_flags.append(cat.genderalign.upper())
        if self.sexuality_label.upper() in Pelt.all_pridegen_accessories:
            valid_flags.append(self.sexuality_label.upper())

        # sexuality flags that dont differ based on gender
        # hacky
        if self.likes_toms and self.likes_she_cats:
            if "bi" in self.sexuality_label:
                valid_flags.append("BISEXUAL")
            elif "pan" in self.sexuality_label:
                valid_flags.append("PANSEXUAL")

        if (
            not self.likes_toms and
            not self.likes_she_cats and
            not self.likes_enbies and
            self.arospec == Arospec.ARO and
            self.acespec == Acespec.ACE
        ):
            valid_flags.append("AROACE")
            valid_flags.append("AROACEFLUX")

        if self.arospec.upper() in Pelt.all_pridegen_accessories:
            valid_flags.append(self.arospec.upper())
        if self.acespec.upper() in Pelt.all_pridegen_accessories:
            valid_flags.append(self.acespec.upper())

        if self.arospec == Arospec.DEMI and self.acespec == Acespec.DEMI:
            valid_flags.append("DEMIAROACE")
        if self.arospec == Arospec.GREY and self.acespec == Acespec.GREY:
            valid_flags.append("GREYAROACE")

        if len(cat.mate) > 1:
            valid_flags.append("POLYAMOROUS")

        if cat.genderalign in Sexuality.male_genders:
            if self.likes_toms:
                valid_flags.append("ACHILLEAN")
                valid_flags.append("RAINBOW_BANDANA")
                valid_flags.append("NEPTUNIC")
                if not self.likes_she_cats:
                    valid_flags.append("GAY")
            elif self.likes_she_cats:
                valid_flags.append("STRAIGHT")
        elif cat.genderalign in Sexuality.female_genders:
            if self.likes_she_cats:
                valid_flags.append("SAPPHIC")
                valid_flags.append("RAINBOW_BANDANA")
                valid_flags.append("URANIC")
                if not self.likes_she_cats:
                    valid_flags.append("LESBIAN")
                    valid_flags.append("BUTCH")
            elif self.likes_toms:
                valid_flags.append("STRAIGHT")
        else:
            valid_flags.append("NONBINARY")
            if self.likes_she_cats and not self.likes_toms:
                valid_flags.append("GYNOSEXUAL")
            elif self.likes_toms and not self.likes_she_cats:
                valid_flags.append("ANDROSEXUAL")

        new_valid_flags = []
        for flag in valid_flags:
            if flag not in new_valid_flags:
                new_valid_flags.append(flag)

        return new_valid_flags
    

     # PRIDEGEN
    def give_bandanas(self, cat):
        """
        Updates bandana inventories.
        """
        # TODO: clan setting for disabling bandanas
        if cat.age.is_baby():
            return

        correct_flags = cat.sexuality.find_valid_flags(cat)

        for flag in Pelt.all_pridegen_accessories:
            if flag in cat.pelt.inventory:
                cat.pelt.inventory.remove(flag)
                cat.pelt.accessory = tuple(
                    accessory for accessory in cat.pelt.accessory if
                    accessory != flag
                )

        sorted_flags = list(set(correct_flags))

        for acc in sorted_flags:
            if acc not in cat.pelt.inventory:
                cat.pelt.inventory.append(acc)

        # TODO: if autoequip setting
        autoequip = True
        if autoequip:
            skip = False
            for acc in cat.pelt.accessory:
                if acc in correct_flags:
                    skip = True
                    break
            if not skip:
                cat.pelt.accessory = cat.pelt.accessory + (sorted_flags[0],)
                if sorted_flags[0] not in cat.pelt.inventory:
                    cat.pelt.inventory.append(sorted_flags[0])

        cat.pelt.rebuild_sprite = True

