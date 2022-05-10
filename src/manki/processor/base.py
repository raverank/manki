from typing import Dict, Any
from manki.qa_data_struct import QAPackage


class MankiProcessor:
    def __init__(self, config: Dict[str, Any], package: QAPackage):
        self.config = config
        self.package = package

    def process(self):
        raise NotImplementedError(f"The '{self.__class__}'-Processor is not implemented correctly!")
