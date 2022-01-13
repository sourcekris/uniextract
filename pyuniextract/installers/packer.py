#
# packer.py -
# archiver packing functions.

import os, os.path
import tempfile
from base64 import b64decode
from subprocess import Popen, PIPE
from .config import get_def, tools_path, default_fn, is_blob
from .template import prepare_cmdline, prepare_exe

# return the most preferred extension for archive profile.
def get_pack_ext(d):
    if "unpack" in d and "extension" in d["unpack"]:
        return d["unpack"]["extension"]
    if "install" in d and "extensions" in d["install"] and len(d["install"]["extensions"]) > 0:
        return d["install"]["extensions"][0]
    return None

def get_packer_cmd(d):
    exe = cmdline = ""
    if "pack" in d:
        if "exe" in d["pack"]:
            exe = d["pack"]["exe"]
        if "cmdline" in d["pack"]:
            cmdline = d["pack"]["cmdline"]
    return exe, cmdline

def get_content(d):
    if "test" in d and "content" in d["test"] and "padbyte" not in d["test"]:
        return d["test"]["content"]
    
    if "test" in d and "padbyte" in d["test"] and "content" in d["test"] and "padlen" in d["test"]:
        return d["test"]["content"] + (d["test"]["padbyte"] * d["test"]["padlen"])    

def pack_blob(d, filename):
    if "pack" in d and "blob" in d["pack"]:
        open(filename,'wb').write(b64decode(d["pack"]["blob"]))

# Creates an archive given an arbitrary archiver.
def pack_file(archiver, filename=default_fn):
    d = get_def(archiver)

    cwd = os.getcwd()
    tools = os.path.join(cwd, tools_path)
    exe, cmdline = get_packer_cmd(d)
    ext = "." + get_pack_ext(d)
    arcname = filename+ext

    content = get_content(d)
    if not content:
        content = archiver.upper()

    tmpdir = tempfile.mkdtemp()
    fullarc = os.path.join(tmpdir, arcname)
    os.chdir(tmpdir)

    if is_blob(d):
        pack_blob(d, arcname)
        os.chdir(cwd)
        return fullarc

    open(filename, "w").write(content) # write the file to archive to disk
    cmdline = prepare_cmdline(prepare_exe(exe, tools), cmdline, tools, file=filename, ext=ext)
    # print(f"cmdline: {cmdline}")
    try:
        p = Popen(cmdline, shell=True, stderr=PIPE, stdout=PIPE) # run the archiver
        outs, errs = p.communicate()
    except Exception as e:
        print(f"failed packing with {archiver} due to: {e}")
        os.chdir(cwd)
        return None

    if os.path.exists(arcname.upper()): # dos archivers use uppercase.
        arcname = arcname.upper()
        fullarc = os.path.join(tmpdir, arcname)

    if not os.path.exists(arcname):
        print(f"failed packing file with {archiver}: {arcname} was not created")
        os.chdir(cwd)
        return None

    os.chdir(cwd)
    return fullarc