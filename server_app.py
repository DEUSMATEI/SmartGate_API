from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask import abort
from configparser import ConfigParser
import requests
import objectpath

# CONFIG Required Data
#   "Name": Data key in response Json
#   "path": Path to data in response form OpenWeatherMap
CONFIG_REQUIRED_DATA = [
    {"name": "coord", "path": "$.coord"},
    {"name": "temp", "path": "$.main.temp"},
    {"name": "wind_speed", "path": "$.wind.speed"}
]

#Store API Key during runtime
CONFIG_APIKEY = ''
#Store Acces control allow origin
CONFIG_ACC_CONTROL_ALLOW_ORIGIN = ''

# Configure path parameters
parser = reqparse.RequestParser()
parser.add_argument('city', type=str, required=True)
parser.add_argument('state', type=str, required=True)

app = Flask(__name__)
api= Api(app)

@app.before_first_request
def loadConfig():
    global CONFIG_APIKEY
    global CONFIG_ACC_CONTROL_ALLOW_ORIGIN
    try:
        parser = ConfigParser()
        parser.read('config.ini')
        #load API Key from config file 
        CONFIG_APIKEY = parser.get('DEFAULT','API_KEY')
        #load allowed origin
        CONFIG_ACC_CONTROL_ALLOW_ORIGIN = parser.get('DEFAULT','ACC_CONTROL_ALLOW_ORIGIN')    
    except:        
        abort(500)
 
#
# after_request(response)
#
# Takes one arg:
#   -> response: API response
#
# This function is executed after every request
# and add data in response header
#
# Returns:
#   Response with updated header
#
@app.after_request 
def after_request(response):    
    global CONFIG_ACC_CONTROL_ALLOW_ORIGIN
    #Check if allowed origin is configured
    if CONFIG_ACC_CONTROL_ALLOW_ORIGIN == '':
        abort(500)        

    header = response.headers
    #Allow API use only from a configured location
    header['Access-Control-Allow-Origin'] = CONFIG_ACC_CONTROL_ALLOW_ORIGIN
    return response

# get_weather(apiKey, city, state)
#
# Takes 3 args:
#   -> apiKey: Api key for OpenWeatherMap
#   -> city: city name
#   -> state: state name
#
# This function call openWeatherMap API to get current weather data for provided city
# then filter result data according to CONFIG_REQUIRED_DATA. If Api Key is loaded
# and API response is ok filtered data is returned otherwise abort with code 500 (Internal error)
# or code 404 (Bad request)
# 
# Return:
#   Required data in Json format
#
def get_weather(apiKey, city, state):
    #Check if apiKey is loaded
    if apiKey =='':
        abort(500)

    #Get data from openweathermap API
    url= "https://api.openweathermap.org/data/2.5/weather?q={},{}&units=metric&appid={}".format(city, state, apiKey)   
    r=requests.get(url)        

    #Convert respone to json
    z= r.json()    
    
    #Check if API response is OK
    if z['cod'] != 200:
        abort(404)

    #Init search tree
    jsonnn_tree = objectpath.Tree(z)
    
    #Init empty dictionary 
    data = {}

    #Filter return data, get only required data
    for d in CONFIG_REQUIRED_DATA:
        data[d["name"]] = jsonnn_tree.execute(d["path"])
            
    #Return required data in Json format
    return (data)    

class Weather(Resource):
    def get(self):
        #get city and state from arg
        args = parser.parse_args()
        city = args['city']
        state = args['state']       

        #Check if provided args are ok
        if city == "" or state == "":
            abort(400)
        
        #return required data for given city 
        return get_weather(CONFIG_APIKEY, city, state)

#Add path to api
api.add_resource(Weather, '/weather')

#Start Server only if is executed in __main__
if __name__ == '__main__':
    try:        
        app.run(port='5001', debug=True)        
    except:
        print("Server can't start")
