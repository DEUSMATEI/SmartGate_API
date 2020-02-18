from flask import Flask
from flask_restful import Resource, Api, reqparse
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


#configure parameters
parser = reqparse.RequestParser()
parser.add_argument('city', type=str, required=True)
parser.add_argument('state', type=str, required=True)

app = Flask(__name__)
api= Api(app)

@app.before_first_request
def loadConfig():
    global CONFIG_APIKEY
    try:
        parser = ConfigParser()
        parser.read('config.ini')
        #load API Key from config file 
        CONFIG_APIKEY = parser.get('DEFAULT','API_KEY')    
    except:
        print("Can't load config file")
 
@app.after_request 
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = 'https://ui-weather.herokuapp.com'
    return response

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

class Weather(Resource):
    def get(self):
        #get city and state from arg
        args = parser.parse_args()
        city = args['city']
        state = args['state']       

        #return required data for given city 
        return get_weather(CONFIG_APIKEY, city, state)


api.add_resource(Weather, '/weather')

#Start Server
if __name__ == '__main__':
    try:         
        app.run(port='5001', debug=True)        
    except:
        print("Server can't start")
