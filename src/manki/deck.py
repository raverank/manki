import hashlib
import importlib

from genanki import Deck, Model, Package
import importlib.resources as pkg_resources
import logging

logger = logging.getLogger(__name__)


class AnkiPackage(Package):
    def __init__(self, name):
        super(AnkiPackage, self).__init__()
        self.name = name
        self.decks = []

    def add_deck(self, deck: Deck):
        deck.name = self.name + "::" + deck.name
        self.decks.append(deck)

    def export(self):
        logger.info("Exporting '%s' with '%d' decks", self.name + ".apkg", len(self.decks))
        self.write_to_file(self.name + ".apkg")


class AnkiDeck(Deck):
    def __init__(self, name: str):
        super(AnkiDeck, self).__init__(name=name)
        self.deck_id = int(hashlib.sha1(name.encode("utf-8")).hexdigest(), base=16) % (10**10)
        logger.debug("Creating new deck '%s' with ID '%i'", name, self.deck_id)


class TemplateModel(Model):
    def __init__(self, name: str, template_name: str):
        super(TemplateModel, self).__init__(name=name)
        self.model_id = int(hashlib.sha1(name.encode("utf-8")).hexdigest(), 16) % (10**10)
        logger.debug("Creating new model '%s' with ID '%i'", name, self.model_id)

        template_module = f"manki.templates.{template_name}"
        template_properties = dict()
        for prop, file_name in {
            "qfmt": "qfmt.html",
            "afmt": "afmt.html",
            "style": "style.css",
        }.items():
            try:
                template_properties[prop] = pkg_resources.read_text(template_module, file_name)
                logger.debug(
                    "Read template definition '%s' from '%s'",
                    prop,
                    pkg_resources.path(template_module, file_name),
                )
            except ModuleNotFoundError:
                logger.error("The requested template '%s' could not be found!", template_name)
            except FileNotFoundError:
                logger.error("Could not find the '%s' definition '%s'!", prop, file_name)

        self.set_fields(
            [
                {"name": "Front"},
                {"name": "Back"},
            ]
        )

        self.set_templates(
            [
                {
                    "name": "Card",
                    "qfmt": template_properties["qfmt"],
                    "afmt": template_properties["afmt"],
                }
            ]
        )

        # deck = Deck(deck_id=1, name="Test")
        # model = Model(
        #     1607392319,
        #     "Simple Model",
        #     fields=[
        #         {"name": "Front"},
        #         {"name": "Back"},
        #     ],
        #     css=".card {\n"
        #         "  font-family: arial;\n"
        #         "  font-size: 20px;\n"
        #         "  text-align: left;\n"
        #         "  color: black;\n"
        #         "  background-color: white;\n}\n\n"
        #         ".question {\n"
        #         "  color: white;\n"
        #         "  background-image: linear-gradient(to bottom, #2e5c8a, #193552);\n"
        #         "  padding: 0.5em;\n"
        #         "  border-radius: 0.2em;\n}\n\n"
        #         ".solution {\n"
        #         "  color: black;\n"
        #         "  padding: 0.3em;\n}",
        #     templates=[
        #         {
        #             "name": "Card 1",
        #             "qfmt": '<div class="question">{{Front}}</div>',
        #             "afmt": '{{FrontSide}}\n\n<div class="solution">\n{{Back}}\n</div>',
        #         },
        #     ],
        # )
        # deck.add_model(model)
        # mc = Markdown2AnkiDeck(content, deck, root)
        # notes = [n.fields for n in mc.deck.notes]
