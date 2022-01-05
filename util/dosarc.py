#!/usr/bin/python

# utility to make a config for a dos archiver based on a few variables.

import argparse
import sys
import subprocess
import os, os.path
import inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from pyuniextract.installers.extracttool import extracttool

jsontemplate = """{
    "name": "#NAME#",
    "comment": "http://fileformats.archiveteam.org/wiki/#NAME#",
    "extensions": ["#EXT#"],
    "install": {
        "method": "apt",
        "packages": ["dosbox"],
        "tool":"#BIN#",
        "container":"dos/#EXT#/#DIST#"#DEPBLOCK#
    },
    "pack": {
        "exe": "dosbox",
        "cmdline": "$tool -noconsole -c \\"mount d $tools\\" -c \\"mount e $(pwd)\\" -c \\"e:\\" -c \\"d:#BIN# #ADD# $file.#EXT# $file\\" -c \\"exit\\"",
        "type": "dosbox"
    },
    "unpack": {
        "exe": "dosbox",
        "cmdline": "$tool -noconsole -c \\"mount d $tools\\" -c \\"mount e $destdir\\" -c \\"mount f $arcloc\\" -c \\"e:\\" -c \\"d:#BIN2# #EXTRACT# F:$shortname \\" -c \\"exit\\"",
        "extension": "#EXT#",
        "force_extension": true
    },
    "test": {
        "blob": "#BLOB#",
        "file": "0",
        "content": "#MSG#",
        "delete": true
    }
}
"""

def main(argv):
    ap = argparse.ArgumentParser(description="Create a dos archiver profile (JSON config)")
    ap.add_argument("-e","--extension",required=True, help="file extension (without .), will be used as the profile name and archive payload too by default")
    ap.add_argument("-b", "--binary", help="archiver executable name. Default is whatever the extension is e.g. arj")
    ap.add_argument("-u", "--unarchiver", help="unarchiver executable name. Default is whatever the extension is e.g. arj")
    ap.add_argument("-d", "--distfile", help="Archive distfile from dos/*/??.zip")
    ap.add_argument("-n", "--name", help="Profile name, default is whatever the extension is in uppercase. e.g. arj -> ARJ")
    ap.add_argument("-m", "--msg", help="Archive message, default is whatever the extension is in uppercase. e.g. arj -> ARJ")
    ap.add_argument("-a", "--addfiles", default="a", help="The command the archiver uses to add files to an archive.")
    ap.add_argument("-x", "--extfiles", default="x", help="The command the archiver uses to extract files from an archive.")
    args = ap.parse_args(argv)

    os.chdir('..')
    def_file = os.path.join("defs", args.extension + ".json")
    if os.path.isfile(def_file):
        print(f"{def_file} already exists, aborting.")
        return

    binary = args.binary
    if not args.binary:
        binary = args.extension

    depblock = ""
    binary2 = args.unarchiver
    if not args.unarchiver:
        binary2 = binary
    else:
        depblock = f",\n        \"dependencies\":[\"{binary2}\"]"
    
    tool = os.path.join("tools", binary.upper() + ".EXE")
    if not os.path.isfile(tool):
        print(f"binary {tool} doesn't exist so maketest might fail later.")
    
    name = args.name
    if not args.name:
        name = args.extension.upper()
    
    msg = args.msg
    if not args.msg:
        msg = args.extension.upper()
    
    addfiles = args.addfiles
    addfiles = addfiles.replace("_", "-")
    extfiles = args.extfiles
    extfiles = extfiles.replace("_", "-")
        
    
    config = jsontemplate.replace("#BIN#", binary)
    config = config.replace("#EXT#", args.extension)
    config = config.replace("#NAME#", name)
    config = config.replace("#ADD#", addfiles)
    config = config.replace("#EXTRACT#", extfiles)
    config = config.replace("#MSG#", msg)
    config = config.replace("#DIST#", args.distfile)
    config = config.replace("#BIN2#", binary2)
    config = config.replace("#DEPBLOCK#", depblock)

    print(f'writing config: {def_file}')
    open(def_file,'w').write(config)

    print(f'asking maketests.py to make me a test blob')
    cmdline = ["./maketests.py","-s",name]
    p = subprocess.Popen(cmdline,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    outs, errs = p.communicate()
    if 'H4s' not in outs.decode():
        print(f"blob making failed with this cmdline: {' '.join(cmdline)}")
        return
    
    blob = outs.decode().split(': ')[1].strip()
    config = jsontemplate.replace("#BIN#", binary)
    config = config.replace("#EXT#", args.extension)
    config = config.replace("#NAME#", name)
    config = config.replace("#ADD#", addfiles)
    config = config.replace("#EXTRACT#", extfiles)
    config = config.replace("#MSG#", msg)
    config = config.replace("#BLOB#", blob)
    config = config.replace("#DIST#", args.distfile)
    config = config.replace("#BIN2#", binary2)
    config = config.replace("#DEPBLOCK#", depblock)

    print(f'writing config w/blob this time: {def_file}')
    open(def_file,'w').write(config)

if __name__ == "__main__":
    main(sys.argv[1:])