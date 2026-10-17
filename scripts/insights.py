"""Collect Instagram and Threads stats for posted posts and the follower counts into logs/insights.json.

Read-only (never publishes). Run by .github/workflows/insights.yml; the Content Hub dashboard reads the file.
Env: IG_USER_ID, IG_ACCESS_TOKEN, THREADS_ACCESS_TOKEN (optional), THREADS_USER_ID (optional, default "me"),
     GRAPH_VERSION (default v24.0).
Output: {"updated": "YYYY-MM-DD HH:MM", "posts": {queue date key: {"ig": {...}, "threads": {...}}},
         "followers": [{"date": "YYYY-MM-DD", "ig": n, "threads": n}]}   (one row per day, last value wins)
"""
import datetime
import json
import os
import pathlib
import zoneinfo

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "logs" / "insights.json"
IG_API = f"https://graph.instagram.com/{os.environ.get('GRAPH_VERSION', 'v24.0')}"
TH_API = "https://graph.threads.net/v1.0"
IG_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
TH_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "")


def get(base, token, path, **params):
    r = requests.get(f"{base}/{path}", params={**params, "access_token": token}, timeout=60)
    r.raise_for_status()
    return r.json()


def metrics(data):
    out = {}
    for x in data:
        v = x.get("values", [{}])[0].get("value") if x.get("values") else x.get("total_value", {}).get("value")
        out[x["name"]] = v or 0
    return out


def ig_post(media_id):
    for m in ("views,reach,likes,comments,shares,saved", "reach,likes,comments,shares,saved"):
        try:
            return metrics(get(IG_API, IG_TOKEN, f"{media_id}/insights", metric=m)["data"])
        except requests.RequestException:
            continue
    return None


def th_post(thread_id):
    for m in ("views,likes,replies,reposts,quotes,shares", "views,likes,replies,reposts,quotes"):
        try:
            return metrics(get(TH_API, TH_TOKEN, f"{thread_id}/insights", metric=m)["data"])
        except requests.RequestException:
            continue
    return None


def main():
    now = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh"))
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    posts = old.get("posts", {})
    for qfile in sorted((ROOT / "queue").glob("*.json")):
        for p in json.loads(qfile.read_text(encoding="utf-8")):
            if p.get("status") != "posted":
                continue
            entry = posts.get(p["date"], {})
            if IG_TOKEN and p.get("media_id"):
                entry["ig"] = ig_post(p["media_id"]) or entry.get("ig")
            if TH_TOKEN and p.get("threads_id"):
                entry["threads"] = th_post(p["threads_id"]) or entry.get("threads")
            posts[p["date"]] = entry

    row = {"date": now.date().isoformat(), "ig": None, "threads": None}
    try:
        row["ig"] = get(IG_API, IG_TOKEN, os.environ["IG_USER_ID"], fields="followers_count")["followers_count"]
    except Exception as e:
        print("ig followers failed:", type(e).__name__)
    if TH_TOKEN:
        try:
            d = get(TH_API, TH_TOKEN, f"{os.environ.get('THREADS_USER_ID') or 'me'}/threads_insights",
                    metric="followers_count")["data"][0]
            row["threads"] = (d.get("total_value") or {}).get("value", d.get("values", [{}])[0].get("value"))
        except Exception as e:
            print("threads followers failed:", type(e).__name__)
    followers = [f for f in old.get("followers", []) if f["date"] != row["date"]] + [row]

    OUT.write_text(json.dumps({"updated": now.strftime("%Y-%m-%d %H:%M"), "posts": posts, "followers": followers},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(posts)} posts, followers {row}")


if __name__ == "__main__":
    main()
