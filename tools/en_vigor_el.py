"""Prints the law of Bolivia as it stood on a given day, read from this repository's history.

    python tools/en_vigor_el.py 2016-02-20 constitucion art-168     # art. 168 the day before the 2016 referendum
    python tools/en_vigor_el.py 2026-10-28 constitucion 168         # the same article, by number, today
    python tools/en_vigor_el.py 2010-01-01 constitucion           # the whole Constitution on 1 January 2010
    python tools/en_vigor_el.py --law 2020-01-01 constitucion 168  # also name the law behind that wording

A thin wrapper around tools/on.py: the version is chosen by each commit's `In-force:` trailer, never by its commit
date, and branches named wip* are ignored. Standard library only.
"""
import runpy
import sys
from pathlib import Path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.argv[0] = str(Path(__file__).with_name('on.py'))
    runpy.run_path(sys.argv[0], run_name='__main__')
