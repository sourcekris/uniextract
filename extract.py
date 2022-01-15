#!/usr/bin/env python

# extract a file to a folder - irrespective of the underlying format.

import argparse
import sys

def main(argv):
    ap = argparse.ArgumentParser(description=f"Extract Files.", 
                                 epilog="Please file bugs on the GitHub Issues. Thanks")
    ap.add_argument("-e", "--extract", required=True, help=f"The {ext} file to extract.", metavar="FILENAME")
    ap.add_argument("-d", "--destination", help="An optional output folder.", metavar="PATH")
    args = ap.parse_args(argv)


if __name__ == "__main__":
    main(sys.argv[1:])