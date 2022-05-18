from manki.configuration import MankiConfig
from .base import MankiProcessor
from typing import Dict, Any
from manki.util import deep_get
from manki.data_struct import QAItem, QAPackage
import random


class RandomQuestionProcessor(MankiProcessor):
    def __init__(self, config: MankiConfig, package: QAPackage):
        super().__init__(config, package)

    def _deep_get(self, key, default=None):
        return self.config.get("processor.randomquestions." + key, default=default)

    def process(self):
        max_qa = self._deep_get("max_questions", 3)
        start_after = self._deep_get("start_after", 5)
        qas = self._deep_get("questions", "foo")
        items = [QAItem(q, a) for q, a in qas]

        n_cards = 0
        for chp in self.package.chapters:
            n_cards += len(chp.items)

        positions = [random.choice(range(start_after, n_cards)) for _ in range(max_qa)]
        positions = sorted(positions)
        items = [random.choice(items) for _ in range(max_qa)]

        i = 0  # the total count of items seen so far (incementing)
        j = 0  # the current index that gets the random questions and its index
        for chp in self.package.chapters:
            # this loops through all chapters and checks if a random question has to be
            # inserted in the
            chp_items = len(chp.items)
            while j < max_qa and positions[j] < i + chp_items:
                chp.items.insert(positions[j], items[j])
                j += 1
                chp_items += 1
            i += chp_items
