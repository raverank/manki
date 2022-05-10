import html
from pathlib import Path
from typing import Dict, Any, List

from pygments.formatters import HtmlFormatter

from manki.qa_data_struct import QAPackage
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
    def __init__(self, config, name: str):
        super(TemplateModel, self).__init__(name=name)

        self.model_id = get_hash(name)
        logger.debug("Creating new model '%s' with ID '%i'", name, self.model_id)

        template_name = deep_get(config, "general.template", "default")
        template_module = f"manki.templates.{template_name}"
        template_properties = dict()
        for prop, file_name in {
            "qfmt": "qfmt.html",
            "afmt": "afmt.html",
            "css": "style.css",
        }.items():
            try:
                template_properties[prop] = pkg_resources.read_text(template_module, file_name)
                logger.debug(
                    "Read template definition '%s' from '%s'",
                    prop,
                    pkg_resources.path(template_module, file_name),
                )
            except ModuleNotFoundError:
                logger.error("The requested template '%s' could not be found!", template_name)
            except FileNotFoundError:
                logger.error("Could not find the '%s' definition '%s'!", prop, file_name)

        self.set_fields(
            [
                {"name": "Front"},
                {"name": "Back"},
            ]
        )

        macros_file = deep_get(config, "input.macros", None)
        macros = ""
        if macros_file:
            root: Path = deep_get(config, "general.root")
            macros_file = root.joinpath(macros_file).resolve()
            macros = open(macros_file, mode="r").read()
            macros = "<div overflow: hidden>\\(" + macros.strip().strip("$") + "\\)</div>\n"

        self.set_templates(
            [
                {
                    "name": "Card",
                    "qfmt": macros + template_properties["qfmt"],
                    "afmt": template_properties["afmt"],
                }
            ]
        )

        self.css = template_properties["css"] or ""

        # append pygments css for code highlighting
        try:
            pygments_css = pkg_resources.read_text(template_module, "pygments.css")
            logger.debug(
                "Read pygments higlighing style sheet from '%s'",
                pkg_resources.path(template_module, file_name),
            )
        except FileNotFoundError:
            logger.debug("No pygments style 'pygments.css' provided. Using 'friendly' fallback")
            fmt = HtmlFormatter(style="friendly")
            pygments_css = fmt.get_style_defs()
            
        self.css += "\n\n" + pygments_css
            


class AnkiExporter(MankiExporter):
    def __init__(self, config: Dict[str, Any], package: QAPackage):
        super().__init__(config, package)
        sanitized_title = sanitize_string(self.package.title)
        model = TemplateModel(config, sanitized_title + "_model")

        decks = [
            Deck(
                get_hash(sanitized_title + "_deck"),
                self.package.title,
                deep_get(config, "general.preamble", ""),
            )
        ]

        for chap in self.package.chapters:
            chap_name = self.package.title + "::" + chap.title
            deck = Deck(deck_id=chap.chapter_id, name=chap_name)
            deck.add_model(model=model)
            for item in chap.items:
                fields = [item.question, item.answer]
                logger.debug("New Item with fields\nQuesion: %s\nAnswer: %s", fields[0], fields[1])
                note = Note(model=model, fields=fields, guid=item.item_id)
                deck.add_note(note)
            decks.append(deck)

        self.apkg = Package(decks, self.package.media)

    def export(self):
        file_name = sanitize_string(self.package.title) + ".apkg"
        n_decks = len(self.package.chapters)
        n_cards = 0
        for chp in self.package.chapters:
            n_cards += len(chp.items)
        logger.info("Exporting '%s' with '%d' decks and %d cards in total", file_name, n_decks, n_cards)
        self.apkg.write_to_file(file_name)
