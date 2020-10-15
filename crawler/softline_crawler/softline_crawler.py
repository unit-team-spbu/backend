import requests
from bs4 import BeautifulSoup
from nameko.rpc import rpc
from nameko.web.handlers import http
import json


class SoftlineCrawler:

    # Vars

    name = 'softline_crawler'
    _URL = 'https://softline.ru/events?page=1'
    # for testing & collecting data you may use the following url instead of the previous one
    # _URL = 'https://softline.ru/events/past?page=1'

    # Logic

    def _parse_date(self, tstr):
        cur_str = tstr
        cur_str = cur_str.replace('\n', "")
        cur_str = cur_str.replace('\t', "")
        cur_str = cur_str.replace(' ', "")
        cur_str = cur_str.replace('января', '.01.')
        cur_str = cur_str.replace('февраля', '.02.')
        cur_str = cur_str.replace('марта', '.03.')
        cur_str = cur_str.replace('апреля', '.04.')
        cur_str = cur_str.replace('мая', '.05.')
        cur_str = cur_str.replace('июня', '.06.')
        cur_str = cur_str.replace('июля', '.07.')
        cur_str = cur_str.replace('августа', '.08.')
        cur_str = cur_str.replace('сентября', '.09.')
        cur_str = cur_str.replace('октября', '.10.')
        cur_str = cur_str.replace('ноября', '.11.')
        cur_str = cur_str.replace('декабря', '.12.')
        return cur_str

    def get_events(self) -> list:
        url = self._URL
        is_next = True
        events = []

        while is_next:
            try:
                r = requests.get(url)
            except requests.exceptions.RequestException as e:
                print(e)
                return []
            soup = BeautifulSoup(r.text, "html.parser")

            # all events on the page
            try:
                events_tmp = soup.find(
                    'div', {'id': 'events-items'}).find_all('div', {'class': 'b-section__in'})
            except requests.exceptions.RequestException as e:
                print(e)
                return []

            for event in events_tmp:

                title = event.find(
                    'a', {'class': 'b-section__title-text b-link'}).text

                description = event.find(
                    'div', {'class': 'b-section__summary'})
                if description:
                    description = description.text

                dateStart_tmp = event.find(
                    'span', {'itemprop': 'startDate'}).text.split(',')
                if len(dateStart_tmp) == 3:
                    location = dateStart_tmp[0]
                    startDate = self._parse_date(dateStart_tmp[1])
                    isOnline = False
                else:
                    location = None
                    startDate = self._parse_date(dateStart_tmp[0])
                    isOnline = True
                dateEnd_tmp = event.find(
                    'span', {'itemprop': 'endDate'}).text.split(',')
                if len(dateEnd_tmp) == 2:
                    endDate = self._parse_date(dateEnd_tmp[0])
                else:
                    endDate = None

                meta = event.find(
                    'a', {'class': 'b-section__title-text b-link'}).get("href").split('/')[-1]

                events.append({
                    "title": title,
                    "type": None,
                    "isPaid": None,
                    "isOnline": isOnline,
                    "location": location,
                    "startDate": startDate,
                    "endDate": endDate,
                    "description": description,
                    "meta": {
                        self.name: meta
                    }
                })

            # go to the next page
            next_url = soup.find(
                'a', {'class': 'b-pagination__next b-link b-i b-i_content_pagination-desktop-right-arrow'}).get('href')
            if next_url:
                url = next_url
            else:
                is_next = False

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
