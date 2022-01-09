import tempfile
from gzip import decompress
from base64 import b64decode
import os, os.path
import subprocess
from .config import tools_path, should_skip_test
from .template import prepare_cmdline, prepare_exe

# used for:
#  - archivers that extract entire blocks to disk e.g. CPM archivers.
#  - archivers that refuse to compress small files
def pad(data, padbyte, padlen):
    pb = chr(int(padbyte, 16))
    pbl = padlen - divmod(len(data), padlen)[1]
    return data + (pb * pbl)

# test the archiver give the test parameters in the definition for that archiver
def test_archiver(d, field="install"):
    if "test" not in d or len([True for x in ["blob", "file", "content"] if x in d["test"]]) != 3:
        # a test is not properly defined.
        return -1
    
    # It's sometimes desirable to be able to force skip a test if a config has multiple tests.
    if should_skip_test(d, field=field):
        print("Skipping Test ", end="")
        # its ok to skip, so return 1
        return 1
    
    # what extension should our test archive have?
    extension = d["extensions"][0]              # default.
    if "extension" in d["unpack"]:
        extension = d["unpack"]["extension"]    # preferred one.
    
    if not extension.startswith("."):
        extension = "." + extension

    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as arcfile:
        try:
            try:
                arcfile.write(decompress(b64decode(d["test"]["blob"])))
                arcfile.flush()
            except Exception as e:
                print(f"error writing test data: {e}\nfilename: {arcfile.name}")
                return 0
                
            with tempfile.TemporaryDirectory() as tmpdir:
                tools = os.path.join(os.getcwd(), tools_path)
                basename = os.path.splitext(os.path.basename(arcfile.name))[0]
                exe = prepare_exe(d["unpack"]["exe"], tools)
                cmdline = prepare_cmdline(exe, d["unpack"]["cmdline"], tools, destdir=tmpdir, archive=arcfile.name, ext=extension)

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

                resultdata = ""
                try:
                    resultdata = open(extracted_file).read()
                except Exception as e:
                    print(f"error opening unarchived test data: {e}")
                    #print(subprocess.check_output(f"ls -la {tmpdir}",shell=True).decode())

                # did we get want we want?
                want = d["test"]["content"]
                if "padbyte" in d["test"] and "padlen" in d["test"]:
                    # some formats come padded (CP/M)
                    want = pad(want, d["test"]["padbyte"],d["test"]["padlen"])

                if resultdata == want:
                    return 1
                else:
                    print(f"archiver test file content mismatch:\ngot: {resultdata.encode()}\nwant: {want.encode()}")
                    return 0
        finally:
            if "delete" in d["test"] and d["test"]["delete"]:
                os.unlink(arcfile.name)