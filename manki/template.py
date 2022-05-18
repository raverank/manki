from os import PathLike
from pathlib import Path
from typing import Callable, Sequence, Tuple, Union
from jinja2 import Environment, Template, TemplateNotFound, BaseLoader
import abc
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)


TEMPLATE_PATH = Path(__file__).parent.parent.joinpath("templates").resolve()


class TemplateLoader(BaseLoader):
    @staticmethod
    def _find_template(name):
        logger.debug("Searching templates in '%s'", TEMPLATE_PATH)
        root = Path(TEMPLATE_PATH).joinpath(name)
        if not (root.exists() and root.is_dir()):
            raise FileNotFoundError(f"The requested template '{name}' could not be found!")
        return root

    def load_resource(self, group: str, resource_name: str, or_default_template=True):
        group = self.root.joinpath(group)

        resource_path = group.joinpath(resource_name)
        try:
            with open(resource_path, "r") as f:
                logger.debug("Reading template resource file '%s'", resource_path)
                return f.read()
        except FileNotFoundError:
            if or_default_template:
                # use default template instead
                logger.info(
                    "The requested template resource '%s' does not exist.\nTrying to use 'default' template instead.",
                    resource_path,
                )
                return Template("default").load_resource(group, resource_name, or_default_template=False)
            else:
                # no common style and group not found...
                logger.critical(
                    f"The requested template resource '{resource_path}' does not exist "
                    + "and no alternatives have been defined."
                )
                exit(code=1)
