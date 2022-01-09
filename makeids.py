#!/usr/bin/env python

# makeids.py -
# pack an archive then attempt to uniquely identify the format using file, trid, idarc etc.

import argparse
import sys
import os, os.path
import tempfile
from gzip import compress
from base64 import b64encode, b64decode
from subprocess import Popen, PIPE
from pyuniextract.installers.config import load_defs, default_fn, tools_path
from pyuniextract.installers.testarchiver import pad
from pyuniextract.installers.template import prepare_cmdline, prepare_exe

def_store = "defs/"

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
    ap.add_argument('-s',"--test", help="Run a specific identification only, if test not found nothing is done.")
    ap.add_argument('-t',"--type", help="Run a specific type of identification only.")
    ap.add_argument('-l',"--list", choices=["tests", "types"], help="List tests or types of tests.")
    args = ap.parse_args(argv[1:])

    do_types = ["blob", "archiver", "dosbox", "wine"]
    if args.type:
        do_types = [args.type]

    defs = load_defs(addfn=True)
    found_types = []
    for d in defs:
        name = d["name"]
        fn = os.path.basename(d["definition_filename"])
        del d["definition_filename"]

        if not valid_def(d):
            continue
        test_type = d["pack"]["type"]
        def_extension = d["extensions"][0]

        if args.test and args.test != name:
            continue

        msg = d["test"]["content"]
        if "padbyte" in d["test"] and "padlen" in d["test"]:
            msg = pad(msg, d["test"]["padbyte"], d["test"]["padlen"])

        if args.test:
            if test_type == "blob":
                do_blob_test(name, d["pack"]["blob"])
            elif test_type == "archiver":
                do_archiver_test(name, msg, def_extension, d["pack"]["exe"], d["pack"]["cmdline"], d["test"]["delete"])
            elif test_type == "wine":
                do_archiver_test(name, msg, def_extension, d["pack"]["exe"], d["pack"]["cmdline"], d["test"]["delete"])
            elif test_type == "dosbox":
                # seperated so we can opt to skip them as they take a little while to run.
                do_archiver_test(name, msg, def_extension, d["pack"]["exe"], d["pack"]["cmdline"], d["test"]["delete"])
            else:
                print(f"not yet implemented for test {name}")
                return
            
            return
    
        if args.list == "types":
            if d["pack"]["type"] not in found_types:
                found_types.append(d["pack"]["type"])
                continue

        if args.list == "tests":
            print(f"{fn}: {name}")
            continue

        if test_type == "blob" and "blob" in do_types:
            do_blob_test(name, d["pack"]["blob"])
        
        if test_type == "archiver" and "archiver" in do_types:
            do_archiver_test(name, msg, def_extension, d["pack"]["exe"], d["pack"]["cmdline"], d["test"]["delete"])
        
        if test_type == "wine" and "wine" in do_types:
            # seperated so we can opt to skip them as they take a little while to run.
            do_archiver_test(name, msg, def_extension, d["pack"]["exe"], d["pack"]["cmdline"], d["test"]["delete"])

        if test_type == "dosbox" and "dosbox" in do_types:
            # seperated so we can opt to skip them as they take a little while to run.
            do_archiver_test(name, msg, def_extension, d["pack"]["exe"], d["pack"]["cmdline"], d["test"]["delete"])

    if args.list == "types":
        print(f"Test types: {found_types}")

if __name__ == "__main__":
    main(sys.argv)
