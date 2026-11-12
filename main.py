#!/usr/bin/env python3
"""make.fun 'coolest art' entry: copies the bundled entry.png to the output dir.

The artwork is a giant celestial koi -- vermillion, white and gold -- swimming
through swirling clouds above a lantern-lit village under a crescent moon,
with a soft golden sparkle trail streaming from its tail fin.
Pure standard library. The art itself is generated procedurally by generate.py.
"""
import os
import shutil

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(here, "entry.png"), os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
