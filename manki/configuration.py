from datetime import datetime
from functools import reduce
from pathlib import Path
from typing import Union
from jinja2 import ChoiceLoader, Environment, FileSystemLoader
import toml

import logging

from manki.util import ensure_list


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)


def get_dict_branches(tree, parent_path=()):
    for path, node in tree.items():
        current_path = parent_path + (path,)
        if isinstance(node, dict):
            for inner_path in get_dict_branches(node, current_path):
                yield inner_path
        else:
            yield current_path + (node,)


class MankiConfig(object):
    def __init__(self, root: Union[str, Path], file_name="manki.toml") -> None:
        self.root = Path(root).resolve()
        self._config_file = self.root.joinpath(file_name)
        self._config_dict = {}
        self.template_env: Environment = None
        self._load_config_file()
        self._init_template()
        self._update_config()

    def get(self, key: str, default=None):
        return reduce(
            lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
            key.split("."),
            self._config_dict,
        )

    def set(self, key: str, value, overwrite=True):
        keys = key.split(".")
        dic = self._config_dict
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})
        if not overwrite and dic.get(keys[-1], None):
            return None

        dic[keys[-1]] = value

    def render_template(self, name: str):
        self.template_env.globals = self._config_dict
        return self.template_env.get_template(name).render()

    def _load_config_file(self):
        logger.debug("Loading configuration file from '%s", self._config_file)
        try:
            self._config_dict = toml.load(self._config_file)
        except FileNotFoundError:
            logger.critical("There is no configuration file 'manki.toml' in your project directory!")
            exit(code=1)
        except (ValueError, toml.TomlDecodeError) as e:
            logger.critical(
                "Your configuration file could not be decoded. Please check if it contains errors!\n\n%s",
                e.with_traceback(),
            )
            exit(code=1)

        self.set("general.root", self.root)

    def _init_template(self):
        TMPLT_PATH = Path(__file__).parent.parent.joinpath("templates").resolve()
        tmplt_name = self.get("general.template", default="default")
        loader = ChoiceLoader(
            [
                FileSystemLoader(TMPLT_PATH.joinpath(tmplt_name)),
                FileSystemLoader(TMPLT_PATH.joinpath("default")),
            ]
        )
        self.template_env = Environment(loader=loader)

    def _update_config(self):
        """This method is called to update some values in the config object. This includes
        - Updating values based on the template manki.toml file
        - Updating time and date variables
        - Ensuring that the authors are given as a list.
        """
        MANKI_TOML = "manki.toml.j2"
        config = self.render_template("_common/" + MANKI_TOML)
        if config:
            config = toml.loads(config)
            for branch in get_dict_branches(config):
                path = ".".join(branch[:-1])
                value = branch[-1]
                self.set(path, value, overwrite=False)

        self.set("general.author", ensure_list(self.get("general.author", default="None")))
        self.set(
            "general.date",
            datetime.now().strftime("%d.%m.%Y"),
            overwrite=False,
        )
        self.set(
            "general.time",
            datetime.now().strftime("%H:%M:%S"),
            overwrite=False,
        )
