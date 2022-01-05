import subprocess
from .testarchiver import test_archiver
from .extracttool import extracttool

def install_pip_packages(definitions):
    for d in definitions:
        if "install" in d and "method" in d["install"]:
            if "pip" in d["install"]["method"] and "packages" in d["install"]:
                print(f"trying to install archiver: {d['name']}: ", flush=True, end="")
                args = ['sudo','pip','install']
                args += d["install"]["packages"]
                try:
                    aptres = subprocess.check_output(args, stderr=subprocess.PIPE)
                except Exception as e:
                    print(f'error installing archiver {d["name"]}: {e}')
                    continue

                extracttool(d)
                if test_archiver(d):
                    print("OK")
                else:
                    print("Failed")