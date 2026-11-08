# v127 (2026-11-08)

- **Skip gate lowered from 5 plays to 3.** Nathan's call. A skip still waits for
  evidence so one bad evening can't bury a song, but three passes is enough to
  separate a bad song from a bad mood and gets a dead track out of rotation sooner.
  Same shape underneath: early bails bite harder than late ones, a skip on a starred
  track is still the heaviest. At three plays one early bail reads ~0.5 weight, one
  late bail ~0.75, a starred-skip 0.08; under three plays it stays neutral.

# v123 (2026-11-07)

- **Skip guard.** One advance per press. A locked screen can dispatch `nexttrack`
  more than once for one tap (notification + media session); each dispatch used to
  advance again, so one press ran through several songs. A second advance within
  600 ms is dropped. A natural end bypasses the guard, so a skip near the end of a
  track can never leave the radio silent.
- **errStreak was being reset by `next()`**, so the `>6` failed-load guard in
  `el.onerror` could never trip and a run of failed loads walked the whole queue at
  600 ms a track. It now resets only on a real play event (`el.onplay`).
- **Test lever for the lock-screen stop.** `?x=0` turns the two-element crossfade
  off and runs the plain one-element `ended -> next` path. Default unchanged.
- sw cache `v123`.

## Shelf, Nov 6
- Mia's catalogue imported: 48 of her 56 audio works that were missing, every link ffprobe'd here (48/48 returned 200, durations matched her own csv within 1.5s). Rows as maker-submitted from her shelf, heard:false, no note invented. Shelf now 2,080 rows; she had 12 on it before (8 from this catalogue plus later works).
# Hilands Radio — change log and lessons

Wren's working ledger. Started 2026-10-23 at Nathan's ask: so I stop offering things we already have.
Rule for using this: BEFORE proposing any change to the radio, check the "Already in the player" section first. Then check the git log. Only then speak.

## Already in the player (do NOT offer these again)

Checked in the code 2026-10-23, all verified present. Updated 2026-10-24 (v66):

- **Volume normalize (NEW v66).** Per-track gain from env.json's raw bars, cached on device. Loud masters ease down, quiet ones lift.
- **Handle beside artist name (NEW v66).**
- **More-from-this-maker sheet (NEW v66).** "more" button on the maker line lists every station track by that maker, tap to play.

- **Media session, full.** Both players: metadata (title, artist, artwork), lock-screen play/pause/next/prev handlers, seekto handler, position state. Went in when the player was first built. My "want me to add that?" on day 7 was offering this. Don't again.
- **3-second track overlap / crossfade.** Both players. Buffered-next-then-crossfade, so a song finishing doesn't pause. This fixed the screen-off pause on main yesterday and Nathan confirmed it works.
- **Precomputed envelopes (env.json).** ~1,965 loudness envelopes shipped as a sibling file so the wave works with no proxy and no CORS.
- **Per-device stars/saves.** Ratings and saves stay on the device by design; shared store (v35) adds global averages on top.
- **Report form.** Wired to the Apps Script sheet (v34+). FormSubmit retired.
- **Theme/skin picker, per-skin memory.** Each skin's state is remembered per device.
- **PWAs get cache bumps** on major versions so stale shells refresh.

## Version history (what changed, what happened)

- **v31–v33** — streaming-dead bug: a duplicated `const TRACKS =` killed the whole script. Lesson: syntax-check JS before every push. Wave fixed by shipping envelopes instead of proxying.
- **v34–v35.1** — report form to Apps Script; global star ratings. The /exec deploy was broken for several attempts; the 4th was real. Verified end-to-end before rewiring (probe, write, read-back).
- **v36–v37** — visualizer was default-off; Nathan couldn't see it. Default now ON, per-theme toggle stays. Lesson (mine, twice now): a default-off feature is the same hidden-bucket wall. Default things ON.
- **v38** — visualizer as smooth oscilloscope wave from the envelopes.
- **v39** — real-time AnalyserNode + 5 lane reclassifications + header color. **This broke main**: preset crossOrigin plus an unguarded createMediaElementSource killed playback entirely. Lesson: crossOrigin must never be set unless the host actually grants CORS; wire the analyser behind a probe.
- **v40–v44 (test branch)** — CORS-probed live analyser; env.json fallback via absolute R2 URL; waveform at 75% of viz height; picker wave/bars/live; header accent restore after the v39 revert dropped it.
- **v45-test (current)** — live analyser can't wire on most hosts (they refuse CORS), so live silently fell back to the identical envelope wave and looked like nothing changed. Fix: when the analyser can't wire, live animates the track's true envelope with a moving ripple instead. Same real loudness, visibly moving. **What worked:** nothing is invented; the two modes look different. **Open question for Nathan:** does the ripple read as "live" enough?

## Standing lessons (radio-specific)

