from pathlib import Path
from typing import Dict, Any, ItemsView, List
from bs4 import BeautifulSoup, Tag

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

import weasyprint
import pdfkit


class PdfExporter(MankiExporter):
    def __init__(self, config: Dict[str, Any], package: QAPackage):
        super().__init__(config, package)
        sanitized_title = sanitize_string(self.package.title)

        template_name = deep_get(config, "general.template", "default")
        template_module = f"manki.templates.{template_name}"
        self.html = pkg_resources.read_text(template_module, "htmlpage.html")
        self.html = self.html.replace(r"{{Title}}", self.package.title)

        macros_file = deep_get(config, "input.macros", None)
        macros = ""
        if macros_file:
            root: Path = deep_get(config, "general.root")
            macros_file = root.joinpath(macros_file).resolve()
            macros = open(macros_file, mode="r").read().strip().strip("$")

        self.html = self.html.replace(r"{{Macros}}", "\\(" + macros + "\\)")

        style = pkg_resources.read_text(template_module, "htmlstyle.css")
        self.html = self.html.replace(r"{{Style}}", style)

        qas = []
        qa_template = pkg_resources.read_text(template_module, "htmlqa.html")
        for chap in self.package.chapters:
            qas.append("<h2>" + chap.title + "</h2>")
            for item in chap.items:
                item_str = qa_template
                item_str = item_str.replace(r"{{Front}}", item.question)
                item_str = item_str.replace(r"{{Back}}", item.answer)
                qas.append(item_str)

        qas = "\n\n".join(qas)

        self.html = self.html.replace(r"{{QA}}", qas)
        
        soup = BeautifulSoup(self.html, features="html.parser")
        for img in soup.find_all("img"):
            replaced = False
            for media in self.package.media:
                if media.name == img.attrs["src"]:
                    logger.info("Updating '%s' with '%s'", img.attrs["src"], media.resolve())
                    img.attrs["src"] = media.resolve()
                    replaced = True
            if not replaced:
                logger.warning("Could not replace %s", img.attrs["src"])
            
        self.html = str(soup)

    def export(self):
        file_name = sanitize_string(self.package.title) + ".pdf"
        n_decks = len(self.package.chapters)
        n_cards = 0
        for chp in self.package.chapters:
            n_cards += len(chp.items)
        logger.info("Exporting '%s' with '%d' decks and %d cards in total to pdf", file_name, n_decks, n_cards)

        pdf = pdfkit.from_string(self.html, options={"enable-local-file-access": ""})
        # pdf = weasyprint.HTML(string=self.html).write_pdf()
        with open(file_name, "wb") as f:
            f.write(pdf)
