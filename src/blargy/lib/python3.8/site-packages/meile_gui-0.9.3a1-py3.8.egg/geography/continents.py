import awoc as awoc

class OurWorld():
    our_world = awoc.AWOC()
    
    CONTINENTS   = our_world.get_continents_list()
    Africa       = our_world.get_countries_list_of(CONTINENTS[0])
    Anarctica    = our_world.get_countries_list_of(CONTINENTS[1])
    Asia         = our_world.get_countries_list_of(CONTINENTS[2])
    Europe       = our_world.get_countries_list_of(CONTINENTS[3])
    NorthAmerica = our_world.get_countries_list_of(CONTINENTS[4])
    Oceania      = our_world.get_countries_list_of(CONTINENTS[5])
    SouthAmerica = our_world.get_countries_list_of(CONTINENTS[6])
