from glob import glob
import os.path
import json

# config
definitions_path = "defs/"
tools_path = "tools/"
default_fn = "0"

def load_defs(addfn=False, defpath=None):
    if not defpath:
        defpath = definitions_path
    defnames = glob(os.path.join(defpath, "*.json"))
    definitions = []
    for d in defnames:
        try:
            jd = json.loads(open(d).read())
        except Exception as e:
            print(f'error loading archiver definition {d}: {e}, continuing...')
            continue

        if addfn:
            jd["definition_filename"] = d
        definitions.append(jd)
    return definitions
