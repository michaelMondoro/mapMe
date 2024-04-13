import asyncio
from mitmproxy import options, http
from mitmproxy.tools import dump
import requests, json
import sqlite3
import redis
import os
import logging
from mitmproxy import ctx

logger = logging.getLogger()
logging.basicConfig(filename='mitmproxy.log', 
                    format="%(asctime)s [%(levelname)-8s] %(message)s", 
                    datefmt="%Y-%m-%d %H:%M",
                    level=logging.INFO)

class Map:
    def __init__(self):
        ctx.options.block_global = False 
        self.cache = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.system_host = os.environ.get("HOST_IP")
        self.token = os.environ.get("API_TOKEN")
    
    def load(self, loader):
        loader.add_option(
            name="block_global",
            typespec=bool,
            default=False,
            help="Block global",
    )
        
    def client_connected(self, client) -> None:
        name = client.peername[0]

    def request(self, flow: http.HTTPFlow) -> None:
        host = flow.request.host
        logger.info(f"Request TO: {host}")
        if host == self.system_host:
            flow.request.headers["MITM-HOST"] = flow.client_conn.peername[0] 

    def response(self, flow: http.HTTPFlow) -> None:
        host = flow.request.host
        
        client_name = flow.client_conn.peername[0]

        # update user in cache
        user = self.cache.hgetall(f"user:id_{client_name}")
        logger.info(f"Request from USER: {client_name}")
        if user:
            if user['live'] == 'true':
                logger.info(f"CACHE HIT: user [ {client_name} ]")
                logger.info(f"User is live - will update")
                if host in user.keys():
                    user[host] = int(user[host]) + 1
                    self.cache.hset(f"user:id_{client_name}", mapping=user)
                else:
                    logger.info(f"ADDING NEW HOST {host}")
                    user[host] = 1
                    self.cache.hset(f"user:id_{client_name}", mapping=user)
            else:
                logger.info(f"User is not live - checking for configuration ping")
                if flow.request.path == "/poll" and proxy_ip in flow.request.host:
                    logger.info(f"Initial ping detected - forwarding request")
                elif flow.request.host == "mitm.it":
                    logger.info(f"mitm.it ping detected - forwarding request")
                else:
                    if proxy_ip not in flow.request.host:
                        logger.error(f"User [{client_name}] session not live - dropping request")
                        flow.kill()
                        return
        else:
            if proxy_ip not in flow.request.host:
                logger.error(f"User does not exist - dropping request")
                flow.kill()
                return
        
        # Update server in cache
        cached_host = self.cache.hgetall(f"server:{host}")
        if cached_host:
            logger.info(f"CACHE HIT: server [ {host} ]")
        else:
            self.save(flow)

    def save(self, flow: http.HTTPFlow) -> None:
        print(f"server_conn: {flow.request.host}")
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
        if 'anycast' in data.keys(): data.pop('anycast')

        data['hostname'] = host
        if referer: 
            data['referer'] = referer 
        else: 
            data['referer'] = ""
        logger.info(f"DATA: {data}")
        self.cache.hset(f"server:{host}", mapping=data)
        logger.info(f"SAVED new host: {host}")


    def done() -> None:
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
    proxy_ip = os.environ.get("HOST_IP")
    if not proxy_ip:
        print("Please set 'HOST_IP' environment variable")
        exit(1)

    if not os.environ.get("API_TOKEN"):
        print("Please set 'API_TOKEN' environment variable")
        exit(1)
    proxy = Proxy()
    asyncio.run(proxy.start_proxy('0.0.0.0', 8080))