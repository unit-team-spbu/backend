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
    like_reaction_rpc = RpcProxy('like_reaction')

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

    # API

    @http('POST', '/register')
    @http('POST', '/register/')
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
        user_data = self._get_content(request)
        login, password = user_data['login'], user_data['password']
        if self.auth_rpc.register(login, password):
            return Response(json.dumps({"message": "User was registered"}), status=201)
        else:
            return Response(json.dumps({"message": "Unable to sign up user"}), status=400)
    
    @http('POST', '/login')
    @http('POST', '/login/')
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
        user_data = self._get_content(request)
        login, password = user_data['login'], user_data['password']
        token = self.auth_rpc.login(login, password)
        if not token:
            return Response(json.dumps({"message": "Wrong credentials"}), status=400)
        return Response(json.dumps({"token": token}), 202)

    @http('GET', '/feed')
    @http('GET', '/feed/')
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
        authorized, user = self._token_validate(request)
        if authorized:
            # if token is invalid
            if not user:
                return Response(json.dumps({"message": "Invalid token"}), status=403)

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

        return Response(json.dumps(events, ensure_ascii=False), status=200)

    @http('GET', '/feed/<string:event_id>')
    @http('GET', '/feed/<string:event_id>/')
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
        authorized, user = self._token_validate(request)
        if authorized and not user:
            return Response(json.dumps({"message": "Invalid token"}), status=403)
        
        try:
            event = self.event_das_rpc.get_event_by_id(event_id)
        finally:
            return Response(json.dumps(event, ensure_ascii=False), 200)

    @http('POST,PUT,GET', '/profile/interests')
    @http('POST,PUT,GET', '/profile/interests/')
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
        authorized, user = self._token_validate(request)
        if not authorized:
            return Response(json.dumps({"message": "User is not authorized"}), 401)
        elif not user:
            return Response(json.dumps({"message": "Invalid token"}), 403)

        if request.method == 'GET':
            interests = self.uis_rpc.get_weights_by_id(user)
            clean_interests = list()
            for item in interests.items():
                if item[1]:
                    clean_interests.append(item[0])
            return Response(json.dumps(clean_interests, ensure_ascii=False), 200)
        
        interests = self._get_content(request)['interests']
        try:
            self.uis_rpc.create_new_q([user, interests])
        finally:
            if request.method == 'POST':
                return Response(json.dumps({"message": "Interests added"}), 201)
            else:
                return Response(json.dumps({"message": "Interests changed"}), 200)

    @http('POST', '/reaction/<string:reaction_type>') 
    @http('POST', '/reaction/<string:reaction_type>/')  
    def reaction_handler(self, request, reaction_type):
        """Making reaction
        request body:
            {
                "token": <token>,
                "value": <value>, (like, dislike)
                "event_id": <event_id>
            }
        response:
            code message
            {
                "message": <msg>
            }
        """
        authorized, user = self._token_validate(request)
        if not authorized:
            return Response(json.dumps({"message": "User is not authorized"}), 401)
        elif not user:
            return Response(json.dumps({"message": "Invalid token"}), 403)
        
        content = self._get_content(request)

        if reaction_type == 'like':
            like = content['value']
            event_id = content['event_id']
            # TODO: add service
            try:
                self.like_reaction_rpc.make_reaction(user, like, event_id)
            finally:
                pass
        return Response(json.dumps({"message": "Reaction committed"}), 200)
