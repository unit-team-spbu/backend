import json
import re
import statistics

import nltk
import numpy as np
import pymorphy2
from nameko.rpc import RpcProxy, rpc
from nameko.web.handlers import http
from nltk.corpus import stopwords
from werkzeug.wrappers import Request

nltk.download("stopwords")

# ! this hand-written tags were sopposed to be a bit odd
# tags = [
#     {
#         "tag": "WEB",
#         "aliases": [
#             "js",
#             "javascript",
#             "ts",
#             "typescript",
#             "css",
#             "html",
#             "es5",
#             "es6",
#             "asp.net",
#             "css3",
#             "html5",
#             "php",
#             "webassembly",
#             "web",
#             "веб",
#             "сайт",
#             "nodejs",
#             "node",
#             "react",
#             "angular",
#             "vue"
#         ]
#     },
#     {
#         "tag": "GD",
#         "aliases": [
#             "unity",
#             "unreal",
#             "игра",
#             "gamedev",
#             "игры",
#             "unity3d",
#             "c#",
#             "c++"
#         ]
#     },
#     {
#         "tag": "mobile",
#         "aliases": [
#             "android",
#             "ios",
#             "kotlin",
#             "java",
#             "google"
#             "мобил",
#             "мобильный"
#         ]
#     },
#     {
#         "tag": "robot",
#         "aliases": [
#             "робототехника",
#             "робот",
#             "дрон",
#             "ros",
#             "arduino",
#             "raspberry",
#             "микроконтроллеры"
#         ]
#     },
#     {
#         "tag": "devops",
#         "aliases": [
#             "devops",
#             "docker",
#             "jenkins",
#             "container",
#             "контейнер",
#             "развертка",
#             "kubernetes",
#             "ansible",
#             "k8s",
#             "слёрм",
#             "gitlab",
#             "linux",
#             "ci/cd",
#             "ci",
#             "cd"
#         ]
#     },
#     {
#         "tag": "qa",
#         "aliases": [
#             "qa",
#             "testing",
#             "selenium",
#             "tdd"
#             "тест",
#             "тестирование",
#             "тестировщик"
#         ]
#     },
#     {
#         "tag": "ds",
#         "aliases": [
#             "machine",
#             "learning",
#             "python",
#             "hadoop",
#             "bigdata",
#             "data",
#             "neural",
#             "нейроны",
#             "нейроный",
#             "анализ"
#             "данные"
#             "r",
#             "mining",
#             "искуственный"
#         ]
#     },
#     {
#         "tag": "ui",
#         "aliases": [
#             "интерфейсы",
#             "интерфейс",
#             "юзабилити",
#             "usability",
#             "дизайн",
#             "ux",
#             "ui",
#             "interface",
#         ]
#
# # ! this hand-written tags were sopposed to be a bit odd    }
# ]


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
            # TODO: replace this with call of tag_das
            # selected_tags = [t["tag"] for t in tags if word in t["aliases"]]
            selected_tags = self.tag_das.get_tags_by_alias(word)

            print("For word: {} tags are: {}".format(word, selected_tags))

            for tag in selected_tags:
                if tag["tag"] in tags:
                    tags[tag["tag"]] += 1
                else:
                    tags[tag["tag"]] = 1

        tag_num = np.sum([v for _, v in tags.items()])

        for key, value in tags.items():
            tags[key] = float(value / tag_num)

        print("Tags: {} ".format(tags))

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
