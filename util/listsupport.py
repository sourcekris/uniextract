#!/usr/bin/python

# Print a table of supported archive formats.

import inspect
import sys
import os, os.path

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from pyuniextract.config import load_defs

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

    names = []
    n2e = {}
    for d in defs:
        names.append(d["name"])
        n2e[d["name"]] = d["extensions"]
    
    names.sort()

    for d in names:
        print(f'| {d.ljust(namelen," ")} | {", ".join(n2e[d]).ljust(extlen," ")} |')


if __name__ == "__main__":
    main(sys.argv[1:])