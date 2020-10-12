from nameko.rpc import rpc
from nameko.rpc import RpcProxy
from nameko.timer import timer
from nameko.web.handlers import http
import config as cfg


class REC:
    """Microservice for requesting events from every crawler"""
    name = "raw_events_collector"
    crawlers_rpc = list()
    
    def update_crawlers(self):
        """Updating crawlers list"""
        self.crawlers_rpc = list()
        for crawler in cfg.CRAWLERS:
            self.crawlers_rpc.append(RpcProxy(crawler))

    @timer(interval=cfg.TIMER)
    def update(self):
        """Requests crawlers for events
        :returns a batch with all events"""
        self.update_crawlers()
        events = list()
        get_res = list()

        # requesting events from each crawler
        for ev_rpc in self.crawlers_rpc:
            get_res.append(ev_rpc.get_upcoming_events.call_async())

        # getting results
        for res in get_res:
            events += res.result()

        # TODO: Pass events to the next service 
        return events

    @http('GET', '/events')
    def force_update(self):
        return self.update()
