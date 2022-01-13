
from .config import toolsdist_path, tools_path, should_rename_tool
import zipfile
import tempfile
import os.path
import shutil

def get_tool_config(d, field="install"):
    if field not in d:
        return
    
    toolcfg = {"container":"", "tool":"", "dependencies":[], "renametool":""}
    if "container" in d[field] and "tool" in d[field]:
        toolcfg["container"] = d[field]["container"]
        toolcfg["tool"] = d[field]["tool"]
        if "dependencies" in d[field]:
            toolcfg["dependencies"] += d[field]["dependencies"]
        if should_rename_tool(d):
            toolcfg["renametool"] = d[field]["renametool"]

        return toolcfg

def get_tool_from_container(toolcfg):
    flist = [toolcfg["tool"]]
    flist += toolcfg["dependencies"]

    clist = []
    if toolcfg["renametool"]:
        clist.append(toolcfg["renametool"])
    else:
        clist.append(toolcfg["tool"])
    clist += toolcfg["dependencies"]

    inst = []
    for fn in clist:
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
                if toolcfg["renametool"] and fn == toolcfg["tool"]:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        zf.extract(fn, path=tmpdir)
                        shutil.move(os.path.join(tmpdir, fn), os.path.join(tools_path, toolcfg["renametool"]))
                else:            
                    zf.extract(fn, path=tools_path)
    
    if len(extracted) == len(flist):
        return True
    
    return False
    
def extracttool(d, field="install"):
    tc = get_tool_config(d, field=field)
    if tc:
        return get_tool_from_container(tc)
    