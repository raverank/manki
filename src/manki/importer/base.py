from typing import Any, Dict

from manki.qa_data_struct import QAPackage
from manki.util import ensure_list


class MankiImporter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.title = config["general"]["title"]
        self.authors = ensure_list(config["general"]["author"])
        self.package = QAPackage(title=self.title, author=self.authors)

    def create_package(self, raw_source: Dict[str, str]) -> QAPackage:
        """Custom method that creates the QAPackage with all QAChapter and QAItem

        Args:
            raw_source: Dictionary with the file name of the source as key and the file
            content as value

        Returns:
            QAPackage: The fully defined QAPackage
        """
        raise NotImplementedError(f"The '{self.__class__}'-Importer is not implemented correctly!")
