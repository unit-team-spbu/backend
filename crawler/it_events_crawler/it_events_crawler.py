from nameko.web.handlers import http
from nameko.rpc import rpc
from bs4 import BeautifulSoup
from typing import Tuple
import requests
import json
import math
import re

# TODO: find & impl reliable and centralized logging for crawler


class ITEventsCrawler:
    # Vars

    name = "it_events_crawler"
    _URL = "https://it-events.com"
    _MONTHS = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12}

    # Logic

    def _parse_date(self, date: str) -> Tuple[str, str]:
        """Converts date in it-events.com format our format dd/mm/YYYY

        Args:
            date (str): of one of the following formats

            1. day(int) month(str) year(int)
            2. day(int) - day(int) month(str) year(str)
            3. day(int) month(str) year(str) - day(int) month(str) year(str)

        Returns:
            Tuple[str, str]: start and end date pair. End date might be None (for 1st case)
        """
        spld = re.sub(' +', ' ', date).strip().split(' ')

        if len(spld) == 3:
            day = int(spld[0])
            month = self._MONTHS[spld[1]]
            year = int(spld[2])

            return ("{}/{}/{}".format(day, month, year), None)
        elif len(spld) == 5:
            day_1 = int(spld[0])
            day_2 = int(spld[2])
            month = self._MONTHS[spld[3]]
            year = int(spld[4])

            return ("{}/{}/{}".format(day_1, month, year), "{}/{}/{}".format(day_2, month, year))
        else:
            day_1 = int(spld[0])
            month_1 = self._MONTHS[spld[1]]
            year_1 = int(spld[2])
            day_2 = int(spld[4])
            month_2 = self._MONTHS[spld[5]]
            year_2 = int(spld[6])

            return ("{}/{}/{}".format(day_1, month_1, year_1), "{}/{}/{}".format(day_2, month_2, year_2))

    def _parse_is_paid(self, soup: BeautifulSoup) -> bool:
        """From page content finds out of event is paid or not

        Args:
            soup (BeautifulSoup): event page

        Returns:
            bool: event is paid?
        """
        return soup.find("div", {
            "class": "event-header__line event-header__line_icon event-header__line_icon_price"}
        ).text != "Участие бесплатное"

    def _parse_meta(self, soup: BeautifulSoup) -> dict:
        """From page content finds out meta-information about event

        Args:
            soup (BeautifulSoup): event page

        Returns:
            dict: pair of info source http address and event ID in the IS 
        """
        return {
            self._URL: (soup.find("a", {"class": "header__item"})[
                "href"]).split('/')[-1]
        }

    def _parse_description(self, soup: BeautifulSoup) -> str:
        """From page content gets text that describes event

        Args:
            soup (BeautifulSoup): event page

        Returns:
            str: text that describes event
        """
        description_raw = soup.find(
            "div", {"class": "col-md-8 user-generated"})

        description = re.sub(' +', ' ', "".join(
            description_raw.find_all(text=True, recursive=True))).strip()

        return description

    def _parse_event(self, soup: BeautifulSoup) -> dict:
        """Parses entire event from page

        Args:
            soup (BeautifulSoup): event page

        Returns:
            dict: event object as dictionary (for easy json conversion)
        """
        title, type, location_online, date = soup.find(
            "title").text.split(" / ")

        startDate, endDate = self._parse_date(date)

        location_online_split = location_online.split(", ")

        is_online = location_online_split[-1] == "Онлайн трансляция"

        location = ", ".join(location_online_split[:-1])

        return {
            "title": title,
            "type": type,
            "isPaid": self._parse_is_paid(soup),
            "isOnline": is_online,
            "location": location,
            "startDate": startDate,
            "endDate": endDate,
            "description": self._parse_description(soup),
            "meta": self._parse_meta(soup)
        }

    def _get_event_urls(self) -> list:
        """Scarps https://it-events.com for event urls

        Returns:
            list: of event urls as strs
        """
        soup = BeautifulSoup(requests.get(self._URL).text, "html.parser")

        upcoming_nav_soup = soup.find(
            "li", {"class": "nav-tabs-item nav-tabs-item_active nav-tabs-item_main"})

        upcoming_events_count = int(upcoming_nav_soup.find(
            "span", {"class": "nav-tabs-item__count"}).text)

        page_count = math.ceil(upcoming_events_count / 20)

        page_urls = [self._URL + "/?page={}".format(i)
                     for i in range(1, page_count + 1)]

        event_urls = []

        for url in page_urls:
            res = requests.get(url)

            page_soup = BeautifulSoup(res.text, "html.parser")

            event_links = page_soup.find_all(
                "a", {"class": "event-list-item__title"})

            event_urls.extend([self._URL + event_link["href"]
                               for event_link in event_links])

        return event_urls

    def get_events(self) -> list:
        """Parses all upcoming events from https://it-events.com

        Returns:
            list: of events as dictionaries for easy json encoding
        """
        event_urls = self._get_event_urls()

        print(
            "Acquiring information about {} of upcoming events".format(len(event_urls)))

        events = []

        for url in event_urls:
            print(
                "Parsing event at {}".format(url))

            res = requests.get(url)

            event_soup = BeautifulSoup(res.text, "html.parser")

            events.append(self._parse_event(event_soup))

        return events

    # API

    @rpc
    def get_upcoming_events(self):
        events = self.get_events()
        return events

    @http("GET", "/events")
    def get_upcoming_events_http(self, request):
        events = self.get_events()

        # ensure_ascii=True due to cyrillic symbols
        return json.dumps(events, ensure_ascii=False)
