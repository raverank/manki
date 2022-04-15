import pytest
from manki.converter import Html2Anki
from genanki import Deck, Note, Model

DATA_DIR = "./data"


def _get_referece_deck():
    model = Model(
        1,
        "TestModel",
        fields=[
            {"name": "Front"},
            {"name": "Back"},
        ],
        templates=[
            {
                "name": "TestCard",
                "qfmt": '<div class="question">{{Front}}</div>',
                "afmt": '{{FrontSide}}\n\n<div class="solution">\n{{Back}}\n</div>',
            },
        ],
    )
    deck = Deck()
    deck.add_model(model)
    return deck


@pytest.mark.parametrize(
    ["html", "fields"],
)
def test_html_to_qa(html, fields):
    ref_deck = _get_referece_deck()
    ref_deck.add_note(Note(fields=fields))
    hc = Html2Anki(html, _get_referece_deck(), DATA_DIR)
    assert len(hc.deck.notes) == 1
    assert ref_deck.notes[0].fields == hc.deck.notes[0].fields