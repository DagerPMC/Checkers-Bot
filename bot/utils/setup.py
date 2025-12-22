import os

import yaml

from bot.config import Config, Settings


def init_config() -> None:
    config_path = os.environ.get('CONFIG')

    if not config_path:
        raise Exception('Config required')

    with open(config_path) as stream:
        config_content = yaml.safe_load(stream)

    Config.c = Settings.model_validate(config_content)

    assert Config is not None
