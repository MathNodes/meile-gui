from continents import OurWorld

C = "Czechia"
D = "Seychelles"
if C == "Czechia":
    C = "Czech Republic"
    print(OurWorld.our_world.get_country_ISO2(C))
    
print(OurWorld.our_world.get_country_ISO2(D))