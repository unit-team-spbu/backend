from nameko.web.handlers import http
from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler, EventDispatcher
from nameko_mongodb import MongoDatabase
from werkzeug.wrappers import Request, Response
import json
from bson.objectid import ObjectId


class UIS:
    # Vars

    # users' interests service
    name = "uis"

    db = MongoDatabase()
    dispatch = EventDispatcher()

    # here will be the user-top-service
    next_service_rpc = RpcProxy('next_service')

    event_das_rpc = RpcProxy('event_das')

    # Logic

    def _add_questonnaire_data(self, new_q):
        '''
        had received message from API about new questionnaire
         and therefore the list
         [user_id, ['tag_1', 'tag_2', ..., 'tag_n']],
         should write the line into the db
         with columns:
             'user_id'
             'raw_tags' - the list:
                 [{'tag_name': 1.0}, ...]
                     where 1.0 is a weight of the tag
             'count_changes':
                 how many changes of weights the user in effect had done
        '''

        user_id = new_q[0]
        raw_tags_list = new_q[1]
        for raw_tag in raw_tags_list:
            raw_tag = {raw_tag: 1.0}

        collection = self.db["interests"]
        collection.insert_one(
            {"_id": user_id, "raw_tags": raw_tags_list, "count_changes": 1}
        )
        return {user_id: raw_tags_list}

    def _update_like_data(self, message, event_tags=[]):
        '''
        having had the like-event:
            [user_id, event_id]
        changes weights due to the following principal:
            the weight of the tag equals to probability of the fact that
            that tag is presented in a random chosen event that the user has liked

        for that:
        assume that all tags are of the same authority

        total_weight = (total_weight*count + \
                        new_weight_of_this_tag)/(count+1.0)
        ++count

        event_tags - list of tags related to liked event
        '''
        collection = self.db["interests"]
        user_id = message[0]
        user_tags = collection.find_one(
            {"_id": user_id},
            {"_id": 0, "raw_tags": 1}
        )
        count = collection.find_one(
            {"_id": user_id},
            {"_id": 0, "count_changes": 1}
        )

        for event_tag in event_tags:
            if event_tag in user_tags:
                total_weight = user_tags[event_tag]
            else:
                total_weight = 0.0
            total_weight = (total_weight*count + 1.0)/(count+1.0)
            user_tags[event_tag] = total_weight

        collection.update_one(
            {'_id': user_id}, {'$set': {"count_changes": count+1, "raw_tags": user_tags}})

        return {user_id: user_tags}

    def _get_weights_by_id(self, id):
        collection = self.db["interests"]
        user_weights = collection.find_one({
            {"_id": id},
            {"_id": 0, "raw_tags": 1}
        })
        return user_weights

    # API

    @rpc
    def create_new_q(self, questionnaire):
        '''
            questionnaire - [user_id, [tag_1, tag_2, ..., tag_n]]
        '''
        data = self._add_questonnaire_data(questionnaire)
        self.dispatch("make_top", data)
        return data

    @rpc
    @event_handler("like_service", "like")
    def update_q(self, message):
        '''
        message - [user_id, event_id]
        '''
        # нужно получить список тегов для мероприятия
        event = self.event_das_rpc.get_event_by_id(ObjectId(message[1]))

        event_tags = event['tags']
        # this field does not exist yet
        # must be like ['tag_1', 'tag_2', ... , 'tag_n]

        data = self._update_like_data(message, event_tags)
        self.dispatch("make_top", data)
        return data

    @rpc
    def get_weights_by_id(self, id):
        return self._get_weights_by_id(id)

    @http("POST", "/newq")
    def create_new_q_handler(self, request: Request):
        content = request.get_data(as_text=True)
        questionnaire = json.loads(content)
        data = self._add_questonnaire_data(questionnaire)
        self.dispatch("make_top", data)
        return Response(status=201)

        # POST http://localhost:8000/newq HTTP/1.1
        # Content-Type: application/json
        #
        # [1324, [
        #     'free', 'docker', 'forum', 'online'
        # ]]

    @http("POST", "/got_like")
    def update_q_handler(self, request: Request):
        content = request.get_data(as_text=True)
        like_message = json.loads(content)

        # нужно получить список тегов для мероприятия
        event = self.event_das_rpc.get_event_by_id(ObjectId(like_message[1]))

        event_tags = event['tags']
        # this field does not exist yet
        # must be like ['tag_1', 'tag_2', ... , 'tag_n]

        data = self._update_like_data(like_message, event_tags)
        self.dispatch("make_top", data)

        return Response(status=201)

        # POST http://localhost:8000/got_like HTTP/1.1
        # Content-Type: application/json
        #
        # [1324, 8325453]

    @http("GET", "/get_weights/<id>")
    def get_weights_by_id_handler(self, request: Request, id):
        user_weights = self._get_weights_by_id(id)
        return json.dumps(user_weights, ensure_ascii=False)
