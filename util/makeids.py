#!/usr/bin/env python

# makeids.py -
# pack an archive then attempt to uniquely identify the format using file, trid, idarc etc.

import argparse
import sys
import os, os.path
import inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from pyuniextract.installers.identify import identify_archive
from pyuniextract.installers.config import load_defs
from pyuniextract.installers.packer import pack_file

def main(argv):
    ap = argparse.ArgumentParser(description="Make test archives then attempt to identify them")
    ap.add_argument('-s',"--specific", help="Run a specific identification only, if test not found nothing is done.")
    ap.add_argument('-t',"--type", choices=["file","trid", "idarc"],help="Use file, trid or idarc only.")
    args = ap.parse_args(argv[1:])

    dp = os.path.join(os.getcwd(), "..", "defs")
    defs = load_defs(addfn=True, defpath=dp)
    for d in defs:
        name = d.name
        if args.specific:
            if name == args.specific:
                af = pack_file(name, defpath=dp, toolpath="../tools")
                id = identify_archive(af, idtype=args.type)
                print(f'archiver {name} identified as: {id}')

            continue

        af = pack_file(name, defpath=dp, toolpath="../tools")
        id = identify_archive(af, idtype=args.type)
        print(f'archiver {name} identified as: {id}')
        
if __name__ == "__main__":
    main(sys.argv)
