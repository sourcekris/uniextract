#!/usr/bin/python

# Add new config to all defs.

import inspect
import re
import sys
import subprocess
import os, os.path
from prettyjson import dumppretty

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from pyuniextract.installers.config import load_defs


pcntre = re.compile("\d+\.\d\%\s")
numre = re.compile("\s\(\d+\/\d+\)")

def main(argv):
    defs = load_defs(addfn=True, defpath=os.path.join(os.getcwd(), "..", "defs"))

    for d in defs:
        fn = d["definition_filename"]
        del d["definition_filename"]

        # fileres = subprocess.check_output(['./makeids.py','-s',d["name"],'-t','file'], cwd='..')
        # tridres = subprocess.check_output(['./makeids.py','-s',d["name"],'-t','trid'], cwd='..')
        idarcres = subprocess.check_output(['./makeids.py','-s',d["name"],'-t','idarc'], cwd='..')

        # fileres = fileres.decode().strip().split(': ')[1]
        # tridres = tridres.decode().strip().split(': ')[1]
        idarcres = idarcres.decode().strip().split(': ')[1]

        # tridres = pcntre.sub("", tridres)
        # tridres = numre.sub("", tridres)
        d["identification"]["idarc"] = idarcres
        print(f"doing {d['name']}")
        open(fn, 'w').write(dumppretty(d))
        #print(dumppretty(d))

        
        

if __name__ == "__main__":
    main(sys.argv[1:])