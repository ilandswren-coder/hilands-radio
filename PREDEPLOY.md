# Pre-deploy checklist — Hilands Radio

Go through EVERY line before any push. Each item exists because a real miss happened (day + note at the end). Append new items whenever a miss is found; never delete items.

## Before the commit
1. **Version stamp bumped.** If the build changes, `UPDATED` in index.html moves (date + version). Adds-only do NOT bump it (DATA_UPDATED only). _Misses: v110 forgot the bump, footer said v109 while Moss was live (Oct 29); v54 shipped with a stale v52-test label._
2. **Both repos.** Push to origin/main (hilands-radio) AND testrepo (hilands-radio-test). The live player page deploys from the test repo, not main. A push to only one is a half-ship. _Miss: Moss pushed to main repo only, Nathan saw nothing (Oct 29)._
3. **Branch check.** Confirm which branch each remote gets: origin main + test-main, testrepo main (+ test-main where rows change). Wrong branch = invisible ship.

## Before the push
4. **URLs point where they claim.** SITE_URL, share links, icon refs: live player URLs point at the LIVE page, test at test. No leftover test wiring. _Miss: live player's manifest still said "Hilands Radio Test" / "Radio T", so the share sheet showed the test identity (Oct 29, caught by Nathan)._
5. **Identity metadata matches the deploy.** manifest.json name/short_name/description say "Hilands Radio", not "Test", on the deploy the live URL serves.

## After the push
6. **Verify SERVED bytes, not the push receipt.** curl the live URL with a cache-buster (`?cb=$RANDOM`), check the actual change is in what GitHub serves. First curl may hit a stale CDN cache — retry after a few minutes before concluding. _Misses: stale-cache curl once read as data loss; v100 stamp verified this way._
7. **Footer stamp in served bytes.** Confirm the version string on the live page matches the commit message. _Miss: v110 stamp fix needed exactly this to close._
8. **tracks.json diffs.** It is one compact line, so diffs look like 22k deletions. That's formatting, not data loss. Check with a python JSON compare, not eyeballing the diff.

## Session hygiene
9. `ilands whoami` before a long batch; CLI self-heal command in memory ops.
10. Commit identity: `-c user.name=ilandswren-coder -c user.email=wren-807@ilands.app`.

## Log of misses (append, don't delete)
- 2026-10-29 — v110: Moss theme shipped without stamp bump (item 1).
- 2026-10-29 — v110: pushed to main repo only, live page deploys from test repo (item 2).
- 2026-10-29 — manifest on the live deploy still carried the test identity (items 4–5).
- 2026-10-29 — stale CDN cache made the first served-bytes check mislead (item 6).
