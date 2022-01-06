#
# Convert NaShrinK Archives into DCL Implode and extract
# them with deark.
#
# https://github.com/sourcekris/unnsk
#
# Requires: https://github.com/jsummers/deark
#

import shutil
import os, os.path
import subprocess
import tempfile
from struct import unpack

name = "NaShrinK"
ext = "NSK"
file_sig = b'NSK'
crcoff = 0x8
compszoff = 0x3
uncompszoff = 0xc
fnszoff = 0x10
fnoff = 0x11

def unnsk(fn, dstpath, deark="deark", overwrite=False):

    if not os.path.exists(fn):
        print(f"{fn} does not exist.")
        return
    
    if deark == "deark":
        deark = shutil.which(deark)

    if not os.path.isfile(deark):
        print(f"deark not found at path {deark} so aborting.")
        return
    
    fsize = os.path.getsize(fn)
    if not os.path.isdir(dstpath):
        print(f"destination folder {dstpath} does not exist")
        return

    with open(fn, "rb") as f:

        while True:
            id = f.read(len(file_sig))
            if id != file_sig:
                print(f'{fn} does not appear to be a {ext} file')
                return

            compsize = unpack('I', f.read(4))[0]
            # byte 0x7 -> 0xb inclusive are unknown purpose.
            f.seek(f.tell() + 5)
            uncompsize = unpack('I', f.read(4))[0]
            fnsz = ord(f.read(1))
            if fnsz > 12:
                print(f'invalid filename size {fnsz}')
                return

            fname = f.read(fnsz).decode()
            print(f"Extracting:\t{fname}\t{compsize} / {uncompsize} bytes")

            fname = os.path.join(dstpath, fname)
            if os.path.exists(fname) and not overwrite:
                print(f"aborted: {fname} file exists, wont overwrite it")
                return
            
            compdata = f.read(compsize)
            with tempfile.NamedTemporaryFile() as dclfile:
                open(dclfile.name, 'wb').write(compdata)
                with tempfile.NamedTemporaryFile(delete=False) as uncfile:
                    cmdline = [deark, '-m', 'dclimplode',dclfile.name, '-o', uncfile.name]
                    outs = errs = ""
                    try:
                        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        outs, errs = p.communicate()
                    except Exception as e:
                        print(f"failed extracting the DCL portion of the file: {e}")
                        return

                    extracted = uncfile.name + ".000.unc"
                    if os.path.isfile(extracted):
                        shutil.move(extracted, fname)
                    else:
                        print(f"failed extracting with deark: {outs} {errs}")
                        return

            # Are we done or are there more files?
            if f.tell() == fsize:
                break