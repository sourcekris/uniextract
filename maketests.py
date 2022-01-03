#!/usr/bin/env python

import argparse
import sys
import os.path
import json
from pyuniextract.installers.config import load_defs

def_store = "deffix/"

def main(argv):
    ap = argparse.ArgumentParser(description="Make test blobs for the archiver pre-requisites")
    ap.add_argument('-s',"--test", help="Run a specific test only.")
    ap.add_argument('-t',"--type", help="Run a specific type of test only.")
    ap.add_argument('-l',"--list", default="tests", choices=["tests", "types"], help="List tests or types of tests.")

    args = ap.parse_args(argv[1:])

    defs = load_defs(addfn=True)
    for d in defs:
        name = d["name"]
        fn = os.path.basename(d["definition_filename"])

        if "pack" not in d:
            # every def should have a packer but i wont complain.
            continue

        if "type" not in d["pack"]:
            # try and infer it from how it is installed
            if "install" in d and "method" in d["install"]:
                if "apt" in d["install"]["method"] and "packages" in d["install"]:
                    if "dosbox" in d["install"]["packages"]:
                        print(f"inferred test {name} from {fn} is a dosbox type")
                        d["pack"]["type"] = "dosbox"
                        open(os.path.join(def_store, fn)).write(json.dumps(d))
                        continue

                    if "wine" in d["install"]["packages"]:
                        print(f"inferred test {name} from {fn} is a wine type")
                        d["pack"]["type"] = "wine"
                        open(os.path.join(def_store, fn)).write(json.dumps(d))
                        continue

                    print(f"inferred test {name} from {fn} is a archiver type")
                    d["pack"]["type"] = "archiver"
                    open(os.path.join(def_store, fn)).write(json.dumps(d))
            else:
                print(f"test {name} has a broken install method.")
        # test_type = d["pack"]["type"]



if __name__ == "__main__":
    main(sys.argv)
