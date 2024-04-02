import requests
import pandas as pd
import numpy as np
import json 
import os
import redis
import logging 

logger = logging.getLogger()
logging.basicConfig(filename='mitmproxy.log', encoding='utf-8', level=logging.INFO)


clients = {}
system_host = os.popen('hostname -I | cut -d " " -f1 ').read().strip('\n')
token = os.environ.get("API_TOKEN")
cache = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
def client_connected(self, client):
    name = client.peername[0]
    if name not in clients:
        clients[name] = {}

def request(self, flow):
    host = flow.request.host
    logger.info(f"Request TO: {host}")
    if host == system_host:
        flow.request.headers["MITM-HOST"] = flow.client_conn.peername[0] 
        
    
def response(self, flow):
    host = flow.request.host
    client_name = flow.client_conn.peername[0]

    # update user in cache
    user = cache.hgetall(f"user:id_{client_name}")
    logger.info(f"Request from USER: {client_name}")
    if user and user['live'] == 'true':
        logger.info(f"CACHE HIT: user [ {client_name} ]")
        logger.info(f"User is live - will update")
        if host in user.keys():
            user[host] = int(user[host]) + 1
            cache.hset(f"user:id_{client_name}", mapping=user)
        else:
            logger.info(f"ADDING NEW HOST {host}")
            user[host] = 1
            cache.hset(f"user:id_{client_name}", mapping=user)
    else:
        logger.info(f"User is NOT live or does not exist - will NOT update")
        flow.kill()
        return
    
    # Update server in cache
    cached_host = cache.hgetall(f"server:{host}")
    if cached_host:
        logger.info(f"CACHE HIT: server [ {host} ]")
        # cached_host['requests'] = int(cached_host['requests']) + 1
        # cache.hset(f"server:{host}", mapping=cached_host)
    else:
        save(flow)

    

def save(self, flow):
    ip = flow.server_conn.peername[0]
    host = flow.request.host
    referer = flow.request.headers.get_all('referer')
    if len(referer) > 0:
        referer = referer[0]
    else:
        referer = None
    
    res = requests.get(f"https://ipinfo.io/{ip}/json?token={token}")
    if res.status_code != 200:
        logger.error("ERROR getting IP info")
        logger.error(res.content)
        return
    
    data = json.loads(res.content.decode())
    if 'anycast' in data.keys(): data.pop('anycast')

    data['hostname'] = host
    if referer: 
        data['referer'] = referer 
    else: 
        data['referer'] = ""
    logger.info(f"DATA: {data}")
    cache.hset(f"server:{host}", mapping=data)
    logger.info(f"SAVED new host: {host}")


def done():
    logger.info("DONE")
