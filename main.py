import argparse

from testresults import parse_xunit, render_results

parser = argparse.ArgumentParser()
parser.add_argument("--xunit", action="append")
parser.add_argument("--html")
args = parser.parse_args()

xunit_results = []

for fn in (args.xunit or []):
    xunit_results.append(parse_xunit(open(fn)))

if args.html:
    with open(args.html, "w") as f:
        f.write(render_results(xunit_results))
