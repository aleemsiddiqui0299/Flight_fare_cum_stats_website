from folium import Marker, Circle, Choropleth, GeoJson
from folium.plugins import HeatMap, MarkerCluster
from geopandas.tools import geocode
import geopandas as gpd
import urllib.request
import pandas as pd
import requests
import folium
import json
import time





covid_stats = pd.read_json('https://www.mohfw.gov.in/data/datanew.json')
states = gpd.read_file('folium_maps/indian_states.shp')


#api key from AccuWeather developers account
api_key = "pX0Qaueg9sAejtsWAZAv5tfntOOG7QCC"
country_code = 'IN'

state_capitals = {
'Andhra Pradesh'    :'Amaravati',
'Arunachal ':   'Itanagar',
'Assam':   'Dispur',
'Bihar':   'Patna',
'Chhattisgarh':   'Raipur',
'Goa':   'Panaji'          ,
'Gujarat':   'Gandhinagar',
'Haryana':   'Chandigarh',
'Himachal ':   'Shimla',
'Jharkhand':   'Ranchi',
'Karnataka':   'Bengaluru',
'Kerala':   'Thiruvananthapuram',
'Madhya Pradesh':   'Bhopal',
'Maharashtra':   'Mumbai',
'Manipur':   'Imphal',
'Meghalaya':   'Shillong',
'Mizoram':   'Aizawl',
'Nagaland':   'Kohima',
'Odisha':   'Bhubaneswar',
'Punjab':   'Chandigarh',
'Rajasthan':   'Jaipur',
'Sikkim':   'Gangtok',
'Tamil Nadu':   'Chennai',
'Telangana':   'Hyderabad',
'Tripura':   'Agartala',
'Uttar Pradesh':   'Lucknow',
'Uttarakhand':   'Dehradun',
'West Bengal':   'Kolkata'
}

loc_keys = json.load( open( "state_capital_loc_keys/.json" ))


def geo_locator(row):
    try:
        point = geocode(row, provider = 'nominatim').geometry.iloc[0]
        return pd.Series({'Latitude':point.y,'Longitude':point.x, 'geometry':point})
    except:
        return None

def getLocation(country_code, city):
    search_address = "http://dataservice.accuweather.com/locations/v1/cities/"+country_code+"/search?apikey=pX0Qaueg9sAejtsWAZAv5tfntOOG7QCC&q="+city+"&details=true&offset=0"
    #print(search_address)
    with urllib.request.urlopen(search_address) as search_address:
        data = json.loads(search_address.read().decode())
    #print(data)
    location_key = data[0]['Key']
    return location_key

def getForeCast(location_key):
    daily_forecastURL = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + location_key +"?apikey=pX0Qaueg9sAejtsWAZAv5tfntOOG7QCC&details=true"
    print(daily_forecastURL)
    with urllib.request.urlopen(daily_forecastURL) as search_address:
        data = json.loads(search_address.read().decode())
    #print(data)
    return data


def weather_report(state):
    user_input_state = 'Gujarat'

    cap = state_capitals[user_input_state]
    key = loc_keys[cap]
    forecast = getForeCast(key)

    windspeed = forecast['DailyForecasts'][1]['Day']['Wind']['Speed']['Value']
    thunderstorm_prob = forecast['DailyForecasts'][1]['Day']['ThunderstormProbability']
    rain_prob = forecast['DailyForecasts'][1]['Day']['RainProbability']
    desc = forecast['DailyForecasts'][1]['Day']['ShortPhrase']

    covid_sheet = covid_stats.loc[covid_stats['state_name'] == user_input_state]
    loc_sheet = states.loc[states['state_name'] == user_input_state]

    m = folium.Map(location=[loc_sheet['Latitude'], loc_sheet['Longitude']], tiles='openstreetmap', zoom_start=5)

    Marker([loc_sheet['Latitude'], loc_sheet['Longitude']], popup="<a href='google.com'>" + cap + "</a>",
           tooltip='Click').add_to(m)

    print(desc, windspeed, thunderstorm_prob, rain_prob, desc)
    return m





