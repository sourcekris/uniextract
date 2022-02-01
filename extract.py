#!/usr/bin/env python

# extract a file to a folder - irrespective of the underlying format.

import argparse
import sys
import os, os.path
from glob import glob
from pyuniextract.identify.identify import identify_archive
from pyuniextract.installers.unpacker import unpack_archive
from pyuniextract.installers.config import get_def_by_id

defpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'defs')
toolspath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tools')

def extract(fname, dstpath):
    id = identify_archive(fname)
    d = get_def_by_id(id, defpath=defpath)
    if not d:
        print(f"Unrecognized archive type: \"{id}\"")
        return
    
    print(f"Archive type: {d.name}")

    destination = "."
    if dstpath:
        destination = dstpath
    
    if not os.path.isdir(destination):
        print(f"{destination} folder does not exist")
        return

    print(f"Extracting to folder: {destination}")   
    unpack_archive(fname, d, destdir=destination, toolspath=toolspath)

def main(argv):
    ap = argparse.ArgumentParser(description=f"Extract Files.", 
                                 epilog="Please file bugs on the GitHub Issues. Thanks")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("-e", "--extract", help=f"The file to extract.", metavar="FILENAME")
    mode.add_argument("-a", "--all", help=f"Extract all archives in a folder.", metavar="PATH")
    ap.add_argument("-c", "--createsubfolders", help=f"Create subfolders named for the archive when extracting using the --all mode.", action="store_true")
    ap.add_argument("-d", "--destination", help="An optional output folder.", metavar="PATH")
    
    args = ap.parse_args(argv)

    if args.extract:
        extract(args.extract, args.destination)
    
    if args.all:
        files = glob(os.path.join(args.all, "*"))

        for file in files:
            # Skip non files.
            if not os.path.isfile(file):
                continue
            # Decide where to put the output per file.
            dst = args.destination
            if not args.destination:
                dst = "."
            if args.createsubfolders:
                dst = os.path.join(dst, os.path.splitext(os.path.basename(file))[0])
                if os.path.exists(dst):
                    print(f'subfolder {dst} already exists, skipping file {file}')
                    continue
                os.mkdir(dst)
            
            # Extract this file.
            extract(file, dst)

if __name__ == "__main__":
    main(sys.argv[1:])