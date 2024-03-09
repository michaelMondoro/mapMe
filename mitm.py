import asyncio
from mitmproxy import options
from mitmproxy.tools import dump
from map import Map


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
    asyncio.run(proxy.start_proxy('127.0.0.1', 8080))