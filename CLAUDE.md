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
- `.github/workflows/`: `generate.yml` (Generate images), `publish.yml` (daily cron `0 14 * * *` = 21:00 VN; can also publish immediately by committing `publish-now.txt` containing the post date), `ig-check.yml` (connection and quota check, writes `logs/ig_check.txt`).
- `logs/`: `publish_log.txt`, `spend.csv` and `spend_summary.txt` (Gemini cost tracking), `credit.json` (prepay top-ups; add a line on each top-up).
- `review.html`: contact sheet for reviewing generated images.
- `posts/profile/`: avatar candidates (not for posting).

## Status flow
`draft` -> `review` -> `approved` -> `posted`. Nothing is published unless it is `approved`. Trung reviews; Claude re-rolls rejects.

## Secrets (never print, never commit)
- GitHub Actions secrets: `GEMINI_API_KEY`, `IG_USER_ID`, `IG_ACCESS_TOKEN`, and `THREADS_ACCESS_TOKEN` (optional `THREADS_USER_ID`; publish.py posts to Threads after Instagram, best-effort).
- `API Key.txt` in this folder is local only and covered by `.gitignore` (`*key*.txt`, `*.env`). Keep it that way.
- The Instagram token lasts 60 days: remind Trung to renew it in the Meta app and update the secret.

## Git
- Remote: github.com/sau21h/sau21h (public repo; images must be public for the IG API).
- Rebase before pushing; Actions also commit (generated images, status updates), so pull first to avoid races.

## Status as of 13/10/2026
- Style switch: the page moves completely to soft painterly realism (learned from Threads @odwyer_sio9); style key `painterly` in `style/styles.json`. Moon and people only sometimes; mix day/night, indoor/outdoor; rotate palettes; no clear faces.
- All batch 1 `approved` posts set to `retired` (publish.py skips them), so nothing posts until the new batch is approved. Tests: `posts/tests/` (Hà Giang, Sài Gòn, Hà Nội, 1K, rendered locally).
- Generate 3 posts per round, concept table first.
- Round 1 (`queue/2026-10-14_batch2.json`) approved: 13/10 Hà Nội thu, 14/10 Sài Gòn mưa, 15/10 Hà Giang tam giác mạch. Retired batch 1 posts were renamed `retired-<date>` (queue and posts folders) so their dates are free. Next round needed for 16/10 onwards.
- Approved plan 16-25/10 (render 3 per round): 16 Tuyền Lâm dã quỳ, 17 sông Hoài Hội An night, 18 Hồ Tây café (indoor), 19 Trà Sư mùa nước nổi, 20 chợ hoa Hồ Thị Kỷ (20/10), 21 hoa đăng cầu Trường Tiền night, 22 Tả Van homestay window (indoor), 23 Nguyễn Huệ balcony + moon, 24 Tràng An morning, 25 cỏ lau bãi giữa Long Biên sunset. Round 1 of it = `queue/2026-10-16_batch3.json`.
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