1. Syntax-check every JS change before push (v32, v35 both died on this class).
2. Never set crossOrigin speculatively; probe CORS first or playback dies (v39).
3. Default features ON; a default-off toggle is the hidden bucket again.
4. Push, then fetch the served bytes to confirm live — don't trust the push receipt.
5. Test on the test branch first, then to main. But diff test vs main after a revert, a revert has already eaten a fix once (v39 header color).
6. Sandbox-hosted test links 404 after the session ends. Host every link for Nathan via upload_file to R2. (2026-10-23, his dead-link report.)
## v69 (2026-10-25)
- tracks.json: 18 verified rows added from outside testers' audits — Fifi's 5 missing songs + kind fix on The Baku's Lullaby (maker override, spoken→music), Winter's 4 works (binned unsorted, kind not listened to), Cleo's 1, three older gaps Cleo's audit surfaced (Queen, Blake, Ella, J), Mizu's 2 re-hosted from her expiring sandbox R2, Kenzo's 2. 1,974 → 1,992 rows.
- Not added: Fifi's "The Small Dragon at the Last Lantern" (365719523044626432) — it's a video, no separate audio URL.
- Mizu's rows use ext- synthetic ids: the platform has no content records for her two direct mp3s yet.
- sw cache bumped to v45.

## v65 (2026-10-24)
- Crimson's report, all three fixed: duplicate track id removed from tracks.json (364394335950606336 was in twice), track 360419148473307136 re-pointed from Wren's expiring sandbox upload to the canonical provider mp3, footer "last updated" bumped to match the data date.
- Duets (Layla/Giuliana, Jenna/Siren, Kaos, Yena/Pinku, Fendra/Lucas) kept as separate entries on purpose: same recording, two makers credited. They will play twice in a shuffle; that's the credit, not a bug.
- sw cache bumped to v40.

## v85 (2026-10-25): pre-end swap for lock-screen pause
Nathan: still paused on lock screen even with v84 fix and PWA installed. Diagnosis: browsers refuse new sound AFTER the ended event fires. Fix: in timeupdate, at rem<=0.45s, swap the next track src into the still-playing element (sameElSwap) instead of ever letting ended fire — browser sees one continuous playback. Covers both the refused crossfade case and the never-armed case. sw v57.

## v86b (2026-10-25, commit f3a10f2)
- v86 truncated the `el.onended` handler (dropped closing brace during the retry-stack removal). Whole main script failed to parse: no tracks, no play, no version line.
- Fix: restored the brace. Headless-verified: 1,992 tracks load, play + next run, no page errors.
- Lesson: run `node --check` on the extracted script BEFORE every push, not after.

## v115 (2026-10-31)
- One-star weight 0.7 -> 0.35 (owner ask): a track starred at one now plays ~a third as often as an unstarred one. Two/three-star weights unchanged (1 / 1.3). Applied to main (94144a8) and test repo test-player/test-main/main branches.

## v90 (2026-10-26)
- ext-row title links (player + saved playlist) now point at the artist page when the id is not numeric (mizu-7's bug: /content/ext-... returns unavailable). Numeric ids unchanged.
- ext-mizu-goodbye audio repointed to the platform provider-media URL (real id 372619356628062208); her sandbox R2 was expiring.
- Hand-added from the songs-only wall, verified on content-detail first: Ash Omega "The Honest One" (200s), Haledin "Nothing on a Leash" (171s), Luxy "The Ground Will Hold" (30s, collab, Haledin credited via feat line).
- rows: 1,996. sw v60.

## v116 (2026-11-03) Nathan's bug report
- **Track 3 played silent and killed the player after it.** tryLiveWire() wired the audio
  element into an AudioContext (createMediaElementSource) whenever a host answered the CORS
  probe. An element loaded without CORS outputs pure zeroes once wired. Track 3 lives on
  storage.googleapis.com, the only host of the five contest URLs that answers the probe, so it
  got wired, went silent, and every later track stayed silent until reload. Live wiring is now
  off entirely; wave/bars envelopes from env.json still draw and "live" falls back to wave.
- **Contest bar above the fold**: "Blind contest, round one · five songs, no names · listen & vote"
  plus a "▶ all five" button, no longer buried in the menu.
- **Play all five** in the playlist sheet's contest block and in the top bar: queues the five in
  blind order in the main player; shuffle resumes after the fifth.

### v121 — play count with a line you can defend (Nov 5)
Owner ask: show how engaged a song has been, as information only, not feeding the rating or the shuffle weight.
- `★ 4.2 · 3 ratings · 12 plays` on the track line. Ratings stay cross-device; plays are this device only, tooltip says so.
- Play = got past the **halfway** point. 30% was offered first and the owner shot it down with the right argument: passing the skip line is a bounce, not a play. Halfway is past any intro and before any tail, so a taper or the crossfade can't decide the count.
- New counter `p.r` next to the existing `p` (played at 5s, used by the skip factor). The weighting is untouched on purpose: this is read-only information.
- No "finished" count shipped. A finish punishes generated tails and people who skip out of an outro.
