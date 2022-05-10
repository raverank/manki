from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union
from .util import get_hash


@dataclass()
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
