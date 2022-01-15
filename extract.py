#!/usr/bin/env python

# extract a file to a folder - irrespective of the underlying format.

import argparse
import sys
from pyuniextract.identify.identify import identify_archive
from pyuniextract.installers.unpacker import unpack_archive
from pyuniextract.installers.config import get_def_by_id

def main(argv):
    ap = argparse.ArgumentParser(description=f"Extract Files.", 
                                 epilog="Please file bugs on the GitHub Issues. Thanks")
    ap.add_argument("-e", "--extract", required=True, help=f"The file to extract.", metavar="FILENAME")
    ap.add_argument("-d", "--destination", help="An optional output folder.", metavar="PATH")
    args = ap.parse_args(argv)

    id = identify_archive(args.extract)
    d = get_def_by_id(id)
    if not d:
        print(f"Unrecognized archive type: {id}")
        return
    
    print(f"Archive type: {d['name']}")
    if args.destination:
        print(f"Extracting to: {args.destination}")
    
    #unpack_archive(d, args.extract, destdir=args.destination)


if __name__ == "__main__":
    main(sys.argv[1:])