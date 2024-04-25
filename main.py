import argparse
import os

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

passes = sum(r["passes"] for r in xunit_results)
failures = sum(r["failures"] for r in xunit_results)
skipped = sum(r["skipped"] for r in xunit_results)
summary = "%d tests passed, %d failed%s." % (
    passes,
    failures,
    ", %d skipped" % skipped if skipped else "",
)

with open(os.getenv("GITHUB_OUTPUT", "/tmp/github_output.txt"), "a") as f:
    f.write("passes=%d\nfailures=%d\nskipped=%d\nsummary=%s\n" % (
        passes, failures, skipped, summary,
    ))
