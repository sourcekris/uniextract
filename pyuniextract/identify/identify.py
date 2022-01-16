import subprocess
import os.path
from .config import trid_args, trid_env, idarcbin, packerNames

def id_via_file(arcfile):
    id = b""
    try:
        id = subprocess.check_output(['file', arcfile])
    except Exception as e:
        print(f"id_via_file failed: {e}")
        return None
    
    id = id.decode().strip()
    if ":" not in id or id.split(": ")[1] == "data":
        return None
    return id.split(": ")[1]

def id_via_trid(arcfile):
    id = b""
    try:
        id = subprocess.check_output(trid_args + [arcfile], env=trid_env)
        #print(id)
    except Exception as e:
        print(f"id_via_trid failed: {e}\n{e.stdout.decode()}")
        return None
    
    id = id.decode().strip().splitlines()
    if 'Unknown!'  in id[-1]:
        return None

    for i, line in enumerate(id):
        if 'found no file' in line:
            return None
        if 'Collecting data from file' in line:
            break

    if 'Warning: file seems to be plain text/ASCII' in id:
        i += 4

    if len(id) >= i:
        return id[i+1]

def id_via_extension(arcfile):
    if '.' in arcfile:
        return os.path.splitext(os.path.basename(arcfile))[1]

def id_via_arcid(arcfile):
    p = subprocess.Popen([idarcbin, arcfile], stdout=subprocess.PIPE)
    p.communicate()

    if p.returncode in packerNames:
        return packerNames[p.returncode]
    
    return None
      
# given some file arcfile, return an identification string.
def identify_archive(arcfile, idtype=""):
    id = id_via_file(arcfile)
    if idtype == "file":
        return id

    if not id or idtype == "trid":
        id = id_via_trid(arcfile)
        if idtype == "trid":
            return id

    if not id or idtype == "idarc":
        id = id_via_arcid(arcfile)
        if idtype == "idarc":
            return id

    if not id:
        id = id_via_extension(arcfile)
    
    return id