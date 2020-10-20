from nameko.web.handlers import http
from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler
from nameko_mongodb import MongoDatabase
import json
from bson.objectid import ObjectId


class UIS:
    # Vars

    name = "uis"

    db = MongoDatabase()
    next_service_rpc = RpcProxy('next_service')

    # Logic

    def _add_questonnaire_data(self, new_q):
        '''
        had received message from API about new questionnaire
         and therefore the dict
         [user_id, [tag_1, tag_2, ..., tag_n]],
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
        raw_tags_dict = new_q[1]
        for raw_tag in raw_tags_dict:
            raw_tag = {raw_tag: 1.0}

        # каким-то образом получить базу данных
        # collection = self.db["interests"]
        # или
        # collection = self.db.collection
        # ничего из этого не работает, потому что у MongoDatabase нет таких методов (?)

        collection = self.db["interests"]
        collection.insertOne(
            {"_id": user_id, "raw_tags": raw_tags_dict, "count_changes": 1}
        )
        return {user_id: raw_tags_dict}

    def _update_like_data(self, message):
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
        '''
        collection = self.db["interests"]
        user_id = message[0]
        user_tags = collection.findOne(
            {"_id": ObjectId(user_id)},
            {"_id": 0, "raw_tags": 1}
        )
        count = user_tags = collection.findOne(
            {"_id": ObjectId(user_id)},
            {"_id": 0, "count_changes": 1}
        )
        event_id = message[1]
        # get list of tags for event
        event_tags = []

        for event_tag in event_tags:
            if event_tag in user_tags:
                total_weight = user_tags[event_tag]
            else:
                total_weight = 0.0
            total_weight = (total_weight*count + 1.0)/(count+1.0)
            user_tags[event_tag] = total_weight

        collection.updateOne({
            "count_changes": count+1,
            "raw_tags": user_tags
        })
        return {user_id: user_tags}

    @rpc
    def create_new_q(self, questionnaire):
        '''
            questionnaire - [user_id, [tag_1, tag_2, ..., tag_n]]
        '''
        data = self._add_questonnaire_data(questionnaire)
        self.next_service_rpc.update_preferences(data)
        return data

    @event_handler("like_service", "like")
    def update_q(self, message):
        '''
        message - [user_id, event_id]
        '''
        data = self._update_like_data(message)
        self.next_service_rpc.update_preferences(data)
        return data