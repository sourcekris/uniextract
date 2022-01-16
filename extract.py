#!/usr/bin/env python

# extract a file to a folder - irrespective of the underlying format.

import argparse
from os import defpath
import sys
import os.path
from pyuniextract.identify.identify import identify_archive
from pyuniextract.installers.unpacker import unpack_archive
from pyuniextract.installers.config import get_def_by_id

defpath = os.path.join(os.path.realpath(__file__), 'defs')
toolspath = os.path.join(os.path.realpath(__file__), 'tools')

def main(argv):
    ap = argparse.ArgumentParser(description=f"Extract Files.", 
                                 epilog="Please file bugs on the GitHub Issues. Thanks")
    ap.add_argument("-e", "--extract", required=True, help=f"The file to extract.", metavar="FILENAME")
    ap.add_argument("-d", "--destination", help="An optional output folder.", metavar="PATH")
    args = ap.parse_args(argv)

    id = identify_archive(args.extract)
    d = get_def_by_id(id, defpath=defpath)
    if not d:
        print(f"Unrecognized archive type: {id}")
        return
    
    print(f"Archive type: {d['name']}")

    destination = "."
    if args.destination:
        destination = args.destination
    
    if not os.path.isdir(destination):
        print(f"{destination} folder does not exist")
        return

    print(f"Extracting to folder: {destination}")   
    unpack_archive(args.extract, d, destdir=destination, toolspath=toolspath)

if __name__ == "__main__":
    main(sys.argv[1:])