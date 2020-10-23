from typing import final
from nameko.rpc import rpc
from nameko_mongodb import MongoDatabase
from nameko.web.handlers import http
from bs4 import BeautifulSoup
import pymongo
import requests
import json


class TagDAS:
    # Vars

    name = "tag_das"
    db = MongoDatabase()
    _PAGE_SIZE = 20

    # Logic

    def _parse_tags_from_page(self, soup: BeautifulSoup) -> list:

        page_tags = []

        hub_soup = soup.find("ul", {"id": "hubs"})

        tag_soups = hub_soup.find_all(
            "li", {"class": "content-list__item_hubs"})

        for tag_soup in tag_soups:

            title_tag = tag_soup.find(
                "a", {"class": "list-snippet__title-link"})

            if not title_tag:
                print("Failed to get title for tag")
                continue

            title = title_tag.text

            snippet_tags = tag_soup.find(
                "div", {"class": "list-snippet__tags"})

            if not snippet_tags:
                print("Failed to get snippet tags")
                continue

            aliases = "".join(snippet_tags.find_all(text=True))

            tag_aliases = aliases.split(", ")

            rating_tag = tag_soup.find(
                "div", {"class": "stats__counter_rating"})
            try:
                rating = float(rating_tag.text.replace(",", "."))
            except:
                rating = 0.0
                pass

            tag = {
                "tag": title,
                "aliases": tag_aliases,
                "rating": rating
            }

            page_tags.append(tag)

        return page_tags

    def _upload_tags(self):
        _HABR_HUBS_URL = "https://habr.com/ru/hubs/"

        tags = []

        res = requests.get(_HABR_HUBS_URL)

        soup = BeautifulSoup(res.text, "html.parser")

        last_page_title = soup.find("a", {"title": "Последняя страница"})

        if last_page_title:
            href = last_page_title["href"]
            pageNumber = int([s for s in href.split("/") if s != ""][-1][4:])

        else:
            raise Exception("Can't update tags due to lack of page count")

        for i in range(1, pageNumber+1):
            print("Processing page: {}".format(i))

            page = requests.get(_HABR_HUBS_URL + "page{}/".format(i))

            # print("Successfully got page via HTTP: {}".format(page is None))

            soup = BeautifulSoup(page.text, "html.parser")

            print("Successfully generated soup from page: {}".format(soup is None))

            tags += self._parse_tags_from_page(soup)

        return tags

    # API

    @http("GET", "/tags/upload")
    def upload_tags_handler(self, _):
        collection = self.db["tags"]

        tags = self._upload_tags()

        for tag in tags:
            collection.update({"tag": tag["tag"]}, tag, upsert=True)

        return 200, ""

    @http("GET", "/tags")
    def get_tags_handler(self, _):
        collection = self.db["tags"]

        tags = collection.find({}).sort("rating", pymongo.DESCENDING)

        result = []

        for tag in tags:
            del tag["_id"]
            result.append(tag)

        return 200, json.dumps(result, ensure_ascii=False)

    @http("GET", "/tags/<int:page>")
    def get_tags_by_page_handler(self, _, page):
        collection = self.db["tags"]

        tags = collection.find({}).sort("rating", pymongo.DESCENDING).skip(
            self._PAGE_SIZE * (page - 1)).limit(self._PAGE_SIZE)

        result = []

        for tag in tags:
            del tag["_id"]
            result.append(tag)

        return 200, json.dumps(result, ensure_ascii=False)

    @http("GET", "/tag/<string:alias>")
    def get_tag_by_alias(self, _, alias):
        collection = self.db["tags"]

        tags = collection.find({"aliases": alias})

        result = []

        for tag in tags:
            del tag["_id"]
            result.append(tag)

        return 200, json.dumps(result, ensure_ascii=False)

    @rpc
    def get_tags(self):
        collection = self.db["tags"]

        tags = collection.find({}).sort("rating", pymongo.DESCENDING)

        result = []

        for tag in tags:
            del tag["_id"]
            result.append(tag)

        return result

    @rpc
    def get_tags_by_page(self, page):
        collection = self.db["tags"]

        tags = collection.find({}).sort("rating", pymongo.DESCENDING).skip(
            self._PAGE_SIZE * (page - 1)).limit(self._PAGE_SIZE)

        result = []

        for tag in tags:
            del tag["_id"]
            result.append(tag)

        return result

    @rpc
    def get_tags_by_alias(self, alias):
        collection = self.db["tags"]
        print(alias)

        tags = collection.find({"aliases": alias})

        result = []

        for tag in tags:
            print(tag)
            del tag["_id"]
            result.append(tag)

        return result
