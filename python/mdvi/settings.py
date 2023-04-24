import yaml
from pathlib import Path

class Settings(dict):

    DEFAULTS = {
        'insert_mode_update': True,
    }

    CONFIG_FILE = Path.home() / '.mdvirc.yaml'

    def __init__(self):

        self.update(self.DEFAULTS)

        if self.CONFIG_FILE.exists():
            config = yaml.load(open(self.CONFIG_FILE), Loader=yaml.Loader)
            self.update(**config)

    @property
    def insert_mode_update(self):
        return self['insert_mode_update']

SETTINGS = Settings()
