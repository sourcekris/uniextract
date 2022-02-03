import subprocess
import tempfile
import os, os.path
from .testarchiver import test_archiver
from .extracttool import extracttool
from .config import Definition, Installer, tools_path

def exist_checker(cmdline: str, want: str) -> bool:
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
def archiver_in_tools_path(i: Installer) -> bool:
    if len(i.exist_check) > 1:
        cmdline = i.exist_check[0]
        want = i.exist_check[1]

        bin = cmdline.split()[0]
        if os.path.isfile(os.path.join(tools_path, bin)):
            if "$tools" not in cmdline:
                cmdline = tools_path + cmdline
            return exist_checker(cmdline, want)
        
    return False

# return True if the archiver needed to unpack d is already in the system path.
def archiver_in_path(i: Installer) -> bool:
    if len(i.exist_check) > 1:
        cmdline = i.exist_check[0]
        want = i.exist_check[1]
        return exist_checker(cmdline, want)

    return False

def install_from_source(definitions: list[Definition], field: str = "install"):
    for d in definitions:
        i = d.get_installer(field)
        in_path = False
        if archiver_in_path(i):
            d.unpacker.exe = d.unpacker.exe.replace("$tools/","")
            in_path = True

        if in_path or archiver_in_tools_path(i):
            print(f"trying to build archiver: {d.name}: Exists, Testing: ", flush=True, end="")

            if test_archiver(d, field=field):
                print("OK")
            else:
                print("Failed")

            continue
        
        if i.method == "source":
            with tempfile.TemporaryDirectory() as tmpdir:
                print(f"trying to build archiver: {d.name}: ", flush=True, end="")
                try:
                    cloneres = subprocess.check_output(['git','clone',i.repo, tmpdir], stderr=subprocess.PIPE)
                except Exception as e:
                    print(f'error cloning repo {i.repo} to {tmpdir}: {e}')
                    continue

                print("Cloned, ", flush=True, end="")

                # Create build script
                tp = os.path.join(os.getcwd(), tools_path)
                cmdline = i.build
                cmdline = cmdline.replace("$tools", tp)
                try:
                    buildres = subprocess.check_output(cmdline, shell=True, stderr=subprocess.PIPE, cwd=tmpdir)
                except Exception as e:
                    print(f'error building archiver {d.name}: {e}')
                    continue

                print("Built, ", end="")
        
            extracttool(d)
            if test_archiver(d, field=field):
                print("OK")
            else:
                print("Failed")