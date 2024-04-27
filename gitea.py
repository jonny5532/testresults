import json
import urllib.request

def report_commit_status(commit_status_url, summary, state, target_url):
    req = urllib.request.Request(commit_status_url)
    req.add_header('Content-Type', 'application/json')
    data = json.dumps({
        "context": "TestAction",
        "description": summary,
        "state": state,
        "target_url": target_url,
    }).encode('utf-8')
    req.add_header('Content-Length', len(data))
    response = urllib.request.urlopen(req, data)
    print(response.read())
