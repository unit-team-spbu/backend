from nameko.web.handlers import http
from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler, EventDispatcher
from nameko_mongodb import MongoDatabase
from werkzeug.wrappers import Request, Response
import json


class UIS:
    # Vars

    q_weight = 50.0  # assume that one questionnaire is equal to 50 likes of evets with those tags
    # users' interests service
    name = "uis"

    db = MongoDatabase()
    dispatch = EventDispatcher()

    event_das_rpc = RpcProxy('event_das')

    # Logic

    def _add_questonnaire_data(self, new_q):
        '''
        had received message from API about new questionnaire
         and therefore the list
         [user_id, ['tag_1', 'tag_2', ..., 'tag_n']],
         should write the line into the db
         with columns:
             '_id'
             'tags' - the dict:
                 {'tag_name': 1.0, ...}
                     where 1.0 is a weight of the tag
             'count_changes':
                 how many changes of weights the user in effect had done
        '''

        user_id = new_q[0]
        tags_list = new_q[1]
        new_tags = {}  # new questionnaire tags
        for tag in tags_list:
            new_tags[tag] = 1.0

        collection = self.db["interests"]

        previous_questionnaire_tags = collection.find_one(
            {"_id": user_id},
            {"_id": 0, "q_tags": 1}
        )['q_tags']  # list type
        print(previous_questionnaire_tags)

        if previous_questionnaire_tags:

            tags = collection.find_one(
                {"_id": user_id},
                {"_id": 0, "tags": 1}
            )['tags']  # all user tags - dict type
            count = collection.find_one(
                {"_id": user_id},
                {"_id": 0, "count_changes": 1}
            )['count_changes']  # count_changes var is not gonna be incremented
            # because we simply replace one questionnaire with another one

            # getting rid of influence of previous questionnaire
            for old_tag in previous_questionnaire_tags:
                weight = tags[old_tag] - self.q_weight/count
                if weight < 0:  # actually that gonna be only in case of a deviation
                    weight = 0
                tags[old_tag] = weight

            # add weights from new questionnaire
            for new_tag in new_tags:
                if new_tag in tags:
                    # that tag is already presented
                    total_weight = tags[new_tag]
                else:
                    # this is the new tag
                    total_weight = 0.0
                weight = (total_weight * count + self.q_weight)/count
                tags[new_tag] = weight

            collection.update_one(
                {'_id': user_id}, {'$set': {"tags": tags, "q_tags": tags_list}})
            return [user_id, tags]
        else:
            collection.insert_one(
                {"_id": user_id, "tags": new_tags,
                    "count_changes": self.q_weight, "q_tags": tags_list}
            )
            return [user_id, new_tags]

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
            {"_id": 0, "tags": 1}
        )['tags']
        count = collection.find_one(
            {"_id": user_id},
            {"_id": 0, "count_changes": 1}
        )['count_changes']

        for event_tag in event_tags:
            if event_tag in user_tags:
                total_weight = user_tags[event_tag]
            else:
                total_weight = 0.0
            total_weight = (total_weight*count + 1.0)/(count+1.0)
            user_tags[event_tag] = total_weight

        for user_tag in user_tags:
            if user_tag not in event_tags:
                user_tags[user_tag] = user_tags[user_tag]*count/(count+1.0)

        collection.update_one(
            {'_id': user_id}, {'$set': {"count_changes": count+1, "tags": user_tags}})

        return [user_id, user_tags]

    def _get_weights_by_id(self, id):
        collection = self.db["interests"]
        user_weights = collection.find_one(
            {"_id": id},
            {"_id": 0, "tags": 1}
        )['tags']
        return user_weights

    # API

    @rpc
    def create_new_q(self, questionnaire):
        '''
            questionnaire - 
        '''
        data = self._add_questonnaire_data(questionnaire)
        self.dispatch("make_top", data)

    @rpc
    @event_handler("like_service", "like")
    def update_q(self, message):
        '''
        message - [user_id, event_id]
        '''
        event_tags = self.event_das_rpc.get_tags_by_id(message[1])

        data = self._update_like_data(message, event_tags)
        self.dispatch("make_top", data)

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
        event = self.event_das_rpc.get_event_by_id(like_message[1])

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


