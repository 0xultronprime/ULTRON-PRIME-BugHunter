"""ULTRON PRIME BugHunter — single-file HTML report generator.

Black / red / silver ULTRON PRIME theme. Stdlib only. The report always
carries a scope + authorization statement: every finding in it must come
from authorized testing only.
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone

from .triage import score_finding

VERSION = "1.0.0"

SEV_COLORS = {
    "Critical": "#ff2a2a",
    "High": "#ff6b1a",
    "Medium": "#ffcc00",
    "Low": "#3ec6ff",
    "Informational": "#9aa3ad",
}
VERDICT_COLORS = {"REPORT-READY": "#22c55e", "DOWNGRADE": "#ffcc00", "KILL": "#ff2a2a"}

AUTH_STATEMENT = (
    "AUTHORIZATION STATEMENT — All findings in this report were produced during "
    "authorized testing only: assets owned by the tester, in-scope bug-bounty "
    "targets, an authorized penetration test under a signed Rules of Engagement, "
    "or a lab / CTF target. No unauthorized target was tested. If a finding "
    "required going beyond authorized scope to prove impact, it was downgraded "
    "or killed — never exploited further."
)


def _esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def build_report(findings: list, target: str = "", program: str = "") -> str:
    """Return a complete standalone HTML report string."""
    seen: dict[str, str] = {}
    scored = [score_finding(f, seen) for f in findings]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    counts = {
        v: sum(1 for r in scored if r.verdict == v)
        for v in ("REPORT-READY", "DOWNGRADE", "KILL")
    }

    rows = []
    for finding, result in zip(findings, scored):
        sev = result.severity
        sev_color = SEV_COLORS.get(sev, "#9aa3ad")
        verdict_color = VERDICT_COLORS.get(result.verdict, "#9aa3ad")
        evidence = finding.get("evidence", "")
        if isinstance(evidence, list):
            evidence_html = "".join(f"<li>{_esc(e)}</li>" for e in evidence)
            evidence_html = f"<ul>{evidence_html}</ul>" if evidence_html else "<em>No evidence supplied.</em>"
        else:
            evidence_html = f"<p>{_esc(evidence)}</p>" if str(evidence).strip() else "<em>No evidence supplied.</em>"
        gate_html = "".join(
            f"<li class=\"{'pass' if g['passed'] else 'fail'}\">"
            f"{'&#10003;' if g['passed'] else '&#10007;'} {g['question']}: {_esc(g['text'])}</li>"
            for g in result.gate
        )
        reasons_html = "".join(f"<li>{_esc(r)}</li>" for r in result.reasons) or "<li>No notes.</li>"
        rows.append(f"""
        <section class="finding">
          <h2>{_esc(result.title)}</h2>
          <p class="meta">
            <span class="badge" style="background:{sev_color}">{sev} &middot; {result.score:.1f}/10</span>
            <span class="badge verdict" style="background:{verdict_color}">{result.verdict}</span>
            <span class="tag">{_esc(result.vrt_category)}</span>
            <span class="tag">Confidence: {result.confidence}</span>
            <span class="tag">Target: {_esc(finding.get('target', target))}</span>
          </p>
          <h3>Evidence</h3>
          {evidence_html}
          <h3>Impact</h3>
          <p>{_esc(finding.get('impact', 'Not stated.'))}</p>
          <h3>7-Question Gate</h3>
          <ul class="gate">{gate_html}</ul>
          <h3>Triage notes</h3>
          <ul>{reasons_html}</ul>
        </section>""")

    body = "\n".join(rows) if rows else "<p>No findings supplied.</p>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ULTRON PRIME BugHunter — Report{(' — ' + _esc(target)) if target else ''}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #050505; color: #e8e8e8; font-family: 'Segoe UI', Arial, sans-serif; }}
  header {{ background: linear-gradient(135deg, #0a0a0a 0%, #1a0505 55%, #2b0202 100%); border-bottom: 3px solid #ff2a2a; padding: 32px 24px; }}
  header h1 {{ margin: 0; font-size: 34px; letter-spacing: 2px; color: #f2f2f2; }}
  header h1 span {{ color: #ff2a2a; }}
  header p {{ color: #c0c0c0; margin: 6px 0 0; }}
  main {{ max-width: 960px; margin: 0 auto; padding: 24px; }}
  .summary {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 0 0 20px; }}
  .stat {{ background: #111; border: 1px solid #333; border-left: 4px solid #ff2a2a; padding: 12px 16px; min-width: 130px; }}
  .stat b {{ display: block; font-size: 26px; color: #fff; }}
  .auth {{ background: #160404; border: 1px solid #ff2a2a; padding: 14px 16px; font-size: 14px; line-height: 1.5; margin-bottom: 24px; }}
  .finding {{ background: #0d0d0d; border: 1px solid #2a2a2a; border-left: 4px solid #ff2a2a; padding: 18px 20px; margin-bottom: 20px; }}
  .finding h2 {{ margin: 0 0 10px; color: #fff; }}
  .finding h3 {{ color: #ff5a5a; margin: 16px 0 6px; font-size: 15px; text-transform: uppercase; letter-spacing: 1px; }}
  .badge {{ display: inline-block; color: #000; font-weight: 700; padding: 3px 10px; border-radius: 3px; margin-right: 6px; }}
  .badge.verdict {{ color: #fff; }}
  .tag {{ display: inline-block; background: #1c1c1c; border: 1px solid #444; color: #ccc; padding: 3px 8px; border-radius: 3px; margin-right: 6px; font-size: 13px; }}
  .gate li.pass {{ color: #7ee2a0; }} .gate li.fail {{ color: #ff7a7a; }}
  ul {{ line-height: 1.55; }} footer {{ text-align: center; color: #777; font-size: 13px; padding: 20px; border-top: 1px solid #222; }}
  code {{ color: #ff8a8a; }}
</style>
</head>
<body>
<header>
  <h1>ULTRON <span>PRIME</span> &mdash; BUGHUNTER REPORT</h1>
  <p>Target: {_esc(target or '—')} &middot; Program: {_esc(program or '—')} &middot; Generated: {now} &middot; ULTRON PRIME BugHunter v{VERSION}</p>
</header>
<main>
  <div class="summary">
    <div class="stat"><b>{len(scored)}</b>findings triaged</div>
    <div class="stat"><b>{counts['REPORT-READY']}</b>report-ready</div>
    <div class="stat"><b>{counts['DOWNGRADE']}</b>downgrade</div>
    <div class="stat"><b>{counts['KILL']}</b>killed</div>
  </div>
  <div class="auth"><strong>&#9888; {_esc(AUTH_STATEMENT)}</strong></div>
  {body}
</main>
<footer>ULTRON PRIME BugHunter &middot; Fork of elementalsouls/Claude-BugHunter (MIT / CC BY 4.0) &middot; Authorized testing only.</footer>
</body>
</html>
"""


def report_from_file(findings_path: str, out_path: str, target: str = "", program: str = "") -> str:
    with open(findings_path, encoding="utf-8") as fh:
        data = json.load(fh)
    findings = data.get("findings", data) if isinstance(data, dict) else data
    if not target and isinstance(data, dict):
        target = str(data.get("target", ""))
    if not program and isinstance(data, dict):
        program = str(data.get("program", ""))
    rendered = build_report(findings, target=target, program=program)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(rendered)
    return out_path
