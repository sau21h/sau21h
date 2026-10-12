# sau21h: Instagram + Threads AI-art page

**@sau21h** is a Vietnamese AI-art page modelled on @codex_401, for a Vietnamese (young, Gen Z) audience. One post every evening at 21:00, on Instagram and Threads. The goal is to become a sales channel later (wallpaper packs, prints), not to chase follower counts.

## Positioning
**Phone-wallpaper-grade art of Vietnam, mostly anime.** Every image should be good enough to set as a lock screen. Learn from @codex_401 (vast clean sky, one subject, one warm light) but make it Vietnamese: recognisable landmarks, seasons, daily life.

Sales path, later and only if the page gains traction:
1. Paid wallpaper packs (city packs, Tết 2027 pack) through a link in the bio.
2. Printed posters and a Tết 2027 calendar (Tết is 6 Feb 2027, so sell in Dec and Jan).
3. Comment-to-DM (ManyChat paid plan) only once there is something to deliver. For now: no CTAs, no "comment X" promises.

## Content rules (agreed with Trung, Oct 2026)
- **Anime first.** House anime style = codex-style key visual: near-flat single-colour sky over 55 to 65% of the frame, one clear subject as a silhouette in the lower third, one cool colour plus one warm accent light, crisp clean shapes. Rotate sky colours between posts so the grid does not turn all violet.
- **Realistic (cinematic) images sparingly**, with film grain, and never with clearly visible faces (backs, silhouettes, distance).
- **Mood: warm, hopeful, cozy.** Not gloomy, lonely or scary. Couples and friends are welcome.
- **Every post needs a recognisable place**: Landmark 81, Bitexco, Nhà thờ Đức Bà, Nhà thờ Con Gà (Đà Lạt), Hồ Gươm and Tháp Rùa, Cầu Rồng... Check landmark details (the AI often gets bridges and lake layouts wrong). More Sài Gòn than Hà Nội.
- **Mix day and night scenes.** Posting at 21:00 does not mean every image is at night.
- **Aesthetic topics only**: skip mundane daily-life topics (late-night food etc.) and forced folklore jokes.
- **At least 2 images per post** (Instagram only allows adding music to multi-image posts). Trung adds music manually in the app after the post goes live.
- **Text on images**: only a small film-style subtitle, only when truly needed. Drawn by the script (Noto Serif Italic, pale yellow), never by the model.
- **Captions**: one short, simple lowercase Vietnamese line, then `#sau21h` on the next line. Nothing else.
- **Reference post** that ticks every box: 12/10 metro (focused subject, Landmark 81, good colour, simple caption).

## Image format
- Each slide is rendered once as a **9:16** wallpaper (`<n>_916.jpg`). Only this costs money.
- Instagram feed image (`<n>.jpg`) = the whole 9:16 image centred on a **black 4:5 canvas** (like codex_401). Free.
- Threads gets the full 9:16 image.

## Weekly workflow
```
Weekend session with Claude
  1. research trends and date hooks, write a CONCEPT table (scene, landmark, day/night, subtitle, caption)
  2. Trung approves concepts in text (free)
  3. push queue/<date>_batchN.json  ->  "Generate images" Action renders 9:16 + feed images  (status: review)
  4. Trung reviews review.html, Claude re-rolls rejects  ->  status: approved
  5. "Publish daily post" Action at 21:00: Instagram, then Threads  (status: posted)
```
Nothing is published unless it is `approved`. To publish a post immediately, commit `publish-now.txt` containing its date.

## Tools and cost (budget: 1,000,000 VND per month)
| Job | Tool | Cost |
|---|---|---|
| Images | Gemini Nano Banana 2.1, 2K, 9:16 | about 1,300 VND per image |
| Prompts, captions, research | Claude | already paid |
| Hosting, rendering, scheduling | GitHub public repo + Actions | free |
| Publishing | Instagram API + Threads API | free |

A weekly batch (7 posts x 2 slides plus a few re-rolls) costs roughly 20,000 to 25,000 VND. Spend is logged per image in `logs/spend.csv`; `logs/spend_summary.txt` shows the estimated balance. Add every Gemini top-up to `logs/credit.json`.

## One-time setup (done)
1. @sau21h is a Creator account. Bio and avatar still to be finalised.
2. Gemini API key with prepay billing, stored as GitHub secret `GEMINI_API_KEY`.
3. Public repo github.com/sau21h/sau21h.
4. Meta app `sau21h-publisher` with two use cases: Instagram API with Instagram login, and Threads API. @sau21h is both Instagram tester and Threads tester.
5. GitHub secrets: `IG_USER_ID`, `IG_ACCESS_TOKEN`, `THREADS_ACCESS_TOKEN`.

**Both Meta tokens expire after about 60 days (around 10/12/2026).** Regenerate them in the Meta app and update the secrets. If token generation says the user has not accepted the invite, the browser is logged into another Instagram or Threads account: use an incognito window logged in as @sau21h.
