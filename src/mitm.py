import asyncio
from mitmproxy import options
from mitmproxy.tools import dump
import requests, json
import sqlite3
import os
import logging
import pandas as pd
import numpy as np
from mitmproxy import ctx

logger = logging.getLogger()
logging.basicConfig(filename='mitmproxy.log', encoding='utf-8', level=logging.INFO)
class Map:
    def __init__(self):
        ctx.options.block_global = False 

        self.clients = {}
        self.con = sqlite3.connect('maps.db')
        self.cursor = self.con.cursor()
        self.system_host = os.popen('hostname -I | cut -d " " -f1 ').read().strip('\n')
        self.token = os.environ.get("API_TOKEN")

    def load(self, loader):
        loader.add_option(
            name="block_global",
            typespec=bool,
            default=False,
            help="Block global",
    )
        
    def client_connected(self, client):
        name = client.peername[0]
        if name not in self.clients:
            self.clients[name] = {}

    def request(self, flow):
        host = flow.request.host
        logger.info(f"Request TO: {host}")
        if host == self.system_host:
            flow.request.headers["MITM-HOST"] = flow.client_conn.peername[0] 
            
        
    def response(self, flow):
        host = flow.request.host
        client_name = flow.client_conn.peername[0]
        con = sqlite3.connect('maps.db')
        cursor = con.cursor()
        
        df = pd.read_sql(f"SELECT * FROM maps WHERE client_id='{client_name}' AND hostname='{host}' ", con)
        if (len(df) > 0):
            cursor.execute(f"UPDATE maps SET requests = requests+1 WHERE client_id='{client_name}' AND hostname='{host}'")
            con.commit()
        else:
            self.save(client_name, flow, con)

    def save(self, client, flow, con):
        ip = flow.server_conn.peername[0]
        host = flow.request.host
        referer = flow.request.headers.get_all('referer')
        if len(referer) > 0:
            referer = referer[0]
        else:
            referer = None
        
        res = requests.get(f"https://ipinfo.io/{ip}/json?token={self.token}")
        if res.status_code != 200:
            logger.error("ERROR getting IP info")
            logger.error(res.content)
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
        logger.info("DONE")

class Proxy:
    def __init__(self):
        pass

    async def start_proxy(self, host, port):
        opts = options.Options(listen_host=host, listen_port=port)

        master = dump.DumpMaster(
            opts,
            with_termlog=False,
            with_dumper=False,
        )
        master.addons.add(Map())
        
        await master.run()
        return master

if __name__ == "__main__":
    proxy = Proxy()
    asyncio.run(proxy.start_proxy('0.0.0.0', 8080))