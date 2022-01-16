#
# unpacker.py -
# archiver unpacking functions.

import subprocess
import tempfile
import os, os.path
import shutil
from .config import get_pack_ext, tools_path
from .template import prepare_cmdline, prepare_exe

def unpack_archive(archive, d, destdir=None, toolspath=tools_path):
    extension = get_pack_ext(d)

    with tempfile.TemporaryDirectory() as tmpdir:
        tools = os.path.join(os.getcwd(), toolspath)
        exe = prepare_exe(d["unpack"]["exe"], tools)
        cmdline = prepare_cmdline(exe, d["unpack"]["cmdline"], tools, destdir=tmpdir, archive=archive, ext=extension)

        try:
            extractres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"error running unarchive of test data: {e}\ncmdline: {cmdline}")
            #print(subprocess.check_output(f"ls -la {tmpdir}",shell=True).decode())
            return 0

        files = os.listdir(tmpdir)
        for fn in files:
            shutil.move(os.path.join(tmpdir, fn), destdir)
