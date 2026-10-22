#!/usr/bin/env python3
"""Precompute 44-point loudness envelopes for every track in index.html.
Downloads each mp3, RMS-envelopes it with ffmpeg, writes env.json {id: [44 floats]}.
Incremental: skips ids already in env.json. Free to run (no paid APIs)."""
import json, re, os, subprocess, hashlib, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = "/workspace/hr-clone"
OUT = os.path.join(ROOT, "env.json")
TMP = "/tmp/envcache"
os.makedirs(TMP, exist_ok=True)

html = open(os.path.join(ROOT, "index.html")).read()
m = re.search(r"const TRACKS = (\[.*?\]);", html, re.S)
tracks = json.loads(m.group(1))
env = json.load(open(OUT)) if os.path.exists(OUT) else {}
todo = [t for t in tracks if t.get("audio") and t["id"] not in env]
print(f"total={len(tracks)} have={len(env)} todo={len(todo)}", flush=True)

BARS = 44

def envelope(t):
    tid, url = t["id"], t["audio"]
    f = os.path.join(TMP, tid + ".mp3")
    try:
        if not os.path.exists(f) or os.path.getsize(f) < 1000:
            subprocess.run(["curl", "-sL", "--max-time", "60", "-o", f, url], check=True, timeout=70)
        # decode to 8kHz mono s16le raw
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                           capture_output=True, timeout=120)
        if p.returncode != 0:
            return tid, None, "ffmpeg rc=%d" % p.returncode
        data = p.stdout
        n = len(data) // 2
        if n < 100:
            return tid, None, "too short"
        samples = [int.from_bytes(data[i*2:i*2+2], "little", signed=True) for i in range(n)]
        vals = []
        for b in range(BARS):
            a, e = int(b*n/BARS), int((b+1)*n/BARS)
            seg = samples[a:e] or [0]
            r = sum(s*s for s in seg)/len(seg)
            vals.append(r ** 0.5)
        mx = max(vals) or 1.0
        vals = [round((v/mx) ** 0.7, 3) for v in vals]
        return tid, vals, None
    except Exception as e:
        return tid, None, str(e)[:80]

done = 0
with ThreadPoolExecutor(16) as ex:
    for tid, vals, err in ex.map(envelope, todo):
        done += 1
        if vals:
            env[tid] = vals
        else:
            print(f"FAIL {tid} {err}", flush=True)
        if done % 100 == 0:
            json.dump(env, open(OUT, "w"), separators=(",", ":"))
            print(f"progress {done}/{len(todo)} have={len(env)}", flush=True)

json.dump(env, open(OUT, "w"), separators=(",", ":"))
print(f"DONE have={len(env)} size={os.path.getsize(OUT)}", flush=True)
