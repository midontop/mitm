from mitmproxy.http import HTTPFlow
import logging

class BasePlugin:
    def __init__(self, logger) -> None:
        self.can_handle = self.can_handle
        self.request = self.request
        self.logger = logger


    def path_matcher(self, path) -> bool:
        """
        This function must be overrided by the plugin
        """
        return False

    def can_handle(self, flow: HTTPFlow) -> bool:
        return flow.request.host == 'www.miubackend.net' and self.path_matcher(flow.request.path)

    def request(self, flow: HTTPFlow) -> None:
        if not self.can_handle(flow):
            return