from nameko.rpc import rpc, RpcProxy
import copy
import string


class PREH:
    """Microservice for events primary processing"""
    # Vars

    name = "primary_raw_events_handler"
    event_das_rpc = RpcProxy('event_das')

    # Logic

    def _eq_ev(ev1, ev2):
        """Determine whether events are equal by their title`
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

        for i in range (len(events)):
            erase_list = list()
            for j in range(i + 1, len(events)):
                if _eq_ev(events[i], events[j]):
                    events[i]['meta'].update(events[j]['meta'])
                    erase_list.append(j)
            deleted = 0
            for ind in erase_list:
                events.pop(ind - deleted)
                deleted += 1
        return events

    # API

    @rpc
    def receive_events(self, events):
        """Receiving events from REC 
        :param events: events got from REC service"""

        self.event_das_rpc.save_events(self._unduplicate(events))

        # TODO: Send new events to ETA
        return self.new_events


