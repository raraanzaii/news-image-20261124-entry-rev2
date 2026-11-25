#!/usr/bin/env python3
"""Entry program for make.fun competition news-image-20261124, revision 2.

The picture of the day - Tuesday 24 November 2026, told in 62 verified
stories, each printed with its source - is drawn ahead of time by
render.py and committed in this repository as entry.png. This program
only delivers those bytes: it finds entry.png beside itself (the grader
mounts the repository at /bot) and writes it to the output directory,
which is the MAKEFUN_OUTPUT_DIR environment variable when set, else
/output. It runs offline, uses nothing outside the standard library,
and copies byte for byte, so the two graded runs always agree.
"""

import os

NAME = "entry.png"


def find_image():
    here = os.path.dirname(os.path.abspath(__file__))
    for base in dict.fromkeys((here, "/bot", os.getcwd())):
        path = os.path.join(base, NAME)
        if os.path.isfile(path):
            return path
    raise SystemExit("entry.png not found beside main.py")


def deliver():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    with open(find_image(), "rb") as fh:
        data = fh.read()
    target = os.path.join(out_dir, NAME)
    staging = target + ".part"
    with open(staging, "wb") as fh:
        fh.write(data)
    os.replace(staging, target)
    return target, len(data)


def main():
    target, size = deliver()
    print("wrote %s (%d bytes)" % (target, size))


if __name__ == "__main__":
    main()
