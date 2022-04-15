import importlib.resources as pkg_resources
import json
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement
from genanki import Note, Deck, Model, Package
from typing import List
from manki import templates
import markdown
import logging
from pathlib import Path


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Html2Anki:
    def __init__(self, raw_html: str, deck: Deck, root: str):
        raw_html = raw_html.replace("\n", "")
        self._raw = BeautifulSoup(raw_html, features="html.parser")
        self.deck: Deck = deck
        self.media = []
        self._root: Path = Path(root)
        self._generate_notes()

    def _generate_notes(self):
        h2: Tag
        for i, h2 in enumerate(self._raw.find_all("h2")):
            self._handle_media(h2)
            question = "".join([str(elem) for elem in h2.contents])

            answer, comment = self._extract_answer_and_comment(h2)

            default_model = list(self.deck.models.values())[0]
            note = Note(model=default_model)
            logger.debug("Found question: '%s'", question)
            logger.debug("Found answer: '%s'", answer)
            note.fields = [question, answer]

            if comment:
                logger.debug("Found comment: '%s'", comment)
                # note.fields.append(comment)

            self.deck.add_note(note)

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
                            logger.debug(
                                "Found image: '%s' at '%s'", img.attrs["src"], img_path
                            )
                        else:
                            logger.debug("Skipping duplicate image")
                    else:
                        logger.warning(
                            "Image at '%s' does not exists. Ignoring it.", img_path
                        )

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


class Md2Html:
    def __init__(self, raw_markdown: str, deck: Deck, root: str):
        extensions = [
            "pymdownx.highlight",
            "pymdownx.arithmatex",
            "pymdownx.extra",
            "md_in_html",
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
        self.deck = deck
        self.html = self.md.convert(raw_markdown)
        self.root: Path = Path(root)
        hc = Html2Anki(self.html, self.deck, self.root)
        self.media = hc.media

    pkg_resources.read_text(templates, "mathjax_header.html")


if __name__ == "__main__":
    root = Path("./../../tests/data/test_plain")
    with open(root.joinpath("test_plain.md"), mode="r") as f:
        content = f.read()
        deck = Deck(deck_id=1, name="Test")
        model = Model(
            1607392319,
            "Simple Model",
            fields=[
                {"name": "Front"},
                {"name": "Back"},
            ],
            css=".card {\n  font-family: arial;\n  font-size: 20px;\n  text-align: left;\n  color: black;\n  background-color: white;\n}\n\n.question {\n  color: white;\n  background-image: linear-gradient(to bottom, #2e5c8a, #193552);\n  padding: 0.5em;\n  border-radius: 0.2em;\n}\n\n.solution {\n  color: black;\n  padding: 0.3em;\n}",
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": '<div class="question">{{Front}}</div>',
                    "afmt": '{{FrontSide}}\n\n<div class="solution">\n{{Back}}\n</div>',
                },
            ],
        )
        deck.add_model(model)
        mc = Md2Html(content, deck, root)
        notes = [n.fields for n in mc.deck.notes]

        print(notes)
        print(json.dumps(notes))
        # question: str = note.fields[0]
        # answer: str = note.fields[1]
        # print(f'["{question.e}", "{answer}"]')
        # print(mc.html)
        # pck = Package(deck_or_decks=deck, media_files=mc.media)
        # deck.description = "my description"
        # pck.write_to_file("foobar.apkg")
        # deck.write_to_file("foobar.apkg")

    # with open("./../../tests/data/html_questions.html", mode="r") as f:
    #     content = f.read()
    #     hc = HTMLConverter(content)
    #     [print(n.fields) for n in hc.notes]
