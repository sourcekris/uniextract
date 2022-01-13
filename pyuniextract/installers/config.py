from glob import glob
import os.path
import json

# config
definitions_path = "defs/"
tools_path = "tools/"
toolsdist_path = "toolsdist/"
default_fn = "0"

trid_defs = "/usr/share/trid/triddefs.trd"
trid_args = ['/usr/local/bin/trid', '-n:1', f'-d:{trid_defs}']
trid_env = {"LC_ALL":"C"}

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

def get_def(defname, addfn=False, defpath=None):
    if not defpath:
        defpath = definitions_path

    defs = load_defs(addfn=addfn, defpath=defpath)
    for d in defs:
        if "name" in d and d["name"] == defname:
            return d
    
    return None

def is_builtin(d):
    if "unpack" in d and "type" in d["unpack"] and d["unpack"]["type"] == "builtin":
        return True
    return False

def is_apt(d, field="install"):
    if is_builtin(d):
        return False
    if field in d and "method" in d[field] and d[field]["method"] == "apt":
        return True
    return False

def is_pip(d, field="install"):
    if is_builtin(d):
        return False
    if field in d and "method" in d[field] and d[field]["method"] == "pip":
        return True
    return False

def is_source(d, field="install"):
    if is_builtin(d):
        return False
    if field in d and "method" in d[field] and d[field]["method"] == "source":
        return True
    return False

def is_blob(d):
    if "pack" in d and "type" in d["pack"] and d["pack"]["type"] == "blob":
        return True
    return False

def should_skip_test(d, field="install"):
    if field in d and "test_install" in d[field]:
        if not d[field]["test_install"]:
            return True
    return False

def has_unpackinstall(d):
    if "unpackinstall" in d:
        return True
    return False

def has_packinstall(d):
    if "packinstall" in d:
        return True
    return False

def should_rename_tool(d):
    if "install" in d and "renametool" in d["install"] and "tool" in d["install"]:
        if d["install"]["renametool"] != d["install"]["tool"]:
            return True
    return False

