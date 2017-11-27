import configparser, os, shutil
from enum import Enum

class Conversion(Enum):
    LMtoRM = 'LeftToRightMaps'
    RMtoLM = 'LeftToRightMapsInverted'
    #dropping support for these mappings
    #LMtoLS = 'LShiftLeftMaps'
    #LMtoLL = 'LShiftRightMaps'
    #RMtoRS = 'RShiftLeftMaps'
    #RMtoRL = 'RShiftRightMaps'

class ConfigParser(configparser.ConfigParser):
    def optionxform(self, opt):
        return opt

    def key_for_value(self, section, value):
        match = value
        for item in self.items(section):
            if item[1] == value:
                match = item[0]
        return match

    def write(self, file):
        return super().write(file, space_around_delimiters=False)

keymapper = ConfigParser()
keymapper.read('KeyMappings.ini')


def remap_single_key_value(key, conversion_type):
    remapped = ""
    try:
        if conversion_type == Conversion.RMtoLM:
            remapped = keymapper.key_for_value(Conversion.LMtoRM.value, key)
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

# probably should use the configparse file write operation, not a custom file output
def convert_hotkey_file(inputfilename, outputfilename, conversion_type):
    print("converting " + inputfilename + " to " + outputfilename)

    hotkeyfile = ConfigParser()
    hotkeyfile.allow_no_value=True
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

def right_filename_from_left(left_name):
    if 'Left' in left_name:
        return left_name.replace('Left', 'Right')
    elif 'left' in left_name:
        return left_name.replace('left', 'right')


for f in ["build", "temp"]:
    if not os.path.isdir(f): os.makedirs(f)

# step one is to convert the left layout to the right layout
for file_name in os.listdir('hotkey_sources'):
    right_version = right_filename_from_left(file_name)
    if right_version:
        convert_hotkey_file(file_name, right_version, Conversion.LMtoRM)

# the right layouts should be tested in StarCraft and editied if need be
# once the right layouts look good, run the conversion again to generate all the other layouts
source_files = os.listdir('hotkey_sources')
for file_name in source_files:
    full_file_name = os.path.join('hotkey_sources/', file_name)
    shutil.copy(full_file_name, 'build/')


def unify_left_and_right_layouts():
    # this converts the right layout back to the left layout and merges it with the original left layout
    prefix = 'build/Core '
    convert_hotkey_file(prefix + 'Right.SC2Hotkeys', 'temp/Core Left.SC2Hotkeys', Conversion.RMtoLM)
    hotkeyfile = ConfigParser()
    hotkeyfile.allow_no_value=True
    hotkeyfile.read('temp/Core Left.SC2Hotkeys')
    hotkeyfile.read(prefix + 'Left.SC2Hotkeys')
    hotkeyfile.write(open('temp/merged.SC2Hotkeys', 'w'))

