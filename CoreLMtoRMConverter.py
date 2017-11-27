import configparser, os, shutil
from enum import Enum

class Conversion(Enum):
    LMtoRM = 'LeftToRightMaps'
    RMtoLM = 'LeftToRightMaps'
    LMtoLS = 'LShiftLeftMaps'
    LMtoLL = 'LShiftRightMaps'
    RMtoRS = 'RShiftLeftMaps'
    RMtoRL = 'RShiftRightMaps'

class ConfigParser(configparser.ConfigParser):
    def optionxform(self, opt):
        return opt

    def key_for_value(self, section, value):
        match = value
        for item in self.items(section):
            if item[1] == value:
                match = item[0]
                print('found inverted match: ' + value + ' ' + match)
        return match

keymapper = ConfigParser()
keymapper.read('KeyMappings.ini')


def remap_single_key_value(key, conversion_type):
    remapped = ""
    try:
        if conversion_type == Conversion.RMtoLM:
            remapped = keymapper.key_for_value(conversion_type.value, key)
        else:
            remapped = keymapper.get(conversion_type.value, key)
    except configparser.NoOptionError:
        remapped = key
    return remapped

def convert_hotkey_values(keystring, conversion_type):
    remapped = ""

    commasplitkeys = keystring.split(",")
    commasplitcount = 1

    for cs in commasplitkeys:
        plussplitkeys = cs.split('+')
        plussplitcount = 1
        for ps in plussplitkeys:
            remapped += remap_single_key_value(ps, conversion_type)
            if plussplitcount != len(plussplitkeys):
                remapped += "+"
            plussplitcount+=1

        if commasplitcount != len(commasplitkeys):
            remapped += ","
        commasplitcount+=1

    return remapped

# should be an option for update-only, not rewrite
# probably should use the configparse file write operation, not a custom file output
def convert_hotkey_file(inputfilename, outputfilename, conversion_type):
    print("converting " + inputfilename + " to " + outputfilename)

    hotkeyfile = ConfigParser()
    hotkeyfile.read(inputfilename)

    with open (outputfilename, "w") as outputfile:
        for section in hotkeyfile.sections():
            outputfile.write("\n[" + section + "]\n")

            for item in hotkeyfile.items(section):
                if section == "Commands" or section == "Hotkeys":
                    remapped = convert_hotkey_values(item[1], conversion_type)
                    if remapped:
                        outputfile.write(item[0] + "=" + remapped + "\n")
                else:
                    outputfile.write(item[0] + "=" + item[1] + "\n")


# need a 'merge files' function

if not os.path.isdir("build"):
    os.makedirs("build")

if not os.path.isdir("temp"):
    os.makedirs("temp")

races = ['Z','P','T','R']
prefix = 'hotkey_sources/TheCore '

# step one is to convert the left medium layouts to right medium layouts
for race in races:
    convert_hotkey_file(prefix + race + 'LM.SC2Hotkeys', prefix + race + 'RM.SC2Hotkeys', Conversion.LMtoRM)

# the right medium layouts should be tested in StarCraft and editied if need be
# once the right medium layouts look good, run the conversion to generate all the other layouts
source_files = os.listdir('hotkey_sources')
for file_name in source_files:
    full_file_name = os.path.join('hotkey_sources/', file_name)
    shutil.copy(full_file_name, 'build/')

prefix = 'build/TheCore '
for race in races:
    convert_hotkey_file(prefix + race + 'RM.SC2Hotkeys', prefix + race + 'RL.SC2Hotkeys', Conversion.RMtoRL)
    convert_hotkey_file(prefix + race + 'RM.SC2Hotkeys', prefix + race + 'RS.SC2Hotkeys', Conversion.RMtoRS)
    convert_hotkey_file(prefix + race + 'LM.SC2Hotkeys', prefix + race + 'LL.SC2Hotkeys', Conversion.LMtoLL)
    convert_hotkey_file(prefix + race + 'LM.SC2Hotkeys', prefix + race + 'LS.SC2Hotkeys', Conversion.LMtoLS)


hotkeyfile = ConfigParser()
hotkeyfile.read(prefix + 'ZLM.SC2Hotkeys')
convert_hotkey_file(prefix + 'ZRM.SC2Hotkeys', 'temp/TheCore ZLM.SC2Hotkeys', Conversion.RMtoLM)
hotkeyfile.read('temp/TheCore ZLM.SC2Hotkeys')
hotkeyfile.write(open('merged.SC2Hotkeys', 'w'))


