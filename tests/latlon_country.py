from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
   
# declare an empty list to store
# latitude and longitude of values 
# of city column
longitude = []
latitude = []
   
# function to find the coordinate
# of a given city 
def findGeocode(country):
       
    # try and catch is used to overcome
    # the exception thrown by geolocator
    # using geocodertimedout  
    try:
          
        # Specify the user_agent as your
        # app name it should not be none
        geolocator = Nominatim(user_agent="Meile")
          
        return geolocator.geocode(country)
      
    except GeocoderTimedOut:
          
        return findGeocode(country) 
    

if __name__ == "__main__":
    loc = findGeocode("Hong Kong")
    longitude.append(loc.longitude)
    latitude.append(loc.latitude)

    for lat, long in zip(latitude, longitude):
        print("%s,%s" % (lat, long))