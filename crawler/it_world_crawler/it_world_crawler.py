# coding=utf-8
import requests
from bs4 import BeautifulSoup
from nameko.rpc import rpc
from nameko.web.handlers import http
import json


class ITWorldCrawler:

    # Vars

    name = 'it_world_crawler'
    _URL = 'https://www.it-world.ru/events/'

    # Logic

    def _parse_description(self, text):
        text = text.replace('\t', ' ')
        text = text.replace('\n', ' ')
        while text.find('  ') != -1:
            text = text.replace('  ', ' ')
        text = text.replace('·', '')
        return text

    def get_events(self):
        url = self._URL
        events = []

        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
            return []
        soup = BeautifulSoup(r.text, "html.parser")

        events_tmp = soup.find(
            'div', {'class': 'content'})
        if not events_tmp:
            print('main page has not been loaded')
            return[]
        else:
            events_tmp = events_tmp.find_all(
                'div', {'class': 'news-float separator'})

        for event in events_tmp:

            title = event.find(
                'h3')
            if title:
                title = title.text

            # get description
            link_tail = event.find(
                'a', {'class': 'title-middle marker-future'})
            if not link_tail:
                link_tail = event.find(
                    'a', {'class': 'title-middle marker-current'})
            if link_tail:
                link_to_event = 'https://www.it-world.ru' + \
                    link_tail.get('href')
                link_to_event = link_to_event.replace('.html', '/')

                is_page_available = True
                try:
                    r1 = requests.get(link_to_event)
                except requests.exceptions.RequestException as e:
                    print(e)
                    description = None
                    is_page_available = False

                if is_page_available:
                    soup1 = BeautifulSoup(r1.text, "html.parser")
                    description = soup1.find('div', {'class': 'detail'})
                    if description:
                        description = description.text.split(
                            'Зарегистрироваться')[-1]
                        description = self._parse_description(description)

                meta = link_to_event.split('/')[-2]
                # for getting the page url you should get
                # https://www.it-world.ru/events/forums/<meta>/
                # it doesn't matter that the event might be not 'forums' type
            else:
                description = None
                meta = None
            # gotten -------
            type = event.find('div').find('a')
            if type:
                type = type.text

            location = event.find('div', {'class': 'ico-line ico-place'})
            if location:
                location = location.text
                isOnline = False
            else:
                isOnline = True

            date = event.find('div', {'class': 'ico-line ico-date'}).text
            if date.find('–') != -1:
                startDate = date.split('–')[0].strip(' ')
                endDate = date.split('–')[1].strip(' ')
            else:
                startDate = date
                endDate = None

            isPaid = event.find('div', {'class': 'ico-line ico-price'})
            if isPaid:
                isPaid = True
            else:
                isPaid = False

            events.append({
                "title": title,
                "type": type,
                "isPaid": isPaid,
                "isOnline": isOnline,
                "location": location,
                "startDate": startDate,
                "endDate": endDate,
                "description": description,
                "meta": {
                    self.name: meta
                }
            })
        return events

    # API

    @rpc
    def get_upcoming_events(self):
        events = self.get_events()
        return events

    @http("GET", "/events")
    def get_upcoming_events_http(self, request):
        events = self.get_events()
        return json.dumps(events, ensure_ascii=False)
