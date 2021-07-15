from folium import Marker, Circle, Choropleth, GeoJson
from folium.plugins import HeatMap, MarkerCluster
from geopandas.tools import geocode
import geopandas as gpd
import urllib.request
import pandas as pd
import requests
import folium
import json
import matplotlib.pyplot as plt
from PIL import Image
import base64
import io
import time

import numpy as np






covid_stats = pd.read_json('https://www.mohfw.gov.in/data/datanew.json')
states = gpd.read_file('indian_state_locations/indian_states.shp')


state_capitals = {
'Andhra Pradesh'        :'Amaravati',
'Arunachal Pradesh'            :     'Itanagar',
'Assam'                 :   'Dispur',
'Bihar'                 :   'Patna',
'Chhattisgarh'          :   'Raipur',
'Goa'                   :   'Panaji'          ,
'Gujarat'               :   'Gandhinagar',
'Haryana'               :   'Chandigarh',
'Himachal Pradesh'             :   'Shimla',
'Jharkhand'             :   'Ranchi',
'Karnataka'             :   'Bengaluru',
'Kerala'                :   'Thiruvananthapuram',
'Madhya Pradesh'        :   'Bhopal',
'Maharashtra'           :   'Mumbai',
'Manipur'               :   'Imphal',
'Meghalaya'             :   'Shillong',
'Mizoram'               :   'Aizawl',
'Nagaland'              :   'Kohima',
'Odisha'                :   'Bhubaneswar',
'Punjab'                :   'Chandigarh',
'Rajasthan'             :   'Jaipur',
'Sikkim'                :   'Gangtok',
'Tamil Nadu'            :   'Chennai',
'Telangana'             :   'Hyderabad',
'Tripura'               :   'Agartala',
'Uttar Pradesh'         :   'Lucknow',
'Uttarakhand'           :   'Dehradun',
'West Bengal'           :   'Kolkata'
}


#only for airports covered in the training dataset
city_to_state = {
    'Chennai' : 'Tamil Nadu',
    'Mumbai' : 'Maharashtra',
    'Cochin' : 'Kerala',
    'Hyderabad' : 'Telangana',
    'Kolkata' : 'West Bengal',
    'Delhi':'Delhi',
    'New Delhi':'Delhi'
}

#Reaging daily feed from MOHFW website
df = pd.read_json('https://www.mohfw.gov.in/data/datanew.json')
df = df.set_index('state_name',drop = False)
total_states = np.arange(len(df['state_name']))



def plot_statewise(state):
    plt.figure()
    df[df['state_name'] == state].plot.barh(stacked=False,align = 'center',figsize=(5, 5))
    plt.title("Covid statistics of "+state)
    plt.savefig('./static/img/statwise_' + state + '.jpg')


#plots particular feature of al states
def plot_feature(feature):
    plt.figure(num=None, figsize=(9, 6), dpi=80, facecolor='w', edgecolor='k')
    plt.barh(total_states, df[feature], alpha=0.5,align = 'center',
             color=(1, 0, 0),
             edgecolor=(0.5, 0.2, 0.8))

    plt.yticks(total_states, df['state_name'])
    plt.xlim(1, max(df['positive']) + 100)
    plt.xlabel('Positive Number of Cases')
    plt.title('Corona Virus Cases')
    plt.savefig('./static/img/all_states_'+feature+'.jpg')

#plots covid statistics of all states
def plot_all():
    plt.figure()
    df.plot.barh(stacked=True, figsize=(10, 10),align = 'center')
    plt.title("Covid statistics of all states in terms of number of cases")
    plt.savefig('./static/img/all_states_all_features.jpg')
    

#api key from AccuWeather developers account
api_key = "pX0Qaueg9sAejtsWAZAv5tfntOOG7QCC"
country_code = 'IN'


#location keys stored for every state excluding Delhi
loc_keys = json.load( open( "state_capital_loc_keys.json" ))
Delhi_loc_key = '202396'
Delhi_coordinates = [28.6517, 77.2219]




#geoencoding to download coordinates of input location
def geo_locator(row):
    try:
        point = geocode(row, provider = 'nominatim').geometry.iloc[0]
        return pd.Series({'Latitude':point.y,'Longitude':point.x, 'geometry':point})
    except:
        return None

#Accuweather location API
def getLocation(country_code, city):
    search_address = "http://dataservice.accuweather.com/locations/v1/cities/"+country_code+"/search?apikey=pX0Qaueg9sAejtsWAZAv5tfntOOG7QCC&q="+city+"&details=true&offset=0"
    #print(search_address)
    with urllib.request.urlopen(search_address) as search_address:
        data = json.loads(search_address.read().decode())
    #print(data)
    location_key = data[0]['Key']
    return location_key

#Accuweather Forecast API
def getForeCast(location_key):
    try:
        daily_forecastURL = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + location_key +"?apikey=pX0Qaueg9sAejtsWAZAv5tfntOOG7QCC&details=true"
        print(daily_forecastURL)
        with urllib.request.urlopen(daily_forecastURL) as search_address:
            data = json.loads(search_address.read().decode())
    except:
        data = "503"
    #print(data)
    return data


