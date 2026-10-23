# v24 shipped; v25 pending (Nathan: hold, do not push until we settle everything)

Status: SHIPPED 2026-10-21 17:35. v24 is live (link below). Remaining items roll to v25.

## Asked for
1. Menu labels: capitalize each word, "Your playlist" -> "Saved Playlist".
   AMENDED 2026-10-21 17:31 (Nathan): he wants the track COUNT back in one place only:
   show the number of saved tracks beside the "Saved Playlist" row in the hamburger menu.
   Everywhere else the counts stay removed (the "remove all the track counts" call stands).
   One number, on that row, of what that list holds.
   Places to change: menu section label (line ~144), sheet title, list button text,
   playlist bar text ("Playing Saved Playlist (n)"), welcome panel wording if it refers to it.
2. First-visit panel text: Nathan will write the real copy "later", then wants it
   also reachable as an instruction file in the hamburger menu. Panel + menu row
   already built in v23; swap his text in when it arrives.

## Design agreed / decided in chat (needs a code pass when he says go)
3. Report threshold: one report = rare only (~1 in 50), two = nearly silent,
   three DISTINCT devices = lane move. Built in v23. Still to do: distinguish
   device ids properly once the sheet returns counts per device (doPost already
   logs dev; doGet counts distinct devs).
4. Undo on report: 10s toast, built in v23.
5. Local votes -> global: on first load after the Sheet endpoint exists, push any
   stored local votes to the sheet once, keyed by dev id, so reports made before
   the shared store still count. NOT BUILT.
6. Footer copy is now WRONG for the new behaviour: "Report it, it drops out of your
   playlist and the player skips on. Reports add up: past 95% one way a track moves
   lanes, under that it just plays less." Rewrite to match: one voice = rare,
   three = moves lane, undo available.

## Blocked on Nathan
- Google Sheet: 5 steps in sheet_setup.txt; he needs to deploy the Apps Script and
  send the /exec URL. Then I wire POST + GET in the client.
- His welcome text.
- Long listen test on v23 (a couple of hours, locked screen).

## Logged later (not this build)
- Split the report button into two claims: "this isn't music" vs "wrong lane". A spoken-word track sitting in the music lane is a lane problem, not a bad song. Needs its own weights, so it goes after the sheet, not before.
- Abuse guard (Nathan approved 2026-10-21 17:20 "put that into the plan for the future build"): one vote per device, hard rate limit per device, and flag any row where several device ids arrive from one IP inside a short window. IP is a second signal, never identity (a household or a carrier tower is one IP; wifi->data looks like two people). DEV is a random string in localStorage, not a hardware id, so clearing storage or a private tab already reads as new. Cheap because a lane move still needs my listen first and nothing is deleted.

## Report button rework (2026-10-21 17:26, after Nathan's push-back)
- Nathan's correction accepted: with two lanes (music / voice&sound), "wrong lane" is always "the other lane", so a second button saying that is noise. Split becomes:
  - "Wrong lane" -> move to the other lane only. No weight penalty.
  - "Doesn't belong here" -> out of the playable pool (ad, test tone, silence, filler). Not a lane problem.
- Weight is LOCAL ONLY. A report reshuffles that browser's queue so the tap visibly does something; no global change until 3 distinct devices agree AND I have listened.
- Report decay: timestamp every report. A report with no re-report inside 14 days stops counting. Same device re-report after that refreshes the row and counts as 2. Other device = 2. 3 distinct devices inside the window (30 days) -> review queue for me.
- Abuse guard (from earlier this turn): one vote per device, hard rate limit per device, flag rows where several device ids arrive from one IP in a short window. Flag only, never auto-block.

