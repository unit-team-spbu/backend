# Authentication service

Название сервиса: `auth`

## API
### RPC
Регистрация нового пользователя (логин пользователя должен быть уникальным):
```
n.rpc.auth.register(login, password)
```
Вход в систему (получение JWT токена):
```
n.rpc.auth.login(login, password)
```
Проверка JWT токена на валидность:
```
n.rpc.auth.check_jwt(jwt_token)
```
## Запуск
### Локальный запуск
Для локального запуска сервиса из папки `auth` выполнить:
```
docker-compose up
```
