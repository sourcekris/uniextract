import subprocess

from pyuniextract.installers.config import Definition
from .testarchiver import test_archiver
from .extracttool import extracttool

# return True if the apt packages are already installed.
def apt_already_installed(d: Definition, field:str = "install") -> bool:
    results = []
    i = d.get_installer(field)
    for pkg in i.packages:
        cmdline = ["apt","list",pkg,"--installed"]
        try:
            res = subprocess.check_output(cmdline, stderr=subprocess.PIPE)
            if pkg in res.decode() and "[installed]" in res.decode():
                results.append(True)
        except subprocess.CalledProcessError as e:
            results.append(False)
    
    if all(results) and len(i.packages) == len(results):
        return True
    
    return False

def install_apt_packages(definitions: list[Definition], field: str = "install") -> None:
    for d in definitions:
        i = d.get_installer(field)
        if i.method == "apt" and len(i.packages) > 0:
            print(f"trying to install archiver: {d.name}: ", flush=True, end="")

            if not apt_already_installed(d, field=field):
                args = ['sudo','apt','-y','install']
                args += i.packages
                try:
                    aptres = subprocess.check_output(args, stderr=subprocess.PIPE)
                except Exception as e:
                    print(f'error installing archiver {d.name}: {e}')
                    continue

            extracttool(d, field=field)
            if test_archiver(d):
                print("OK")
            else:
                print("Failed")