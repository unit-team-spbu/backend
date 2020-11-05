from nameko.web.handlers import http
import json
from werkzeug.wrappers import Response


class Gateway:
    """API gateway"""

    # Vars

    name = 'gateway'

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
        return Response(json.dumps({"message": "User was registered"}), status=201)
    
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
        token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsIm5hbWUiOiJKb2huIEdvbGQiLCJhZG1pbiI6dHJ1ZX0K.LIHjWCBORSWMEibq-tnT8ue_deUqZx1K0XxCOXZRrBI"
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
        events = [
                {
                    "title": "Видео+Конференция 2020",
                    "location": "Москва, Россия",
                    "startDate": "13/10/2020",
                    "endDate": "14/10/2020",
                    "description": "3-я Международная научно-техническая конференция «Современные сетевые технологии» собирает представителей международного научного сообщества, исследовательских подразделений корпораций, стартапов, промышленности и бизнеса, институтов развития и органов государственной власти для обсуждения перспективных и актуальных технологий в сфере компьютерных сетей, виртуализации сетевых ресурсов и облачных вычислений, использования методов искусственного интеллекта.",
                    "meta": {
                        "it_events_crawler": "18960"
                    },
                    "tags": [
                        "Конференция",
                        "Paid",
                        "Online"
                    ]
                },
                {
                    "title": "JavaScript-разработка",
                    "location": "Тверь, Россия",
                    "startDate": "29/10/2020",
                    "endDate": "15/02/2021",
                    "description": "JavaScript – один из самых популярных и кроссплатформенных языков программирования, позволяющий работать как с веб-интерфейсами так и с серверной частью и мобильными клиентами. Вы тоже хотите освоить востребованную профессию фронтенд-разработчика? Тогда регистрируйтесь на бесплатный тренинг EPAM «JavaScript-разработка».",
                    "meta": {
                        "it_events_crawler": "18961"
                    },
                    "tags": [
                        "JavaScript",
                        "Free",
                        "Online",
                        "Web-разработка",
                        "Тренинг"
                    ]
                },
                {
                    "title": "Вводное занятие по контекстной рекламе",
                    "location": "Москва, Россия",
                    "startDate": "02/11/2020",
                    "endDate": "02/11/2020",
                    "description": "На занятии разберем структуру систем контекстной рекламы, расскажем, для чего подбирать и как прогнозировать ключевые слова. Такое занятие будет полезно всем начинающим в области digital. Вы поймете насколько для вас интересен полный курс Контекстной рекламы, хотели бы в дальнейшем развиваться в этой сфере, нравится ли преподаватель и планируете ли продолжить обучение в MyAcademy.",
                    "meta": {
                        "it_events_crawler": "18962"
                    },
                    "tags": [
                        "Лекция",
                        "Free",
                        "Реклама",
                        "Тренинг"
                    ]
                }
            ]

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
        event = {
                "title": "Вводное занятие по контекстной рекламе",
                "location": "Москва, Россия",
                "startDate": "02/11/2020",
                "endDate": "02/11/2020",
                "description": "На занятии разберем структуру систем контекстной рекламы, расскажем, для чего подбирать и как прогнозировать ключевые слова. Такое занятие будет полезно всем начинающим в области digital. Вы поймете насколько для вас интересен полный курс Контекстной рекламы, хотели бы в дальнейшем развиваться в этой сфере, нравится ли преподаватель и планируете ли продолжить обучение в MyAcademy.",
                "meta": {
                    "it_events_crawler": "18962"
                },
                "tags": [
                    "Лекция",
                    "Free",
                    "Реклама",
                    "Тренинг"
                ]
            }
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

        if request.method == 'GET':
            clean_interests = ['C++', 'Стажировка', 'Хакатон', 'Тестирование']

            return Response(json.dumps(clean_interests, ensure_ascii=False), 200)
        
        interests = self._get_content(request)['interests']

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
        content = self._get_content(request)

        if reaction_type == 'like':
            like = content['value']
            event_id = content['event_id']

        return Response(json.dumps({"message": "Reaction committed"}), 200)
