from nameko.rpc import rpc
from nameko_redis import Redis
from nameko.web.handlers import http
from nameko.events import event_handler
import json


class Top_DAS:
    """Microservice for user's top events storage"""
    # Vars

    name = 'top_das'
    db = Redis('redis')

    # Logic

    # API

    @rpc
    def update_top(self, user, new_top):
        """Setting new top to the database
        :params:
            user - user login
            new_top - list of IDs [id1, id2, ..] of event top"""
        self.db.set(user, json.dumps(new_top))

    @rpc 
    def get_top(self, user):
        """Getting top events by user"""
        try:
            top = json.loads(self.db.get(user))
        except:
            top = []
        return top

    @http('POST', '/update')
    def update_top_handler(self, request):
        """Request:
            {
                "user": <user>,
                "top": [..]
            }
            """
        content = request.get_data(as_text=True)
        content = json.loads(content)
        user, new_top = content['user'], content['top']

        self.update_top(user, new_top)
        return 200, "OK"

    @http('GET', '/top')
    def get_top_handler(self, request):
        """Request:
            {
                "user": <user>
            }
            """
        content = request.get_data(as_text=True)
        user = json.loads(content)['user']

        return 200, json.dumps(self.get_top(user), ensure_ascii=False)

    @rpc
    @event_handler("event_das", "expired_events")
    def delete_events(self, event_ids):
        """Removes expired events from users` tops"""
        users = self.db.keys()
        for user in users:
            top = self.get_top(user)
            update = list()
            for id in top:
                if id not in event_ids:
                    update.append(id)
            self.update_top(user, update)

    @http('DELETE', '/delete')
    def delete_events_handler(self, request):
        """HTTP Handler for delete_events method
        Request:
            {
                "ids": [...] - list of event_id
            }
            """
        content = request.get_data(as_text=True)
        ids = json.loads(content)['ids']
        self.delete_events(ids)

        return 200, "OK"