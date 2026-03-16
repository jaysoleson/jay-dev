from strenum import StrEnum
import random

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
        self.likes_toms = random.choice([True, False])
        self.likes_she_cats = random.choice([True, False])

        # likes enbies cant be true if the other two are false. no enby chasers sorry
        self.likes_enbies = random.choice([True, False]) if self.likes_toms or self.likes_she_cats else False


        self.acespec = random.choice([Acespec.ALLO, Acespec.DEMI, Acespec.GREY, Acespec.ACE])
        self.arospec = random.choice([Arospec.ALLO, Arospec.DEMI, Arospec.GREY, Arospec.ARO])

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
