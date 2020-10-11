from bs4 import BeautifulSoup
import requests
from nameko.rpc import rpc
from nameko.web.handlers import http
import json
import re
from datetime import datetime

_months_dict = {
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


def _parse_date(sdate):
    """Takes string dates from https://it-events.com/ and converts them to datetime objects

    Args:
        sdate (str): string that contains date or date range on one of the specified formats:

        1. "day(int) month(string) year(int)"

        2. "day(int) - day(int) month(string) year(int)"

        3. "day(int) month(string) year(int) - day(int) month(string) year(int)"

    Returns:
        [tuple(datetime, datetime)]: depending on string format we return start date
        which is the first tuple element and end date (second one). End date can be None
        which means we had only one date in string
    """

    spl = re.sub(' +', ' ', sdate).strip().split(' ')

    if len(spl) == 3:
        day = int(spl[0])
        month = _months_dict[spl[1]]
        year = int(spl[2])

        return (datetime(year, month, day), None)
    elif len(spl) == 5:
        day_1 = int(spl[0])
        day_2 = int(spl[2])
        month = _months_dict[spl[3]]
        year = int(spl[4])

        return (datetime(year, month, day_1), datetime(year, month, day_2))
    else:
        day_1 = int(spl[0])
        month_1 = _months_dict[spl[1]]
        year_1 = int(spl[2])
        day_2 = int(spl[4])
        month_2 = _months_dict[spl[5]]
        year_2 = int(spl[6])

        return (datetime(year_1, month_1, day_1), datetime(year_2, month_2, day_2))


def _read_events_from_page(page):
    """Reads upcoming events from one specific page on https://it-events.com/

    Args:
        page (BeautifulSoup): html page

    Returns:
        [list]: list of events as dictionaries
    """
    events = []

    for event in page.find_all("div", {"class": "event-list-item"}):

        _type = event.find("div", {"class": "event-list-item__type"})
        split = _type.string.replace("\n", "").split(" / ")

        type = split[0]
        isPaid = split[1]

        title_tag = event.find(
            "a", {"class": "event-list-item__title"})
        title = title_tag.string.replace("\n", "")
        meta_id = title_tag["href"].split('/')[-1]

        date = event.find(
            "div", {"class": "event-list-item__info"}).string.replace("\n", "")
        _location = event.find(
            "div", {"class": "event-list-item__info event-list-item__info_location"})
        _isOnline = event.find(
            "div", {"class": "event-list-item__info event-list-item__info_online"})

        location = _location.string.replace(
            "\n", "") if _location is not None else None
        isOnline = _isOnline.string.replace(
            "\n", "") if _isOnline is not None else None

        startDate, endDate = _parse_date(date)

        event_page_soup = BeautifulSoup(requests.get(
            "https://it-events.com" + title_tag["href"]).text, "html.parser")

        description_raw = event_page_soup.find(
            "div", {"class": "col-md-8 user-generated"})

        description = re.sub(' +', ' ', "".join(
            description_raw.find_all(text=True, recursive=True))).strip()

        events.append(
            {
                "title": title,
                "type": type,
                "isPaid": True if isPaid == "Платное" else False,
                "isOnline": True if isOnline is not None else False,
                "location": location,
                "startDate": startDate.strftime("%d:%m:%Y"),
                "endDate": endDate.strftime("%d:%m:%Y") if endDate is not None else None,
                "description": description,
                "meta": {
                    "https://it-events.com/": meta_id
                }
            }
        )

    return events


def read_events():
    """Recursively reads upcoming events from each page
    while there is next one on https://it-events.com/

    Returns:
        [list]: list of events as dictionaries
    """

    # TODO: async request process
    # we can try to use asyncio for this purpsoe

    events = []

    url = "https://it-events.com"
    content = requests.get(url)
    soup = BeautifulSoup(content.text, "html.parser")

    while True:
        events.append(_read_events_from_page(soup))

        next = soup.find("a", text="Следующая")

        if next is None:
            break
        else:
            content = requests.get(url + next["href"])
            soup = BeautifulSoup(content.text, "html.parser")

    return events


class ITEventsCrawler:
    name = "it_events_crawler"

    @rpc
    def get_upcoming_events(self):
        events = read_events()

        return events

    @http("GET", "/events")
    def get_upcoming_events_http(self, request):
        events = read_events()

        return json.dumps(events, ensure_ascii=False)
