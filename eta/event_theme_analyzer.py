from typing import Counter
from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from pymorphy2 import analyzer
from werkzeug.wrappers import Request
import re
import pymorphy2
import nltk
import json
import statistics
import numpy as np

nltk.download("stopwords")


class EventThemeAnalyzer:
    # Vars

    name = "event_theme_analyzer"
    tag_das = RpcProxy("tag_das")
    stop_words = stopwords.words("russian")
    morph = pymorphy2.MorphAnalyzer()

    # array of arrays fro tags where each inner array is a subset of aliases for tag

    # Logic

    def _preprocess(self, text) -> dict:
        text = text.lower()
        text = re.sub(r"""[,.;@?!&$/]+ \ *""", " ", text, flags=re.VERBOSE)
        text = re.sub(r"^\s+|\n|\r|\t|\s+$", "", text)
        text = " ".join([word for word in text.split(
            " ") if (word not in self.stop_words)])
        text = " ".join([t for t in text.split(" ") if len(t) > 0])
        text = " ".join(
            [self.morph.parse(word)[0].normal_form for word in text.split(" ")])
        return text

    def _analyze(self, text):
        text = self._preprocess(text)

        print("TEXT:\n{}\n\n".format(text))

        words = text.split(" ")

        tags = {}

        for word in words:
            loaded_tags = self.tag_das.get_tags_by_alias(word)

            for tag in loaded_tags:
                if tag["tag"] in tags:
                    tags[tag["tag"]] += 1
                else:
                    tags[tag["tag"]] = 1

        tag_num = np.sum([v for _, v in tags.items()])

        for key, value in tags.items():
            tags[key] = float(value / tag_num)

        print(tags)

        if len(tags) == 0:
            return []

        mean = statistics.mean([tags[key] for key in tags.keys()])

        print(mean)

        result = []

        for tag in tags.keys():
            if tags[tag] > mean:
                result.append(tag)

        return result

    # API

    @http("GET", "/preprocess")
    def preprocess_handler(self, request: Request):
        return 200, self._preprocess(request.get_data(as_text=True))

    @http("POST", "/analyze")
    def analyze_handler(self, request: Request):
        description = request.get_data(as_text=True)

        return 200, json.dumps(self._analyze(description), ensure_ascii=False)

    @rpc
    def analyze_events(self, events):
        for event in events:
            event["tags"].extend(self._analyze(event["description"]))

        return events
