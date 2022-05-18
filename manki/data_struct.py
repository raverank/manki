from dataclasses import asdict, dataclass, field
from functools import reduce
from pathlib import Path
from typing import Any, Dict, List, Union
from .util import get_hash


@dataclass
class QAItem:
    """
    Question-answer pair with an optional comment.
    Questions and answers have to be formatted with valid HTML.
    """

    question: str
    answer: str
    comment: str = None
    tags: List[str] = None
    item_id: str = field(init=False)

    def __post_init__(self):
        self.item_id = get_hash(self.question + self.answer)

    def to_dict(self) -> Dict[str, Any]:
        dct = {}
        dct["question"] = self.question
        dct["answer"] = self.answer
        dct["comment"] = self.comment
        dct["tags"] = self.tags
        dct["item_id"] = self.item_id
        return dct

@dataclass()
class QAChapter:
    """
    A chapter with multiple QA-items
    """

    title: str
    items: List[QAItem] = field(default_factory=list)
    chapter_id: str = field(init=False)

    def __post_init__(self):
        self.chapter_id = get_hash(self.title)

    def add_item(self, item: QAItem):
        self.items.append(item)

    @property
    def n_items(self) -> int:
        return len(self.items)

    def to_dict(self) -> Dict[str, Any]:
        dct = {}
        dct["title"] = self.title
        dct["chapter_id"] = self.chapter_id
        dct["n_items"] = self.n_items
        dct["items"] = [itm.to_dict() for itm in self.items]
        return dct


@dataclass()
class QAPackage:
    """Contains one or more chapters with questions and answers."""

    title: str
    author: Union[str, List[str]]
    chapters: List[QAChapter] = field(default_factory=list)
    media: List[Path] = field(default_factory=list)
    package_id: str = field(init=False)

    def __post_init__(self):
        self.package_id = get_hash(self.title)

    def add_chapter(self, chapter: QAChapter):
        self.chapters.append(chapter)

    @property
    def n_chapters(self) -> int:
        return len(self.chapters)

    @property
    def n_items(self) -> int:
        return sum([chap.n_items for chap in self.chapters])

    def to_dict(self) -> Dict[str, Any]:
        dct = {}
        dct["title"] = self.title
        dct["author"] = self.author
        dct["media"] = self.media
        dct["package_id"] = self.package_id
        dct["n_chapters"] = self.n_chapters
        dct["n_items"] = self.n_items
        dct["chapters"] = [chp.to_dict() for chp in self.chapters]
        return dct
