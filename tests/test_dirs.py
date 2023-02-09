from pathlib import Path
from typing import Any, Dict
from manki.configuration import MankiConfig
from manki.data_struct import QAPackage
from manki.importer.importer_markdown import MarkdownImporter
import json
import pytest


TEST_DIR = "tests"


def _make_media_path_relative(path):
    return path.relative_to(Path.cwd())


def _create_test_references(path: Path, pack: QAPackage):
    dct = pack.to_dict()
    dct["media"] = [str(_make_media_path_relative(x)) for x in dct["media"]]
    with open(path.joinpath(f"{path.stem}.json"), "w") as f:
        json.dump(dct, f)


def check_json_recursively(dcta: Dict[str, Any], dctb: Dict[str, Any], level=0) -> bool:
    success = True
    for k, v in dcta.items():
        try:
            if isinstance(v, dict):
                success = check_json_recursively(v, dctb[k], level=level + 1)
            else:
                assert v == dctb[k]
        except KeyError:
            print(f"Key '{k}' cannot be found in second dictionary")
        except AssertionError:
            print(f"Wrong value for key {k}: Got '{dctb[k]}, expected {v}'")
            success = False
    return success


@pytest.mark.parametrize("directory", ["plain", "math", "images", "code"])
def test_directories(directory):
    path = Path.cwd().joinpath(TEST_DIR).joinpath(directory)
    stem = path.stem
    config = MankiConfig(root=path)
    importer = MarkdownImporter(config)
    sources = {src: open(path.joinpath(src)).read() for src in config.get("input.source")}
    pack = importer.create_package(sources)
    pack_dict = pack.to_dict()
    pack_dict["media"] = [str(_make_media_path_relative(x)) for x in pack_dict["media"]]
    _create_test_references(path, pack)
    js = json.load(open(path.joinpath(f"{stem}.json")))
    assert check_json_recursively(pack_dict, js)


if __name__ == "__main__":
    test_directories()
