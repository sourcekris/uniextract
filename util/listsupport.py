#!/usr/bin/python

# Print a table of supported archive formats.

import inspect
import sys
import os, os.path

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from pyuniextract.installers.config import load_defs

def main(argv):
    defs = load_defs(addfn=True, defpath=os.path.join(os.getcwd(), "..", "defs"))

    namelen = 0
    extlen = 0
    for d in defs:
        if len(d["name"]) > namelen:
            namelen = len(d["name"])
        
        if len(", ".join(d["extensions"])) > extlen:
            extlen = len(", ".join(d["extensions"]))

    print(f'| {"Archive type".ljust(namelen," ")} | {"Common file extension(s)".ljust(extlen," ")} |')
    print(f'| {"-".ljust(namelen,"-")} | {"-".ljust(extlen,"-")} |')
    for d in defs:
        print(f'| {d["name"].ljust(namelen," ")} | {", ".join(d["extensions"]).ljust(extlen," ")} |')


if __name__ == "__main__":
    main(sys.argv[1:])