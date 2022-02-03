
from .config import toolsdist_path, tools_path, Definition
import zipfile
import tempfile
import os.path
import shutil

def get_tool_config(d: Definition, field: str = "install") -> dict:
    i = d.get_installer(field)
    toolcfg = {"container":"", "tool":"", "dependencies":[], "renametool":""}
    if i.container and i.tool:
        toolcfg["container"] = i.container
        toolcfg["tool"] = i.tool
        if i.dependencies:
            toolcfg["dependencies"] += i.dependencies
        if i.should_rename_tool():
            toolcfg["renametool"] = i.renametool

        return toolcfg

def get_tool_from_container(toolcfg: dict) -> bool:
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
    
def extracttool(d: Definition, field: str = "install"):
    tc = get_tool_config(d, field=field)
    if tc:
        return get_tool_from_container(tc)
    