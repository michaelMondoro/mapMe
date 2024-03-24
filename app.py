from flask import Flask
from flask import render_template, request, jsonify
import pandas as pd
import sqlite3
import geopandas
import os 
import requests, json
from src.db import *

app = Flask(__name__)
app.config['HOSTNAME'] = os.environ.get("HOSTNAME")
host_ip = os.environ.get("HOST_IP")
token = os.environ.get("API_TOKEN")

def check_mitm_header(request):
    if request.headers.get('MITM-HOST'):
        client = request.headers['MITM-HOST']
        print(f"MITM: {client}")
    else:
        client = request.remote_addr
        print(f"NORMAL: {client}")
    return client

@app.route("/")
def home():
    
    return render_template('index.html', 
                           client=request.remote_addr, 
                           host=app.config['HOSTNAME'], 
                           rendered=False)

@app.route("/update")
def update():
    client = check_mitm_header(request)

    con = sqlite3.connect('maps.db')
    data = pd.read_sql(f"select * from maps where client_id='{client}'",con)

    points = geopandas.points_from_xy(x=data.longitude, y=data.latitude)
    gdf = geopandas.GeoDataFrame(data, geometry=points)
    
    cols = data.columns.tolist()
    rows = []
    for i in range(len(data)):
        rows.append(data.loc[i,:].to_dict())
    
    direct_hosts = data.loc[(data['referer'].isna())]['hostname'].values.tolist()
    hosts = data.sort_values('requests',ascending=False)['hostname'].tolist()
    servers = set(data.sort_values('requests',ascending=False)['ip'].tolist())

    response = jsonify({
        "geo":gdf.to_json(),
        "hosts": hosts,
        "direct_hosts": direct_hosts,
        "servers": list(servers),
        "columns": cols,
        "rows": rows
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 

@app.route("/clear_session", methods=["POST"])
def clear_session():
    con = sqlite3.connect('maps.db')
    client = check_mitm_header(request)
    cursor = con.cursor()
    print(client)
    cursor.execute(f"DELETE FROM maps WHERE client_id='{client}'")
    con.commit()
    return ""

if __name__ == "__main__":
    # proxy = subprocess.Popen(["python3", "mitm.py", "/dev/null"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    db = mongo_connect()
    if not db:
        print("Failed to connect to db . . . exiting . . .")
    app.run(host='0.0.0.0', port='5000', debug=True)
    
