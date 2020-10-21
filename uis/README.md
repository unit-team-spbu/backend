## UIS - Сервис интересов пользователя

Может вызываться в API после регистрации и заполнения регистрационной анкеты. Ничего не возвращает.

Необходимо подключить сервис как обычно, затем из nameko shell вызвать

```
n.rpc.uis.create_new_q(<questionnaire>)
```
где questionnaire должно быть такого вида:
  
```
[user_id, ['tag_1', ..., 'tag_n']]
```
  
Может вызываться из сервиса лайков и прочих сервисов реакции. Ничего не возвращает.

Для этого в сервисе реакции должен быть метод, в котором выбрасывается сообщение с помощью функции nameko.events.EventDispatcher()
```
from nameko events import EventDispatcher

class like_service:
  # Vars
  ...
  dispatch = EventDispatcher()
  ...
  # Logic
  ...
  def your_func():
    ...
    self.dispatch("like", message)
    ...
  ...
```
"like_service" - название сервиса, который прослушивается uis'ом

"like" - название события, при получении которого начнает работу функция uis.update.update_q 

(эти названия, конечно, можно придумать свои)

message - сообщение вида
```
[user_id, event_id]
```

Отправляет данные дальше с помощью dispatch в сервис ранжирования.
