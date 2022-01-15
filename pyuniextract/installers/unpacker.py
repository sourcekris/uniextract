#
# unpacker.py -
# archiver unpacking functions.

import subprocess
import tempfile
import os, os.path
from .config import get_pack_ext, tools_path
from .template import prepare_cmdline, prepare_exe

def unpack_archive(archive, d, destdir=None):
    extension = get_pack_ext(d)

    with tempfile.TemporaryDirectory() as tmpdir:
        tools = os.path.join(os.getcwd(), tools_path)
        basename = os.path.splitext(os.path.basename(archive))[0]
        exe = prepare_exe(d["unpack"]["exe"], tools)
        cmdline = prepare_cmdline(exe, d["unpack"]["cmdline"], tools, destdir=tmpdir, archive=archive, ext=extension)

        try:
            extractres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"error running unarchive of test data: {e}\ncmdline: {cmdline}")
            #print(subprocess.check_output(f"ls -la {tmpdir}",shell=True).decode())
            return 0

        #print("Extracted, ", flush=True, end="") 
        #print(subprocess.check_output(f"ls -la {os.path.basename(arcfile.name)}",shell=True).decode())
        extracted_file = os.path.join(tmpdir, d["test"]["file"])
        if extracted_file.endswith("?"):
            # in case the archive does not store the name of the compressed file, e.g. gzip.
            extracted_file = os.path.join(tmpdir, basename)
        
        if "?/" in extracted_file:
            fn = extracted_file.split("/")[-1]
            # in case the archive creates a folder based on the archive name to put the files into e.g. msi.
            extracted_file = os.path.join(tmpdir, basename, fn)
        
    
        print(f'filename: {extracted_file}')