from nameko.rpc import rpc, RpcProxy

class Filter:
    """Microservice for filtering top events"""
    # Vars

    name = 'filter'
    top_das_rpc = RpcProxy('top_das')
    event_das_rpc = RpcProxy('event_das')

    # Logic

    # API

    @rpc 
    def get_events(self, user, tags):
        """Getting tags, sending filtered events back
        :params:
            user - user login
            tags - list of tags
        :returns:
            filtered_events - filtered top user's events"""
        tags = set(tags)
        top_events = self.top_das_rpc.get_top(user)

        events = list()
        for event_id in top_events:
            events.append(self.event_das_rpc.get_event_by_id(event_id))

        filtered_events = list()
        for event in events:
            event_tags = set(event['tags'])
            if tags.issubset(event_tags):
                filtered_events.append(event)

        return filtered_events