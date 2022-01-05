#!/usr/bin/python

# List definitions by field.

import inspect
import argparse
import sys
import subprocess
import os, os.path

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from pyuniextract.installers.config import load_defs

def walk(d, node, key, f, z):
    if type(node) is dict:
        return {k: walk(d, v, k, f, z) for k, v in node.items()}
    elif type(node) is list:
        return [walk(d, x, key, f, z) for x in node]
    else:
        if (not z and key == f) or (z and key == f and node == z):
            fn = os.path.basename(d['definition_filename'])
            print(f"{fn}\t:\t{key} = {node}")
        
        return  

def main(argv):
    ap = argparse.ArgumentParser(description="List definition details per field.")
    ap.add_argument("-f","--field",required=True, help="Field (key) to list by.")
    ap.add_argument("-v", "--value", help="Value to filter for. If none then all values will be emitted.")
    args = ap.parse_args(argv)

    defs = load_defs(addfn=True, defpath=os.path.join(os.getcwd(), "..", "defs"))

    for d in defs:
        walk(d, d, None, args.field, args.value)

if __name__ == "__main__":
    main(sys.argv[1:])