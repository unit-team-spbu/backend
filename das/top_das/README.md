# Top Data Access Service

Имя сервиса: `top_das`

## API
### RPC
Для обновления топа мероприятий пользователя:
```
rpc.top_das.update_top(user, new_top)
```
Для получения топа мероприятий пользователя:
```
rpc.get_top(user)
```
### HTTP
Для ручного тестирования. Чтобы добавить или обновить данные:
```
POST http://localhost:8000/update HTTP/1.1
Content-Type: application/json

{
    "user": <user>,
    "top": [..]
}
```
Для получения топа:
```
GET http://localhost:8000/top HTTP/1.1
Content-Type: application/json

{
    "user": <user>
}
```
## Запуск в контейнере
Сервис взаимодействует через RabbitMQ и связан базой данный Redis
Из папки сервиса:
```
docker-compose up
```
