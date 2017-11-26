import configparser


class ConfigParser(configparser.ConfigParser):
    """Case-sensitive ConfigParser."""

    def optionxform(self, opt):
        return opt

    def write(self, file):
        return super().write(file, space_around_delimiters=False)

keymapper = ConfigParser()
keymapper.read('KeyMappings.ini')

def convert_LM_key_to_RM(key):
    return keymapper.get('LeftToRightMappings', key)

print(convert_LM_key_to_RM('W'))
