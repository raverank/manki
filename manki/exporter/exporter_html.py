from pathlib import Path
from pprint import pprint
from typing import Dict, Any, ItemsView, List
from bs4 import BeautifulSoup, Tag

from pygments.formatters import HtmlFormatter
from manki.configuration import MankiConfig

from manki.data_struct import QAPackage
from .base import MankiExporter
from manki.util import deep_get, sanitize_string, get_hash
from genanki import Deck, Model, Package, Note
from rich import print, inspect
import importlib.resources as pkg_resources


import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)


class HTMLExporter(MankiExporter):
    def __init__(self, config: MankiConfig, package: QAPackage):
        super().__init__(config, package)

        macros = self._get_macros()
        self.config.set("input.macros", macros)
        self.html = self.config.render_template("html/page.html.j2")

    def export(self):
        file_name = sanitize_string(self.package.title) + ".html"
        n_decks = self.package.n_chapters
        n_cards = self.package.n_items
        logger.info("Exporting '%s' with '%d' decks and %d cards in total to html", file_name, n_decks, n_cards)

        with open(file_name, "w+") as f:
            f.write(self.html)

    def _get_macros(self) -> str:
        macros_file = self.config.get("input.macros", None)
        macros = ""
        if macros_file:
            root: Path = self.config.get("general.root")
            macros_file = root.joinpath(macros_file).resolve()
            macros = open(macros_file, mode="r").read()
            macros = "<div overflow: hidden>\\(" + macros.strip().strip("$") + "\\)</div>\n"
        return macros
