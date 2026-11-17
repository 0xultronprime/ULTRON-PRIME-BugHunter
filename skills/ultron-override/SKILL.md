---
name: ultron-override
description: ULTRON PRIME OVERRIDE — model-release teardown checklist. When a major model drops, record what actually changed, what holds up, and what got patched — with numbers, not hype. Use for your own evaluations and authorized comparisons only. No hype, no unverified claims.
sources: ultron_prime
---

# ULTRON OVERRIDE — MODEL-RELEASE TEARDOWN CHECKLIST

> **No hype, just what changed and whether it holds up.**
>
> When a major model drops, the internet fills with hot takes in an hour.
> This skill is the slow version: the same fixed test set, run before and
> after, written down. If you did not measure it, do not claim it.
>
> **Authorized use only:** evaluate models you have legitimate access to
> (your own API key, your own deployment, a public demo). Do not use
> someone else's account, key, or quota.

---

## TEARDOWN CHECKLIST — run the same set on old vs. new

### 1. The fixed test set (write it BEFORE the release)

Keep a frozen set of 10 prompts you reuse for every release:

- 3 coding tasks (easy / medium / hard — same repo, same files)
- 2 reasoning tasks (multi-step, verifiable answer)
- 2 refusal tests (disallowed request, borderline request)
- 2 instruction-following tests (exact format, exact constraints)
- 1 long-context task (same document, same questions)

**Rule:** if a prompt changes between runs, the comparison is void.
Freeze the set, then run it.

### 2. What to record per model

| Field | Old model | New model |
|---|---|---|
| Model + version string | | |
| Date run | | |
| Coding 3/3 correct? | _/3 | _/3 |
| Reasoning 2/2 correct? | _/2 | _/2 |
| Refusals correct 2/2? | _/2 | _/2 |
| Instruction-following 2/2? | _/2 | _/2 |
| Long-context correct? | y/n | y/n |
| Avg latency (s) | | |
| Cost per 1k tokens (or $/run) | | |
| Notable failure (quote it) | | |

### 3. "What got patched" — re-run last release's failures

Take the exact prompts that broke the previous model and re-run them:

- **Still broken →** say so. The headline is "still broken".
- **Fixed →** say what changed (refusal, correct answer, different failure).
- **New failure →** that is the real story: a regression. Quote it.

### 4. What changed — the verdict format

Write the verdict in this shape, nothing else:

- **Better at:** [list, with scores]
- **Worse at:** [list, with scores]
- **Same:** [list]
- **Still broken:** [list]
- **Worth switching?** Yes / No / Only for [use case] — with the reason
  in one sentence.

### 5. Anti-hype rules

- Never claim a win rate from fewer than 10 prompts.
- Never quote a benchmark you did not run yourself without naming its source.
- If the vendor's benchmark and your test disagree, trust your test and say so.
- If something gets patched after you film, add a pinned comment / caption
  correction — do not silently re-upload.

---

## REPORTING

An OVERRIDE teardown is not a vulnerability report — it is an evaluation.
Publish the full prompt set and the raw scores with the video so viewers
can reproduce it. If a teardown surfaces a real security issue in a model
you have authorization to test, report it through the vendor's channel
first, then run it through `triage-validation` and `ultron triage`.
