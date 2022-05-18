from pathlib import Path
import warnings

from manki.configuration import MankiConfig

# from manki.template import Template
from jinja2 import FileSystemLoader, Environment
from manki.exporter.exporter_html import HTMLExporter
from manki.exporter.exporter_pdf import PdfExporter

from manki.processor.random_question import RandomQuestionProcessor

# from typing import Any, Dict

# from .converter import Markdown2AnkiDeck
from .cli import parser
from .util import deep_get, ensure_list
from manki.importer.importer_markdown import MarkdownImporter
from manki.exporter.exporter_anki import AnkiExporter
import logging
from rich import print
from rich.logging import RichHandler
import rich.traceback as traceback

traceback.install()

# from rich import print
import toml


logger = logging.getLogger()
handler = RichHandler()
logger.addHandler(handler)
handler.setLevel(logging.DEBUG)

# filter warnings from genanki
warnings.filterwarnings("ignore", module="genanki", message="^Field contained the following invalid HTML tags")


def main():
    args = parser.parse_args()
    if args.verbose:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)

    root = args.root or Path.cwd()
    config = MankiConfig(root=root)
    # page = config.render_template("anki/question.html")
    # print(page)
    sources = {}
    for input in config.get("input.source"):
        file_path = root.joinpath(input)
        with open(file_path, "r") as f:
            sources[file_path.stem] = f.read()
            # print(sources)

    # prepare the importer
    importer = MarkdownImporter(config)
    pack = importer.create_package(sources)
    if config.get("processor.randomquestions"):
        logger.info("Running random question processor.")
        rqp = RandomQuestionProcessor(config, pack)
        rqp.process()

    config.set("package", pack.to_dict())

    if args.format == "apkg":
        exporter = AnkiExporter(config, pack)
    elif args.format == "pdf":
        exporter = PdfExporter(config, pack)
    elif args.format == "html":
        exporter = HTMLExporter(config, pack)
    else:
        logger.error("The output format '%s' is unknown.", args.format)
        exit(code=1)
        
    exporter.export()


if __name__ == "__main__":
    main()
