#!/usr/bin/env python

# prereqs.py -
# Installs the pre-requisite archivers, packages, and platforms necessary to extract the archive types.

import sys
import argparse
from pyuniextract.installers.apt import install_apt_packages
from pyuniextract.installers.pip import install_pip_packages
from pyuniextract.installers.source import install_from_source
from pyuniextract.installers.config import load_defs, is_apt, is_builtin, is_source, is_pip

def main(argv):
    ap = argparse.ArgumentParser(description="Install and test the archiver pre-requisites")
    ap.add_argument('-s',"--specific", help="Install one specific archiver and run that test only.")
    ap.add_argument('-t',"--type", help="Install and run tests of a specific type only.")
    ap.add_argument('-l',"--list", choices=["archivers", "types"], help="List archivers or types of archivers.")
    args = ap.parse_args(argv)

    defs = load_defs()
    types = set()
    if args.list:
        # Just print the list and return.
        for d in defs:
            if args.list == "archivers":
                print(d["name"])
            if "install" in d and "method" in d["install"]:
                types.add(d["install"]["method"])
            
            if "unpack" in d and "type" in d["unpack"]:
                types.add(d["unpack"]["type"])
    
        if args.list == "types":
                print(types)
        return

    if args.specific:
        for d in defs:
            if "name" in d and d["name"] == args.specific:
                if is_builtin(d):
                    print(f"pack install and test for {args.specific} is not yet implemented.")
                    return
                if is_apt(d):
                    install_apt_packages([d])
                    return
                if is_pip(d):
                    install_pip_packages([d])
                    return
                if is_source(d):
                    install_from_source([d])
                    return
                
                print(f"unknown archiver type so bailing out")
                break
        return
            
    if args.type:
        if args.type == "apt":
            install_apt_packages(defs)
        if args.type == "pip":
            install_pip_packages(defs)
        if args.type == "source":
            install_from_source(defs)
        if args.type == "builtin":
            print(f'not yet implemented')
            #install_from_source(defs)   
        return

    install_apt_packages(defs)
    install_pip_packages(defs)
    install_from_source(defs)

if __name__ == "__main__":
    main(sys.argv[1:])
