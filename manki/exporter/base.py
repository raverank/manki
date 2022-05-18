from typing import Any, Dict, Generic, TypeVar
from manki.configuration import MankiConfig

from manki.data_struct import QAPackage

T = TypeVar("T")


class MankiExporter(Generic[T]):
    def __init__(self, config: MankiConfig, package: QAPackage):
        self.config = config
        self.package = package

    def export(self) -> T:
        """Custom method that exports the QAPackage to a custom format.

        Returns:
            T: The custom data format.
        """
        raise NotImplementedError(f"The '{self.__class__}'-Exporter is not implemented correctly!")
