from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union
import hashlib


def get_hash(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest(), base=16) % (10**10)


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

    name: str
    items: List[QAItem] = field(default_factory=list)
    chapter_id: str = field(init=False)

    def __post_init__(self):
        self.chapter_id = get_hash(self.name)

    def add_item(self, item: QAItem):
        self.items.append(item)


@dataclass()
class QAPackage:
    """Contains one or more chapters with questions and answers."""

    name: str
    author: Union[str, List[str]]
    chapters: List[QAChapter] = field(default_factory=list)
    media: List[Path] = field(default_factory=list)
    package_id: str = field(init=False)

    def __post_init__(self):
        self.package_id = get_hash(self.name)

    def add_chapter(self, chapter: QAChapter):
        self.chapters.append(chapter)
