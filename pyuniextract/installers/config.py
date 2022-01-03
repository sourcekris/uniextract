from glob import glob
import os.path
import json

# config
definitions_path = "defs/"
tools_path = "tools/"

def load_defs(addfn=False):
    defnames = glob(os.path.join(definitions_path, "*.json"))
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