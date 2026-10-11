# sau21h: Instagram AI-art page

**@sau21h** ("nhớ ai sau 9h đêm") is a Vietnamese AI-art page modelled on @codex_401, for a Vietnamese audience. It posts daily and is meant to become a sales channel later, not to chase follower counts.

## Positioning
**Vietnamese nostalgia and Vietnamese beauty as wallpaper-quality art.** People save it, share it and send it to their mom. The sales path builds on that:
1. **Now:** "Comment KEYWORD for the full HD file" posts. Each comment turns into a DM, which builds a contact list.
2. **Month 2–3:** sell paid wallpaper packs (Tết 2027 pack, city packs) through a link in the bio.
3. **Later:** printed posters and canvases, a 2027 Tết calendar (Tết is 6 Feb 2027, so sell it in Dec–Jan), and phone cases.

## Weekly rhythm (7 posts/week, published 21:00)
| Day | Pillar | Format |
|---|---|---|
| Mon | Events / hot topic of the week | carousel |
| Tue | Seasonal Vietnamese places (mùa & cảnh Việt) | carousel, wallpaper |
| Wed | Trend formats ("If Vietnam were a Ghibli film…") | carousel |
| Thu | Vietnamese legends as anime (truyền thuyết Việt) | carousel |
| Fri | Chill reel | 5–8 s animated scene |
| Sat | Nostalgia / food & daily life | carousel |
| Sun | Mood line + wallpaper (tâm trạng) | single image |

Dates and trends override the table, e.g. 20/10, Halloween, 20/11 and Tết.

## Tools and monthly cost (budget: 1,000,000 VND)
| Job | Tool | ≈ Cost/month |
|---|---|---|
| Images | Gemini **Nano Banana 2.1**, 2K, ~$0.05/image × ~180 including re-rolls | ~240k VND |
| Covers with Vietnamese text | Nano Banana Pro, if 2.1 gets the diacritics wrong (~$0.13/image × 30) | ~110k VND |
| Reels, phase 2 | Kling / Seedance image-to-video via fal.ai (~$0.45 per 5 s × 8) | ~100k VND |
| Prompts, captions, trend research | Claude, in the weekly session | already paid |
| Hosting + scheduler | GitHub (public repo + Actions) | free |
| Publishing | Instagram API | free |
| Comment → DM | ManyChat free tier | free |
| **Total** | | **~450k VND**, leaving ~550k for boosting the best posts |

## How it runs
```
Weekend session with Claude
  └─ research trends, write next week's queue/<date>_batchN.json (prompts + Vietnamese captions)
      └─ push → GitHub Action "Generate images" → posts/<date>/1.jpg …  (status: review)
          └─ you review the contact sheet, I re-roll the rejects → status: approved
              └─ GitHub Action "Publish daily post" at 21:00 → Instagram  (status: posted)
```
Post status: `draft` → `review` → `approved` → `posted`. Nothing is published unless it is `approved`.

## One-time setup (things only you can do)
1. **Instagram:** switch the account to **Creator** or **Business** (Settings → Account type).
2. **Gemini API key:** go to aistudio.google.com → Get API key → turn on billing (paid tier is required for image output). Optionally set a budget alert at $25.
3. **GitHub:** create a free account and a **public** repo (done: github.com/sau21h/sau21h). Instagram downloads images from the repo's public URLs.
4. **Meta app for publishing:** developers.facebook.com → Create app → add the *Instagram* product → "API setup with Instagram login" → add your IG account → generate a token with `instagram_business_content_publish`. Copy the **IG user ID** and the **access token**.
5. In the GitHub repo, go to Settings → Secrets → Actions and add `GEMINI_API_KEY`, `IG_USER_ID` and `IG_ACCESS_TOKEN`.
6. **ManyChat** (free): connect IG, then create a "comment contains KEYWORD → send DM with the link" automation.

The Instagram token lasts 60 days, so renew it monthly in the Meta app and update the secret.
