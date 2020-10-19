# Primary Raw Events Handler

Название сервиса: `primary_raw_events_handler`

## API
### RPC
Для получения событий от сборщика:
```
n.rpc.promary_raw_events_handler.receive_events(<events>)
```
## Запуск
### Локальный запуск
Сервисы взаимодействуют друг с другом с помощью контейнера RabbitMQ, для его запуска нужно:
```
sudo docker run -p 5672:5672 --hostname nameko-rabbitmq rabbitmq:3
```
Затем из папки `preh` выполнить:
```
nameko run preh
```
