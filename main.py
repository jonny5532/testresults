import os
import sys

from archives import open_archive
from testresults import parse_xunit, render_results

buffer = open(sys.argv[1], "rb").read()
zf = open_archive(buffer)

output_dir = sys.argv[2]
os.makedirs(output_dir)

xunit_results = []

for fn in zf.namelist():
    if fn.endswith(".xml"):
        with zf.open(fn) as f:
            # if the file does not contain a testcase, skip it
            if not b"<testcase " in f.read():
                continue
        xunit_results.append(parse_xunit(zf.open(fn)))

if len(xunit_results):
    with open(output_dir + "/index.html", "w") as f:
        f.write(render_results(xunit_results))
