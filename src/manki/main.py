import glob
from pathlib import Path

from .converter import Markdown2AnkiDeck
from .deck import AnkiDeck, TemplateModel, AnkiPackage
from .cli import parser
import logging
from rich.logging import RichHandler


logger = logging.getLogger()
logger.addHandler(RichHandler())
logger.setLevel(logging.DEBUG)


def main():
    args = parser.parse_args()

    root = args.root or Path.cwd()
    name = args.name or Path(args.input[0]).stem
    package = AnkiPackage(name)
    model = TemplateModel(name + "-model", args.style)

    for input in args.input:
        # deck.add_model(model)
        file_path = root.joinpath(input)
        mda = Markdown2AnkiDeck(file_path, model, root)
        print(len(mda.decks))
        print(mda.decks)
        for deck in mda.decks:
            package.add_deck(deck)
        package.export()
    # print(args)


if __name__ == "__main__":
    main()
