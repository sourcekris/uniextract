from glob import glob
from jsonschema import validate
import os.path
import json
import re

from .schema import schema

# config
definitions_path = "defs/"
tools_path = "tools/"
toolsdist_path = "toolsdist/"
default_fn = "0"

trid_defs = "/usr/share/trid/triddefs.trd"
trid_args = ['/usr/local/bin/trid', '-n:1', f'-d:{trid_defs}']
trid_env = {"LC_ALL":"C"}

pcntre = re.compile("\d+\.\d\%\s")
numre = re.compile("\s\(\d+\/\d+\)")

class Installer:
    def __init__(self, d: dict) -> None:
        self.method = d["method"]
        self.test_install = d["test_install"] if "test_install" in d else True
        self.container = d["container"] if "container" in d else ""
        self.tool = d["tool"] if "tool" in d else ""
        self.dependencies = d["dependencies"] if "dependencies" in d else None
        self.renametool = d["renametool"] if "renametool" in d else None
        self.exist_check = []

        if self.is_apt() or self.is_pip():
            self.packages = d["packages"]
        
        if self.is_source():
            self.repo = d["repo"]
            self.build = d["build"]
            self.exist_check = d["exist_check"]

    def is_apt(self) -> bool:
        if self.method == "apt":
            return True
        return False
    
    def is_pip(self) -> bool:
        if self.method == "pip":
            return True
        return False
    
    def is_source(self) -> bool:
        if self.method == "source":
            return True
        return False
    
    def should_rename_tool(self) -> bool:
        if self.renametool and self.renametool != self.tool:
            return True
        return False
    
    def should_skip_test(self) -> bool:
        return not self.test_install

class Unpacker:
    def __init__(self, d: dict) -> None:
        self.exe = d["exe"]
        self.cmdline = d["cmdline"]
        self.extension = d["extension"]
        self.force_extension = d["force_extension"]

class Packer:
    def __init__(self, d: dict) -> None:
        self.type = d["type"]
        self.blob = d["blob"] if self.type == "blob" else None
        if self.type != "blob":
            self.exe = d["exe"]
            self.cmdline = d["cmdline"]

class Identity:
    def __init__(self, d: dict) -> None:
        self.trid = d["trid"]
        self.file = d["file"]
        self.idarc = d["idarc"]
    
    def identities(self) -> list:
        return [self.trid, self.file, self.idarc]

class ArcTest:
    def __init__(self, d: dict) -> None:
        self.blob = d["blob"]
        self.file = d["file"]
        self.content = d["content"]
        self.delete = d["delete"]
        self.padbyte = None
        self.padlen = None

        if "padlen" in d:
            self.padbyte = d["padbyte"]
            self.padlen = d["padlen"]

class Definition:
    def __init__(self, d: dict) -> None:
        validate(schema=schema, instance=d)
        self.name = d["name"]
        self.extensions = d["extensions"]
        self.installer = Installer(d["install"])
        self.unpack_installer = Installer(d["unpackinstall"]) if "unpackinstall" in d else None
        self.pack_installer = Installer(d["packinstall"]) if "packinstall" in d else None
        self.packer = Packer(d["pack"])
        self.unpacker = Unpacker(d["unpack"])
        self.identity = Identity(d["identification"])
        self.test = ArcTest(d["test"])
    
    def addfn(self, fname: str) -> None:
        self.definition_filename = fname
    
    def is_blob(self) -> bool:
        if self.packer.type == "blob":
            return True
        return False
    
    def get_pack_ext(self) -> str:
        if self.unpacker.extension:
            return '.' + self.unpacker.extension
        if len(self.extensions) > 0:
            return '.' + self.extensions[0]
        return None
    
    def get_content(self) -> str:
        if self.test.padbyte:
            pb = chr(int(self.test.padbyte, 16))
            pbl = self.test.padlen - divmod(len(self.test.content), self.test.padlen)[1]
            return self.test.content + (pb * pbl)
        return self.test.content
    
    def get_installer(self, field: str) -> Installer:      
        if field == "packinstall":
            return self.pack_installer
        
        if field == "unpackinstall":
            return self.unpack_installer
        
        return self.installer
            

def load_defs(addfn:bool = False, defpath: str = None) -> list[Definition]:
    if not defpath:
        defpath = definitions_path
    defnames = glob(os.path.join(defpath, "*.json"))
    definitions = []
    for d in defnames:
        try:
            jd = json.loads(open(d).read())
            validate(schema=schema, instance=jd)
        except Exception as e:
            print(f'error loading archiver definition {d}: {e}, continuing...')
            continue
        do = Definition(jd)
        if addfn:
            do.addfn(d)
        definitions.append(do)
    return definitions

def get_def(defname: str, addfn: bool = False, defpath: str = definitions_path) -> Definition:
    defs = load_defs(addfn=addfn, defpath=defpath)
    for d in defs:
        if d.name == defname:
            return d
    
    return None

def get_def_by_id(id: str, defpath: str = definitions_path) -> Definition:
    id = pcntre.sub("", numre.sub("", id))
    defs = load_defs(defpath=defpath)
    for d in defs:
        if id in d.identity.identities():
            return d
        
        if id.startswith('.') and id[1:] == d.unpacker.extension:
            return d
    
    return None