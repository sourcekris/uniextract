#!/usr/bin/env python

import sys
from pyuniextract.installers.apt import install_apt_packages
from pyuniextract.installers.pip import install_pip_packages
from pyuniextract.installers.source import install_from_source
from pyuniextract.installers.config import load_defs

def main(args):
    defs = load_defs()

    if len(args) > 1:
        if args[1] in ["apt", "pip", "source"]:
            if "apt" in args[1]:
                if len(args) == 3:
                    for d in defs:
                        if d["name"] == args[2]:
                            install_apt_packages([d])
                else:
                    install_apt_packages(defs)
                return

            if "pip" in args[1]:
                install_pip_packages(defs)
                return

            if "source" in args[1]:
                install_from_source(defs)
                return

    install_apt_packages(defs)
    install_pip_packages(defs)
    install_from_source(defs)

if __name__ == "__main__":
    main(sys.argv)
