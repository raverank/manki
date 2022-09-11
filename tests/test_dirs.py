from pathlib import Path
from manki.configuration import MankiConfig
from manki.data_struct import QAPackage
from manki.importer.importer_markdown import MarkdownImporter
import json
import pytest


TEST_DIR = "tests"


def _create_test_references(path: Path, pack: QAPackage):
    dct = pack.to_dict()
    dct["media"] = [str(x) for x in dct["media"]]
    with open(path.joinpath(f"{path.stem}.json"), "w") as f:
        json.dump(dct, f)


@pytest.mark.parametrize("directory", ["plain", "math", "images", "code"])
def test_directories(directory):
    path = Path.cwd().joinpath(TEST_DIR).joinpath(directory)
    stem = path.stem
    config = MankiConfig(root=path)
    importer = MarkdownImporter(config)
    sources = {src: open(path.joinpath(src)).read() for src in config.get("input.source")}
    pack = importer.create_package(sources)
    pack_dict = pack.to_dict()
    pack_dict["media"] = [str(x) for x in pack_dict["media"]]
    # _create_test_references(path, pack)
    js = json.load(open(path.joinpath(f"{stem}.json")))
    assert pack_dict == js


if __name__ == "__main__":
    test_directories()
