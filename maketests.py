#!/usr/bin/env python

import sys
from pyuniextract.installers.config import load_defs

bt = ["ACE","ALZIP","EGG","SITX","MacBinary","AppleSingle","LZX","ZOO","CPShrink","Crush","DGC","LBR","PMArc","crlzh","Squeeze","Squeeze2","crunch","SQX","ACB"]

def main(args):
    defs = load_defs()
    for d in defs:
        name = d["name"]
        if ' ' in name:
            print(f'archiver "{name}" has space in name')
        # if "pack" not in d:
        #     print(f"archiver {name} has no packer")


if __name__ == "__main__":
    main(sys.argv)
