# Агрегатор IT мероприятий

## Deploy Configuration

| Service                    | Hostname    | Port      | Description |
| -------------------------- | ----------- | --------- | ----------- |
| Raw Events Collector       | `rec`       | 8001      |             |
| Primary Raw Events Handler | `preh`      | 8002      |             |
| Event Data Access Service  | `event_das` | 8003/8083 |             |
| Tag Data Access Service    | `tag_das`   | 8004/8084 |             |
| Top Data Access Service    | `top_das`   | 8005/8085 |             |
| Event Theme Analyzer       | `eta`       | 8006      |             |
| Filter                     | `filter`    | 8007      |             |
| User Interest Service      | `uis`       | 8008/8086 |             |
| Ranking                    | `ranking`   | 8009      |             |
| Auth                       | `auth`      | 8010      |             |
| Likes                      | `likes`     | 8011/8087 |             |
| Favorites                  | `favorites` | 8012/8088 |             |
| Logger                     | `logger`    | 8013/8089 |             |
| Gateway                    | `gateway`   | 8000      |             |

## How to push changes
После изменения кода микросервис нужно поместить в DockerHub. Для этого нужно выполнить:
- Если образ уже создан
```
sudo docker tag <image_name> maxkuznets0v/aggregator:<service_name>
```
- Если образа нет
```
sudo docker build -t maxkuznets0v/aggregator:<service_name> .
```
И запушить образ в репозиторий:
```
sudo docker push maxkuznets0v/aggregator:<service_name>
```
