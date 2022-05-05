import importlib.resources as pkg_resources
import json
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement, ResultSet
from genanki import Note, Deck, Model, Package
from .deck import AnkiDeck
from typing import List, Union

import markdown
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)


def _find_deck_name(html):
    h1: ResultSet = html.find_all("h1")
    if len(h1) > 1:
        raise ValueError("Too many top level header in the current HTML-string!")
    elif len(h1) == 0:
        return "Unnamed-Deck"
    else:
        return h1[0].contents[0]


class Html2AnkiDeck:
    def __init__(self, raw_html: str, model: Model, root: Union[Path, str]):
        raw_html = raw_html.replace("\n", "")
        splitted = ["<h1" + i for i in raw_html.split("<h1") if i]
        self.html_raw = [BeautifulSoup(i, features="html.parser") for i in splitted]
        self.model: Model = model
        self.media = []
        self.decks = []
        self._root: Path = Path(root)

    def generate_decks(self):
        for raw in self.html_raw:
            name = _find_deck_name(raw)
            deck = AnkiDeck(name)
            deck.add_model(self.model)
            self.decks.append(self._generate_notes(raw, deck))

    def _generate_notes(self, html, deck):
        h2: Tag
        for i, h2 in enumerate(html.find_all("h2")):
            self._handle_media(h2)
            question = "".join([str(elem) for elem in h2.contents])

            answer, comment = self._extract_answer_and_comment(h2)

            default_model = list(deck.models.values())[0]
            note = Note(model=default_model)
            logger.debug("Found question %d: '%s'", i, question)
            logger.debug("Found answer   %d: '%s'", i, answer)
            note.fields = [question, answer]

            if comment:
                logger.debug("Found comment: '%s'", comment)
                # note.fields.append(comment)

            deck.add_note(note)
        return deck

    def _extract_answer_and_comment(self, h2_tag):
        answer, comment = [], []
        is_comment = False
        for next_sibling in h2_tag.find_next_siblings():
            if next_sibling is None or next_sibling.name == "h2":
                # if the next sibling is another question (h2-tag), break the loop
                break
            elif next_sibling.name == "hr":
                # if a ruler is present, everything after is treated as comment
                is_comment = True
            else:
                if is_comment:
                    comment.append(next_sibling)
                else:
                    answer.append(next_sibling)

        self._handle_media(answer)
        self._handle_media(comment)

        answer_string = "".join([str(elem) for elem in answer])
        comment_string = "".join([str(elem) for elem in comment])

        return answer_string, comment_string

    def _handle_media(self, elements: List[PageElement]):
        for elem in elements:
            if isinstance(elem, Tag):
                img: Tag
                for img in elem.find_all("img", recursive=True):
                    img_path = self._root.joinpath(img.attrs["src"]).resolve()
                    if img_path.exists():
                        if not self._is_duplicate_image(img_path):
                            self.media.append(img_path)
                            img.attrs["src"] = img_path.name
                            logger.debug("Found image: '%s' at '%s'", img.attrs["src"], img_path)
                        else:
                            logger.debug("Skipping duplicate image")
                    else:
                        logger.warning("Image at '%s' does not exists. Ignoring it.", img_path)

    def _is_duplicate_image(self, img_path: Path):
        for path in self.media:
            if path == img_path:
                logger.info(
                    "Reusing image '%s' at '%s'",
                    img_path.name,
                    img_path,
                )
                return False
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


class Markdown2AnkiDeck:
    def __init__(self, raw_markdown: Union[Path, str], model: Model, root: Union[Path, str]):
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
                "generic": True,
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

        if isinstance(raw_markdown, Path):
            raw_markdown = "".join(open(raw_markdown, mode="r").readlines())

        self.html = self.md.convert(raw_markdown)
        self.root: Path = Path(root)
        hc = Html2AnkiDeck(self.html, model, self.root)
        hc.generate_decks()
        self.decks = hc.decks
        self.media = hc.media

    pkg_resources.read_text("manki.templates", "mathjax_header.html")
