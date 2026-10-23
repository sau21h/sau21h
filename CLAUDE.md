# CLAUDE.md: sau21h

Read README.md first. It is the source of truth for positioning, the weekly content rhythm, tools, budget and one-time setup. This file adds how to work in the repo and where things stand.

## Owner and context
- Personal side project of Trung (not DMX work). Instagram AI-art page @sau21h ("nhớ ai sau 9h đêm"), Vietnamese audience, posts daily at 21:00 Vietnam time.
- Communicate with Trung in Vietnamese or English. No em dashes or en dashes in any writing. Vietnamese captions must read as natural Vietnamese.
- Ask before changing approved posts, workflows or scripts; never overwrite files Trung has edited without asking.

## Repo layout
- `queue/<date>_batchN.json`: list of posts. Each post has `date`, `pillar`, `format`, `status`, `hook`, caption fields and `slides[]` (each slide: `style` = `cinematic` or `anime`, `prompt`, optional `subtitle` / `subtitle_y`).
- `style/styles.json`: the two house styles appended to every prompt. `style/fonts/NotoSerif-Italic.ttf` is the subtitle font.
- `scripts/generate.py`: renders every `draft` post with Gemini (default `gemini-nano-banana-2.1`, 2K, 9:16). Writes `posts/<date>/<n>_916.jpg` (wallpaper) and `<n>.jpg` (9:16 centred on a black 4:5 1080x1350 canvas for the IG feed). Subtitles are drawn by the script, never by the model (`<n>_raw.jpg` keeps the clean image). Moves posts `draft` -> `review`. To re-roll a slide, delete both its files and run again.
- `scripts/publish.py`: publishes today's `approved` post to Instagram (graph.instagram.com), then Threads (graph.threads.net, full 9:16 images, best-effort), using the public raw GitHub URLs. Records `media_id` and `threads_id`.
- `.github/workflows/`: `generate.yml` (Generate images), `publish.yml` (cron 20:30 VN, job waits until 21:00; backup run 21:30; can also publish immediately by committing `publish-now.txt` containing the post date), `ig-check.yml` (connection and quota check, writes `logs/ig_check.txt`).
- `logs/`: `publish_log.txt`, `spend.csv` and `spend_summary.txt` (Gemini cost tracking), `credit.json` (prepay top-ups; add a line on each top-up).
- Review happens in the Content Hub (see below); the old `review.html` contact sheet was removed 17/10/2026.
- `posts/profile/`: avatar candidates (not for posting).

## Status flow
`draft` -> `review` -> `approved` -> `posted`. Nothing is published unless it is `approved`. Trung reviews; Claude re-rolls rejects.

## Secrets (never print, never commit)
- GitHub Actions secrets: `GEMINI_API_KEY`, `IG_USER_ID`, `IG_ACCESS_TOKEN`, and `THREADS_ACCESS_TOKEN` (optional `THREADS_USER_ID`; publish.py posts to Threads after Instagram, best-effort).
- No API key files in this folder (the old `API Key.txt` was deleted 17/10/2026; Actions use GitHub secrets). `.gitignore` still blocks `*key*.txt` and `*.env`.
- The Instagram token lasts 60 days: remind Trung to renew it in the Meta app and update the secret.

## Git
- Remote: github.com/sau21h/sau21h (public repo; images must be public for the IG API).
- Rebase before pushing; Actions also commit (generated images, status updates), so pull first to avoid races.

## Status as of 13/10/2026
- Style switch: the page moves completely to soft painterly realism (learned from Threads @odwyer_sio9); style key `painterly` in `style/styles.json`. Moon and people only sometimes; mix day/night, indoor/outdoor; rotate palettes; no clear faces.
- All batch 1 `approved` posts set to `retired` (publish.py skips them), so nothing posts until the new batch is approved.
- Generate 3 posts per round, concept table first.
- Round 1 (`queue/2026-10-14_batch2.json`) approved: 13/10 Hà Nội thu, 14/10 Sài Gòn mưa, 15/10 Hà Giang tam giác mạch. Retired batch 1 posts were renamed `retired-<date>` (queue and posts folders) so their dates are free. Next round needed for 16/10 onwards.
- Approved plan 16-25/10 (render 3 per round): 16 Tuyền Lâm dã quỳ, 17 sông Hoài Hội An night, 18 Hồ Tây café (indoor), 19 Trà Sư mùa nước nổi, 20 chợ hoa Hồ Thị Kỷ (20/10), 21 hoa đăng cầu Trường Tiền night, 22 Tà Xùa săn mây (sống lưng khủng long, cây cô đơn, trà Shan tuyết bên cửa sổ = indoor; replaced Tả Van; `queue/2026-10-22_taxua.json`), 23 Nguyễn Huệ balcony + moon, 24 Tràng An morning, 25 cỏ lau bãi giữa Long Biên sunset. Round 1 of it = `queue/2026-10-16_batch3.json`.
- 13/10 Hà Nội was reposted with new slides 1 and 3 (old post ids kept as `old_media_id`/`old_threads_id`; Trung deletes the old one in the app). 14-18/10 approved. Next round to render: 19-21/10 (Trà Sư, Hồ Thị Kỷ 20/10, hoa đăng Trường Tiền).
- Image edits: local renders/edits go in a temporary `posts/tests/` (delete after use; folders of posted dates are removed during cleanups) (Gemini image-edit with the existing image as input); feed 4:5 images can be rebuilt locally with PowerShell System.Drawing (no local Python).
- Mix rules: day/night ~50/50, indoor ~20%, neighbourhood-level locations, all people Vietnamese, captions lowercase but proper place names capitalised.
- Trung topped up again on 13/10 (amount not yet logged in `logs/credit.json`).

