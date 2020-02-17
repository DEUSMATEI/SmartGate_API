from configparser import ConfigParser

#CONFIG DATA 
CONFIG_REQUIRED_DATA = [
    {"name": "coord", "path": "$.coord"},
    {"name": "temp", "path": "$.main.temp"},
    {"name": "wind_speed", "path": "$.wind.speed"}
]

CONFIG_APIKEY = ''

def loadConfig():
    global CONFIG_APIKEY
    try:
        parser = ConfigParser()
        parser.read('config.ini')
        #load API Key from config file 
        CONFIG_APIKEY = parser.get('DEFAULT','API_KEY')    
    except:
        print("Can't load config file")
    
#Start Server
if __name__ == '__main__':
    try:
        loadConfig()        
    except:
        print("Server can't start")
