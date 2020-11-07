from nameko.web.handlers import http
from nameko.rpc import rpc
from nameko.events import EventDispatcher
from nameko_mongodb import MongoDatabase
from werkzeug.wrappers import Request, Response
import json


class Likes:
    # Vars

    name = "likes"

    db = MongoDatabase()
    dispatch = EventDispatcher()

    # Logic

    def _new_like(self, like_data) -> bool:
        '''
         like_data is [user_id, event_id]
         Save info in database
         Returns True if new info is added, False otherwise
        '''
        user_id, event_id = like_data
        collection = self.db["likes"]
        # here we have a table | user_id | [event_1_id, ..., event_n_id] |
        current_likes_list = collection.find_one(
            {"_id": user_id},
            {"_id": 0, "likes_list": 1}
        )

        if current_likes_list:
            '''
            check whether this event is presented in current list
            if so, change nothing, else add event_id in the list
            '''
            current_likes_list = current_likes_list["likes_list"]
            if event_id not in current_likes_list:
                current_likes_list.append(event_id)
                collection.update_one(
                    {'_id': user_id},
                    {'$set': {"likes_list": current_likes_list}}
                )
                return True
            return False
        else:
            collection.insert_one(
                {"_id": user_id, "likes_list": [event_id]}
            )
            return True

    def _cancel_like(self, like_data) -> bool:
        '''
         like_data is [user_id, event_id]
         Delete info from database
         Returns True if some info is deleted, False otherwise
        '''
        user_id, event_id = like_data
        collection = self.db["likes"]
        # here we have a table | user_id | [event_1_id, ..., event_n_id] |
        try:
            current_likes_list = collection.find_one(
                {"_id": user_id},
                {"_id": 0, "likes_list": 1}
            )["likes_list"]
        except Exception:
            print(Exception)
            return False
        if event_id in current_likes_list:
            if len(current_likes_list) > 1:
                '''
                just delete one item in list
                '''
                current_likes_list.remove(event_id)
                collection.update_one(
                    {'_id': user_id},
                    {'$set': {"likes_list": current_likes_list}}
                )
            else:
                '''
                delete all record in db 
                '''
                collection.delete_one(
                    {"_id": user_id}
                )
            return True
        return False

    def _get_likes(self, user_id):
        collection = self.db["likes"]
        likes = collection.find_one(
            {"_id": user_id},
            {"_id": 0, "likes_list": 1}
        )
        if likes:
            return likes["likes_list"]
        else:
            return None

    # API

    @rpc
    def new_like(self, like_data):
        '''
        like_data should be [user_id, event_id] 
        '''
        is_new_info = self._new_like(like_data)
        if is_new_info:
            self.dispatch("like", like_data)

    @rpc
    def cancel_like(self, like_data):
        '''
        like_data should be [user_id, event_id] 
        '''
        is_deleted_info = self._cancel_like(like_data)
        if is_deleted_info:
            self.dispatch("like_cancel", like_data)
        else:
            print('ERROR: we try to cancel a like which we does not have gotten')

    @rpc
    def get_likes_by_id(self, user_id):
        return self._get_likes(user_id)

    @rpc
    def is_event_liked(self, user_id, event_id):
        likes = self._get_likes(user_id)
        if event_id in likes:
            return True
        return False

    @http("POST", "/new_like")
    def new_like_http(self, request: Request):
        content = request.get_data(as_text=True)
        like_data = json.loads(content)
        is_new_info = self._new_like(like_data)
        if is_new_info:
            self.dispatch("like", like_data)
        return Response(status=201)

        # POST http://localhost:8000/new_like HTTP/1.1
        # Content-Type: application/json
        #
        # [user_id, event_id]

    @http("POST", "/cancel_like")
    def cancel_like_http(self, request: Request):
        content = request.get_data(as_text=True)
        like_data = json.loads(content)
        is_deleted_info = self._cancel_like(like_data)
        if is_deleted_info:
            self.dispatch("like_cancel", like_data)
            return Response(status=201)
        '''
        else it turns out we try to cancel a like which we does not have gotten
        '''
        return Response(status=404)

        # POST http://localhost:8000/cancel_like HTTP/1.1
        # Content-Type: application/json
        #
        # [user_id, event_id]

    @http("GET", "/get_likes/<id>")
    def get_likes_by_id_http(self, request: Request, id):
        likes = self._get_likes(id)
        return json.dumps(likes, ensure_ascii=False)

    @http("GET", "/is_liked/<user_id>/<event_id>")
    def is_event_liked_http(self, request: Request, user_id, event_id):
        likes = self._get_likes(user_id)
        if event_id in likes:
            return json.dumps(True, ensure_ascii=False)
        return json.dumps(False, ensure_ascii=False)
