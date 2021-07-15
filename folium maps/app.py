import folium
import json
import os
from flask import Flask, render_template,request


with open('templates/config.json','r') as c:
    params =json.load(c)["params"]
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    start_coords = (46.9540700, 142.7360300)
    folium_map = folium.Map(location = start_coords, zoom_start = 14)
    return  render_template("index.html",param = folium_map._repr_html_())

if __name__ == "__main__":
    app.run(debug=True)