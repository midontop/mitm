from mitmproxy.http import HTTPFlow, Response
from base import BasePlugin
from datetime import datetime, timedelta, timezone
import importlib
import config
class WeeklyPlugin(BasePlugin):
    
    def __init__(self, logger) -> None:
        super().__init__(logger)
        self.weekly = importlib.import_module("weekly." + config.weekly if config.weekly != "online" else "weekly.airwaves") # Airwaves is a placeholder
        if config.weekly == "online":
            self.logger.debug(f'Not loading weekly')
        else:
            self.logger.debug(f'Loaded weekly {self.weekly.name}')

    def path_matcher(self, path):
        return "/parse/classes/ChallengeStats_Mayhem?where=%7B%22LevelID%22%3A%22CHALLENGE_DATA%22%7D" in path or "LBChallengeStats_Mayhem" in path # handles getting the CHALLENGE_DATA or POSTing to LBChallengeStats_Mayhem
    
    def replace_weekly(self, flow: HTTPFlow):
        self.logger.debug(f'Replacing weekly data on request {flow.request.path} with custom weekly {self.weekly.name}')
        weekly_data = self.weekly.weekly.replace("placeholder_date", ((datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0).isoformat() + "Z")).encode()
        flow.response = Response.make(200, weekly_data, {"content-type":"application/json"})

    def request(self, flow: HTTPFlow):
        if not super().can_handle(flow):
            return
        self.logger.debug(f'Handling request: {flow.request.method} {flow.request.path}')
        if "LBChallengeStats_Mayhem" in flow.request.path and flow.request.method == "POST" and config.offline_weekly:
            # do not forward LBChallengeStats_Mayhem requests
            self.logger.debug(f'Ignoring LBChallengeStats_Mayhem POST request')
            flow.kill()
        
        if "ChallengeStats_Mayhem" in flow.request.path and config.weekly != "online":
            self.replace_weekly(flow)

plugin = WeeklyPlugin