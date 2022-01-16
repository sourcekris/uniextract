#!/usr/bin/env python

# makeids.py -
# pack an archive then attempt to uniquely identify the format using file, trid, idarc etc.

import argparse
import sys
import os.path
from pyuniextract.identify.identify import identify_archive
from pyuniextract.installers.config import load_defs
from pyuniextract.installers.packer import pack_file

# makes sure we can pack an archive with this profile.
def valid_def(d):
    if "pack" not in d:
        if "test" not in d:
            return False
        if "blob" in d["test"]:
            # we can use the test blob.
            return True
        return False
    # if there's a packer, we assume its valid.    
    return True   

def main(argv):
    ap = argparse.ArgumentParser(description="Make test archives then attempt to identify them")
    ap.add_argument('-s',"--specific", help="Run a specific identification only, if test not found nothing is done.")
    ap.add_argument('-t',"--type", choices=["file","trid", "idarc"],help="Use file, trid or idarc only.")
    args = ap.parse_args(argv[1:])

    defs = load_defs(addfn=True)
    for d in defs:
        if not valid_def(d):
            continue

        name = d["name"]
        fn = os.path.basename(d["definition_filename"])

        if args.specific:
            if name == args.specific:
                af = pack_file(name)
                id = identify_archive(af, idtype=args.type)
                print(f'archiver {name} identified as: {id}')

            continue

        af = pack_file(name)
        id = identify_archive(af, idtype=args.type)
        print(f'archiver {name} identified as: {id}')
        
if __name__ == "__main__":
    main(sys.argv)
