#!/usr/bin/env python

import os.path
import subprocess
from glob import glob
import json
import tempfile
import base64
from gzip import decompress

# config
definitions_path = "defs/"

def load_defs():
    defnames = glob(os.path.join(definitions_path, "*.json"))
    definitions = []
    for d in defnames:
        try:
            jd = json.loads(open(d).read())
        except Exception as e:
            print(f'error loading archiver definition {d}: {e}, continuing...')
            continue

        definitions.append(jd)
    return definitions

# test the archiver give the test parameters in the definition for that 
# archiver
def test_archiver(d):
    if "test" not in d or len([True for x in ["blob", "file", "content"] if x in d["test"]]) != 3:
        # a test is not properly defined.
        return -1
    
    # what extension should our test archive have?
    extension = d["extensions"][0]              # default.
    if "extension" in d["unpack"]:
        extension = d["unpack"]["extension"]    # preferred one.
    
    if not extension.startswith("."):
        extension = "." + extension

    with tempfile.NamedTemporaryFile(suffix=extension) as arcfile:
        try:
            arcfile.write(decompress(base64.b64decode(d["test"]["blob"])))
            arcfile.flush()
        except Exception as e:
            print(f"error writing test data: {e}\nfilename: {arcfile.name}")
            return 0
    

        with tempfile.TemporaryDirectory() as tmpdir:
            cmdline = d["unpack"]["cmdline"]
            cmdline = cmdline.replace("$tool", d["unpack"]["exe"])
            cmdline = cmdline.replace("$archive", arcfile.name)
            cmdline = cmdline.replace("$destdir", tmpdir)

            try:
                extractres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE)
            except Exception as e:
                print(f"error running unarchive of test data: {e}\ncmdline: {cmdline}")
                return 0
            
            extracted_file = os.path.join(tmpdir, d["test"]["file"])
            if extracted_file.endswith("?"):
                # in case the archive does not store the name of the compressed file, e.g. gzip.
                basename = os.path.splitext(os.path.basename(arcfile.name))[0]
                extracted_file = os.path.join(tmpdir, basename)

            resultdata = ""
            try:
                resultdata = open(extracted_file).read()
            except Exception as e:
                print(f"error opening unarchived test data: {e}\ncmdline: {cmdline}")

            if resultdata == d["test"]["content"]:
                return 1
            else:
                print(f"archiver test file content mismatch:\ngot: {resultdata}\nwant: {d['test']['content']}")
                return 0

def install_apt_packages(definitions):
    for d in definitions:
        if "install" in d and "method" in d["install"]:
            if "apt" in d["install"]["method"] and "package" in d["install"]:
                print(f"trying to install archiver: {d['name']}: ", end="")
                try:
                    aptres = subprocess.check_output(['sudo','apt','install',d["install"]["package"]], stderr=subprocess.PIPE)
                except Exception as e:
                    print(f'error installing archiver {d["name"]}: {e}')
            
                if test_archiver(d):
                    print("OK")
                else:
                    print("Failed")

def install_pip_packages(definitions):
    for d in definitions:
        if "install" in d and "method" in d["install"]:
            if "pip" in d["install"]["method"] and "package" in d["install"]:
                print(f"trying to install archiver: {d['name']}: ", end="")
                try:
                    aptres = subprocess.check_output(['sudo','pip','install',d["install"]["package"]], stderr=subprocess.PIPE)
                except Exception as e:
                    print(f'error installing archiver {d["name"]}: {e}')
            
                if test_archiver(d):
                    print("OK")
                else:
                    print("Failed")

def main():
    defs = load_defs()
    install_apt_packages(defs)
    install_pip_packages(defs)

if __name__ == "__main__":
    main()
