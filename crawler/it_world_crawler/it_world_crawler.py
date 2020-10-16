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
        try:
            events_tmp = soup.find(
                'div', {'class': 'content'}).find_all('div', {'class': 'news-float separator'})
        except requests.exceptions.RequestException as e:
            print(e)
            return []

        for event in events_tmp:

            title = event.find(
                'h3').text

            # get description
            link_to_event = 'https://www.it-world.ru' + event.find(
                'a', {'class': 'title-middle marker-future'}).get('href')
            try:
                r1 = requests.get(link_to_event)
            except requests.exceptions.RequestException as e:
                print(e)
                return []
            soup1 = BeautifulSoup(r1.text, "html.parser")
            description = self._parse_description(
                soup1.find('div', {'class': 'detail'}).text.split(
                    'Зарегистрироваться')[-1]
            )
            # gotten -------

            meta = link_to_event.split('/')[-1].split('.')[0]
            # for getting the page url you should get
            # https://www.it-world.ru/events/forums<meta>
            # it doesn't matter that the event might be not 'forums' type

            type = event.find('div').find('a').text

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
