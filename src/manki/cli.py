import argparse

parser = argparse.ArgumentParser(prog="Manki",
                                 add_help=True,
                                 description="This program allows you to convert question and answer-style markdown "
                                             "files into ANKI card decks or other useful formats like PDF or HTML.")

parser.add_argument(
    "--input", "-i",
    type=str,
    nargs="+",
    help="One or more Markdown Files to be converted to Anki",
)
parser.add_argument(
    "--title", "-t",
    type=str,
    help="Title of the Anki deck.py",
)
parser.add_argument(
    "--output", "-o",
    type=str,
    help="Name of the output file. If omitted, the same name as the (single) input file is used "
         "or a generic name if a pattern was used as input",
)
parser.add_argument(
    "--root", "-r",
    type=str,
    help="The projects root",
)
parser.add_argument(
    "--format", "-f",
    type=str,
    default="apkg",
    help="Output format to be converted to. Default is 'apkg' which is the default Anki-package format. "
         "Other options are 'pdf' or 'html' or custom defined output types"
)
parser.add_argument(
    "--macros", "-m",
    type=str,
    default="macros.tex",
    help="A file with (MathJax compatible) definitions of TeX macros. Default is 'macros.tex'",
)
parser.add_argument(
    "--style", "-s",
    type=str,
    default="default",
    help="Define the style "
)
parser.add_argument(
    "--verbose", "-v",
    action="store_true",
    default=False,
    help="Set the output to DEBUG mode"
)