from nameko.web.handlers import http
from nameko.rpc import rpc
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

    def _process_events_save(self, events: dict) -> list:
        """Saves a collection of events analyzing them on updates
        and theme tags. If event is already present in the system
        than we just try to update it, if not, then we send it
        to be analyzed on themes to acquire theme tags

        Args:
            events (dict): events to be saved or analyzed

        Returns:
            list: stringed ObjectIds for saved events
        """
        collection = self.db["events"]

        new_events = []

        for event in events:
            is_present, saved_event = self._check_event_presence(event)

            print("{} is present".format(str(
                saved_event["_id"])) if is_present else "{} is not present".format(event["title"]))

            if is_present:
                # TODO: think if this update scheme is enough
                # we want to check most vulnerable for update information:
                # - location
                # - date
                # - online format
                # we compose update request

                update = dict()

                if event["location"] != saved_event["location"]:
                    update["location"] = event["location"]

                if event["startDate"] != saved_event["startDate"]:
                    update["startDate"] = event["startDate"]

                if event["endDate"] != saved_event["endDate"]:
                    update["endDate"] = event["endDate"]

                if event["isOnline"] != saved_event["isOnline"]:
                    update["isOnline"] = event["isOnline"]

                print("Update: {}".format(update))

                if len(update) > 0:
                    collection.update(
                        {"_id": saved_event["_id"]},
                        {"$set": update})
            else:
                new_events.append(event)

                # TODO: send to Theme Analyzer and save analyzed event
                # ! BLOCKED: no Event Theme Analyzer service present currently

        if len(new_events) > 0:
            collection.insert_many(new_events)

    # API

    @http("POST", "/events")
    def save_events_handler(self, request: Request):
        """Handler for _save_events() method

        Args:
            request (Request): http request with events in body

        Returns:
            (list): of ids (string ObjectId)
        """
        content = request.get_data(as_text=True)
        events = json.loads(content)

        self._process_events_save(events)

        return (201, "Success")

    @rpc
    def save_events(self, events):
        self._process_events_save(events)

        return
