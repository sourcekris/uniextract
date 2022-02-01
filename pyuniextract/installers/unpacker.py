#
# unpacker.py -
# archiver unpacking functions.

import subprocess
import tempfile
import os, os.path
import shutil
from .config import tools_path, Definition
from .template import prepare_cmdline, prepare_exe

def unpack_archive(archive: str, d: Definition, destdir: str = None, toolspath: str = tools_path) -> None:
    extension = d.get_pack_ext()

    with tempfile.TemporaryDirectory() as tmpdir:
        tools = os.path.join(os.getcwd(), toolspath)
        exe = prepare_exe(d.unpacker.exe, tools)
        cmdline = prepare_cmdline(exe, d.unpacker.cmdline, tools, destdir=tmpdir, archive=archive, ext=extension)

        try:
            extractres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"error running unarchive of test data: {e}\ncmdline: {cmdline}")
            #print(subprocess.check_output(f"ls -la {tmpdir}",shell=True).decode())
            return 0

        files = os.listdir(tmpdir)
        for fn in files:
            dst = os.path.join(destdir, fn)
            if os.path.exists(dst):
                print(f'destination file exists, not overwriting: {dst}')
                continue
            shutil.move(os.path.join(tmpdir, fn), destdir)
