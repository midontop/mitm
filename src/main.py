#!/bin/env python
import asyncio
import sys
from mitmproxy import http
from mitmproxy import options
from mitmproxy.tools import dump
import logging
import os
import inspect
import importlib

logger = logging.Logger('midontop/mitm', level=logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class FunnyLogger:
    def request(self, flow: http.HTTPFlow):
        if not flow.request.url.startswith("https://www.miubackend.net"):
            return
        
        if flow.request:
            logger.info(f'Request: {flow.request.method} {flow.request.pretty_url}\n\n{flow.request.headers}\n\n{flow.request.content}')

    def response(self,flow: http.HTTPFlow):
        if not flow.request.url.startswith("https://www.miubackend.net"):
            return
        if flow.response:
            logger.info(f'Response to {flow.request.method} {flow.request.pretty_url}\n\n{flow.response.headers}\n\n{flow.response.content}')

    def error(self, flow: http.HTTPFlow):
        if not flow.request.url.startswith("https://www.miubackend.net"):
            return
        if flow.error:
            logger.error(f'Error: {flow.error.msg}')
        

async def start_proxy(host, port):
    opts = options.Options(listen_host=host, listen_port=port)
    master = dump.DumpMaster(
        opts,
        with_termlog=False,
        with_dumper=False,
    )
    for plugin in os.listdir('plugins'):
        if plugin.endswith('.py'):
            plugin = plugin[:-3]
            try:
                plugin_module = importlib.import_module(f'plugins.{plugin}')
                if not hasattr(plugin_module, 'plugin'):
                    logger.error(f'Failed to load plugin {plugin}: invalid plugin')
                    continue
                master.addons.add(plugin_module.plugin(logger)) 
            except Exception as e:
                logger.error(f'Failed to load plugin {plugin}: {e}')
                continue
            logger.info(f'Loaded plugin {plugin}')
    master.addons.add(FunnyLogger())
    await master.run()
    return master

if __name__ == '__main__':
    if len(sys.argv) < 3:
        host = '127.0.0.1'
        port = 8080
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
    asyncio.run(start_proxy(host, port))