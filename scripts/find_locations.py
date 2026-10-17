"""Look up Threads location IDs for upcoming posts and store them in the queue.

For every post that has a "place" (search text, e.g. "Hồ Tuyền Lâm") but no "location_id" yet,
calls Threads GET /location_search, takes the best match in Vietnam and saves its id and name as
"location_id" / "location_name". publish.py tags that location on Threads and also tries it on
Instagram (falling back to no location if Instagram rejects it). Results go to logs/locations.txt.

Env: THREADS_ACCESS_TOKEN.
"""
import json
import os
import pathlib

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = "https://graph.threads.net/v1.0/location_search"
TOKEN = os.environ["THREADS_ACCESS_TOKEN"]

log = []
# Diagnostics: which account and which permissions the token carries (the token itself is never printed).
me = requests.get("https://graph.threads.net/v1.0/me", params={"fields": "id,username", "access_token": TOKEN}, timeout=60)
log.append(f"token me: {me.status_code} {me.text[:200]}")
dbg = requests.get("https://graph.threads.net/v1.0/debug_token", params={"input_token": TOKEN, "access_token": TOKEN}, timeout=60)
log.append(f"token debug: {dbg.status_code} {dbg.text.replace(TOKEN, chr(42) * 3)[:600]}")
for qfile in sorted((ROOT / "queue").glob("*.json")):
    posts = json.loads(qfile.read_text(encoding="utf-8"))
    changed = False
    for post in posts:
        if not post.get("place") or post.get("location_id") or post.get("status") in ("posted", "retired"):
            continue
        r = requests.get(API, params={"q": post["place"], "fields": "id,name,city,country",
                                      "access_token": TOKEN}, timeout=60)
        if not r.ok:
            log.append(f"{post['date']} {post['place']}: ERROR {r.status_code} {r.text[:300]}")
            continue
        found = r.json().get("data", [])
        vn = [x for x in found if (x.get("country") or "").lower() in ("vietnam", "viet nam", "vn")] or found
        log.append(f"{post['date']} {post['place']}: " + "; ".join(
            f"{x.get('id')} {x.get('name')} ({x.get('city')}, {x.get('country')})" for x in found[:5]) or "no results")
        if vn:
            post["location_id"], post["location_name"] = vn[0]["id"], vn[0].get("name", "")
            changed = True
    if changed:
        qfile.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(ROOT / "logs").mkdir(exist_ok=True)
(ROOT / "logs" / "locations.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
print("\n".join(log))
