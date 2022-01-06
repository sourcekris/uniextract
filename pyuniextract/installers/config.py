from glob import glob
import os.path
import json

# config
definitions_path = "defs/"
tools_path = "tools/"
toolsdist_path = "toolsdist/"
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

def is_builtin(d):
    if "unpack" in d and "type" in d["unpack"] and d["unpack"]["type"] == "builtin":
        return True
    return False

def is_apt(d):
    if is_builtin(d):
        return False
    if "install" in d and "method" in d["install"] and d["install"]["method"] == "apt":
        return True
    return False

def is_pip(d):
    if is_builtin(d):
        return False
    if "install" in d and "method" in d["install"] and d["install"]["method"] == "pip":
        return True
    return False

def is_source(d):
    if is_builtin(d):
        return False
    if "install" in d and "method" in d["install"] and d["install"]["method"] == "source":
        return True
    return False

