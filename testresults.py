import base64
import html
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


def parse_xunit(fn):
    tree = ET.parse(fn)
    root = tree.getroot()

    passes, failures, skipped = 0, 0, 0
    for ts in root.findall(".//testcase"):
        if len(ts.findall("error")) or len(ts.findall("failure")):
            failures += 1
        elif len(ts.findall("skipped")):
            skipped += 1
        else:
            passes += 1

    return {
        "passes": passes,
        "failures": failures,
        "skipped": skipped,
        "root": root,
        #"dirname": os.path.dirname(fn),
    }


def render_results(results):
    def render_time(time):
        if time < 1:
            return "&lt;1s"
        return "%ds" % time

    def render_test(test):
        errors = test.findall("error") + test.findall("failure")
        skipped = test.findall("skipped")
        success = len(errors) == 0
        ret = """<tr>
			<td width="20" align="center" style="color: {fg}; background: {bg}; border-color: {bg}; border-left-color: {bg}; font-size: 18px; padding: 4px 2px 4px 3px">{mark}</td>
			<td style="border-right: none">&nbsp; {name} &nbsp;</td>
			<td width="50" style="border-left: none; font-size: 0.9rem" align="right">&nbsp;{elapsed}&nbsp;&nbsp;</td>
		</tr>""".format(
            name=html.escape(test.attrib["name"]),
            elapsed=render_time(float(test.attrib["time"])),
            mark="\u2717" if len(errors) else "\u26A0" if len(skipped) else "\u2713",
            bg="#D54C53" if len(errors) else "#edd529" if len(skipped) else "#8BC04D",
            fg="#84771f" if len(skipped) else "#fefefe",
        )

        for error in errors:
            ret += """
			<tr>
				<td colspan="3" style="background: #D54C53; border-left-color: #D54C53; border-bottom-color: #D54C53; color: #fefefe; padding: 4px 9px 1px">
					<div style="max-height: 100px; overflow: auto;"><strong>{}:</strong> {}</div>
				</td>
			</tr>
			<tr>
				<td colspan="3" style="padding: 0; border-left-color: #222222; ">
					<div style="padding: 8px 12px; font: 12px Courier, monospace; line-height: 13px; background: #222222; color: #e1e1e1; white-space: pre-wrap; max-height: 150px; overflow-y: scroll;">{}</div>
				</td>
			</tr>""".format(
                html.escape(error.attrib.get("type", "Error")),
                html.escape(error.attrib.get("message", "").split("\n")[0]),
                html.escape(error.text),
            )

        if False:
            try:
                slug = re.sub(r"[^_\-a-zA-Z0-9]", "", test.attrib["name"].replace(" ", "_"))
                # lazy!
                for res in results:
                    screenshot = os.path.join(res["dirname"], slug + ".png")
                    if os.path.exists(screenshot):
                        ret += """
                        <tr>
                            <td colspan="3">
                                <div style="overflow: scroll; max-width: 1000px">
                                    <img src="%s">
                                </div>
                            </td>
                        </tr>""" % screenshot_to_data_uri(
                            screenshot
                        )
                        break
            except Exception as e:
                pass#print("Screenshot embedding failed:", e)

        return ret

    def render_collection(name, testcases):
        tests = []
        for test in testcases:
            tests.append(render_test(test))
        return """<h3>{}</h3>
			<table cellpadding="2" border="1" bordercolor="#e4e4e4" style="border-collapse: collapse; line-height: 20px; background: #ffffff;" width="100%">
			{}
			</table>
		""".format(
            html.escape(name), "\n".join(tests)
        )

    def render_report(results):
        passes, failures, skipped = (
            sum(r["passes"] for r in results),
            sum(r["failures"] for r in results),
            sum(r["skipped"] for r in results),
        )

        summary = "%d tests passed, %d failed%s." % (
            passes,
            failures,
            ", %d skipped" % skipped if skipped else "",
        )

        groups = {}
        for res in results:
            for test in res["root"].findall(".//testcase"):
                classname = test.attrib["classname"]
                if classname not in groups:
                    groups[classname] = []
                groups[classname].append(test)

        sorted_groups = sorted(
            groups.items(),
            key=lambda kv: (
                -sum(len(tc.findall("failure")) for tc in kv[1]),
                -sum(len(tc.findall("skipped")) for tc in kv[1]),
            ),
        )

        for kv in sorted_groups:
            kv[1].sort(key=lambda tc: (
                -len(tc.findall("failure")),
                -len(tc.findall("skipped")),
                -float(tc.attrib["time"])
            ))


        collections = []
        for k, v in sorted_groups:
            collections.append(render_collection(k, v))

        return """<!DOCTYPE html>
		<html>
        <head><meta charset="utf-8"></head>
		<body style="font: 15px 'Open Sans', Roboto, sans-serif; color: #444444; line-height: 25px; background: #efefef; padding: 30px 20px;">
		<div style="max-width: 1000px">
        <div style="color: #444444; font-size: 2rem; font-weight: 400; margin-bottom: 2rem;">{}</div>
		{}
		</div>
		</body>
		</html>
		""".format(
            summary,
            "\n".join(collections)
        )

    return render_report(results)


def screenshot_to_data_uri(fn):
    png = subprocess.check_output(
        ["pngquant", "--nofs", "--quality", "90", "--output", "-", fn]
    )
    return "data:image/png;base64," + base64.b64encode(png).replace(b"\n", b"").decode(
        "ascii"
    )


if __name__ == "__main__":
    results = [parse_xunit(sys.argv[1])]
    summary = "%d tests passed, %d failed%s." % (
        results[0]["passes"],
        results[0]["failures"],
        ", %d skipped" % results[0]["skipped"] if results[0]["skipped"] else "",
    )
    #print(summary)
    print(render_results(results))