## Status as of 12/10/2026 (evening)
- Posted: 11/10 "mai lại thứ hai rồi" (2-image carousel; Threads copy shared manually from the app) and 12/10 metro (Instagram + Threads via API).
- Batch 1 rescheduled to fill gaps: 13/10 chung cư, 14/10 Đà Lạt mưa, 15/10 dã quỳ, 16/10 Ghibli, 17/10 tối thứ 7, 18/10 Thủ Thiêm, 19/10 mẹ, 20/10 tự mua hoa, 21/10 Sài Gòn mưa, 22/10 nhớ ai sau 9h đêm. All approved, every post has 2+ slides, captions are one line + #sau21h.
- Known defect: 20/10 slide 2 has a visible horizontal seam (re-roll costs about 1,300 VND if Trung wants it).
- Avatar: posts/profile/avatar_A.jpg and avatar_B.jpg (square crops); Trung has not picked yet.
- Bio: not settled. Trung rejected taglines, puns, gimmick formats (lock screen, ticket, alarm). Last proposal followed the codex formula (two short parallel halves, one contrast, honest about AI): "Ảnh giả, nhớ thật." / "Pixel lạ, phố quen." Awaiting feedback.
- Instagram cannot add music via API; Trung adds music in the app after posting.
- Meta tokens (Instagram and Threads) expire around 10/12/2026: remind Trung before then.

## Earlier status
- Batch `queue/2026-10-14_batch1.json`: 11/10 posted; 14/10 to 25/10 approved and rendered (Sài Gòn, Đà Lạt, Hà Nội, Hoài niệm, 20/10, Trend pillars); avatar v2 (2 variants) in `review`, not for posting.
- Gemini spend: 103 images, about 136,578 VND; topped up 150,000 VND on 11/10, so the estimated balance is only about 13,000 VND. Top up before generating the next batch.
- Latest change: simpler one-line captions with only #sau21h underneath.

## Next steps
1. Before the next batch: Gemini balance is about 13,000 VND, Trung must top up (log it in `logs/credit.json`).
2. Batch 2 (posts from 23/10): concept table first, following the content rules in README.md; date hooks Halloween 31/10, 20/11, Tết 2027 (6/2/2027).
3. Settle bio and avatar.
4. After every render, report to Trung: spent this run, total spent, estimated balance (`logs/spend_summary.txt`).
5. Later: wallpaper packs; comment-to-DM only once there is something to deliver.

## Content Hub (since 16/10/2026, replaces the weekly review page for approval)
- Trung approves sau21h in the shared Content Hub (https://claude.ai/artifact/XHT1REZpF9bzpWuaiTqHEw, source `1. Business/0. Content Hub`). The Hub build (`0. Content Hub/build.js`) reads `queue/*.json` and `posts/<date>/` directly (post id S21-YYYYMMDD; review = Chờ duyệt, draft without images = Chưa có ảnh); see the Hub memory for the sync rules. Decisions made in the Hub must be written to the queue and pushed, or publish.py will not see them.

## Weekly review page (15/10/2026, superseded by the Content Hub)
- Weekly review happens only in the Content Hub (the separate sau21h preview artifact was deleted 17/10/2026).
- `scripts/week-preview/notes.json` (known issues per date) is read by the Hub build; nothing else in that folder is used.

## Weekend noon posts (since 17/10/2026)
- Saturday and Sunday have 2 posts: 11:30 and 21:00. Noon posts use the queue date key "<date>-1130" and folder posts/<date>-1130; publish.yml runs at 11:00 (waits to 11:30) with a 12:00 backup and sets POST_SLOT=1130. Content Hub id: S21-YYYYMMDD1130.
- Every new post must be pushed to the queue and shown in the Content Hub (rebuild + republish) before asking Trung to approve.

## Watermark (since 17/10/2026)
- Every post image gets a small "21h" stamp (rounded square outline, Quicksand Bold, style/fonts/Quicksand-wght.ttf) in the exact centre, ~4.5% of the width. Opacity follows the background under it: dark ~6% white and no outline, bright ~19% white with a faint dark outline (lowered 17/10 evening), linear in between (Trung approved).
- `scripts/stamp.py` runs in the Generate images workflow after generate.py: keeps the unstamped original as <n>_clean.jpg (for wallpaper packs), stamps <n>_916.jpg, rebuilds the 4:5 <n>.jpg, and records hashes in posts/<key>/stamped.json so it never stamps twice. Profile images are never stamped. To re-roll a slide, delete <n>.jpg, <n>_916.jpg and <n>_clean.jpg.

## Project stopped (Trung, 23/10/2026)
- Trung decided to stop sau21h after the last scheduled posts: 23/10, 24/10, 25/10 and 26/10 (all approved). The 27/10 cat post (never approved) was set to `retired`.
- publish.yml stops itself for scheduled runs after 26/10 and insights.yml after 27/10 (date guard step "Project end check"); manual runs still work. No new content, no renders. To restart, remove the guard steps and plan a new batch.
- Repo, images (incl. <n>_clean.jpg originals for possible wallpaper packs) and tokens stay as they are; the Meta tokens expire around 10/12/2026.
