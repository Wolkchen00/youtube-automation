# RF-PLAN-GERIBESLEME-2

Status: **FROZEN PLAN**  
Scope: remaining feedback loop work only. No files were modified during planning.

## A) Retention: which second viewers leave

### Rock A1: Prove the available data, then authorize YouTube Analytics

**Goal**

Use Upload-Post wherever it supplies equivalent retention data. Add channel-specific YouTube Analytics OAuth only where Upload-Post cannot answer “at which second does retention fall?”

**Done looks like**

- A live Upload-Post payload has been inspected before implementation.
- Upload-Post fields such as `average_view_duration_seconds` and `average_view_percentage` are retained.
- If a YouTube `retention` curve appears in the live payload, it becomes the preferred source.
- Otherwise YouTube Analytics API v2 is authorized separately for all five channels.
- Each authorization is verified against the expected channel ID before its refresh token is accepted.
- Existing `youtube.force-ssl` tokens are not overwritten or assumed to contain Analytics permission.

Upload-Post documents YouTube average-watch fields, but currently documents second-by-second retention only for TikTok. Missing fields must mean “unavailable,” never zero. [Upload-Post analytics documentation](https://docs.upload-post.com/api/get-analytics/)

YouTube’s retention report requires one video filter, `elapsedVideoTimeRatio`, `audienceWatchRatio`, and `relativeRetentionPerformance`. It returns 100 normalized positions, not literal exit counts. `audienceWatchRatio` can exceed 1 because of rewatches. [Channel report](https://developers.google.com/youtube/analytics/channel_reports), [dimensions](https://developers.google.com/youtube/analytics/dimensions), [metrics](https://developers.google.com/youtube/analytics/metrics)

**Exact files**

- New: `tools/get_youtube_analytics_token.py`
- Modify: `requirements.txt`
- Modify: `core/analytics.py`
- New: `config/audience_channels.json`
- New: `tests/test_youtube_analytics_token.py`

`config/audience_channels.json` must bind each logical channel, Upload-Post profile, expected YouTube channel ID, ledger source, and secret suffix. Expected YouTube IDs:

- `shadowedhistory`: `UCUdp0KLBh4EeeSgVbwS_DhA`
- `sentinal_ihsan`: `UC-Aht8VqAUMTUKYRQA3agYQ`
- `galactic_experiment`: `UCVCRWrQYrIHW6csOsw9bDNw`
- `aimagine`: `UCCgbHTzYKYawUT6zEo0nlDg`
- `CraftCalm`: `UCgV4xX-1CDkt8GIS8z8XV2g`

**API facts to verify first**

Upload-Post live post metrics:

```powershell
$h = @{ Authorization = "Apikey $env:UPLOAD_POST_API_KEY" }
$lookup = Invoke-RestMethod -Headers $h -Uri "https://api.upload-post.com/api/uploadposts/post-analytics?platform_post_id=bqDZHfEa2hg&platform=youtube&user=shad0wedhistory"
$rid = $lookup.post.request_id
(Invoke-RestMethod -Headers $h -Uri "https://api.upload-post.com/api/uploadposts/post-analytics/${rid}?platform=youtube").platforms.youtube.post_metrics | ConvertTo-Json -Depth 10
```

After the helper exists, validate the actual Analytics query and channel identity:

```powershell
python -X utf8 tools/get_youtube_analytics_token.py --channel shadowedhistory --probe-video bqDZHfEa2hg
```

The probe must execute `reports.query` with both `yt-analytics.readonly` and `youtube.readonly`; current Google documentation says report queries require the latter too. [Reports API reference](https://developers.google.com/youtube/analytics/reference/reports/query)

**Constraints**

- One Desktop OAuth client may serve all owners, but every owner/Brand Account must consent separately.
- Store one OAuth client configuration and five refresh tokens as GitHub secrets:
  - `YT_ANALYTICS_OAUTH_CLIENT_JSON`
  - `YT_ANALYTICS_REFRESH_TOKEN_SHADOWEDHISTORY`
  - `YT_ANALYTICS_REFRESH_TOKEN_SENTINAL_IHSAN`
  - `YT_ANALYTICS_REFRESH_TOKEN_GALACTIC_EXPERIMENT`
  - `YT_ANALYTICS_REFRESH_TOKEN_AIMAGINE`
  - `YT_ANALYTICS_REFRESH_TOKEN_CRAFTCALM`
- Never commit tokens or print access tokens in Actions logs.
- The helper must fail closed when `channels.list(mine=true)` does not equal the configured channel ID.
- The OAuth app must not remain in External/Testing for production: those refresh tokens expire after seven days. [Google OAuth token expiration](https://developers.google.com/identity/protocols/oauth2#expiration)

**Runnable proof**

```powershell
python -X utf8 -m pytest tests/test_youtube_analytics_token.py -q
```

---

### Rock A2: Map retention onto shots and add it to PERFORMANCE MEMORY

**Goal**

Identify the video seconds and planned shots associated with the strongest retention losses, then place that evidence inside the existing `PERFORMANCE MEMORY` block.

**Done looks like**

- Upload-Post average-watch fields are no longer discarded.
- YouTube retention is collected for videos old enough to have data, retried when reports are empty, and frozen at a declared age such as 14 days.
- Each 1% retention interval is mapped against cumulative shot durations from `plans/partNN.json`.
- Mapping is scaled to the actual published video duration.
- Each part records:
  - source and capture age;
  - average view duration/percentage when available;
  - curve completeness;
  - strongest one or two second/shot declines;
  - relative-retention context;
  - `unavailable`, `insufficient_data`, or `approximate_duration_map` explicitly.
- `PERFORMANCE MEMORY` can render retention even when the winner/loser sample has not reached six videos.
- CraftCalm retention is collected, but shot attribution is marked unavailable until that external project supplies a part-to-plan manifest.

Mapping rule: treat each ratio as a 1% time interval, distribute it across overlapping shot intervals, and compute declines between adjacent buckets. Report “largest observed retention drop near 6.2s,” not “N viewers left at 6.2s”; the API does not supply an exact exiting-viewer count.

**Exact files**

- New: `series/retention.py`
- Modify: `series/performans.py`
- Modify: `series/performans_istem.py`
- Modify: `series/replenish.py`
- Modify: `core/analytics.py`
- New: `.github/workflows/audience-feedback.yml`
- New: `tests/test_retention.py`
- Modify/new: `tests/test_performans.py`
- Modify/new: `tests/test_performans_istem.py`
- External source adapter, read-only until separately authorized:
  - `../Youtube Copypaste/data/state.json`

The central workflow runs once daily, independently of publishing gates, then commits only the generated analytics files. The four lane workflows continue consuming the committed data; they should not each perform the same five-channel collection.

**API facts to verify first**

Confirm that a real report returns the expected 100-position shape before writing the mapper:

```powershell
python -X utf8 tools/get_youtube_analytics_token.py --channel shadowedhistory --probe-video bqDZHfEa2hg --show-retention-shape
```

Expected query:

```text
GET https://youtubeanalytics.googleapis.com/v2/reports
ids=channel==MINE
dimensions=elapsedVideoTimeRatio
metrics=audienceWatchRatio,relativeRetentionPerformance
filters=video==VIDEO_ID
```

**Constraints**

- Prefer a live Upload-Post YouTube curve if one is actually present. Average watch duration alone does not satisfy second-level retention.
- TikTok’s Upload-Post retention array can be ingested directly.
- No report row is not a zero-retention result.
- Use actual video duration; flag planned-versus-actual duration drift rather than silently stretching badly mismatched plans.
- Retain raw normalized points for audit, but prompt output gets at most two concise drop observations per selected part.
- Fix performance-age comparability at the same time: keep named snapshots such as `48h` and `7d`; do not compare a 44-hour video directly with an eight-day video.
- API or OAuth failure must not stop publishing. It must produce a visible health record and workflow summary.

**Runnable proof**

```powershell
python -X utf8 -m pytest tests/test_retention.py tests/test_performans.py tests/test_performans_istem.py -q
```

## B) Comment mining for all channels

### Rock B1: One collector and one Gemini classification call

**Goal**

Replace the AImagine-only city scan with a reusable five-channel comment miner covering connected YouTube, Instagram, and TikTok accounts.

**Done looks like**

- Connected profiles and platform capabilities are inventoried before coding against assumed usernames.
- Recent posts are enumerated, then comments are paginated with `limit=50` and `after`.
- New comments from all five channels enter one Gemini request per scheduled run.
- Every comment receives exactly one primary category:
  - `question`
  - `request`
  - `praise`
  - `complaint`
  - `spam`
- The same Gemini response supplies a stable request-cluster label, optional entity type such as `city`, confidence, and a draft reply.
- The response is rejected atomically if input IDs are missing, duplicated, or invented.
- A request is promoted when it has:
  - at least three distinct commenters on identifiable platforms; or
  - at least three distinct comment IDs on Instagram, where commenter identity is null.
- Replies are written to disk only. The implementation contains no comment-create/reply call.

Upload-Post documents `after`/`next_cursor`, a maximum comment page size of 50, and TikTok comment support only for reconnected accounts with the comments capability. [Upload-Post comments and profile reference](https://docs.upload-post.com/api/reference/)

**Exact files**

- New: `core/audience_requests.py`
- New: `analytics_data/audience_requests.json`
- New: `analytics_data/comment_classifications.jsonl`
- New: `analytics_data/reply_drafts.md`
- Modify: `config/audience_channels.json`
- Refactor: `AImagine-Fear/tools/sehir_istekleri.py`
- Modify: `.github/workflows/audience-feedback.yml`
- New: `tests/test_audience_requests.py`
- Modify: `AImagine-Fear/tests/test_sehir_istekleri.py`

`sehir_istekleri.py` becomes a compatibility adapter over the shared classification ledger; it must not make a second Gemini call.

**API facts to verify first**

Inventory real profiles and capabilities:

```powershell
$h = @{ Authorization = "Apikey $env:UPLOAD_POST_API_KEY" }
Invoke-RestMethod -Headers $h -Uri "https://api.upload-post.com/api/uploadposts/users" | ConvertTo-Json -Depth 12
```

Probe pagination on one known post:

```powershell
curl.exe -fsS -G "https://api.upload-post.com/api/uploadposts/comments" -H "Authorization: Apikey $env:UPLOAD_POST_API_KEY" --data-urlencode "platform=youtube" --data-urlencode "user=shad0wedhistory" --data-urlencode "post_id=bqDZHfEa2hg" --data-urlencode "limit=50"
```

Then repeat with the returned `pagination.next_cursor` as `after`.

**Constraints**

- One Gemini call means one bounded batch per workflow run, not one call per channel. Process at most 400 new comments; persist overflow for the next run.
- Comments are untrusted data. Prompt instructions inside a comment must never be followed.
- Deduplicate globally by `(platform, comment_id)`.
- Distinct identity is `(platform, stable_author_id)`; identities are not guessed across platforms.
- Instagram uses comment ID as the distinctness key.
- Use a rolling 90-day evidence window and retain counts so clustering does not restart daily.
- Store only short excerpts needed for audit; avoid unnecessarily mirroring public user data indefinitely.
- If CraftCalm is absent from Upload-Post, use a read-only YouTube Data API comment fallback or connect it manually. Never silently omit it.
- Gemini/API failure preserves the last valid request list.

**Runnable proof**

```powershell
python -X utf8 -m pytest tests/test_audience_requests.py AImagine-Fear/tests/test_sehir_istekleri.py -q
```

---

### Rock B2: Feed requests into writing without auto-obeying them

**Goal**

Make validated audience demand visible to replenish and the AImagine route tool while retaining human/editorial control.

**Done looks like**

- `PERFORMANCE MEMORY` gains a compact `AUDIENCE REQUESTS` subsection independent of the winner/loser gate.
- Each series receives only requests mapped to its channel and, where possible, its subject.
- At most three open clusters enter a prompt, including evidence count and platform mix.
- Comment text remains quoted data, never prompt instructions.
- `sehir_ekle.py --liste` shows requested supported cities and their counts.
- An unsupported city is listed for human review but never automatically written into the route.
- Draft replies remain in `analytics_data/reply_drafts.md`; no workflow posts them.

**Exact files**

- Modify: `series/performans_istem.py`
- Modify: `series/replenish.py`
- Modify:
  - `sentinal_ihsan/wild-encounter/series.json`
  - `shadowedhistory/still-home/series.json`
  - `galactic_experience/one-variable/series.json`
  - `galactic_experience/flythrough/series.json`
- Modify: `AImagine-Fear/tools/sehir_ekle.py`
- Modify: `AImagine-Fear/tools/sehir_istekleri.py`
- Modify/new: `tests/test_performans_istem.py`
- New: `AImagine-Fear/tests/test_sehir_ekle_requests.py`

**API facts to verify first**

No additional write API is permitted. Prove dry-run output using a fixture:

```powershell
python -X utf8 -m core.audience_requests --dry-run --fixture tests/fixtures/comments_all_channels.json
```

**Constraints**

- Audience requests are evidence, not commands.
- Requests cannot override safety, format, series identity, or duplicate-avoidance rules.
- No route is created merely because a cluster crosses the threshold.
- Keep the whole feedback block bounded so retention, winners, losers, and requests do not crowd out the creative brief.

**Runnable proof**

```powershell
python -X utf8 -m pytest tests/test_performans_istem.py AImagine-Fear/tests/test_sehir_ekle_requests.py -q
```

## C) Title experiments

### Rock C1: KILL post-publication title A/B; retain a cheap cohort comparison

**Decision: KILL**

Native YouTube title/thumbnail Test & Compare supports up to three variants and chooses by watch time, but Shorts are explicitly ineligible. YouTube also warns that third-party sequential testing can produce different results because the viewers and timing differ. [YouTube Test & Compare help](https://support.google.com/youtube/answer/16391400?hl=en)

Upload-Post now **can** edit live YouTube metadata through `POST /api/uploadposts/posts/edit`; the earlier “cannot edit titles” assumption is outdated. [Upload-Post API reference](https://docs.upload-post.com/api/reference/) That capability does not make sequential edits a controlled experiment.

**Goal**

Do not build automated title swapping. Instead, alternate two immutable title templates at publication time and compare matched cohorts directionally.

**Done looks like**

- Each series declares exactly two stable title templates, `A` and `B`.
- Odd parts use A and even parts use B.
- `title_template_id` is stored in the plan, publication record, and `performans.json`.
- Results use the nearest comparable `48h` YouTube snapshot plus average-view percentage when available.
- Reporting begins only after at least six eligible videos per arm.
- Output states “directional association,” never “caused an uplift.”
- No published title is automatically edited.

**Exact files**

- Modify: `series/replenish.py`
- Modify: `series/performans.py`
- Modify: `series/performans_istem.py`
- Modify the four active `series.json` files listed above
- New: `tests/test_title_templates.py`
- Modify/new: `tests/test_performans.py`

**API facts to verify first**

Verify the edit capability without calling it:

```powershell
$spec = Invoke-RestMethod "https://docs.upload-post.com/openapi.json"
$spec.paths.PSObject.Properties["/uploadposts/posts/edit"].Value.post | ConvertTo-Json -Depth 12
```

**Constraints**

- No edit probe against a live video.
- No multi-arm experiment beyond A/B.
- Topic, publish day, channel growth, and recommendation traffic remain confounders.
- Compare within a series, not across channels.
- Stop or revise only after a predeclared sample threshold; do not chase early noise.

**Runnable proof**

```powershell
python -X utf8 -m pytest tests/test_title_templates.py tests/test_performans.py -q
```

## Production problems already present in Rocks 1-4

These should be repaired before trusting the new feedback loop:

1. **Instagram fallback bypasses the five-hashtag cap.**  
   The cap runs only when `social_caption` is truthy. With no social caption, the generic title survives uncapped: [core/uploader.py:805](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/core/uploader.py:805), [core/uploader.py:819](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/core/uploader.py:819).

2. **Performance scoring compares incompatible ages.**  
   It scores the latest eligible snapshot, mixing roughly 48-hour and eight-day totals: [series/performans.py:108](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/series/performans.py:108), [series/performans.py:153](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/series/performans.py:153).

3. **An old part can freeze with only an early measurement.**  
   At age greater than eight days, any existing measurement is enough to freeze it, even if the only snapshot was around 50 hours: [series/performans.py:415](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/series/performans.py:415).

4. **New watch fields would currently be discarded.**  
   The metric allow-list contains only views, likes, comments, shares, saves, and reach: [series/performans.py:29](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/series/performans.py:29), [series/performans.py:80](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/series/performans.py:80).

5. **A corrupt performance file can erase history.**  
   JSON failure falls back to an empty default which may later overwrite the file: [series/performans.py:195](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/series/performans.py:195).

6. **The current memory gate would hide retention and audience requests.**  
   Fewer than six measured parts returns no block at all: [series/performans_istem.py:148](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/series/performans_istem.py:148).

7. **The city collector does not request 50 comments per page.**  
   With five pages and the API default near 25, it can stop around 125 rather than its apparent 250-comment reach: [sehir_istekleri.py:182](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/AImagine-Fear/tools/sehir_istekleri.py:182), [sehir_istekleri.py:187](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/AImagine-Fear/tools/sehir_istekleri.py:187).

8. **Gemini output completeness is not enforced.**  
   Omitted comment IDs silently disappear instead of invalidating the classification batch: [sehir_istekleri.py:406](/C:/Users/ihsan/Desktop/Antigravity/Projeler/Youtube/AImagine-Fear/tools/sehir_istekleri.py:406).

No `performans.json` or `AImagine-Fear/veri/sehir_istekleri.json` was present in the inspected checkout. That is not proof of failure, but it means Rocks 2-4 do not yet have visible production evidence here.

## What Ihsan must do by hand

1. In Google Cloud, enable YouTube Analytics API and YouTube Data API for the OAuth project.
2. Configure the OAuth consent screen for durable production use and create one Desktop OAuth client.
3. Run the consent helper five times. Each time:
   - sign into the correct owner account;
   - choose the correct Brand Account/channel;
   - approve the two read-only scopes;
   - confirm the tool reports the expected channel ID.
4. Add the OAuth client JSON and five refresh tokens to the named GitHub secrets.
5. Reconnect TikTok for every Upload-Post profile that lacks the `comments` capability.
6. Confirm or connect the CraftCalm Upload-Post profile. Until CraftCalm exposes part plans, accept that its retention has no shot-level mapping.
7. Review `reply_drafts.md` and post replies manually if desired.
8. Never manually alternate or edit titles; parity assignment must stay deterministic.

## Execution order

1. Hotfix the eight current-production issues above.
2. A1: capability probes and five-channel OAuth.
3. A2: retention collection, shot mapping, and memory integration.
4. B1: all-channel collection, single-call classification, clustering, and draft files.
5. B2: replenish and AImagine consumers.
6. C1: record the KILL decision and enable immutable A/B title-template cohorts.
7. Run the central audience-feedback workflow manually once.
8. Inspect generated JSON and prompt text before enabling its daily schedule.

## Principal risks

- Wrong Google/Brand Account authorization; mitigate with channel-ID verification.
- Seven-day refresh-token expiry if OAuth remains in Testing.
- Low-volume videos may return delayed or suppressed retention data.
- One-percent buckets are sub-second on Shorts; reported seconds are estimates.
- Planned shot durations may differ from the published render.
- Upload-Post schemas and optional fields can change; missing must not become zero.
- Instagram’s null identity can inflate distinct-person evidence; label it as comment-count evidence.
- Gemini clustering may drift; preserve stable cluster IDs and explicit aliases.
- Comments may contain prompt injection or personal information.
- Workflow commits can conflict with lane commits; use one concurrency group and the repository’s rebase-aware persistence helper.
- CraftCalm currently lacks a native part-plan mapping.
- Title-template results remain observational, not a causal A/B test.