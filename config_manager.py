import configparser

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file_location = 'config.ini'

    def load_api_key(self, section, key):
        self.config.read(self.config_file_location)
        return self.config[section][key]
