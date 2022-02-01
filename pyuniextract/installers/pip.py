import subprocess

from .config import Definition
from .testarchiver import test_archiver
from .extracttool import extracttool

def install_pip_packages(definitions: list[Definition]):
    for d in definitions:
        if "pip" in d.installer.method and len(d.installer.packages) > 0:
            print(f"trying to install archiver: {d.name}: ", flush=True, end="")
            args = ['sudo','pip','install']
            args += d.installer.packages
            try:
                aptres = subprocess.check_output(args, stderr=subprocess.PIPE)
            except Exception as e:
                print(f'error installing archiver {d.name}: {e}')
                continue

            extracttool(d)
            if test_archiver(d):
                print("OK")
            else:
                print("Failed")