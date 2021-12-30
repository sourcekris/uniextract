#!/usr/bin/env python

import os
import os.path
import subprocess
from glob import glob
import json
import tempfile
import base64
from gzip import decompress

# config
definitions_path = "defs/"
tools_path = "tools/"

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

# return True if the archiver needed to unpack d is already in the system path.
def archiver_in_path(d):
    if "install" in d and "exist_check" in d["install"] and len(d["install"]["exist_check"]) > 1:
        cmdline = d["install"]["exist_check"][0]
        want = d["install"]["exist_check"][1]

        try:
            res = subprocess.check_output(cmdline, shell=True)
            if want in res.decode():
                return True
        except subprocess.CalledProcessError as e:
            # Some processes return an erroneous exit code even when they are working.
            if want in e.stdout.decode() or want in e.stderr.decode():
                return True
            return False
    return False

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

    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as arcfile:
        try:
            try:
                arcfile.write(decompress(base64.b64decode(d["test"]["blob"])))
                arcfile.flush()
            except Exception as e:
                print(f"error writing test data: {e}\nfilename: {arcfile.name}")
                return 0
                
            with tempfile.TemporaryDirectory() as tmpdir:
                exe = d["unpack"]["exe"]
                exe = exe.replace("$tools", os.path.join(os.getcwd(), tools_path))
                cmdline = d["unpack"]["cmdline"]
                cmdline = cmdline.replace("$tool", exe)
                cmdline = cmdline.replace("$archive", arcfile.name)
                cmdline = cmdline.replace("$destdir", tmpdir)
                cmdline = cmdline.replace("$basename", os.path.splitext(os.path.basename(arcfile.name))[0])

                #print(f"{cmdline}", flush=True, end="")
                try:
                    extractres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE)
                except Exception as e:
                    print(f"error running unarchive of test data: {e}\ncmdline: {cmdline}")
                    # print(subprocess.check_output(f"ls -la {tmpdir}",shell=True).decode())
                    return 0

                #print("Extracted, ", flush=True, end="") 
                #print(subprocess.check_output(f"ls -la {os.path.basename(arcfile.name)}",shell=True).decode())
                extracted_file = os.path.join(tmpdir, d["test"]["file"])
                if extracted_file.endswith("?"):
                    # in case the archive does not store the name of the compressed file, e.g. gzip.
                    basename = os.path.splitext(os.path.basename(arcfile.name))[0]
                    extracted_file = os.path.join(tmpdir, basename)

                resultdata = ""
                try:
                    resultdata = open(extracted_file).read()
                except Exception as e:
                    print(f"error opening unarchived test data: {e}")
                    # print(subprocess.check_output(f"ls -la {tmpdir}",shell=True).decode())

                if resultdata == d["test"]["content"]:
                    return 1
                else:
                    print(f"archiver test file content mismatch:\ngot: {resultdata}\nwant: {d['test']['content']}")
                    return 0
        finally:
            if "delete" in d["test"] and d["test"]["delete"]:
                os.unlink(arcfile.name)

def install_apt_packages(definitions):
    for d in definitions:
        if "install" in d and "method" in d["install"]:
            if "apt" in d["install"]["method"] and "packages" in d["install"]:
                print(f"trying to install archiver: {d['name']}: ", flush=True, end="")
                args = ['sudo','apt','install']
                args += d["install"]["packages"]
                try:
                    aptres = subprocess.check_output(args, stderr=subprocess.PIPE)
                except Exception as e:
                    print(f'error installing archiver {d["name"]}: {e}')
                    continue

                #print(f"Installed, Testing: ", flush=True, end="")
                if test_archiver(d):
                    print("OK")
                else:
                    print("Failed")

def install_pip_packages(definitions):
    for d in definitions:
        if "install" in d and "method" in d["install"]:
            if "pip" in d["install"]["method"] and "packages" in d["install"]:
                print(f"trying to install archiver: {d['name']}: ", flush=True, end="")
                args = ['sudo','pip','install']
                args += d["install"]["packages"]
                try:
                    aptres = subprocess.check_output(args, stderr=subprocess.PIPE)
                except Exception as e:
                    print(f'error installing archiver {d["name"]}: {e}')
                    continue
            
                if test_archiver(d):
                    print("OK")
                else:
                    print("Failed")

def install_from_source(definitions):
    for d in definitions:
        if archiver_in_path(d):
            print(f"trying to build archiver: {d['name']}: Exists, Testing: ", flush=True, end="")

            # archiver is in path so, overwrite the local stash folder that comes in the config.
            d["unpack"]["exe"] = d["unpack"]["exe"].replace("$tools/","")
            if test_archiver(d):
                print("OK")
            else:
                print("Failed")

            continue

        if "install" in d and "method" in d["install"]:
            if "source" in d["install"]["method"] and "repo" in d["install"]:
                with tempfile.TemporaryDirectory() as tmpdir:
                    print(f"trying to build archiver: {d['name']}: ", flush=True, end="")
                    try:
                        cloneres = subprocess.check_output(['git','clone',d["install"]["repo"], tmpdir], stderr=subprocess.PIPE)
                    except Exception as e:
                        print(f'error cloning repo {d["install"]["repo"]} to {tmpdir}: {e}')
                        continue

                    print("Cloned, ", flush=True, end="")

                    # Create build script
                    tp = os.path.join(os.getcwd(), tools_path)
                    cmdline = d["install"]["build"]
                    cmdline = cmdline.replace("$tools", tp)
                    try:
                        buildres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE, cwd=tmpdir)
                    except Exception as e:
                        print(f'error building archiver {d["name"]}: {e}')
                        continue

                    print("Built, ", end="")
            
                if test_archiver(d):
                    print("OK")
                else:
                    print("Failed")

def main():
    defs = load_defs()
    install_apt_packages(defs)
    #install_pip_packages(defs)
    #install_from_source(defs)

if __name__ == "__main__":
    main()
