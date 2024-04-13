from flask import Flask
from flask import render_template, request, jsonify
import pandas as pd
import sqlite3
import geopandas
import os 
import redis

app = Flask(__name__)
app.config['HOSTNAME'] = os.environ.get("HOSTNAME")
host_ip = os.environ.get("HOST_IP")
token = os.environ.get("API_TOKEN")
if not host_ip: 
    print("Set 'HOST_IP' env variable") 
    exit(1)
if not app.config['HOSTNAME']:
    print("Set 'HOSTNAME' env variable") 
    exit(1)
if not token:
    print("Set 'API_TOKEN' env variable") 
    exit(1)

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

@app.route("/error")
def error():
    return render_template('error.html',host=host_ip)

@app.route("/poll", methods=["POST"])
def poll_user():
    if request.remote_addr != host_ip:
        print(f"user is not connected to the proxy")
        print(f"IP {request.remote_addr} != {host_ip}")
        return "false"

    client = check_mitm_header(request)
    user_data = cache.hgetall(f"user:id_{client}")
    # TODO: need to add some way of verifying cert - not just traffic coming from proxy
    if user_data:
        print(f"User [{client}] exists - setting status")
        user_data['connected'] = 'true'
        user_data['live'] = 'true'
        cache.hset(f"user:id_{client}", mapping=user_data)
        return "true"
    else:
        print(f"User [{client}] does not exist")
        return "false"

@app.route("/update")
def update():
    client = check_mitm_header(request)
    user_data = cache.hgetall(f"user:id_{client}")
    print(user_data)
    data = get_results(user_data)
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

@app.route("/stop_session", methods=["POST"])
def stop_session():
    client = check_mitm_header(request)
    user = cache.hgetall(f"user:id_{client}")
    if not user:
        print(f"No such user [{client}]")
        return "false"
    
    user['live'] = 'false'
    cache.hset(f"user:id_{client}", mapping=user)
    print(f"Stopped session for user: [ {client} ]")

    data = get_results(user)
    print(data)
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
    return render_template('index.html', 
                           client=request.remote_addr, 
                           host=app.config['HOSTNAME'], 
                           rendered=True)

@app.route("/start_session", methods=["POST"])
def start_session():
    client = check_mitm_header(request)
    user = cache.hgetall(f"user:id_{client}")
    if not user:
        cache.hset(f"user:id_{client}", mapping={'live':'false','connected':'false'})
        cache.expire(f"user:id_{client}", 600)
        print(f"Created entry for user: [ {client} ]")
    else:
        print(f"User [{client}] already exists")
    return "success"


def get_results(user_data:dict) -> dict:
    for key in user_data:
        if key != "live" and key != "connected":
            request_count = user_data[key]




if __name__ == "__main__":
    # proxy = subprocess.Popen(["python3", "mitm.py", "/dev/null"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

    app.run(host='0.0.0.0', port='5000', debug=True)
    
