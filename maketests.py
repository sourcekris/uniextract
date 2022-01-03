#!/usr/bin/env python

import sys
from pyuniextract.installers.config import load_defs

bt = ["ACE","ALZIP","EGG","SITX","MacBinary","AppleSingle","LZX","ZOO","CPShrink","Crush","DGC","LBR","PMArc","crlzh","Squeeze","Squeeze2","crunch","SQX","ACB"]

def main(args):
    defs = load_defs()
    for d in defs:
        name = d["name"]

        if "pack" not in d and name in bt:
            print(f"archiver {name} has no packer and is a blob test")

if __name__ == "__main__":
    main(sys.argv)
