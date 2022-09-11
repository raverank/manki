from pathlib import Path
from manki.configuration import MankiConfig
from manki.importer.importer_markdown import MarkdownImporter
import json
from rich.pretty import pprint

TEST_DIRS = ["plain"]


def _read_file(path: Path, as_json=False):
    with open(path, "r") as f:
        if as_json:
            content = json.load(f)
        else:
            content = f.read()
    return content

def _test_one_dir(path: Path):
    stem = path.stem
    js = _read_file(path.joinpath(f"{stem}.json"), as_json=True)
    config = MankiConfig(root=path)
    importer = MarkdownImporter(config)
    sources = {src: _read_file(path.joinpath(src)) for src in config.get("input.source")}
    pack = importer.create_package(sources)
    print(sources)
    pprint(pack.to_dict())
    print(js)


def test_directories():
    for directory in TEST_DIRS:
        path = Path.cwd().joinpath(directory)
        _test_one_dir(path)


if __name__ == "__main__":
    test_directories()
