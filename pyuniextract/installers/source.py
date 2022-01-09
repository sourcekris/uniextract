import subprocess
import tempfile
import os, os.path
from .testarchiver import test_archiver
from .extracttool import extracttool
from .config import tools_path

def exist_checker(cmdline, want):
    try:
        p = subprocess.Popen(cmdline, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()
        if want in out.decode() or want in err.decode():
            return True
    except subprocess.CalledProcessError as e:
        # Some processes return an erroneous exit code even when they are working.
        try:
            if want in e.stdout.decode() or want in e.stderr.decode():
                return True
        except AttributeError:
            return False

    return False

# return True if the archiver needed to unpack d is already in the tools path.
def archiver_in_tools_path(d, field="install"):
    if field in d and "exist_check" in d[field] and len(d[field]["exist_check"]) > 1:
        cmdline = d[field]["exist_check"][0]
        want = d[field]["exist_check"][1]

        bin = cmdline.split()[0]
        if os.path.isfile(os.path.join(tools_path, bin)):
            if "$tools" not in cmdline:
                cmdline = tools_path + cmdline
            return exist_checker(cmdline, want)
        
    return False

# return True if the archiver needed to unpack d is already in the system path.
def archiver_in_path(d, field="install"):
    if field in d and "exist_check" in d[field] and len(d[field]["exist_check"]) > 1:
        cmdline = d[field]["exist_check"][0]
        want = d[field]["exist_check"][1]
        return exist_checker(cmdline, want)

    return False


def install_from_source(definitions, field="install"):
    for d in definitions:
        in_path = False
        if archiver_in_path(d, field=field):
            d["unpack"]["exe"] = d["unpack"]["exe"].replace("$tools/","")
            in_path = True

        if in_path or archiver_in_tools_path(d, field=field):
            print(f"trying to build archiver: {d['name']}: Exists, Testing: ", flush=True, end="")

            if test_archiver(d, field=field):
                print("OK")
            else:
                print("Failed")

            continue

        if field in d and "method" in d[field]:
            if "source" in d[field]["method"] and "repo" in d[field]:
                with tempfile.TemporaryDirectory() as tmpdir:
                    print(f"trying to build archiver: {d['name']}: ", flush=True, end="")
                    try:
                        cloneres = subprocess.check_output(['git','clone',d[field]["repo"], tmpdir], stderr=subprocess.PIPE)
                    except Exception as e:
                        print(f'error cloning repo {d[field]["repo"]} to {tmpdir}: {e}')
                        continue

                    print("Cloned, ", flush=True, end="")

                    # Create build script
                    tp = os.path.join(os.getcwd(), tools_path)
                    cmdline = d[field]["build"]
                    cmdline = cmdline.replace("$tools", tp)
                    try:
                        buildres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE, cwd=tmpdir)
                    except Exception as e:
                        print(f'error building archiver {d["name"]}: {e}')
                        continue

                    print("Built, ", end="")
            
                extracttool(d)
                if test_archiver(d, field=field):
                    print("OK")
                else:
                    print("Failed")