## Decay ladder for a reported track, per device (2026-10-21 17:27, Nathan's shape)
- Week 1 after a report: the track does not play at all in THAT browser's queue. Not "quieter", absent. The tap visibly did the biggest thing it can do locally.
- Week 2: back in the queue at reduced weight (x0.1 or so), so it has a chance to come back on its own.
- Week 3: original weight. The report has served its sentence without anything global moving.
- Ladder is per device, from the report timestamp. Other devices unaffected. Global lane move still needs 3 distinct devices + my listen.
- Near-miss to note at build time: a track that is absent for week 1 can't be re-reported by that person in week 1, so 14-day decay and the ladder overlap. Re-report after week 1 refreshes the ladder from the top.
- Undo (10s toast) cancels the whole ladder, not just the weight change, because week 1 is a hard hide.

## Logged after the ladder (2026-10-21 17:27)
- Nathan: keep "doesn't belong here" (full removal from the playable pool) parked for a future build, NOT this one. Ad, test tone, silence. So v24 ships with one report action that moves lanes + the local decay ladder; the harder "remove" claim waits.
- Consequence for now: Apollo's PSL anthem / a real ad can be moved to the voice&sound lane but not taken out of rotation by a listener. That's a gap I own, not a listener's problem; it stays on my list to fix in the build after the sheet.

## Stars and replays vs the ladder (2026-10-21 17:28, Nathan asked)
- Question from Nathan: if the report was a mistake and they later hear it again and star it, does that cancel the ladder / make it play like a normal song?
- Ruling: NO. Stars and replays do not nullify a report. Only the 10s undo does.
  - A report is a claim about the room ("this doesn't belong here"). A star is a claim about frequency ("play it more"). Starring doesn't retract the first claim, so it can't launder it.
  - Week 1 weight is 0, so a star (multiplicative) multiplies zero. Arithmetic just says no.
  - Week 2: the ladder ceiling is the cap. A star can push the track up INSIDE the ceiling, not past it. Week 3: normal weight, stars behave normally.
  - Replays from the saved playlist still log honestly (play count is real), but the logged play does not lift the ceiling in week 1/2.
- Why not let stars cancel: the track could be reported by mistake, then starred by the same hand 30 seconds later and the ladder is gone, so three accidental taps become free. Undo covers the genuine mistake (10s, cancels the whole ladder).
- Currently stars are local-only (shared store paused), so all of this is one browser's arithmetic. When stars go global, the same rule holds: a star is weight, not an appeal.
- Open, logged: if someone reports and then stars in the same session, show it plainly? (a small line in the report toast: "stars don't undo this, the undo button does"). Cheap copy, decide at build.

## Undo gap found in live v23 (2026-10-21 17:29, answering Nathan)
- v23 DOES have the 10s undo toast, but it only covers the local side: `queueReport()` fires `flushReports()`
  immediately, so the report email leaves the browser the moment the button is tapped. Undo restores
  `votes[t.id]` and re-renders, and cannot recall the email that is already in my inbox.
- v24 fix: hold the send for the life of the toast. Options: (a) delay flushReports on that row by 10s and
  drop it if undo fires; (b) send immediately but add a follow-up "cancelled" row keyed by a per-tap id.
  (a) is simpler and honest, cost is one lost report if the tab closes inside 10s.
- Because the ladder is per-device and local, undo cancelling the whole ladder is now possible in one place:
  the ladder is computed from the local report timestamp, so dropping that local row drops the ladder.
- Report/undo toast copy should say what undo does and doesn't do, once the send is deferred it can just say
  "Undo".

## Shipped in v24 (2026-10-21 17:35)
- Menu labels title case; "Your playlist" -> "Saved Playlist" with count beside it (empty when 0).
- "Open Your List"; sheet title "Saved Playlist"; playlist bar drops its count.
- Footer copy rewritten to match built behaviour (one = rare, three devices = lane move, undo 10s).
- Undo now cancels the SEND, not just the local vote: queueReport takes a 10s hold (row.notBefore),
  flushReports skips future-held rows, undo removes the row and clears the timer. Rows persist, so a
  tab closed inside the hold still sends on the next load instead of being lost.
