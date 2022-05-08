from curses import raw
from pathlib import Path
from posixpath import split
from bs4 import BeautifulSoup, PageElement, ResultSet, Tag
import markdown
from manki.importer import base
from typing import Dict, List

from manki.qa_data_struct import QAChapter, QAItem, QAPackage
from manki.util import extract_html_between_tags, split_at_tags

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)


class MarkdownImporter(base.MankiImporter):
    def __init__(self, config):
        super().__init__(config)
        extensions = [
            "pymdownx.highlight",  # enable code highlighting
            "pymdownx.arithmatex",  # enable math via MathJax
            "pymdownx.betterem",  # better interpretation of emphasize chars
            "markdown.extensions.attr_list",  # enable attribute lists
            "markdown.extensions.def_list",  # enable 'definition' list type
            "markdown.extensions.tables",  # enable tables
            "markdown.extensions.md_in_html",  # enable markdown inside HTML
        ]

        extension_config = {
            "pymdownx.arithmatex": {
                "generic": False,
                "preview": False,
            },
            "pymdownx.highlight": {
                "use_pygments": True,
            },
        }

        self.md = markdown.Markdown(
            extensions=extensions,
            extension_configs=extension_config,
        )

    def create_package(self, raw_source: Dict[str, str]) -> QAPackage:
        """Convert and apped all markdown files to create one big file.
        Files will be sorted in alphabetical order by their h1 header.
        If they do not contain a h1 header, an error will be raised. If they contain more
        than one h1 header, the first occuring header is relevant for sorting.

        Args:
            raw_source (Dict[str, str]): _description_

        Returns:
            base.P: _description_
        """

        ht_sources = [self.md.convert(text) for text in raw_source.values()]
        sources_parsed = [BeautifulSoup(text, features="html.parser") for text in ht_sources]
        for source in sources_parsed:
            self._handle_media(source)
            chap_sources = split_at_tags("h1", source)
            for chap_source in chap_sources:
                chap = self._create_chapter(chap_source)
                self.package.add_chapter(chap)
        return self.package

    def _create_chapter(self, chapter_bs: BeautifulSoup) -> QAChapter:
        name = chapter_bs.find("h1").string
        chap = QAChapter(name)
        item_sources = split_at_tags("h2", chapter_bs)
        for item_source in item_sources:
            chap.add_item(self._create_item(item_source))
        return chap

    def _create_item(self, item_bs: BeautifulSoup) -> QAItem:
        h2_tag = item_bs.find("h2")
        answer, comment = [], []

        is_comment = False
        for next_sibling in h2_tag.find_next_siblings():
            if next_sibling.name == "hr":
                # if a ruler is present, everything after is treated as comment
                is_comment = True
            else:
                if is_comment:
                    comment.append(next_sibling)
                else:
                    answer.append(next_sibling)

        question_string = "".join([str(elem) for elem in h2_tag.contents])
        answer_string = "".join([str(elem) for elem in answer])
        comment_string = "".join([str(elem) for elem in comment]) if comment else None

        return QAItem(question_string, answer_string, comment_string)

    def _find_chapter_name(self, html: BeautifulSoup):
        h1: ResultSet = html.find_all("h1")
        if len(h1) > 1:
            raise ValueError("Too many top level header in the current HTML-string!")
        elif len(h1) == 0:
            return "Unnamed-Deck"
        else:
            return h1[0].contents[0]

    def _handle_media(self, bs: BeautifulSoup):
        for img in bs.find_all("img", recursive=True):
            root = Path(self.config["general"]["root"])
            img_path = root.joinpath(img.attrs["src"]).resolve()
            if img_path.exists():
                if not self._is_duplicate_image(img_path):
                    self.package.media.append(img_path)
                    img.attrs["src"] = img_path.name
                    logger.info("Using image: '%s' from '%s'", img.attrs["src"], img_path)
                else:
                    logger.debug("Skipping duplicate image %s", img.attrs["src"])
            else:
                logger.warning("Image at '%s' does not exists. Ignoring it.", img_path)

    def _is_duplicate_image(self, img_path: Path):
        for path in self.package.media:
            if path == img_path:
                logger.info("Reusing image '%s' from '%s'", img_path.name, img_path)
                return True
            elif path.name == img_path.name:
                logger.warning(
                    "A (different) image of name '%s' is already used. "
                    + "Please rename the image to prevent unwanted results! "
                    + "Current image is at '%s', but I already use an image at '%s'",
                    img_path.name,
                    img_path,
                    path,
                )
                return True
        return False
