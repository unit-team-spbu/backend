# Contribution Guidelines

В этом документе описан процесс разработки нашей команды. ПОмните, что эти правили возникли не просто так и основаны на опыте тысяч разработчиков.

## Как мы разрабатываем (наш Цикл Разработки)

[**Software Development Life Cycle**](https://stackify.com/what-is-sdlc/) - набор методологий, нацеленных на производство высококачественного ПО. SDLC описывает конкретные фазы и этапы разработки, требования к ним.

Мы придерживаемся итеративной модели, где каждая итерация включает в себя следующие этапы:

1. :thinking: Определение проблемы итерации

    Прежде чем писать код, требуется понять, что нам нужно реализовать к конкретной дате (дедлайну, milestone в терминах GitHub). Для этого проводится бизнес и технических анализ при помощи любых удобных инструментов.

2. :bar_chart: Планирование

    Мы формализуем результаты первой фазы итерации. Создаем дедлайн(ы) при помощи [GitHub Milestones](https://docs.github.com/en/github/managing-your-work-on-github/about-milestones), создаем задачи в формате Issues (используя [Issue Templates](https://docs.github.com/en/github/building-a-strong-community/configuring-issue-templates-for-your-repository)), привязываем их к разработчикам (assignees), распределяем по проектам (см. [Project Boards](https://docs.github.com/en/github/managing-your-work-on-github/about-project-boards)), помечаем задачи лейблами (см. [Labels](https://docs.github.com/en/github/managing-your-work-on-github/about-labels)). Помните, что задача должна быть максимально полно описана и вы должны быть готовы ответить на любые вопросы касательно поставленной проблемы.

3. :computer: Разработка

    Выберите задачу над которой вы будете работать и создайте ветку для ее решения (если требуется писать код), назвав ее `issues/xxx` (`xxx` - номер задачи). Данный формат используется для упрощенной навигации по веткам и задачам.

    Работайте над вашей задачей в ветке. Если вы не знаете как решить задачу - проведите исследование, спросите у других разработчиков, ведите обсуждение на GitHub под задачей. Нет ничего страшного в том, чтобы застрять и попросить помощи.

    После того, как вы закончили работу над задачей, сделайте Pull Request, предложите другим разработчиком оценить и просмотреть результат вышей работы. Если всех все устраивает, то Pull Request будет принят и код попадет в нашу кодовую базу (ветку `master`).

После чего мы проводим следующую итерацию по той же схеме.

## Код

### Как мы оформляем код

Желательно пользоваться форматерами и линтерами. Для Python рекомендуется использовать [autopep8](https://pypi.org/project/autopep8/). Для HTML/CSS/JS - [Prettier](https://prettier.io/).

### Как мы называем коммты

git и GitHub имеют ограничение по количеству отображаемых символов в названии коммита, поэтому каждый символ важен. Рекомендуется следующая практика: 

* префиксом к коммиту идет имя ветки (`issues/xxx`)
* используется настоящее время (т.е. не `added`, а `add`) - так короче
* сокращайте слова, но так, чтобы выс поняли (например `upd` вместо `update`)

Пример истории коммитов:

```bash
* dfd91b1 (HEAD -> issues/3, origin/issues/3) issues/3 upd requirements.txt
* f2d7ab6 issues/3 wrap crawler job to execute every day via timeloop
* 71a6b97 issues/3 add csv ignore to gitignore
* 333ee8c issues/3 add reading and importing both upcoming and past events
* bf34594 issues/3 add import to csv
* 02793dd issues/3 add parser 4 it-events.com that gets all upcoming events
* eae213f issues/3 add vscode launch file and requirements.txt for python
* 7315ac6 issues/3 add startup guide in readme
* 2fca75d (origin/master, origin/HEAD, master) import template repo
* 1b61903 Initial commit
```