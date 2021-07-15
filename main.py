from flask import Flask, render_template, request, url_for
from flask_cors import cross_origin
import folium
import json
import requests
import sklearn
import pickle
import pandas as pd
import sys
import os
from plot_maps import *
from cloud_db import *



with open('templates/config.json', 'r') as c:
    params = json.load(c)["params"]
local_server = params['local_server'];

model = pickle.load(open("flight_fare_model.pkl", "rb"))
PEOPLE_FOLDER = os.path.join('static', 'img')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER


@app.route('/',methods=['GET'])
@cross_origin()
def start():
    return render_template('home.html')


@app.route('/index',methods=['GET', 'POST'])
@cross_origin()
def home():
    return render_template('index.html')


@app.route("/predict", methods=['GET', 'POST'])
@cross_origin()
def predict():
    if request.method == "POST":
        date_dep = request.form["Dep_Time"]
        Journey_day = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").day)
        Journey_month = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").month)
        Journey_day_of_week = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").day_of_week)
        # Departure
        Dep_hour = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").hour)
        Dep_min = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").minute)

        # Arrival
        date_arr = request.form["Arrival_Time"]
        Arrival_hour = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").hour)
        Arrival_min = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").minute)

        # Duration
        dur_hour = abs(Arrival_hour - Dep_hour)
        dur_min = abs(Arrival_min - Dep_min)

        Total_stops = int(request.form["stops"])
        airline = request.form['airline']

        airline_cols = [0] * 11
        airline_dict = {'Air_India': 0,
                        'GoAir': 1,
                        'IndiGo': 2,
                        'Jet_Airways': 3,
                        'Jet_Airways_Business': 4,
                        'Multiple_carriers': 5,
                        'Multiple_carriers_Premium_economy': 6,
                        'SpiceJet': 7,
                        'Trujet': 8,
                        'Vistara': 9,
                        'Vistara_Premium_economy': 10}

        if (airline in airline_dict.keys()):
            airline_cols[airline_dict[airline]] = 1

        Source = request.form["Source"]
        Dest = request.form["Destination"]
        source_cols = [0, 0, 0, 0]
        dest_cols = [0, 0, 0, 0, 0]

        source_dict = {
            's_Chennai': 0,
            's_Delhi': 1,
            's_Kolkata': 2,
            's_Mumbai': 3
        }
        dest_dict = {
            'd_Cochin': 0,
            'd_Delhi': 1,
            'd_Hyderabad': 2,
            'd_Kolkata': 3,
            'd_New_Delhi': 4,
        }
        if (Source in source_dict.keys()):
            source_cols[Source] = 1
        if (Dest in dest_dict.keys()):
            dest_cols[Dest] = 1

        features = [[Total_stops,
                     Journey_day,
                     Journey_month,
                     Journey_day_of_week,
                     Dep_hour,
                     Dep_min,
                     Arrival_hour,
                     Arrival_min,
                     dur_hour,
                     dur_min] + airline_cols + source_cols + dest_cols]

        prediction = model.predict(features)
        output = round(prediction[0], 2)
        m, reports = weather_report_m([Source, Dest])
        if 'error' in reports[0].keys():
            temp1 = reports[0]['error']
        else:
            temp1 = """<ul>
                                    <li><b>Thundersorm Probability : """ + str(reports[0]['thunderstorm_prob']) + """</b></li>
                                    <li><b>Wind Speed : </u>""" + str(reports[0]['windspeed']) + """ mi/h</b></li>
                                    <li><b>Rain Probability : """ + str(reports[0]['rain_prob']) + """</b></li>
                                    <li><b>Shorty Summary : """ + str(reports[0]['desc']) + """</b></li>
                                </ul>"""
        if 'error' in reports[1].keys():
            temp2 = reports[1]['error']
        else:
            temp2 = """<ul>
                                            <li><b>Thundersorm Probability : """ + str(reports[1]['thunderstorm_prob']) + """</b></li>
                                            <li><b>Wind Speed : </u>""" + str(reports[1]['windspeed']) + """ mi/h</b></li>
                                            <li><b>Rain Probability : """ + str(reports[1]['rain_prob']) + """</b></li>
                                            <li><b>Shorty Summary : """ + str(reports[1]['desc']) + """</b></li>
                                        </ul>"""

        im1 = encode_image_by_city(Source)
        im2 = encode_image_by_city(Dest)
        return render_template('maps.html', prediction_text="Expected Flight price is {} INR".format(output), param=m._repr_html_(), r1=temp1,
                               r2 = temp2, a1= Source, a2 = Dest, im1=im1.decode('utf-8'), im2=im2.decode('utf-8'))

    return render_template('index/html')

@app.route('/')
@app.route('/maps2', methods = ['GET', 'POST'])
@cross_origin()
def state_stats():
    plot_all()
    if request.method == 'POST':
        state = request.form['state']
        print("Selected State = ", state)
        m, report= weather_report_s(state)
        if 'error' in report.keys():
            temp = report['error']
        else:
            temp = """<ul>
                            <li><b>Thundersorm Probability : """ +str(report['thunderstorm_prob'])  + """</b></li>
                            <li><b>Wind Speed : </u>""" +str(report['windspeed']) +  """ mi/h</b></li>
                            <li><b>Rain Probability : """ + str(report['rain_prob']) + """</b></li>
                            <li><b>Shorty Summary : """ + str(report['desc']) + """</b></li>
                        </ul>"""
        encoded_img_data = encode_image_by_state(state)
        # new_map = show_all_states_covid()
        # print(inp_state)
        return render_template('maps2.html', param=m._repr_html_(), report = temp, img_data = encoded_img_data.decode('utf-8'))

    encoded_img_data = encode_image_by_state("Andhra Pradesh")
    new_map = show_all_states_covid()
    return render_template('maps2.html', param=new_map._repr_html_(), report = "", img_data=encoded_img_data.decode('utf-8'))




@app.route('/about')
@cross_origin()
def about():
    return render_template('about.html')


@app.route('/contacts',methods=['GET','POST'])
@cross_origin()
def contact():
    query_status = "Details not posted"
    if (request.method == 'POST'):
        Name = request.form['Name']
        email = request.form['email']
        phno = request.form['contact']
        query_status = "Details Posted , database status: "+ add_entries(Name, phno, email) + "\n Do not hit refresh ."
        print(Name, email, phno)
    return render_template('contacts.html', ret_text = query_status)


app.run(debug=True)
