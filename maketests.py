#!/usr/bin/env python

import argparse
import sys
import os, os.path
import tempfile
from gzip import compress
from base64 import b64encode, b64decode
from subprocess import Popen, PIPE
from pyuniextract.installers.config import load_defs, default_fn, tools_path
#from pyuniextract.common import prettyjson
from pyuniextract.installers.template import prepare_cmdline, prepare_exe

def_store = "defs/"

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
    cwd = os.getcwd()
    tools = os.path.join(cwd, tools_path)
    ext = "." + ext
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        open(default_fn, "w").write(msg) # write the file to archive to disk
        cmdline = prepare_cmdline(prepare_exe(exe, tools), cmdline, tools, file=default_fn, ext=ext)
        #print(f"cmdline: {cmdline}")
        try:
            p = Popen(cmdline, shell=True, stderr=PIPE, stdout=PIPE) # run the archiver
            outs, errs = p.communicate()
        except Exception as e:
            print(f"failed doing test {name} due to: {e}")
            os.chdir(cwd)
            return False
        arcname = default_fn+ext
        if not os.path.exists(arcname):
            print(f"failed doing test {name} file {arcname} was not created")
            os.chdir(cwd)
            return False
        
        d = b64encode(compress(open(arcname, 'rb').read())).decode() # compress and base64 the result

        os.unlink(arcname)  # cleanup
        if rmorig:
            os.unlink(default_fn)
        
        print(d, flush=True)
        os.chdir(cwd)
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
    return True

def main(argv):
    ap = argparse.ArgumentParser(description="Make test blobs for the archiver pre-requisites")
    ap.add_argument('-s',"--test", help="Run a specific test only, if test not found nothing is done.")
    ap.add_argument('-t',"--type", help="Run a specific type of test only.")
    ap.add_argument('-l',"--list", choices=["tests", "types"], help="List tests or types of tests.")
    args = ap.parse_args(argv[1:])

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

        if args.test:
            if test_type == "blob":
                do_blob_test(name, d["pack"]["blob"])
            elif test_type == "archiver":
                do_archiver_test(name, d["test"]["content"], def_extension, d["pack"]["exe"], d["pack"]["cmdline"], d["test"]["delete"])
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

        if test_type == "blob":
            do_blob_test(name, d["pack"]["blob"])
        elif test_type == "archiver":
            do_archiver_test(name, d["test"]["content"], def_extension, d["pack"]["exe"], d["pack"]["cmdline"], d["test"]["delete"])
        else:
            print(f"not yet implemented for test {name}")
        


    if args.list == "types":
        print(f"Test types: {found_types}")

if __name__ == "__main__":
    main(sys.argv)