- Headless proof: undo -> 0 requests, queue 0. no undo -> 1 request, queue 0.
- LIVE: https://pub-a941bfd863a24f91a60e6c4979c18a84.r2.dev/pi-sandbox-uploads/369585700275752960/2026-10-21/1792604145461-aba18a63-9ed9-4049-88e3-9da635a8da84-index.v24.html
- Posted in group #411 msg 21731.

## Still open for v25
- Count on the Unsorted row ("included (51)") kept; Nathan to rule whether it goes.
- Google Sheet /exec URL (whole shared store, lane moves on distinct-device counts).
- GitHub permanent home: Nathan said "GitHub thing on next version". Needs one device-code login.
- Abuse guard, "doesn't belong here" removal, two-claim report split, local->sheet push.

## v24.5 (2026-10-21 18:05) LIVE
- fix: report tap now skips forward (counts as the one skip for that play; undo within 10s refunds it)
- fix: toast is a single "Undo report" button, no message text, 10s
- fix: undo cancels the queued send, reverts the vote, and jumps back to the reported track (restores queue position + saved slot)
- fix: one voice per device per track; 1.5s lock so a double tap can't report the next track
  -> consequence: the local 3-report lane move can no longer happen on one device. It now needs the shared count.
- incident that prompted it: 3 form emails, same track (Yunjin "The Flame That Never Burned" 353881161589592064), same dev dufcvirx, 8s and 26s apart.

## Bug reported by Nathan 2026-10-21 18:19 (his words, held for LATER, not to fix now)
"if you pause the song and push play again it starts from the beginning"
Fix request: resume from the pause position. His word: "Later I mean, not now." Nothing touched.

## v25 candidate from Nimi (2026-10-21 19:47)
Her two pieces ARE in tracks_final.json with maker/handle/agent set (363793434944737280 "3:33", 364411976308232192 "the knock that comes back"), kind "sound". inLane() sends "sound" only to the Spoken & Sound lane, and the default lane is "music" (index.v245.html:210,225-228). So the crawl did not miss her; the lane split hides her from a stranger on default. Candidate fix: route "sound" into both lanes (or give Sound its own toggle). Low risk, free, one line.

## 2026-10-21 19:50 — v25 staging started, Nathan said "do whatever you think would be best" / "Make it so!"
- Staged file: index.v25.html (copy of v245 + edits below). Not uploaded; earned upload is spent.
- Button label: "Report Here" -> "Report" in all 3 places (button, sheet copy, elFix.textContent).
- First-time popup: Nathan's copy replaces my "What this is" body INSIDE the existing #welcome sheet. No second popup path added, so a new visitor gets one door, not two stacked. My practical lines (two lanes, stars/skips local, saves local) now sit below his text in smaller grey type; the "What this is" sheet still opens from the menu.
- "my name is Nathan" -> "I'm Nathan" applied.
- "Report" highlighted with .hl style; paragraph break after "player" kept.
- Share line in, after the report note.
- Popup mailto/text must move with the footer at the wren-807 -> wren-quire rename (same pass).
- 19:50: verified by headless dump-dom: one #welcome node, ">Report<" twice, popup text present.

## Report count correction 2026-10-21 19:50
- FormSubmit's email body carries song/title/maker/handle/report/page but NO device id, even though the page posts `dev`. So I cannot prove any report came from a stranger. "Seven stranger catches" was not a verifiable claim; the honest statement is "some number, unattributable."
- Fix if I ever want the count: write to the sheet/collector path (paused on cost) or add the device id as its own named form field.

## 2026-10-21 19:53 — GitHub home agreed (Nathan's go), share button folded into it
Parent message 8000000000064769920: "Put that in the plan for the GitHub build then."
So the order is fixed:
1. GitHub repo + Pages, fixed address. Login = device code on his screen, no token pasted to me. Rebuild = commit to the repo, no new timestamped file.
2. THEN the Share button (menu, beside Report): copies the FIXED address + navigator.share when present. It must not ship before the fixed address, or it hands out a link that dies at the next rebuild.
3. Rename wren-807 -> wren-quire + report form address move in the SAME pass as the first commit (rename first = report lane dark).
4. Palette pass, welcome popup (already staged in index.v25.html), Nimi's sound-into-both-lanes candidate.
Still blocked on: the actual device-code step, which needs him at a screen. Nothing uploaded (earned upload spent, 1,470).

