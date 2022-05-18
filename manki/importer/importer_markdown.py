from dataclasses import asdict
from pathlib import Path
from bs4 import BeautifulSoup, ResultSet, Tag
import markdown
from manki.configuration import MankiConfig
from manki.importer import base
from typing import Dict, Union

from manki.data_struct import QAChapter, QAItem, QAPackage
from manki.util import split_at_tags
from rich import print
from htmlmin import minify


import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)


class MarkdownImporter(base.MankiImporter):
    def __init__(self, config: MankiConfig):
        super().__init__(config)
        extensions = [
            "mdx_math",  # enable mathjax output
            "pymdownx.highlight",  # enable code highlighting
            "pymdownx.superfences",
            "pymdownx.betterem",  # better interpretation of emphasize chars
            "markdown.extensions.attr_list",  # enable attribute lists
            "markdown.extensions.def_list",  # enable 'definition' list type
            "markdown.extensions.tables",  # enable tables
        ]

        extension_config = {
            "mdx_math": {"enable_dollar_delimiter": True},
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
        sources_parsed = [self._fix_math(bs) for bs in sources_parsed]
        for source in sources_parsed:
            chap_sources = split_at_tags("h1", source)
            for chap_source in chap_sources:
                chap = self._create_chapter(chap_source)
                self.package.add_chapter(chap)
        return self.package

    def _fix_math(self, bs: BeautifulSoup):
        """As the only markdown extension that reliably detects math is the 'mdx_math' extension, we have to work around
        the fact that it can only output legacy MathJax2 script tags. We want the MathJax3 output and have to fix this
        manually. The Extension 'arithmatex' that could output in this format natively, is not reliable in math
        detection and cannot be used therefore.

        Args:
            bs (BeautifulSoup): The html source to be fixed.

        Returns:
            _type_: _description_
        """
        # fix all display math <script>-blocks
        for displ_math in bs.find_all("script", {"type": "math/tex; mode=display"}):
            displ_math: Tag
            displ_math.name = "div"
            displ_math.attrs = {"class": "math-display"}
            displ_math.insert(0, r"\[")
            displ_math.insert(len(displ_math.contents), r"\]")

        # fix all inline math <script>-blocks
        for inl_math in bs.find_all("script", {"type": "math/tex"}):
            inl_math: Tag
            inl_math.name = "span"
            inl_math.attrs = {"class": "math-inline"}
            inl_math.insert(0, r"\(")
            inl_math.insert(len(inl_math.contents), r"\)")

        return bs

    def _create_chapter(self, chapter_bs: BeautifulSoup) -> QAChapter:
        name = chapter_bs.find("h1").string
        chap = QAChapter(name)
        item_sources = split_at_tags("h2", chapter_bs)
        prev_source: BeautifulSoup = None
        for item_source in item_sources:
            if self._is_long_question(item_source) and prev_source is None:
                prev_source = item_source
            elif prev_source:
                item = self._create_long_item(prev_source, item_source)
                chap.add_item(item)
                prev_source = None
            else:
                item = self._create_normal_item(item_source)
                chap.add_item(item)
        return chap

    def _is_long_question(self, item_bs: BeautifulSoup):
        h2_tag = item_bs.find("h2")
        title: str = h2_tag.contents[0] or None
        return title.startswith("---")

    def _create_long_item(self, question_bs: BeautifulSoup, answer_bs: BeautifulSoup):
        # this creates an item which has at least a correct answer
        item = self._create_normal_item(answer_bs)
        h2_tag = question_bs.find("h2")
        question_string = "".join([str(elem) for elem in h2_tag.next_siblings])
        question_bs = self._handle_media(question_string)
        question_string = str(question_bs)

        return QAItem(question_string, item.answer, item.comment, item.tags)

    def _create_normal_item(self, item_bs: BeautifulSoup) -> QAItem:
        # exit()
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
        # the content of <h2> tags is not parsed by the markdown extension.
        # As the heading might contain complex math, multiple paragraphs, images, ... or
        # other markdown-content, it has to be parsed again (manually).
        question_string = self.md.convert(question_string)
        question_bs = self._handle_media(question_string)
        question_string = str(question_bs)
        # if display math is used in a normal markdown heading (`## Math: $$a+b=c$$`), the two dollars get interpreted
        # as if they would introduce inline math twice and the result is parsed wrong in the second pass as well... This can be fixed manually.
        question_string = question_string.replace(
            r'<span class="arithmatex"><span class="arithmatex">\(&lt;span class="arithmatex"&gt;\(',
            r'<span class="arithmatex">\(',
        )
        question_string = question_string.replace(r"\)</span></span>)", r"\)</span>")

        # this part needs refactoring!
        answer_string = "".join([str(elem) for elem in answer])
        answer_bs = self._handle_media(answer_string)
        answer_string = str(answer_bs)

        comment_string = "".join([str(elem) for elem in comment]) if comment else None
        if comment:
            comment_bs = self._handle_media(comment_string)
            comment_string = str(comment_bs)

        return QAItem(question_string, answer_string, comment_string)

    def _find_chapter_name(self, html: BeautifulSoup):
        h1: ResultSet = html.find_all("h1")
        if len(h1) > 1:
            raise ValueError("Too many top level header in the current HTML-string!")
        elif len(h1) == 0:
            return "Unnamed-Deck"
        else:
            return h1[0].contents[0]

    def _handle_media(self, bs: Union[str, BeautifulSoup]):
        if not isinstance(bs, BeautifulSoup):
            bs = BeautifulSoup(bs, features="html.parser")

        for img in bs.find_all("img", recursive=True):
            root = Path(self.config.get("general.root"))
            img_path = root.joinpath(img.attrs["src"]).resolve()
            if img_path.exists():
                if not self._is_duplicate_image(img_path):
                    self.package.media.append(img_path)
                    logger.info("Using image: '%s' from '%s'", img.attrs["src"], img_path)
                else:
                    logger.debug("Skipping duplicate image %s", img.attrs["src"])
            else:
                logger.warning(
                    "Image at '%s' does not exists. Ignoring it. (Found in: '%s...')", img_path, bs.get_text()[0:30]
                )
        return bs

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
