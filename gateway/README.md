# API Gateway

Название сервиса: `gateway`

## API
### HTTP
 - Регистрация пользователей:
```
POST http://localhost:8000/register HTTP/1.1
Content-Type: application/json

{
    "login": <login>,
    "password": <password>
}

Response (Сообщение об успехе, либо ошибка):
Status: 201 - успех, 400 - ошибка регистрации
Content-Type: application/json

{
    "message": <msg>
}
```
- Вход:
```
POST http://localhost:8000/login HTTP/1.1
Content-Type: application/json

{
    "login": <login>,
    "password": <password>
}

Response (Correct credentials):
Status: 202 - успех
Content-Type: application/json

{
    "token": <token>
}

Response (Wrong credentials):
Status: 400 - неверный логин или пароль
Content-Type: application/json

{
    "message": <msg>
}
```
В теле всех остальных запросов _должен присутствовать JWT токен_, если это зарегистрированный пользователь
- Получение ленты событий:
```
POST http://localhost:8000/feed HTTP/1.1
Content-Type: application/json

{
    "token": <token>, (Может быть не указан, если пользователь не авторизован)
    "tags": [..] - Теги для фильтрации (могут быть не указаны)
}

Response:
Status: 200 - успех
Content-Type: application/json

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

Response (При неверном токене):
Status: 403 - неверный токен
Content-Type: application/json

{
    "message": <msg>
}
```
- Получение определенного события:
```
GET http://localhost:8000/feed/<string:event_id>?token=<token> HTTP/1.1

Query parameters:
{
    "token": <token> (Может быть не указан, если пользователь не авторизован)
}

Response (событие):
Status: 200
Content-Type: application/json

{
    "title": <title>,
    "location": <location>,
    "startDate": <startDate>,
    "endDate": <endDate>,
    "description": <description>,
    "meta": <meta>,
    "tags": [..] - list
}

Response (ошибка):
Status: 403 - неверный токен
Content-Type: application/json

{
    "message": <msg>
}
```
- Получение интересов пользователя
```
GET http://localhost:8000/profile/interests?token=<token> HTTP/1.1

Query parameters:
{
    "token": <token>
}

Response:
Status: 200 - успех
Content-Type: application/json

{
    "interests": ['tag1', 'tag2', ...]
}

Response (Не передан токен, либо он неверный):
Status: 401 - пользователь не авторизован (токен не передан), 403 - неверный токен
Content-Type: application/json

{
    "message": <msg>
}
```
- Добавление новой анкеты интересов:
```
POST http://localhost:8000/profile/interests HTTP/1.1
Content-Type: application/json

{
    "token": <token>,
    "interests": ['tag1', 'tag2', ...]
}

Response (Сообщение об успешном добвалении, либо ошибка):
Status: 200 - успех, 401 - пользователь не авторизован (токен не передан), 403 - неверный токен
Content-Type: application/json

{
    "message": <msg>
}
```
- Изменение интересов:
```
PUT http://localhost:8000/profile/interests HTTP/1.1
Content-Type: application/json

{
    "token": <token>,
    "interests": ['tag1', 'tag2', ...]
}

Response (Сообщение об успешном изменении, либо ошибка):
Status: 200 - успех, 401 - пользователь не авторизован (токен не передан), 403 - неверный токен
Content-Type: application/json

{
    "message": <msg>
}
```
Далее описаны запросы для лайков, для добавление в избранное заменить like на favorite в адресе
- Реакционное событие (добавление лайка):
```
POST http://localhost:8000/reaction/like HTTP/1.1
Content-Type: application/json

{
    "token": <token>,
    "event_id": <event_id>
}

Response (Сообщение об успехе, либо ошибка):
Status: 200 - успех, 401 - пользователь не авторизован (токен не передан), 403 - неверный токен
Content-Type: application/json

{
    "message": <msg>
}
```
- Реакционное событие (получение всех лайков/наличие лайка у мероприятия):
```
GET http://localhost:8000/reaction/like?token=<token>&event_id=<event_id> HTTP/1.1
Content-Type: application/json

Query parameters:
{
    "token": <token>,
    "event_id": <event_id> - Указывается, если нужно узнать наличие лайка у конкретного мероприятия
}

Response (успех, запрос на все лайки):
Status: 200
Content-Type: application/json

[
    event_id1, - id, лайкнутых всех событий
    event_id2,
    ...
]

Response (успех, конкретное мерориятие):
Status: 200
Content-Type: application/json

{
    "value": (true or false)
}

Response (ошибка):
Status: 401 - пользователь не авторизован (токен не передан), 403 - неверный токен
Content-Type: application/json

{
    "message": <msg>
}
```
- Реакционное событие (удаление лайка):
```
DELETE http://localhost:8000/reaction/like HTTP/1.1
Content-Type: application/json

{
    "token": <token>,
    "event_id": <event_id>
}

Response (Сообщение об успехе, либо ошибка):
Status: 200 - успех, 401 - пользователь не авторизован (токен не передан), 403 - неверный токен
Content-Type: application/json

{
    "message": <msg>
}
```