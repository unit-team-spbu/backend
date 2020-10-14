from nameko.rpc import rpc, RpcProxy
import copy
import string


class PREH:
    """Microservice for events primary processing"""
    # Vars

    name = "primary_raw_events_handler"
    event_das_rpc = RpcProxy('event_das')
    new_events = list()
    existing_events = list()

    # Logic

    def _eq_ev(ev1, ev2):
        """Determine whether events are equal by their title
            :param ev1: the first event
                ev2: the second event
            :return bool value"""
        # Punctuation removal
        title1 = ev1['title'].translate(str.maketrans('', '', string.punctuation)).split()
        title2 = ev2['title'].translate(str.maketrans('', '', string.punctuation)).split()
        for title in [title1, title2]:
            for i in range(len(title)):
                title[i] = title[i].lower()
            
        return title1 == title2


    def _unduplicate(self, events):
        """Removes duplicates from different crawlers and 
            appends meta data for duplicate events"""
        unquie_events = list()
        for i in range(len(events)):
            cur_event = copy.deepcopy(events[i])
            for j in range(len(events)):
                if i != j and self._eq_ev(events[i], events[j]):
                    cur_event['meta'].update(events[j]['meta'])
            unquie_events.append(cur_event)
        return unquie_events

    # API

    @rpc
    def receive_events(self, events):
        """Receiving events from REC 
        :param events: events got from REC service"""

        events = self._unduplicate(events)
        for event in events:
            # Check for existing in DB ?
            if self.event_das_rpc.contain(event):
                self.existing_events.append(event)
            else:
                self.new_events.append(event)
        
        self.event_das_rpc.save_events(self.existing_events)

        # TODO: Send new events to ETA
        return self.new_events
