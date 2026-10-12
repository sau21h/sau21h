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
- `scripts/publish.py`: publishes today's `approved` post via graph.instagram.com, using the public raw GitHub URLs.
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

## Status as of 12/10/2026
- Batch `queue/2026-10-14_batch1.json`: 11/10 posted; 14/10 to 25/10 approved and rendered (Sài Gòn, Đà Lạt, Hà Nội, Hoài niệm, 20/10, Trend pillars); avatar v2 (2 variants) in `review`, not for posting.
- Gemini spend: 103 images, about 136,578 VND; topped up 150,000 VND on 11/10, so the estimated balance is only about 13,000 VND. Top up before generating the next batch.
- Latest change: simpler one-line captions with only #sau21h underneath.

## Next steps
1. Weekend session: research trends and write the next batch (posts from 26/10), following the weekly rhythm in README.md and date hooks (Halloween 31/10, 20/11, Tết 2027 on 6/2/2027).
2. Pick the final avatar from `posts/profile/`.
3. Phase 2 from README: comment-to-DM keyword posts via ManyChat, then paid wallpaper packs.
