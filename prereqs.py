#!/usr/bin/env python

import os
import os.path
import sys
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
            p = subprocess.Popen(cmdline, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            out, err = p.communicate()
            #res = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE)
            if want in out.decode() or want in err.decode():
                return True
        except subprocess.CalledProcessError as e:
            # Some processes return an erroneous exit code even when they are working.
            try:
                if want in e.stdout.decode() or want in e.stderr.decode():
                    return True
            except AttributeError:
                return False

            return False
    return False

# return True if the apt packages are already installed.
def apt_already_installed(d):
    results = []
    if "install" in d and "packages" in d["install"]:
        for pkg in d["install"]["packages"]:
            cmdline = ["apt","list",pkg,"--installed"]
            try:
                res = subprocess.check_output(cmdline, stderr=subprocess.PIPE)
                if pkg in res.decode() and "[installed]" in res.decode():
                    results.append(True)
            except subprocess.CalledProcessError as e:
                results.append(False)
    
    if all(results) and len(d["install"]["packages"]) == len(results):
        return True
    
    return False

# used for archivers that extract entire blocks to disk e.g. CPM archivers.
def pad(data, padbyte, padlen):
    pb = chr(int(padbyte, 16))
    pbl = padlen - divmod(len(data), padlen)[1]
    return data + (pb * pbl)

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
                tools = os.path.join(os.getcwd(), tools_path)
                basename = os.path.splitext(os.path.basename(arcfile.name))[0]
                windest = "z:" + tmpdir.replace("/","\\\\")
                winarc = "z:" + arcfile.name.replace("/","\\\\")
                exe = d["unpack"]["exe"]
                exe = exe.replace("$tools", tools)
                cmdline = d["unpack"]["cmdline"]
                cmdline = cmdline.replace("$tools", tools)
                cmdline = cmdline.replace("$tool", exe)
                cmdline = cmdline.replace("$archive", arcfile.name)
                cmdline = cmdline.replace("$arcloc", os.path.dirname(arcfile.name))
                cmdline = cmdline.replace("$windestdir", windest)
                cmdline = cmdline.replace("$winarchive", winarc)
                cmdline = cmdline.replace("$destdir", tmpdir)
                cmdline = cmdline.replace("$basename", basename)
                cmdline = cmdline.replace("$shortname", basename[:6]+"~1"+extension) # for dos unpackers, but ~1 might not be good enough?

                #print(f"{cmdline}", flush=True, end="")
                try:
                    extractres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE)
                except Exception as e:
                    print(f"error running unarchive of test data: {e}\ncmdline: {cmdline}")
                    #print(subprocess.check_output(f"ls -la {tmpdir}",shell=True).decode())
                    return 0

                #print("Extracted, ", flush=True, end="") 
                #print(subprocess.check_output(f"ls -la {os.path.basename(arcfile.name)}",shell=True).decode())
                extracted_file = os.path.join(tmpdir, d["test"]["file"])
                if extracted_file.endswith("?"):
                    # in case the archive does not store the name of the compressed file, e.g. gzip.
                    basename = os.path.splitext(os.path.basename(arcfile.name))[0]
                    extracted_file = os.path.join(tmpdir, basename)
                
                if "?/" in extracted_file:
                    fn = extracted_file.split("/")[-1]
                    # in case the archive creates a folder based on the archive name to put the files into e.g. msi.
                    basename = os.path.splitext(os.path.basename(arcfile.name))[0]
                    extracted_file = os.path.join(tmpdir, basename, fn)

                resultdata = ""
                try:
                    resultdata = open(extracted_file).read()
                except Exception as e:
                    print(f"error opening unarchived test data: {e}")
                    #print(subprocess.check_output(f"ls -la {tmpdir}",shell=True).decode())

                # did we get want we want?
                want = d["test"]["content"]
                if "padbyte" in d["test"] and "padlen" in d["test"]:
                    # some formats come padded (CP/M)
                    want = pad(want, d["test"]["padbyte"],d["test"]["padlen"])

                if resultdata == want:
                    return 1
                else:
                    print(f"archiver test file content mismatch:\ngot: {resultdata.encode()}\nwant: {want.encode()}")
                    return 0
        finally:
            if "delete" in d["test"] and d["test"]["delete"]:
                os.unlink(arcfile.name)

def install_apt_packages(definitions):
    for d in definitions:
        if "install" in d and "method" in d["install"]:
            if "apt" in d["install"]["method"] and "packages" in d["install"]:
                print(f"trying to install archiver: {d['name']}: ", flush=True, end="")

                if not apt_already_installed(d):
                    args = ['sudo','apt','-y','install']
                    args += d["install"]["packages"]
                    try:
                        aptres = subprocess.check_output(args, stderr=subprocess.PIPE)
                    except Exception as e:
                        print(f'error installing archiver {d["name"]}: {e}')
                        continue
                # else:
                #     print('skipped install')

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

def main(args):
    defs = load_defs()

    if len(args) > 0:
        if args[1] in ["apt", "pip", "source"]:
            if "apt" in args[1]:
                if len(args) == 3:
                    for d in defs:
                        if d["name"] == args[2]:
                            install_apt_packages([d])
                else:
                    install_apt_packages(defs)
                return

            if "pip" in args[1]:
                install_pip_packages(defs)
                return

            if "source" in args[1]:
                install_from_source(defs)
                return

    install_apt_packages(defs)
    install_pip_packages(defs)
    install_from_source(defs)

if __name__ == "__main__":
    main(sys.argv)
