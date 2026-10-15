"""Publish today's approved post (Asia/Ho_Chi_Minh date) to Instagram, then Threads.

Uses the Instagram API with Instagram Login (graph.instagram.com) and the Threads API
(graph.threads.net). Images are served from this public repo's raw URLs.
Threads runs only when THREADS_ACCESS_TOKEN is set; a post already on Instagram but not
yet on Threads (no "threads_id") is sent to Threads only.

Env: IG_USER_ID, IG_ACCESS_TOKEN, GITHUB_REPOSITORY (set by Actions),
     THREADS_USER_ID, THREADS_ACCESS_TOKEN (optional),
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
    # short line, optional share prompt, then #sau21h
    caption = "\n".join(filter(None, [post["caption"], post.get("share"), post["hashtags"]]))
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


THREADS_API = "https://graph.threads.net/v1.0"


def threads_call(method, path, **params):
    r = requests.request(method, f"{THREADS_API}/{path}",
                         params={**params, "access_token": os.environ["THREADS_ACCESS_TOKEN"]}, timeout=60)
    if not r.ok:
        raise RuntimeError(f"threads {path}: {r.status_code} {r.text}")
    return r.json()


def threads_wait(container_id):
    for _ in range(30):
        status = threads_call("GET", container_id, fields="status").get("status")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"threads container {container_id}: {status}")
        time.sleep(5)
    raise RuntimeError(f"threads container {container_id} timed out")


def publish_threads(post):
    """Same images and caption on Threads, without hashtags (Threads turns them into a topic tag).
    Uses the full 9:16 wallpaper when it exists."""
    user = os.environ.get("THREADS_USER_ID") or "me"
    caption = "\n".join(filter(None, [post["caption"], post.get("share")]))
    folder = ROOT / "posts" / post["date"]

    def url(n):
        name = f"{n}_916.jpg" if (folder / f"{n}_916.jpg").exists() else f"{n}.jpg"
        return f"{RAW}/posts/{post['date']}/{name}"

    count = len(post["slides"])
    if count == 1:
        cid = threads_call("POST", f"{user}/threads", media_type="IMAGE", image_url=url(1), text=caption)["id"]
    else:
        children = [threads_call("POST", f"{user}/threads", media_type="IMAGE", image_url=url(n),
                                 is_carousel_item="true")["id"] for n in range(1, count + 1)]
        for c in children:
            threads_wait(c)
        cid = threads_call("POST", f"{user}/threads", media_type="CAROUSEL",
                           children=",".join(children), text=caption)["id"]
    threads_wait(cid)
    return threads_call("POST", f"{user}/threads_publish", creation_id=cid)["id"]


def main():
    today = os.environ.get("POST_DATE") or datetime.datetime.now(
        zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
    for qfile in sorted((ROOT / "queue").glob("*.json")):
        posts = json.loads(qfile.read_text(encoding="utf-8"))
        for post in posts:
            if post["date"] != today:
                continue
            if post["status"] not in ("approved", "posted"):
                print(f"{today}: status is '{post['status']}', not approved, skipping")
                return
            if post["status"] == "posted" and (post.get("threads_id") or not os.environ.get("THREADS_ACCESS_TOKEN")):
                print(f"{today}: already posted, skipping")
                return
            if post.get("status") == "approved":
                post["media_id"] = publish(post)
                post["status"] = "posted"
                qfile.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"{today}: posted {post['media_id']}")
            # Threads is best-effort: a failure there never undoes or blocks the Instagram post.
            if os.environ.get("THREADS_ACCESS_TOKEN") and not post.get("threads_id"):
                try:
                    post["threads_id"] = publish_threads(post)
                    qfile.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    print(f"{today}: threads {post['threads_id']}")
                except Exception as e:
                    print(f"{today}: threads FAILED {e}")
            return
    print(f"{today}: nothing queued")


if __name__ == "__main__":
    main()
