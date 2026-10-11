"""Publish today's approved post (Asia/Ho_Chi_Minh date) to Instagram.

Uses the Instagram API with Instagram Login (graph.instagram.com).
Images are served from this public repo's raw URLs.

Env: IG_USER_ID, IG_ACCESS_TOKEN, GITHUB_REPOSITORY (set by Actions),
     GRAPH_VERSION (default v24.0), POST_DATE (optional override, YYYY-MM-DD).
"""
import datetime
import json
import os
import pathlib
import sys
import time
import zoneinfo

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = f"https://graph.instagram.com/{os.environ.get('GRAPH_VERSION', 'v24.0')}"
IG_USER = os.environ["IG_USER_ID"]
TOKEN = os.environ["IG_ACCESS_TOKEN"]
RAW = f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/main"


def call(method, path, **params):
    r = requests.request(method, f"{API}/{path}", params={**params, "access_token": TOKEN}, timeout=60)
    if not r.ok:
        sys.exit(f"{path}: {r.status_code} {r.text}")
    return r.json()


def wait_ready(container_id):
    for _ in range(60):  # videos can take a few minutes to process
        status = call("GET", container_id, fields="status_code")["status_code"]
        if status == "FINISHED":
            return
        if status == "ERROR":
            sys.exit(f"container {container_id} failed processing")
        time.sleep(10)
    sys.exit(f"container {container_id} timed out")


def publish(post):
    caption = f"{post['caption']}\n{post['hashtags']}"  # short line, #sau21h right under it
    folder = f"{RAW}/posts/{post['date']}"
    # Until video generation is set up, a reel slot without reel.mp4 goes out as its keyframe image.
    if post["format"] == "reel" and (ROOT / "posts" / post["date"] / "reel.mp4").exists():
        cid = call("POST", f"{IG_USER}/media", media_type="REELS",
                   video_url=f"{folder}/reel.mp4", caption=caption)["id"]
    elif len(post["slides"]) == 1:
        cid = call("POST", f"{IG_USER}/media", image_url=f"{folder}/1.jpg", caption=caption)["id"]
    else:
        children = [
            call("POST", f"{IG_USER}/media", image_url=f"{folder}/{n}.jpg", is_carousel_item="true")["id"]
            for n in range(1, len(post["slides"]) + 1)
        ]
        for c in children:
            wait_ready(c)
        cid = call("POST", f"{IG_USER}/media", media_type="CAROUSEL",
                   children=",".join(children), caption=caption)["id"]
    wait_ready(cid)
    return call("POST", f"{IG_USER}/media_publish", creation_id=cid)["id"]


def main():
    today = os.environ.get("POST_DATE") or datetime.datetime.now(
        zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
    for qfile in sorted((ROOT / "queue").glob("*.json")):
        posts = json.loads(qfile.read_text(encoding="utf-8"))
        for post in posts:
            if post["date"] != today:
                continue
            if post["status"] != "approved":
                print(f"{today}: status is '{post['status']}', not approved — skipping")
                return
            post["media_id"] = publish(post)
            post["status"] = "posted"
            qfile.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"{today}: posted {post['media_id']}")
            return
    print(f"{today}: nothing queued")


if __name__ == "__main__":
    main()
