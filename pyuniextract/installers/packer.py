import os, os.path
import tempfile
from subprocess import Popen, PIPE
from .config import get_def, tools_path, default_fn
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
    
    
# Creates an archive given an arbitrary archiver.
def pack_file(archiver, filename=default_fn, content=""):
    d = get_def(archiver)

    cwd = os.getcwd()
    tools = os.path.join(cwd, tools_path)
    exe, cmdline = get_packer_cmd(d)
    ext = "." + get_pack_ext(d)

    if not content:
        content = archiver.upper()

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        open(filename, "w").write(content) # write the file to archive to disk
        cmdline = prepare_cmdline(prepare_exe(exe, tools), cmdline, tools, file=filename, ext=ext)
        print(f"cmdline: {cmdline}")
        try:
            p = Popen(cmdline, shell=True, stderr=PIPE, stdout=PIPE) # run the archiver
            outs, errs = p.communicate()
        except Exception as e:
            print(f"failed packing with {archiver} due to: {e}")
            os.chdir(cwd)
            return None

        arcname = filename+ext
        if os.path.exists(arcname.upper()): # dos archivers use uppercase.
            arcname = arcname.upper()

        if not os.path.exists(arcname):
            print(f"failed packing file with {archiver}: {arcname} was not created")
            os.chdir(cwd)
            return None

        os.chdir(cwd)
        return os.path.join(tmpdir, arcname)