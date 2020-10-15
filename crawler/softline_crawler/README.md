# Softline Crawler

Краулер для сбора информации о предстоящих мероприятиях с сайта softline.ru

Название сервиса softline_crawler

Сервис разработан с помощью библиотеки _nameko_

## API

### RPC

Для развертывания из консоли nameko shell:

```
nameko run softline_crawler
nameko shell
n.rpc.softline_crawler.get_upcoming_events()
```

### HTTP

Для межсервисного взаимодействия

```
GET http://localhost:8000/events HTTP/1.1
```
