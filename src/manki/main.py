from pathlib import Path
import warnings
from manki.exporter.exporter_pdf import PdfExporter

from manki.processor.random_question import RandomQuestionProcessor

# from typing import Any, Dict

# from .converter import Markdown2AnkiDeck
from .cli import parser
from .util import deep_get, ensure_list
from manki.importer.importer_markdown import MarkdownImporter
from manki.exporter.exporter_anki import AnkiExporter
import logging
from rich.logging import RichHandler

# from rich import print
import toml


logger = logging.getLogger()
handler = RichHandler()
logger.addHandler(handler)
handler.setLevel(logging.WARNING)

# filter warnings from genanki
warnings.filterwarnings("ignore", module="genanki", message="^Field contained the following invalid HTML tags")


def get_config(root, args):
    root = Path(root).resolve()
    config = toml.load(root.joinpath("manki.toml"))
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
    if args.verbose:
        handler.setLevel(logging.DEBUG)
    else: 
        handler.setLevel(logging.INFO)
    
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
    if deep_get(config, "processor.randomquestions", False):
        logger.info("Running random question processor.")
        rqp = RandomQuestionProcessor(config, pack)
        rqp.process()

    exporter = AnkiExporter(config, pack)
    exporter.export()
    
    # exporter = PdfExporter(config, pack)
    # exporter.export()


if __name__ == "__main__":
    main()
