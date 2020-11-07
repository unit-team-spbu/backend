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
| Gateway                    | `gateway`   | 8000      |             |
