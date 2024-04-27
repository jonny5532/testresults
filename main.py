import argparse
import os
import subprocess

from gitea import report_commit_status
from testresults import parse_xunit, render_results

parser = argparse.ArgumentParser()
parser.add_argument("--xunit", action="append")
parser.add_argument("--html")
parser.add_argument("--gitea-commit-status-url")
parser.add_argument("--gitea-target-url")
parser.add_argument("--s3-endpoint")
parser.add_argument("--s3-source")
parser.add_argument("--s3-destination")
parser.add_argument("--s3-access-key")
parser.add_argument("--s3-secret-key")
args = parser.parse_args()

xunit_results = []

for fn in (args.xunit or []):
    xunit_results.append(parse_xunit(fn))

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

if args.gitea_commit_status_url:
    state = "success" if failures == 0 else "failure"
    report_commit_status(
        args.gitea_commit_status_url,
        summary,
        state,
        args.gitea_target_url,
    )

if args.s3_endpoint and args.s3_source and args.s3_destination:
    subprocess.check_call([
        "rclone", "copy",
        args.s3_source,
        ":s3:" + args.s3_destination,
        "--s3-endpoint", args.s3_endpoint,
        "--s3-env-auth",
    ], env={
        **os.environ,
        'AWS_ACCESS_KEY_ID': args.s3_access_key or "",
        'AWS_SECRET_ACCESS_KEY': args.s3_secret_key or "",
    })
