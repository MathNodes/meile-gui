import awoc
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from time import sleep
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

    def findGeocode(self, country):
        try:
        
            geolocator = Nominatim(user_agent="Meile")              
            return geolocator.geocode(country)
        
        except GeocoderTimedOut:
              
            return findGeocode(country) 
        
        
if __name__ == "__main__":
    MyWorld = OurWorld()
    
    CountryLatLong = {}
    CountriesTimedOut = []
    for country in MyWorld.CONTINENTS:
    #for country in ['Turkmenistan', 'Russia', 'Belize']:
        print(country)
        try:
            loc = MyWorld.findGeocode(country)
        except:
            CountriesTimedOut.append(country)
            continue
        CountryLatLong[country] = [loc.latitude, loc.longitude]
        print(CountryLatLong[country])
        sleep(7)
        
    print(CountryLatLong)
    print(CountriesTimedOut)