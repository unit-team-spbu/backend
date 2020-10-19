from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http
import string
import json


class PREH:
    """Microservice for events primary processing"""
    # Vars

    name = "primary_raw_events_handler"
    event_das_rpc = RpcProxy('event_das')

    # Logic

    def _eq_ev(self, ev1, ev2):
        """Determine whether events are equal by their title`
            :param ev1: the first event
                ev2: the second event
            :return bool value"""
        # Punctuation removal
        title1 = ev1['title'].translate(
            str.maketrans('', '', string.punctuation)).split()
        title2 = ev2['title'].translate(
            str.maketrans('', '', string.punctuation)).split()
        for title in [title1, title2]:
            for i in range(len(title)):
                title[i] = title[i].lower()

        return title1 == title2

    def _unduplicate(self, events):
        """Removes duplicates from different crawlers and 
            appends meta data for duplicate events"""

        for i in range(len(events)):
            erase_list = list()
            for j in range(i + 1, len(events)):
                if self._eq_ev(events[i], events[j]):
                    events[i]['meta'].update(events[j]['meta'])
                    erase_list.append(j)
            deleted = 0
            for ind in erase_list:
                events.pop(ind - deleted)
                deleted += 1
        return events

    def _clean_events(self, events):

        return list(map(lambda event: {
            "title": event["title"],
            "location": event["location"],
            "startDate": event["startDate"],
            "endDate": event["endDate"],
            "description": event["description"].replace("\n", ""),
            "meta": event["meta"],
            "tags": list(filter(None, [
                "online" if event["isOnline"] else None,
                event["type"].lower() if event["type"] else None,
                "paid" if event["isPaid"] else None
            ]))
        }, events))

    # API

    @rpc
    def receive_events(self, events):
        """Receiving events from REC 
        :param events: events got from REC service"""

        unique_events = self._unduplicate(events)
        clean_events = self._clean_events(unique_events)

        print(map(lambda x: x["tags"], clean_events))

        # try/finally allows us to ignore if this service doesn't exist
        # TODO: get rid of this dumb try/finally
        try:
            self.event_das_rpc.save_events(clean_events)
        finally:
            return clean_events

    @http("POST", "/process")
    def receive_events_handler(self, request):

        content = request.get_data(as_text=True)

        events = json.loads(content)

        unique_events = self._unduplicate(events)
        clean_events = self._clean_events(unique_events)

        print(map(lambda x: x["tags"], clean_events))

        # try/finally allows us to ignore if this service doesn't exist
        # TODO: get rid of this dumb try/finall
        try:
            self.event_das_rpc.save_events(clean_events)
        finally:
            return json.dumps(clean_events, ensure_ascii=False)
