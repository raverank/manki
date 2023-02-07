import html
from pathlib import Path
from typing import Dict, Any, List
from bs4 import BeautifulSoup

from pygments.formatters import HtmlFormatter
from manki.configuration import MankiConfig

from manki.data_struct import QAItem, QAPackage
from .base import MankiExporter
from manki.util import deep_get, sanitize_string, get_hash
from genanki import Deck, Model, Package, Note
from rich import print, inspect
import importlib.resources as pkg_resources


import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)


class TemplateModel(Model):
    def __init__(self, config: MankiConfig, name: str):
        super(TemplateModel, self).__init__(name=name)

        self.model_id = get_hash(name)
        self.config: MankiConfig = config
        logger.debug("Creating new model '%s' with ID '%i'", name, self.model_id)

        self.set_fields(
            [
                {"name": "Front"},
                {"name": "Back"},
            ]
        )

        macros = self._get_macros()
        question = self.config.render_template("anki/question.html.j2")
        answer = self.config.render_template("anki/answer.html.j2")
        self.set_templates(
            [
                {
                    "name": "Card",
                    "qfmt": macros + question,
                    "afmt": answer,
                }
            ]
        )

        self.css = self.config.render_template("anki/style.css.j2")

    def _get_macros(self) -> str:
        macros_file = self.config.get("input.macros", None)
        macros = ""
        if macros_file:
            root: Path = self.config.get("general.root")
            macros_file = root.joinpath(macros_file).resolve()
            macros = open(macros_file, mode="r").read()
            macros = "<div overflow: hidden>\\(" + macros.strip().strip("$") + "\\)</div>\n"
        return macros


class AnkiExporter(MankiExporter):
    def __init__(self, config: MankiConfig, package: QAPackage):
        super().__init__(config, package)
        sanitized_title = sanitize_string(self.package.title)
        model = TemplateModel(config, sanitized_title + "_model")

        decks = [
            Deck(
                get_hash(sanitized_title + "_deck"),
                self.package.title,
                self.config.render_template("anki/preamble.html.j2"),
            )
        ]

        for chap in self.package.chapters:
            chap_name = self.package.title + "::" + chap.title
            deck = Deck(deck_id=chap.chapter_id, name=chap_name)
            deck.add_model(model=model)
            for item in chap.items:
                self._fix_img_src_name(item)
                fields = [item.question, item.answer]
                logger.debug("New Item with fields\nQuesion: %s...\nAnswer: %s...", fields[0][:50], fields[1][:50])
                note = Note(model=model, fields=fields, guid=item.item_id)
                deck.add_note(note)
            decks.append(deck)

        self.apkg = Package(decks, self.package.media)

    def _fix_img_src_name(self, item: QAItem):
        """Anki expects the source of the images to be only the stem of the filepath. So instead of `<img
        src="/foo/bar/image.png"/>` it expects `<img
        src="image.png"/>`

        Args:
            item (QAItem): The item for which the names should be fixed
        """

        def _fix(field):
            if field is None:
                return None

            field_bs = BeautifulSoup(field, features="html.parser")
            for img in field_bs.find_all("img", recursive=True):
                img_path = Path(img.attrs["src"])
                img.attrs["src"] = img_path.name
            return str(field_bs)

        item.question = _fix(item.question)
        item.answer = _fix(item.answer)
        item.comment = _fix(item.comment)

    def export(self):
        file_name = sanitize_string(self.package.title) + ".apkg"
        n_decks = self.package.n_chapters
        n_cards = self.package.n_items
        logger.info("Exporting '%s' with '%d' decks and %d cards in total", file_name, n_decks, n_cards)
        self.apkg.write_to_file(file_name)
