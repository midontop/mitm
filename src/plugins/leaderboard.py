import json
from mitmproxy.http import HTTPFlow, Response
from base import BasePlugin
from datetime import datetime, timedelta, timezone
import importlib
import config
class plugin(BasePlugin): 
    def __init__(self, logger) -> None:
        super().__init__(logger)

    def path_matcher(self, path):
        return "SPLeaderboard_Ultra" in path

    def request(self, flow: HTTPFlow):
        if not super().can_handle(flow):
            return
        self.logger.debug(f'Handling request: {flow.request.method} {flow.request.path}')
        if not flow.request.data.content:
            return
        if json.loads(flow.request.data.content.decode())["_noBody"] == False and config.offline_normal:
            # do not forward SPLeaderboard_Ultra requests
            self.logger.debug(f'Ignoring SPLeaderboard_Ultra request')
            flow.kill()