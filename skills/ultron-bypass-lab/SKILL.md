---
name: ultron-bypass-lab
description: ULTRON PRIME BYPASS LAB — local-model and self-hosted setup testing, authorized only. Run models locally (Ollama / llama.cpp / vLLM), self-host open-source apps, compare the cheap self-hosted route with the expensive managed one, and test YOUR OWN setup for misconfiguration. Use only on hardware and networks you own or have written authorization to assess. Never to unlock, root, or bypass controls on devices or services you do not own.
sources: ultron_prime
---

# ULTRON BYPASS LAB — LOCAL & SELF-HOSTED TESTING

> **AUTHORIZED USE ONLY.** Everything in this skill runs on hardware,
> networks, and accounts **you own**, or targets you have **written
> authorization** to assess. A "bypass" here means: the cheap self-hosted
> way to do the expensive thing, tested on your own setup — not unlocking,
> rooting, or circumventing controls on someone else's device or service.
>
> If a step would touch a device, account, or network you do not own —
> stop. That is not this skill.

---

## AUTHORIZATION CHECKLIST — complete BEFORE any test

- [ ] The hardware / VM / cloud account is mine (or named in a signed RoE)
- [ ] No other user's data lives on the test machine
- [ ] Network tests stay on my own LAN / VPC — no scanning of neighbours or public ranges
- [ ] Any credentials used are test-only, rotated afterwards, never production secrets

**Any box unchecked → STOP.**

---

## LAB SETUP (your own machine)

### 1. Local model, cheapest working route

1. Install Ollama (or llama.cpp) on your own machine.
2. Pull a small open model (e.g. a 3–8B instruct model) and run it fully offline.
3. Record: RAM used, tokens/sec, quality on 5 fixed prompts vs. the
   managed API you were paying for.
4. **The video-worthy result is the comparison table**, not the install:
   cost/month managed vs. cost/month self-hosted, quality delta, what breaks.

### 2. Self-host the open-source app (the ULTRON PRIME rebuild loop)

1. Clone the open-source project into a disposable VM / container.
2. Run it exactly as documented first — screenshot the stock version.
3. Then apply your ULTRON PRIME changes (theme, extra features).
4. Self-host the result behind localhost only; expose it publicly only
   after you have checked: no default credentials, no open ports beyond
   the app, no debug mode, no secrets in the repo.

### 3. Misconfiguration checks on YOUR OWN setup

Run these against your own deployment only:

- **Default credentials:** try the documented defaults on your own instance.
  If they still work, that is a finding — rotate them and re-test.
- **Exposed admin / debug endpoints:** list the app's routes; any `/admin`,
  `/debug`, `/metrics` reachable without auth on your own host is a finding.
- **Secrets in repo:** `git log --all -p | grep -iE 'api[_-]?key|password|secret'`
  on your own repo. Any hit = rotate + purge history.
- **Open ports:** `ss -tulpn` on your own host; every listening port must
  have a reason. Close or firewall the rest.

### 4. What "bypass" means here — and what it does NOT mean

| In scope (your own setup) | OUT of scope — never |
|---|---|
| Self-hosting instead of paying for managed | Unlocking / rooting a device you don't own |
| Local model instead of a paid API | Bypassing DRM, licensing, or account controls |
| Finding default creds on your own instance | Bypassing auth on someone else's service |
| Documenting the cheap route with numbers | Evasion / stealth guidance |

---

## REPORTING

A BYPASS LAB finding is reportable only if it passes the 7-Question Gate
(`triage-validation`) and the target is yours or explicitly in scope.
Run `ultron triage` on the finding before writing it up. Include the
comparison numbers (cost, speed, quality) — that is the evidence.
