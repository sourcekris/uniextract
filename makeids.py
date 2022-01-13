#!/usr/bin/env python

# makeids.py -
# pack an archive then attempt to uniquely identify the format using file, trid, idarc etc.

import argparse
import subprocess
import sys
import os, os.path
from subprocess import Popen, PIPE
from pyuniextract.installers.config import load_defs, trid_args, trid_env
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

def id_via_file(arcfile):
    id = b""
    try:
        id = subprocess.check_output(['file', arcfile])
    except Exception as e:
        print(f"id_via_file failed: {e}")
        return None
    
    id = id.decode().strip()
    if ":" not in id or id.split(": ")[1] == "data":
        return None
    return id.split(": ")[1]

def id_via_trid(arcfile):
    id = b""
    try:
        id = subprocess.check_output(trid_args + [arcfile], env=trid_env)
        #print(id)
    except Exception as e:
        print(f"id_via_trid failed: {e}\n{e.stdout.decode()}")
        return None
    
    id = id.decode().strip().splitlines()
    if 'Unknown!'  in id[-1]:
        return None

    for i, line in enumerate(id):
        if 'found no file' in line:
            return None
        if 'Collecting data from file' in line:
            break

    if 'Warning: file seems to be plain text/ASCII' in id:
        i += 4

    if len(id) >= i:
        return id[i+1]

        

def id_via_arcid(arcfile):
    return None

def identify_archive(arcfile):
    return id_via_trid(arcfile)

def main(argv):
    ap = argparse.ArgumentParser(description="Make test archives then attempt to identify them")
    ap.add_argument('-s',"--specific", help="Run a specific identification only, if test not found nothing is done.")
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
                id = identify_archive(af)
                print(f'archiver {name} identified as: {id}')

            continue

        af = pack_file(name)
        id = identify_archive(af)
        print(f'archiver {name} identified as: {id}')
        



if __name__ == "__main__":
    main(sys.argv)