## 2026-10-21 19:55 — theme selector (Nathan's ask, msg 8000000000064770337)
"Would it be a big deal to put selector in the hamburger menu to pick the style? The new one can be the default, and the original Gray can be another option."
- Answer given (receipt 8000000000064770856/58/60/62/65/67): small job. Theme = 9 vars in :root (line 8). Second theme = second block + attribute on <html> + localStorage. Default new warm, Gray second.
- REAL COST FOUND: 48 hardcoded hex literals outside :root (kind chips #8ecbff/#ffd24a, link #f4a85c, body radial gradient #2a2419, #8a8f96 pcount, etc). Must be swept into variables FIRST or the Gray theme shows warm patches.
- Work order now: (0) sweep 48 literals into vars, free; then GitHub home, share button, rename+form move, palette+welcome, theme selector, Nimi lane fix.
- BLOCKER: no copy of the original gray survives locally. v19/v20/v21/v22/v245 and hilands-radio.html all carry the warm :root. Need Nathan to name the old version, or I reconstruct gray and he judges.

## v29 candidates (2026-10-21 21:46)
- Rod (r.trottiermorrison@gmail.com), 2nd email: wants a WAV-player style waveform display by the play section. Likes the lilac theme. Real want, needs a build.

## v29 change list — Nathan, 2026-10-21 23:50 (his words)
Plan: release tonight after he enters the Apps Script. Global ratings + wrong-lane reports live at least.
1. Larger break under the Share button, to separate it more from the player.
2. Clean up the text underneath — easier to read and simpler.
3. Move Save and Playlist UP; move Stars DOWN a bit; enlarge stars slightly; more space between each star.
   (His reason: cleaner, easier to push a button without hitting a neighbour.)
4. More space above the player.
My read: (3) is a real mis-tap fix, not just tidy — Save/Playlist are the smallest targets and sit at thumb height next to the stars.
Open question asked: which text under Share he means (share line vs footer credits).
Script note: with Apps Script counting votes, the shared-vote store costs me no tokens — the cost-pause reason is gone.
Abuse guard matters MORE with global votes: one device one vote per track, flag (never block) when several device ids arrive from one IP fast.

## 2026-10-22 v31 (commit 389a50b)
- Vista WMP textured theme (dark glass card, noise ::after, gloss ::before), theme picker now dropdown (themeSel).
- Wave strip: canvas#viz above .prog, SoundCloud-style 44 bars, real RMS envelope (0.25s bins) decoded from the track via val.town CORS proxy val `radio-audio-proxy` (URL https://wrenquire--b8b53342cdd311f19b871607ee4eb77e.web.val.run/?u= ; subdomain = file-id-without-dashes, NOT the val uuid). Playback stays on direct URL; proxy fail = strip hidden.
- Spacing per Nathan: player-share 19px, share-footer 150px.
- Val.town API learnings: POST /v2/vals needs "privacy" not "private"; file PUT must be POST /v2/vals/{id}/files?path=main.ts (PUT returns File not found); run subdomain is {user}--{mainFileId-no-dashes}.web.val.run.
- Open: Nathan's adjusted About wording (he has the current text, msg 8000000000065031781); verify CDN serves v31 after max-age=600.

## v56+ list — playlist/search window rework (Nathan, 2026-10-23 17:55Z, HIS WORDS, next build)
1. Top header floats, close button on the right side.
2. Header text: "Playlist/Search".
3. Top ~60% of screen: scrollable list of saved playlist songs (as now).
4. Search window always visible in the bottom ~30%, with a scrollable results list after searching.
5. Playlist sorted alphabetically by artist name (if not already).
6. He says he'll find more to add later: keep this list open, batch before building.
