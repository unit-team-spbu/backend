from nameko.web.handlers import http
from nameko_mongodb import MongoDatabase
from werkzeug.wrappers import Request
import json


class EventsDAS:
    # Vars

    name = "event_das"
    db = MongoDatabase()

    # Logic

    def _check_event_presence(self, event):
        """Checks whether event is present in collection of
        events

        Args:
            event (dict): plain event dictionary

        Returns:
            (bool, event): 1st argument tells whether event is
            present in the collection, second is event from the
            collection
        """
        meta = event["meta"]

        filter = {
            "$or": [
                {"meta.{}".format(key): meta[key] for key in meta}
            ]
        }

        in_collection_event = self.db["events"].find_one(filter)

        return in_collection_event is not None, in_collection_event

    # API

    @http("POST", "/events")
    def save_events(self, request: Request):
        """Saves a collection of events analyzing them on updates
        and theme tags. If event is already present in the system
        than we just try to update it, if not, then we send it
        to be analyzed on themes to acquire theme tags

        Args:
            request (Request): http request with events in body

        Returns:
            (int): Status Code
        """

        collection = self.db["events"]
        content = request.get_data(as_text=True)
        events = json.loads(content)

        new_events = []

        for event in events:
            is_present, in_collection_event = self._check_event_presence(event)

            print(
                "{}".format(is_present))

            if is_present:
                # TODO: check for changes between new and old document
                pass
            else:
                new_events.append(event)
                # TODO: send to Theme Analyzer and save analyzed event
                pass
        
        ids = []

        if len(new_events) > 0:
            ids = collection.insert_many(new_events).inserted_ids

        return (200, json.dumps([str(id) for id in ids]))
