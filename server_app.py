from configparser import ConfigParser
import requests
import objectpath

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
 
def get_weather(apiKey, city, state):

    #get data from openweathermap API
    url= "https://api.openweathermap.org/data/2.5/weather?q={},{}&units=metric&appid={}".format(city, state, apiKey)   
    r=requests.get(url)        

    #convert respone to json
    z= r.json()

    #init search tree
    jsonnn_tree = objectpath.Tree(z)
    
    #init empty dictionary 
    data = {}

    #filter get only required data
    for d in CONFIG_REQUIRED_DATA:
        data[d["name"]] = jsonnn_tree.execute(d["path"])
            
    #return required data in Json format
    return (data)    
    
#Start Server
if __name__ == '__main__':
    try:
        loadConfig()        
    except:
        print("Server can't start")
