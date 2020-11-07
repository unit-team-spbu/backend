from nameko.web.handlers import http
from nameko.rpc import RpcProxy
import json
from werkzeug.wrappers import Response


class Gateway:
    """API gateway"""

    # Vars

    name = 'gateway'
    auth_rpc = RpcProxy('auth')
    event_das_rpc = RpcProxy('event_das')
    filter_rpc = RpcProxy('filter')
    uis_rpc = RpcProxy('uis')
    likes_rpc = RpcProxy('likes')
    favorites_rpc = RpcProxy('favorites')

    # Logic

    def _get_content(self, request):
        """Parsing json body request"""
        content = request.get_data(as_text=True)
        return json.loads(content)

    def _token_validate(self, request):
        """By request getting user information
        :returns:
            authorized: True if user is registered
            user: user login"""
        authorized = True
        # Check if there's no token provided
        user = -1
        try:
            token = self._get_content(request)['token']
        except KeyError:
            authorized = False
        if authorized:
            user = self.auth_rpc.check_jwt(token)
        return authorized, user

    def _cors_response(self, response, origin, methods):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = methods
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # API

    @http('POST,OPTIONS', '/register')
    @http('POST,OPTIONS', '/register/')
    def register_handler(self, request):
        """Signing up user
        request body: 
            {
                "login": <login>,
                "password": <password>
            }
        response: 
            {
                "message": <msg>
            }
        """
        if request.method == 'OPTIONS':
            return self._cors_response(Response(), '*', 'POST, OPTIONS')

        user_data = self._get_content(request)
        try:
            login, password = user_data['login'], user_data['password']
        except KeyError:
            return self._cors_response(Response(json.dumps({"message": "Login or password are not provided"}), status=401), '*', 'POST, OPTIONS') 

        if self.auth_rpc.register(login, password):
            return self._cors_response(Response(json.dumps({"message": "User was registered"}), status=201), '*', 'POST, OPTIONS')
        else:
            return self._cors_response(Response(json.dumps({"message": "Unable to sign up user"}), status=400), '*', 'POST, OPTIONS')
    
    @http('POST,OPTIONS', '/login')
    @http('POST,OPTIONS', '/login/')
    def login_handler(self, request):
        """Logging in user, sending JWT token
        request body:
            {
                "login": <login>,
                "password": <password>
            }
        reponse:
            JWT token if all is ok
            {
                "token": <token>,
            }
            or error code otherwise
            {
                "message": <msg>
            }
        """
        if request.method == 'OPTIONS':
            return self._cors_response(Response(), '*', 'POST, OPTIONS')

        user_data = self._get_content(request)
        try:
            login, password = user_data['login'], user_data['password']
        except KeyError:
            return self._cors_response(Response(json.dumps({"message": "Login or password are not provided"}), status=401), '*', 'POST, OPTIONS')
        token = self.auth_rpc.login(login, password)
        if not token:
            return self._cors_response(Response(json.dumps({"message": "Wrong credentials"}), status=400), '*', 'POST, OPTIONS')
        return self._cors_response(Response(json.dumps({"token": token}), 202), '*', 'POST, OPTIONS')

    @http('GET,OPTIONS', '/feed')
    @http('GET,OPTIONS', '/feed/')
    def feed_handler(self, request):
        """Getting top events for authorized user
        request body:
            {
                "token": <token>, (optional)
                "tags": [..], (optional)
            }
        response:
            User's top events json if he is authorized with correct token or
            events for unathorized user by date
            [
                {
                    "title": <title>,
                    "location": <location>,
                    "startDate": <startDate>,
                    "endDate": <endDate>,
                    "description": <description>,
                    "meta": <meta>,
                    "tags": [..] - list
                },
                {
                    "title": <title>,
                    "location": <location>,
                    "startDate": <startDate>,
                    "endDate": <endDate>,
                    "description": <description>,
                    "meta": <meta>,
                    "tags": [..] - list
                }
                ...
            ]
            error code if token is invalid
            {
                "message": <msg>
            }
        """
        if request.method == 'OPTIONS':
            return self._cors_response(Response(), '*', 'GET, OPTIONS')

        authorized, user = self._token_validate(request)
        if authorized:
            # if token is invalid
            if not user:
                return self._cors_response(Response(json.dumps({"message": "Invalid token"}), status=403), '*', 'GET, OPTIONS')

            # if there's no tags provided
            try:
                tags = self._get_content(request)['tags']
            except KeyError:
                tags = []

            try:
                events = self.filter_rpc.get_events(user, tags)
            finally:
                pass
        else:
            try:
                events = self.event_das_rpc.get_events_by_date()
            finally:
                pass

        return self._cors_response(Response(json.dumps(events, ensure_ascii=False), status=200), '*', 'GET, OPTIONS')

    @http('GET,OPTIONS', '/feed/<string:event_id>')
    @http('GET,OPTIONS', '/feed/<string:event_id>/')
    def get_event_handler(self, request, event_id):
        """Getting info about specific event
        request body:
            {
                "token": <token>, (optional)
            }
        response:
            event info
            {
                "title": <title>,
                "location": <location>,
                "startDate": <startDate>,
                "endDate": <endDate>,
                "description": <description>,
                "meta": <meta>,
                "tags": [..] - list
            }
            or error code
            {
                "message": <msg>
            }
        """
        if request.method == 'OPTIONS':
            return self._cors_response(Response(), '*', 'GET, OPTIONS')

        authorized, user = self._token_validate(request)
        if authorized and not user:
            return self._cors_response(Response(json.dumps({"message": "Invalid token"}), status=403), '*', 'GET, OPTIONS')
        
        try:
            event = self.event_das_rpc.get_event_by_id(event_id)
        finally:
            return self._cors_response(Response(json.dumps(event, ensure_ascii=False), 200), '*', 'GET, OPTIONS')

    @http('POST,PUT,GET,OPTIONS', '/profile/interests')
    @http('POST,PUT,GET,OPTIONS', '/profile/interests/')
    def interest_handler(self, request):
        """Changing user's interests
        request body:
            {
                "token": <token>, (optional)
                "interests": ['tag1', 'tag2', ...] (optional)
            }
        response:
            interests if it's GET and message for code 
            {
                "message": <msg>
            }
        """
        if request.method == 'OPTIONS':
            return self._cors_response(Response(), '*', 'POST, PUT, GET, OPTIONS')

        authorized, user = self._token_validate(request)
        if not authorized:
            return self._cors_response(Response(json.dumps({"message": "User is not authorized"}), 401), '*', 'POST, PUT, GET, OPTIONS')
        elif not user:
            return self._cors_response(Response(json.dumps({"message": "Invalid token"}), 403), '*', 'POST, PUT, GET, OPTIONS')

        if request.method == 'GET':
            interests = self.uis_rpc.get_weights_by_id(user)
            clean_interests = list()
            for item in interests.items():
                if item[1]:
                    clean_interests.append(item[0])
            return self._cors_response(Response(json.dumps(clean_interests, ensure_ascii=False), 200), '*', 'POST, PUT, GET, OPTIONS')
        
        interests = self._get_content(request)['interests']
        try:
            self.uis_rpc.create_new_q([user, interests])
        finally:
            if request.method == 'POST':
                return self._cors_response(Response(json.dumps({"message": "Interests added"}), 201), '*', 'POST, PUT, GET, OPTIONS')
            else:
                return self._cors_response(Response(json.dumps({"message": "Interests changed"}), 200), '*', 'POST, PUT, GET, OPTIONS')

    @http('DELETE,GET,POST,OPTIONS', '/reaction/<string:reaction_type>') 
    @http('DELETE,GET,POST,OPTIONS', '/reaction/<string:reaction_type>/')  
    def reaction_handler(self, request, reaction_type):
        """Making reaction
        POST request body:
            {
                "token": <token>,
                "event_id": <event_id>
            }

        GET request body:
            {
                "token": <token>,
                "event_id": <event_id> (optional) - if included gets info about specific event
            }
        
        DELETE request body:
            {
                "token: <token>,
                "event_id": <event_id>
            }
        response:
            code message
            {
                "message": <msg>
            }
        """
        if request.method == 'OPTIONS':
            return self._cors_response(Response(), '*', 'DELETE, GET, POST, OPTIONS')

        authorized, user = self._token_validate(request)
        if not authorized:
            return self._cors_response(Response(json.dumps({"message": "User is not authorized"}), 401), '*', 'DELETE, GET, POST, OPTIONS')
        elif not user:
            return self._cors_response(Response(json.dumps({"message": "Invalid token"}), 403), '*', 'DELETE, GET, POST, OPTIONS')
        
        content = self._get_content(request)

        if request.method == 'POST':
            event_id = content['event_id']

            if reaction_type == 'like':
                self.likes_rpc.new_like([user, event_id])
            elif reaction_type == 'favorite':
                self.favorites_rpc.new_fav([user, event_id])

            return self._cors_response(Response(json.dumps({"message": "Reaction committed"}), 200), '*', 'DELETE, GET, POST, OPTIONS')
        elif request.method == 'GET':
            # Whether we need all user reactions or for specific event
            all_data = True
            try:
                event_id = content['event_id']
            except KeyError:
                all_data = False

            if reaction_type == 'like':
                if all_data:
                    likes = self.likes_rpc.get_likes_by_id(user)
                else:
                    likes = self.likes_rpc.is_event_liked(user, event_id)
                    likes = {"value": likes}
                return self._cors_response(Response(json.dumps(likes), 200), '*', 'DELETE, GET, POST, OPTIONS')
            elif reaction_type == 'favorite':
                if all_data:
                    favs = self.favorites_rpc.get_favs_by_id(user)
                else:
                    favs = self.favorites_rpc.is_event_faved(user, event_id)
                    favs = {"value": favs}
                return self._cors_response(Response(json.dumps(favs), 200), '*', 'DELETE, GET, POST, OPTIONS')
        elif request.method == 'DELETE':
            event_id = content['event_id']
            if reaction_type == 'like':
                self.likes_rpc.cancel_like([user, event_id])
            elif reaction_type == 'favorite':
                self.favorites_rpc.cancel_fav([user, event_id])
            return self._cors_response(Response(json.dumps({"message": "Reaction removed"}), 200), '*', 'DELETE, GET, POST, OPTIONS')
