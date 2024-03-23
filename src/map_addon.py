import requests
import pandas as pd
import numpy as np
import json 
import sqlite3
import os


table = """ CREATE TABLE maps (
            client_id VARCHAR(255) NOT NULL,
            city VARCHAR(255) NOT NULL,
            country VARCHAR(255) NOT NULL,
            hostname VARCHAR(255) NOT NULL,
            ip VARCHAR(255) NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            org VARCHAR(255) NOT NULL,
            postal INT NOT NULL,
            region VARCHAR(255) NOT NULL,
            requests INT NOT NULL,
            timezone VARCHAR(255) NOT NULL,
            referer VARCHAR(255)
        ); """



clients = {}
con = sqlite3.connect('maps.db')
cursor = con.cursor()
system_host = os.popen('hostname -I | cut -d " " -f1 ').read().strip('\n')
token = os.environ.get("API_TOKEN")

def client_connected(client):
    name = client.peername[0]
    if name not in clients:
        clients[name] = {}

def request(flow):
    host = flow.request.host
    if host == system_host:
        flow.request.headers["MITM-HOST"] = flow.client_conn.peername[0] 
        
    
def response(flow):
    host = flow.request.host
    client_name = flow.client_conn.peername[0]
    con = sqlite3.connect('maps.db')
    cursor = con.cursor()
    
    df = pd.read_sql(f"SELECT * FROM maps WHERE client_id='{client_name}' AND hostname='{host}' ", con)
    if (len(df) > 0):
        cursor.execute(f"UPDATE maps SET requests = requests+1 WHERE client_id='{client_name}' AND hostname='{host}'")
        con.commit()
    else:
        save(client_name, flow, con)

def save(client, flow, con):
    ip = flow.server_conn.peername[0]
    host = flow.request.host
    referer = flow.request.headers.get_all('referer')
    if len(referer) > 0:
        referer = referer[0]
    else:
        referer = None
    
    res = requests.get(f"https://ipinfo.io/{ip}/json?token={token}")
    if res.status_code != 200:
        print("ERROR getting IP info")
        print(res.content)
        return
    
    data = json.loads(res.content.decode())
    lat,long = data['loc'].split(',')
    locations = np.array([client, lat, long, data['ip'],data['region'], host,
                            data['city'], data['country'],
                            data['org'], data['postal'], data['timezone'], 1, referer])
    labels = ['client_id','latitude', 'longitude', 'ip', 'region', 'hostname', 'city', 'country', 'org', 'postal', 'timezone', 'requests', 'referer']
    data = pd.DataFrame(data=[locations], columns=labels)
    data.to_sql('maps',con, if_exists='append',index=False)


def done():
    print("DONE")
