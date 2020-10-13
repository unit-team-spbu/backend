# Raw Events Collector

Название сервиса: `raw_events_collector`

## API
### HTTP
```
GET http://localhost:8000/events HTTP/1.1
```
Для запроса краулерам в ручную

## Запуск
### Локальный запуск
Сервисы взаимодействуют друг с другом с помощью контейнера RabbitMQ, для его запуска нужно:
```
sudo docker run -p 5672:5672 --hostname nameko-rabbitmq rabbitmq:3
```
Затем из папки `rec` выполнить:
```
nameko run rec
```
Сервис запустится самостоятельно, и с помощью декоратора `@timer` будет обновлять события каждые сутки
## Настройка и добавление новых краулеров
Файл `config.py` содержит список всех краулеров. Там же настраивается интервал обновления в секундах через `TIMER` и время обновления `TIME`. Для добавления новых добавить 2 строчки: 
```
crawler_name_rpc = RpcProxy('crawler_name')
```
в раздел Crawlers и 
```
get_res.append(self.crawler_name_rpc.get_upcoming_events.call_async())
```
в метод `update()`. 
