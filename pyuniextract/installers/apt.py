import subprocess
from .testarchiver import test_archiver
from .extracttool import extracttool

# return True if the apt packages are already installed.
def apt_already_installed(d, field="install"):
    results = []
    if field in d and "packages" in d[field]:
        for pkg in d[field]["packages"]:
            cmdline = ["apt","list",pkg,"--installed"]
            try:
                res = subprocess.check_output(cmdline, stderr=subprocess.PIPE)
                if pkg in res.decode() and "[installed]" in res.decode():
                    results.append(True)
            except subprocess.CalledProcessError as e:
                results.append(False)
    
    if all(results) and len(d[field]["packages"]) == len(results):
        return True
    
    return False

def install_apt_packages(definitions, field="install"):
    for d in definitions:
        if field in d and "method" in d["install"]:
            if "apt" in d[field]["method"] and "packages" in d[field]:
                print(f"trying to install archiver: {d['name']}: ", flush=True, end="")

                if not apt_already_installed(d, field=field):
                    args = ['sudo','apt','-y','install']
                    args += d[field]["packages"]
                    try:
                        aptres = subprocess.check_output(args, stderr=subprocess.PIPE)
                    except Exception as e:
                        print(f'error installing archiver {d["name"]}: {e}')
                        continue

                extracttool(d, field=field)
                if test_archiver(d):
                    print("OK")
                else:
                    print("Failed")