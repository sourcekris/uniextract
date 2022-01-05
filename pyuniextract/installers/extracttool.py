
from .config import toolsdist_path, tools_path
import zipfile
import os.path

def get_tool_config(d):
    if "install" not in d:
        return
    
    toolcfg = {"container":"", "tool":"", "dependencies":[]}
    if "container" in d["install"] and "tool" in d["install"]:
        toolcfg["container"] = d["install"]["container"]
        toolcfg["tool"] = d["install"]["tool"]
        if "dependencies" in d["install"]:
            toolcfg["dependencies"] += d["install"]["dependencies"]

        return toolcfg

def get_tool_from_container(toolcfg):
    flist = [toolcfg["tool"]]
    flist += toolcfg["dependencies"]

    inst = []
    for fn in flist:
        inst.append(os.path.isfile(os.path.join(tools_path, fn)))
    
    if all(inst):
        # print(f"tool is already installed: {toolcfg['tool']}")
        return True

    zfpath = os.path.join(toolsdist_path, toolcfg["container"])

    if not os.path.isfile(zfpath):
        return False

    extracted = []
    with zipfile.ZipFile(zfpath, 'r') as zf:
        for fn in zf.namelist():
            if fn in flist:
                extracted.append(fn)
                zf.extract(fn, path=tools_path)
                # print(f"extracted tool file: {fn} from {zfpath}")
    
    if len(extracted) == len(flist):
        return True
    
    return False
    
def extracttool(d):
    tc = get_tool_config(d)
    if tc:
        return get_tool_from_container(tc)
    