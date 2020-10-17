# IT World Crawler

Краулер для сбора информации о предстоящих мероприятиях с сайта [it-world](https://www.it-world.ru/events/)

Название сервиса it_world_crawler

Сервис разработан с помощью библиотеки _nameko_

## API

### RPC

Для развертывания из консоли nameko shell:

```
nameko run it_world_crawler
nameko shell
n.rpc.it_world_crawler.get_upcoming_events()
```

### HTTP

Для межсервисного взаимодействия

```
GET http://localhost:8000/events HTTP/1.1
```
