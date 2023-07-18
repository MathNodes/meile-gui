import configparser

if __name__ == "__main__":
    configfile = 'test_config.ini'
    
    CONFIG = configparser.ConfigParser()
    
    CONFIG.read(configfile)
    print(CONFIG.sections())
    
    
    if CONFIG.has_section('network'):
        print("Section 'network' exists")
    else:
        CONFIG.add_section('network')
        CONFIG.set('network', 'rpc', 'https://rpc.mathnodes.com:443')
        
    FILE = open(configfile, 'w')    
    CONFIG.write(FILE)
    
    for section in CONFIG.sections():
        for key,value in CONFIG.items(section):
            print(f"{key}, {value}")