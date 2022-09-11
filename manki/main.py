from pathlib import Path
import warnings

from manki.configuration import MankiConfig

from manki.exporter.exporter_html import HTMLExporter
from manki.exporter.exporter_pdf import PdfExporter

from manki.processor.random_question import RandomQuestionProcessor
from manki.util import sanitize_string

from .cli import parser
from manki.importer.importer_markdown import MarkdownImporter
from manki.exporter.exporter_anki import AnkiExporter
import logging
from rich.logging import RichHandler
import rich.traceback as traceback

from jinja2 import Environment, FileSystemLoader

traceback.install()

logger = logging.getLogger()
handler = RichHandler()
logger.addHandler(handler)
handler.setLevel(logging.DEBUG)

# filter warnings from genanki
warnings.filterwarnings("ignore", module="genanki", message="^Field contained the following invalid HTML tags")


def create_new(args):
    title = args.new
    title_sanitized = sanitize_string(title)
    folder = Path.cwd().joinpath(title_sanitized)
    folder.mkdir(exist_ok=True)
    for name in ["macros.md", "manki.toml", "questions.md"]:
        logger.debug("Creating '%s'", name)
        TMPLT_PATH = Path(__file__).parent.parent.joinpath("templates").resolve()
        loader = FileSystemLoader(TMPLT_PATH)
        template_env = Environment(
            loader=loader,
            line_statement_prefix="§",
            line_comment_prefix="°",
            comment_start_string="°",
        )
        template_env.globals["title"] = title
        template_env.globals["title_sanitized"] = title_sanitized
        rendered = template_env.get_template(f"new_{name}.j2").render()
        with open(folder.joinpath(name), "w") as f:
            f.write(rendered)


def main():
    args = parser.parse_args()
    if args.verbose:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)

    if args.new is not None:
        logger.info(f"Creating new Manki project '{args.new}'")
        create_new(args)
        exit()

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
