from enum import Enum


class NewGenderEnum(Enum):
    nonbinary = "nonbinary"
    trans_male = "trans male"
    trans_female = "trans female"

    # PG
    mossgender = "mossgender"
    moongender = "moongender"
    sungender = "sungender"
    stargender = "stargender"
    apagender = "apagender"
    arkhaigender = "arkhaigender"
    archeogender = "archeogender"
    catgender = "catgender"
    genderdoe = "genderdoe"
    mothgender = "mothgender"
    snowleopardgender = "snowleopardgender"
    tigergender = "tigergender"
    buggender = "buggender"
    genderfaun = "genderfaun"
    xenogender = "xenogender"
    genderflux = "genderflux"
    demifluid = "demifluid"
    genderfluid = "genderfluid"


class GenderEnum(Enum):
    male = "male"
    female = "female"
