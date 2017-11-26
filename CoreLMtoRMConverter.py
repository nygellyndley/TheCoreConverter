import configparser

class ConfigParser(configparser.ConfigParser):
    def optionxform(self, opt):
        return opt

keymapper = ConfigParser()
keymapper.read('KeyMappings.ini')

def remap_single_key_value(key):
    remapped = ""
    try:
        remapped = keymapper.get('LeftToRightMappings', key)
    except configparser.NoOptionError:
        remapped = key
        print("no remapping found for " + key)
    return remapped

def convert_left_medium_key_to_right_medium(keystring):
    remapped = ""

    commasplitkeys = keystring.split(",")
    commasplitcount = 1

    for cs in commasplitkeys:
        plussplitkeys = cs.split('+')
        plussplitcount = 1
        for ps in plussplitkeys:
            remapped += remap_single_key_value(ps)
            if plussplitcount != len(plussplitkeys):
                remapped += "+"
            plussplitcount+=1

        if commasplitcount != len(commasplitkeys):
            remapped += ","
        commasplitcount+=1

    return remapped


def convert_hotkey_file(inputfilename, outputfilename):

    hotkeyfile = ConfigParser()
    hotkeyfile.read(inputfilename)

    with open (outputfilename, "w") as outputfile:
        for section in hotkeyfile.sections():
            outputfile.write("\n[" + section + "]\n")

            for item in hotkeyfile.items(section):
                if section == "Commands" or section == "Hotkeys":
                    remapped = convert_left_medium_key_to_right_medium(item[1])
                    if remapped:
                        outputfile.write(item[0] + "=" + remapped + "\n")
                else:
                    outputfile.write(item[0] + "=" + item[1] + "\n")

convert_hotkey_file('TheCore RLM .SC2Hotkeys', 'TestROutput.SC2Hotkeys')
