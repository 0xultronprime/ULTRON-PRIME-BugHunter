# VIDEO PLAN — ULTRON PRIME BugHunter rebuild

**Channel:** ULTRON PRIME — https://www.youtube.com/@ultronprime_zero
**Format:** 8–10 min, 16:9, screen-recorded demo + talking head / voiceover
**Repo:** ULTRON PRIME BugHunter (fork of elementalsouls/Claude-BugHunter)
**Rule for the whole video:** authorized testing only, on screen and in words.
Every demo uses the fictional SAMPLE findings against `example.com` — say so
out loud. Never show a real target, real credentials, or an unauthorized test.

---

## Outline

### 0:00–0:45 — HOOK
- "This open-source project has 83 bug-hunting skills, 15 commands, and 681
  real disclosed bug-bounty patterns — and it was the #1 trending repo on
  GitHub this week."
- Show the GitHub trending page + the repo README.
- "I rebuilt it as ULTRON PRIME BugHunter — same brain, new theme, and
  three features the original doesn't have. Here's what changed, and the
  live demo."

### 0:45–2:30 — WHAT THE ORIGINAL DOES
- Who built it: Sachin Sharma / elementalsouls — credit on screen, link in
  description. This is a fork, not my original work.
- The 4 layers: Think (methodology) → Hunt (58 hunt-* skills from 681
  disclosed reports) → Perimeter (M365/Entra, Okta, vCenter chains) →
  Ship it (7-Question Gate, VRT severity, evidence hygiene).
- Quick scroll through `skills/` — 83 folders — and one skill file
  (`hunt-xss` / `triage-validation`) to show the depth.
- The `cbh` CLI: `cbh --help`, recon → surface → classify → triage → report.

### 2:30–4:30 — WHAT'S NEW IN THE ULTRON PRIME VERSION
- Rebrand: black/red/silver theme, channel logo + banner in `assets/`,
  name stays ULTRON PRIME.
- NEW 1 — `ultron` CLI: show the ASCII banner, `ultron skills` (86 skills).
- NEW 2 — Auto-triage scorer: VRT-aware score, CVSS-like 0–10, confidence,
  duplicate detection, 7-Question Gate enforcement.
- NEW 3 — HTML reports: single-file, ULTRON PRIME theme, authorization
  statement on every report.
- NEW 4 — Three new skills: `ultron-protocol` (own-model prompt testing),
  `ultron-bypass-lab` (self-hosted / local-model lab), `ultron-override`
  (model-release teardown checklist).
- NEW 5 — One-click installer for Claude Code / Codex / OpenCode / Hermes /
  AntiGravity + the `ultron` CLI.

### 4:30–7:30 — LIVE DEMO (screen recording, terminal)
1. `python3 ultron.py scan --target example.com --scope scope.example.txt`
   → in scope, OK. Then `--target evil.com` → KILL, refused. (Scope gate!)
2. `python3 ultron.py triage sample-findings.json`
   → Stored XSS 7.3 High REPORT-READY; IDOR 8.0 High REPORT-READY;
   clickjacking 0.8 Low KILL — and explain *why* the third one dies
   (no evidence, no demonstrated impact, fails Q1/Q2/Q4/Q6).
3. `python3 ultron.py report sample-findings.json --out sample-report.html`
   → open `sample-report.html` in the browser: black/red theme, severity
   badges, evidence, gate checklist, authorization statement.
4. `python3 -m unittest tests.test_ultron_triage -v` → 10 tests, OK.
   (Proof the new code actually works — don't just claim it.)
5. One-click install: `bash scripts/install-ultron.sh --all` (show it
   completing; don't dwell on the output scroll).

### 7:30–8:30 — SCOPE & HONEST LIMITS
- Say it plainly: authorized testing only — bug bounty in-scope assets,
  authorized pentests, your own lab. No unauthorized targets, no C2,
  no internal AD takeover, no persistence — same limits as the original.
- What this fork does NOT do: it doesn't find bugs for you, it doesn't
  bypass authorization, and a triage score is not a payout — the program
  decides severity.
- The sample findings are fictional (`example.com`) — the demo proves the
  pipeline, not a real hack.

### 8:30–9:30 — OUTRO + LINKS
- Recap in one line: "83 skills in, 3 new ULTRON skills, a real CLI with
  triage + reports — and it kills bad findings before you embarrass
  yourself with them."
- Links (description + pinned comment):
  - ULTRON PRIME BugHunter repo (this fork)
  - Original: github.com/elementalsouls/Claude-BugHunter
  - ULTRON PRIME channel: youtube.com/@ultronprime_zero
- Call to action: "Next video — I take one of these 86 skills and rebuild
  a real open-source app with it. Subscribe so you don't miss it."

---

## B-roll / graphics checklist
- [ ] GitHub trending screenshot (Nov 17, 2026 — Claude-BugHunter #1)
- [ ] Channel logo + banner (assets/ultron-prime-logo.png, ultron-prime-banner.png)
- [ ] Terminal recordings for each demo step (record clean, no typos)
- [ ] Browser shot of sample-report.html (full page)
- [ ] Lower-third: "AUTHORIZED TESTING ONLY — sample data" during every demo

## Pre-publish checks
- [ ] No real target, domain, credential, or IP visible in any frame
- [ ] Original author credited in video + description (Sachin Sharma / elementalsouls)
- [ ] License note in description (MIT code / CC BY 4.0 content)
- [ ] "SAMPLE — fictional findings" caption on the demo section
- [ ] Links verified (fork repo, original repo, channel)
