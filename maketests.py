#!/usr/bin/env python

# maketests.py -
# tests that we can pack an archive with the archiver and emits a compressed, base64 encoded
# archive blob for storage as the json configuration "test"->"blob" value.

import argparse
import sys
import os, os.path, shutil
from gzip import compress
from base64 import b64encode, b64decode
from pyuniextract.installers.config import load_defs
from pyuniextract.installers.testarchiver import pad
from pyuniextract.installers.packer import pack_file

def do_blob_test(name, blob):
    print(f"{name} test: ", flush=True, end="")
    d = b''
    try:
        d = b64decode(blob)
    except Exception as e:
        print(f"error decoding b64 blob: {e}")
        return False
    
    print(b64encode(compress(d)).decode(), flush=True)
    return True

def do_archiver_test(name, msg, ext, exe, cmdline, rmorig):
    print(f"{name} test: ", flush=True, end="")
    arcname = pack_file(name)
    if not arcname:
        return False
    td = os.path.dirname(arcname)

    # compress and base64 the result
    d = b64encode(compress(open(arcname, 'rb').read())).decode() 
    # cleanup
    if td.startswith('/tmp/tmp'):
        shutil.rmtree(td)

    print(d, flush=True)
    return True

# valid_def checks that a definition has the required components to make a test blob.
def valid_def(d):
    if "name" not in d:
        print(f"test is missing a name: {d}")
        return False
    name = d["name"]

    if "pack" not in d:
        print(f"test {name} is missing its packer configuration")
        return False

    if "type" not in d["pack"]:
        print(f"test {name} is missing its pack type")
        return False
    test_type = d["pack"]["type"]
    
    if test_type == "blob" and ("blob" not in d["pack"] or not d["pack"]["blob"]):
        print(f"blob test {name} is missing its blob or the blob is empty")
        return False

    if "extensions" not in d or len(d["extensions"]) == 0:
        print(f"test {name} is missing extensions")
        return False

    if "test" not in d or "content" not in d["test"]:
        print(f"test configuration missing for {name} or no content is specified in test")
        return False
    
    if not d["test"]["content"]:
        print(f"content is empty in test {name}")
        return False

    return True

def main(argv):
    ap = argparse.ArgumentParser(description="Make test blobs for the archiver pre-requisites")
    ap.add_argument('-s',"--test", help="Run a specific test only, if test not found nothing is done.")
    ap.add_argument('-t',"--type", help="Run a specific type of test only.")
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
