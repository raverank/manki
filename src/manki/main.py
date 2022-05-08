from multiprocessing.sharedctypes import Value
from pathlib import Path
from typing import Any, Dict

from .converter import Markdown2AnkiDeck
from .deck import AnkiDeck, TemplateModel, AnkiPackage
from .cli import parser
from .util import ensure_list
from manki.importer.importer_markdown import MarkdownImporter
import logging
from rich.logging import RichHandler
from rich import print
import toml


logger = logging.getLogger()
logger.addHandler(RichHandler())
logger.setLevel(logging.DEBUG)


def get_config(root, args):
    config = toml.load(Path(root).joinpath("manki.toml"))
    config["general"]["root"] = root

    # select the correct title and write it in the config dict.
    # Order of precedence:
    # cli-title > config-title > stem of first file name
    title = args.title or config["general"]["title"] or Path(args.input[0]).stem
    if title is None:
        raise ValueError("Could not infer the deck title.")
    config["general"]["title"] = title

    # update the inputs (use either cli args or config args)
    inputs = args.input or config["input"]["source"]
    config["input"]["source"] = ensure_list(inputs)

    return config


def main():
    args = parser.parse_args()
    root = args.root or Path.cwd()
    config = get_config(root, args)

    inputs = config["input"]["source"]
    sources = {}
    for input in inputs:
        file_path = root.joinpath(input)
        with open(file_path, "r") as f:
            sources[file_path.stem] = f.read()

    # prepare the importer
    importer = MarkdownImporter(config)
    pack = importer.create_package(sources)
    # print(pack)
    

    # package = AnkiPackage(title)
    # model = TemplateModel(title + "-model", args.style)

    # print(sources)
    # mda = Markdown2AnkiDeck(file_path, model, root)
    # print(len(mda.decks))
    # print(mda.decks)
    # for deck in mda.decks:
    #     package.add_deck(deck)
    # package.export()
    # print(args)


if __name__ == "__main__":
    main()