#function to return map with source and destination states being marked as well as their covid stats saved in static img folder
def weather_report_m(airport_cities):
    colors = ['crimson','green']
    itr = 0
    reports = []
    m = folium.Map(location=[25.644, 85.9065], tiles='openstreetmap', zoom_start=5)
    for city in airport_cities:
        itr+=1
        if city == 'Delhi' or city == 'New Delhi':
            key = Delhi_loc_key
        else:
            if city not in state_capitals.values() :
                cap = state_capitals[city_to_state[city]]
                key = loc_keys[cap]
            else:
                #When city is already a capital and hence has it's loc key registered
                key = loc_keys[city]
        forecast = getForeCast(key)

        #extracting useful information from forecast json object
        if(forecast != "503"):
            windspeed = forecast['DailyForecasts'][1]['Day']['Wind']['Speed']['Value']
            thunderstorm_prob = forecast['DailyForecasts'][1]['Day']['ThunderstormProbability']
            rain_prob = forecast['DailyForecasts'][1]['Day']['RainProbability']
            desc = forecast['DailyForecasts'][1]['Day']['ShortPhrase']
            report = {'windspeed': windspeed, 'thunderstorm_prob': thunderstorm_prob,
                      'rain_prob': rain_prob,
                      'desc': desc}
        else:
            report ={'error': "Max daily request limit exceeded for Weather API, please try later"}
        if city == 'Delhi' or city == 'New Delhi':
            covid_sheet = covid_stats.loc[covid_stats['state_name'] == "Delhi"]
            Marker(Delhi_coordinates, popup="Delhi",
                   tooltip='Click').add_to(m)
            Circle(location=(Delhi_coordinates[0], Delhi_coordinates[1]),color=colors[itr%2],
                    fill=True,
                    fill_color = colors[itr%2], radius=150000,
                   popup="Delhi").add_to(m)
        else:
            covid_sheet = covid_stats.loc[covid_stats['state_name'] == city_to_state[city]]
            loc_sheet = states.loc[states['state_name'] == city_to_state[city]]

            Marker([loc_sheet['Latitude'], loc_sheet['Longitude']], popup=loc_sheet['state_name'],
               tooltip='Click').add_to(m)
            Circle(location=(loc_sheet['Latitude'], loc_sheet['Longitude']),color=colors[itr%2],
                    fill=True,
                    fill_color=colors[itr%2],  radius=150000, popup=loc_sheet['state_name'],tooltip=loc_sheet['state_name']).add_to(m)

        #plots and saves covid stats of source and destination
        plot_statewise(city_to_state[city])

        # print(user_input_state+" "+ "forecast : ",desc, windspeed, thunderstorm_prob, rain_prob, desc)
        reports.append(report)
    return m, reports


#returns folium map along with weather report of a single state
def weather_report_s(user_input_state):

    if user_input_state == "Delhi":
        key = Delhi_loc_key
    else:
        cap = state_capitals[user_input_state]
        key = loc_keys[cap]
    forecast = getForeCast(key)

    #extract useful information from the forecast json object
    if(forecast != "503"):
        windspeed = forecast['DailyForecasts'][1]['Day']['Wind']['Speed']['Value']
        thunderstorm_prob = forecast['DailyForecasts'][1]['Day']['ThunderstormProbability']
        rain_prob = forecast['DailyForecasts'][1]['Day']['RainProbability']
        desc = forecast['DailyForecasts'][1]['Day']['ShortPhrase']
        report = {'windspeed': windspeed, 'thunderstorm_prob': thunderstorm_prob,
                  'rain_prob': rain_prob,
                  'desc': desc}

    else:
        report = {'error': "Max daily request limit exceeded for Weather API, please try later"}
    #special case for Delhi
    if user_input_state == 'Delhi':
        covid_sheet = covid_stats.loc[covid_stats['state_name'] == "Delhi"]

        m = folium.Map(location=Delhi_coordinates, tiles='openstreetmap', zoom_start=5)

        Marker(Delhi_coordinates, popup="Delhi",
               tooltip='Click').add_to(m)
        Circle(location=(Delhi_coordinates[0], Delhi_coordinates[1]),color='crimson',
                    fill=True,
                    fill_color='crimson',  radius=150000,
               popup="Delhi").add_to(m)

    else:
        covid_sheet = covid_stats.loc[covid_stats['state_name'] == user_input_state]

        loc_sheet = states.loc[states['state_name'] == user_input_state]

        m = folium.Map(location=[loc_sheet['Latitude'], loc_sheet['Longitude']], tiles='openstreetmap', zoom_start=5)

        Marker([loc_sheet['Latitude'], loc_sheet['Longitude']], popup="<a href='google.com'>" + cap + "</a>",
                   tooltip='Click').add_to(m)
        Circle(location=(loc_sheet['Latitude'], loc_sheet['Longitude']),color='crimson',
      fill=True,
      fill_color='crimson', radius=150000, popup=loc_sheet['state_name'],tooltip=loc_sheet['state_name']).add_to(m)


    plot_statewise(user_input_state)
    # print(user_input_state+" "+ "forecast : ",desc, windspeed, thunderstorm_prob, rain_prob, desc)
    return m, report


def show_all_states_covid():
    m = folium.Map(location = [25.644, 85.9065], tiles = 'openstreetmap', zoom_start = 5)

    # mc = MarkerCluster()
    for idx, row in states.iterrows():
        Marker(location = [row['Latitude'], row['Longitude']], popup = row['state_name']).add_to(m)
        Circle(location = [row['Latitude'], row['Longitude']],color='crimson',
                    fill=True,
                    fill_color='crimson',radius = 150000, popup = row['state_name'], tooltip = row['state_name']).add_to(m)
    # mc.add_to(m)
    return m


#encodes the image file into bytes
def encode_image_by_state(state):
    im = Image.open("./static/img/statwise_" + state+".jpg")
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return encoded_img_data

#encodes the image file into bytes
def encode_image_by_city(city):
    state = city_to_state[city]
    im = Image.open("./static/img/statwise_" +state+".jpg")
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return encoded_img_data









