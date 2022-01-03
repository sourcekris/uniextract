#!/usr/bin/env python

import argparse
import sys
import os.path
import json
import re
from pyuniextract.installers.config import load_defs
from typing import Union

def_store = "defs/"

class CompactJSONEncoder(json.JSONEncoder):
    """A JSON Encoder that puts small containers on single lines."""

    CONTAINER_TYPES = (list, tuple, dict)
    """Container datatypes include primitives or other containers."""

    MAX_WIDTH = 200
    """Maximum width of a container that might be put on a single line."""

    MAX_ITEMS = 2
    """Maximum number of items in container that might be put on single line."""

    INDENTATION_CHAR = " "

    def __init__(self, *args, **kwargs):
        # using this class without indentation is pointless
        if kwargs.get("indent") is None:
            kwargs.update({"indent": 4})
        super().__init__(*args, **kwargs)
        self.indentation_level = 0

    def encode(self, o):
        """Encode JSON object *o* with respect to single line lists."""
        if isinstance(o, (list, tuple)):
            if self._put_on_single_line(o):
                return "[" + ", ".join(self.encode(el) for el in o) + "]"
            else:
                self.indentation_level += 1
                output = [self.indent_str + self.encode(el) for el in o]
                self.indentation_level -= 1
                return "[\n" + ",\n".join(output) + "\n" + self.indent_str + "]"
        elif isinstance(o, dict):
            if o:
                if self._put_on_single_line(o):
                    return "{ " + ", ".join(f"{self.encode(k)}: {self.encode(el)}" for k, el in o.items()) + " }"
                else:
                    self.indentation_level += 1
                    output = [self.indent_str + f"{json.dumps(k)}: {self.encode(v)}" for k, v in o.items()]
                    self.indentation_level -= 1
                    return "{\n" + ",\n".join(output) + "\n" + self.indent_str + "}"
            else:
                return "{}"
        elif isinstance(o, float):  # Use scientific notation for floats, where appropiate
            return format(o, "g")
        elif isinstance(o, str):  # escape newlines
            o = o.replace("\\", "\\\\")
            o = o.replace("\"", "\\\"")
            o = o.replace("\n", "\\n")
            return f'"{o}"'
        else:
            return json.dumps(o)

    def iterencode(self, o, **kwargs):
        """Required to also work with `json.dump`."""
        return self.encode(o)

    def _put_on_single_line(self, o):
        return self._primitives_only(o) and len(o) <= self.MAX_ITEMS and len(str(o)) - 2 <= self.MAX_WIDTH

    def _primitives_only(self, o: Union[list, tuple, dict]):
        if isinstance(o, (list, tuple)):
            return not any(isinstance(el, self.CONTAINER_TYPES) for el in o)
        elif isinstance(o, dict):
            return not any(isinstance(el, self.CONTAINER_TYPES) for el in o.values())

    @property
    def indent_str(self) -> str:
        return self.INDENTATION_CHAR*(self.indentation_level*self.indent)

def dumppretty(s):
    return json.dumps(s, cls=CompactJSONEncoder)

def main(argv):
    ap = argparse.ArgumentParser(description="Make test blobs for the archiver pre-requisites")
    ap.add_argument('-s',"--test", help="Run a specific test only.")
    ap.add_argument('-t',"--type", help="Run a specific type of test only.")
    ap.add_argument('-l',"--list", default="tests", choices=["tests", "types"], help="List tests or types of tests.")

    args = ap.parse_args(argv[1:])

    defs = load_defs(addfn=True)
    for d in defs:
        name = d["name"]
        fn = os.path.basename(d["definition_filename"])
        del d["definition_filename"]

        if "pack" not in d:
            # every def should have a packer but i wont complain.
            continue

        if "type" not in d["pack"]:
            # try and infer it from how it is installed
            if "install" in d and "method" in d["install"]:
                if "apt" in d["install"]["method"] and "packages" in d["install"]:
                    if "dosbox" in d["install"]["packages"]:
                        print(f"inferred test {name} from {fn} is a dosbox type")
                        d["pack"]["type"] = "dosbox"
                        open(os.path.join(def_store, fn),'w').write(dumppretty(d))
                        continue

                    if "wine" in d["install"]["packages"]:
                        print(f"inferred test {name} from {fn} is a wine type")
                        d["pack"]["type"] = "wine"
                        open(os.path.join(def_store, fn),'w').write(dumppretty(d))
                        continue

                    print(f"inferred test {name} from {fn} is a archiver type")
                    d["pack"]["type"] = "archiver"
                    open(os.path.join(def_store, fn),'w').write(dumppretty(d))
            else:
                print(f"test {name} has a broken install method.")
        # test_type = d["pack"]["type"]



if __name__ == "__main__":
    main(sys.argv)
