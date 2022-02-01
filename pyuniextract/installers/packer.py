#
# packer.py -
# archiver packing functions.

import os, os.path
import tempfile
from base64 import b64decode
from subprocess import Popen, PIPE
from .config import get_def, tools_path, default_fn, Definition
from .template import prepare_cmdline, prepare_exe

def pack_blob(d: Definition, filename: str)-> None:
    open(filename,'wb').write(b64decode(d.packer.blob))

# Creates an archive given an arbitrary archiver.
def pack_file(archiver, filename=default_fn):
    d = get_def(archiver)

    cwd = os.getcwd()
    tools = os.path.join(cwd, tools_path)
    exe, cmdline = d.packer.exe, d.packer.cmdline
    ext = d.get_pack_ext()
    arcname = filename+ext

    content = d.get_content()
    if not content:
        content = archiver.upper()

    tmpdir = tempfile.mkdtemp()
    fullarc = os.path.join(tmpdir, arcname)
    os.chdir(tmpdir)

    if d.is_blob():
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