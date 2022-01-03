#!/usr/bin/env python

import argparse
import sys
import os.path
from pyuniextract.installers.config import load_defs
from pyuniextract.common import prettyjson

def_store = "defs/"

def main(argv):
    ap = argparse.ArgumentParser(description="Make test blobs for the archiver pre-requisites")
    ap.add_argument('-s',"--test", help="Run a specific test only.")
    ap.add_argument('-t',"--type", help="Run a specific type of test only.")
    ap.add_argument('-l',"--list", default=None, choices=["tests", "types"], help="List tests or types of tests.")
    args = ap.parse_args(argv[1:])

    defs = load_defs(addfn=True)
    found_types = []
    for d in defs:
        name = d["name"]
        fn = os.path.basename(d["definition_filename"])
        del d["definition_filename"]

        if "pack" not in d:
            # every def should have a packer but i wont complain.
            continue
    
        if args.list == "types":
            if "type" in d["pack"] and d["pack"]["type"] not in found_types:
                found_types.append(d["pack"]["type"])
                continue

        if args.list == "tests":
            print(f"{fn}: {name}")
            continue
        
        if "type" not in d["pack"]:
            # try and infer it from how the packer runs
            if "exe" in d["pack"]:
                if "dosbox" in d["pack"]["exe"]:
                    print(f"inferred test {name} from {fn} is a dosbox type")
                    d["pack"]["type"] = "dosbox"
                    open(os.path.join(def_store, fn),'w').write(prettyjson.dumppretty(d))
                    continue

                if "wine" in d["pack"]["exe"]:
                    print(f"inferred test {name} from {fn} is a wine type")
                    d["pack"]["type"] = "wine"
                    open(os.path.join(def_store, fn),'w').write(prettyjson.dumppretty(d))
                    continue

                print(f"inferred test {name} from {fn} is a archiver type")
                d["pack"]["type"] = "archiver"
                open(os.path.join(def_store, fn),'w').write(prettyjson.dumppretty(d))
            else:
                print(f"test {name} has a broken pack method.")

    if args.list == "types":
        print(f"Test types: {found_types}")

if __name__ == "__main__":
    main(sys.argv)
