# coding=utf-8
from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler
from nameko.rpc import rpc
from nameko.events import event_handler, EventDispatcher
import math


class RankingService:

    # Vars
    name = 'ranking_service'
    top_das_rpc = RpcProxy('top_das')
    uis_rpc = RpcProxy('uis')
    event_das_rpc = RpcProxy('event_das')
    auth_rpc = RpcProxy('auth')

    # Logic

    def _change_top_user(self, user_id, user_tags, events_tags):
        ''' 
        принимает событие от uis или вызывается из функции _change_top_all, 
        получает  user_id, {'tag_1':w_1, ..., 'tag_n':w_n}
        на основе этого должен составить топ для данного пользователя
        и записать данные в хранилище топов мероприятий для пользователей
        например с помощью вызова функции 
        self.top_das_proxy.update_top(user_id, [event_1_id, ..., event_n_id])
        '''
        # events_tags - dict of events and their tags like
        # {'event_id_1': ['tag_1',...,'tag_n'], ..., 'event_id_m':['tag_1',...,'tag_k']}
        # assume that all tags for events have weights 1.0
        # if they are presented in the event and 0 otherwise
        len_y = math.sqrt(sum(val*val for val in user_tags.values()))
        top_events = {}
        for event in events_tags.items():
            event_name, event_tags = event
            len_x = math.sqrt(len(event_tags))
            num = 0.0
            for tag in user_tags.items():
                name, w = tag
                if name in event_tags:
                    num += w
            cosine = num/(len_x*len_y)
            top_events[event_name] = cosine
        top_events = sorted(top_events, key=top_events.get, reverse=True)
        return top_events

    # API

    @rpc
    @event_handler("event_das", "new_events")
    def change_top_all(self, plug):
        '''
        принимает событие от event_das о добавлении новых мероприятий
        должен обновить топы для всех пользователей
        '''
        user_ids = self.auth_rpc.get_all_logins()
        for user_id in user_ids:
            tags = self.uis_rpc.get_weights_by_id(user_id)
            self.change_top_user([user_id, tags])

    @rpc
    @event_handler("uis", "make_top")
    def change_top_user(self, data):
        events_tags = self.event_das_rpc.get_event_tags()
        top_events = self._change_top_user(data[0], data[1], events_tags)
        self.top_das_rpc.update_top(data[0], top_events)
        # for checking
        # self.top_das_rpc.get_top(data[0])
