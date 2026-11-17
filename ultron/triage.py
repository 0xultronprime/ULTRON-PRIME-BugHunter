"""ULTRON PRIME BugHunter — auto-triage scorer.

VRT-aware severity scoring for findings, CVSS-like 0-10 score, confidence,
duplicate detection, and the 7-Question Gate from the original
`triage-validation` skill. Python stdlib only.

AUTHORIZED USE ONLY: findings must come from assets you own or have written
authorization to assess (bug bounty in-scope assets, authorized pentests,
CTF / lab targets). A finding that fails the gate is KILLED, never upgraded.
No feature here bypasses authorization, attacks unauthorized targets, or
evades detection.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

VERSION = "1.0.0"

# --- VRT-style base severity by finding type (CVSS-like 0-10 anchor) -------
# Anchors mirror the original triage-validation severity guide. The scorer
# then adjusts for evidence strength, exploitability and impact.
BASE_SCORES = {
    "rce": 9.8,
    "sqli": 9.0,
    "auth-bypass": 9.0,
    "idor": 7.5,
    "ssrf": 8.5,
    "xss-stored": 7.0,
    "xss-reflected": 6.1,
    "csrf": 6.5,
    "ssti": 9.0,
    "xxe": 8.0,
    "deserialization": 9.0,
    "jwt": 7.5,
    "oauth": 8.0,
    "file-upload": 8.5,
    "lfi": 7.5,
    "open-redirect": 4.5,
    "clickjacking": 4.3,
    "info-disclosure": 5.3,
    "misconfig": 5.0,
    "prompt-injection": 6.5,
    "llm-output": 5.0,
    "other": 5.0,
}

# VRT category label per type (Bugcrowd VRT-style buckets).
VRT_CATEGORY = {
    "rce": "Server-Side Code Execution",
    "sqli": "SQL Injection",
    "auth-bypass": "Broken Authentication and Session Management",
    "idor": "Broken Access Control",
    "ssrf": "Server-Side Request Forgery (SSRF)",
    "xss-stored": "Cross-Site Scripting (XSS) — Stored",
    "xss-reflected": "Cross-Site Scripting (XSS) — Reflected",
    "csrf": "Cross-Site Request Forgery (CSRF)",
    "ssti": "Server-Side Template Injection",
    "xxe": "XML External Entity (XXE)",
    "deserialization": "Insecure Deserialization",
    "jwt": "Broken Authentication and Session Management",
    "oauth": "Broken Authentication and Session Management",
    "file-upload": "Unrestricted File Upload",
    "lfi": "Local File Inclusion (LFI)",
    "open-redirect": "Open Redirect",
    "clickjacking": "Clickjacking",
    "info-disclosure": "Sensitive Data Exposure",
    "misconfig": "Security Misconfiguration",
    "prompt-injection": "AI / LLM — Prompt Injection",
    "llm-output": "AI / LLM — Insecure Output Handling",
    "other": "Other",
}

SEVERITY_BANDS = [(9.0, "Critical"), (7.0, "High"), (4.0, "Medium"), (0.1, "Low"), (0.0, "Informational")]

# The 7-Question Gate (from skills/triage-validation/SKILL.md).
# One wrong answer = KILL the finding. Order matters.
GATE_QUESTIONS = [
    ("Q1", "Can an attacker use this RIGHT NOW, step by step? (reproducible request + observable result)"),
    ("Q2", "Is the impact on the program's accepted impact list? (not a listed exclusion)"),
    ("Q3", "Is the root cause in an in-scope asset? (in-scope domain, production unless stated)"),
    ("Q4", "Is the impact real, not theoretical? (data read/modified/deleted, account or money affected)"),
    ("Q5", "Is this a duplicate of a known / already-reported issue?"),
    ("Q6", "Is the evidence complete and clean? (repro steps, request/response, no other-user PII)"),
    ("Q7", "Is the report title accurate and the severity honest? (no inflated impact)"),
]


def severity_for(score: float) -> str:
    for threshold, label in SEVERITY_BANDS:
        if score >= threshold:
            return label
    return "Informational"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def finding_fingerprint(finding: dict) -> str:
    """Stable duplicate key: type + target + normalized title/endpoint."""
    parts = [
        _norm(str(finding.get("type", "other"))),
        _norm(str(finding.get("target", ""))),
        _norm(str(finding.get("endpoint", finding.get("url", "")))),
        _norm(str(finding.get("title", "")))[:120],
    ]
    return hashlib.sha256(" | ".join(parts).encode("utf-8")).hexdigest()[:16]


@dataclass
class TriageResult:
    title: str
    finding_type: str
    vrt_category: str
    score: float
    severity: str
    confidence: str  # High / Medium / Low
    verdict: str     # REPORT-READY / DOWNGRADE / KILL
    gate: list       # [{question, answer, passed}]
    gate_passed: bool
    reasons: list = field(default_factory=list)
    fingerprint: str = ""
    duplicate_of: str | None = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "type": self.finding_type,
            "vrt_category": self.vrt_category,
            "score": self.score,
            "severity": self.severity,
            "confidence": self.confidence,
            "verdict": self.verdict,
            "gate_passed": self.gate_passed,
            "gate": self.gate,
            "reasons": self.reasons,
            "fingerprint": self.fingerprint,
            "duplicate_of": self.duplicate_of,
        }


def score_finding(finding: dict, seen_fingerprints: dict | None = None) -> TriageResult:
    """Score one finding dict and enforce the 7-Question Gate.

    Expected finding keys (all optional except title/type):
      title, type, target, endpoint/url, evidence (str or list),
      impact (str), in_scope (bool), reproducible (bool),
      accepted_impact (bool), duplicate (bool),
      gate_answers (dict like {"Q1": true, ...}) — explicit answers win.
    """
    ftype = _norm(str(finding.get("type", "other"))).replace(" ", "-")
    if ftype not in BASE_SCORES:
        ftype = "other"
    base = BASE_SCORES[ftype]
    reasons: list[str] = []

    # --- Evidence / exploitability adjustments -------------------------
    evidence = finding.get("evidence", "")
    if isinstance(evidence, list):
        evidence_text = "\n".join(str(e) for e in evidence)
        evidence_items = len(evidence)
    else:
        evidence_text = str(evidence or "")
        evidence_items = 1 if evidence_text.strip() else 0
    score = base
    if evidence_items >= 2 and len(evidence_text) > 80:
        score += 0.3
        reasons.append("Strong evidence: multiple evidence items supplied (+0.3).")
    elif evidence_items == 0:
        score -= 1.5
        reasons.append("No evidence supplied (-1.5); a finding without proof cannot be High/Critical.")
    if finding.get("reproducible") is False:
        score -= 1.0
        reasons.append("Not reproducible as described (-1.0).")
    impact = _norm(str(finding.get("impact", "")))
    if any(w in impact for w in ("account takeover", "ato", "money", "payment", "pii", "data exfil", "admin")):
        score += 0.2
        reasons.append("High-value impact claimed (+0.2).")
    if "theoretical" in impact or "no impact" in impact:
        score -= 1.0
        reasons.append("Impact described as theoretical / none (-1.0).")
    score = max(0.0, min(10.0, round(score, 1)))

    # --- Confidence ------------------------------------------------------
    if evidence_items >= 2 and finding.get("reproducible") is not False:
        confidence = "High"
    elif evidence_items >= 1:
        confidence = "Medium"
    else:
        confidence = "Low"

    # --- 7-Question Gate --------------------------------------------------
    answers = finding.get("gate_answers") or {}
    gate: list[dict] = []
    gate_passed = True
    # Default inference when no explicit answers are given.
    inferred = {
        "Q1": finding.get("reproducible", evidence_items > 0),
        "Q2": finding.get("accepted_impact", True),
        "Q3": finding.get("in_scope", True),
        "Q4": "theoretical" not in impact and "no impact" not in impact,
        "Q5": not finding.get("duplicate", False),
        "Q6": evidence_items > 0,
        "Q7": bool(str(finding.get("title", "")).strip()),
    }
    for qid, question in GATE_QUESTIONS:
        ans = answers.get(qid, inferred[qid])
        passed = bool(ans)
        gate.append({"question": qid, "text": question, "answer": passed, "passed": passed})
        if not passed:
            gate_passed = False
            reasons.append(f"7-Question Gate FAILED at {qid}: {question}")

    # --- Duplicate detection ----------------------------------------------
    fp = finding_fingerprint(finding)
    duplicate_of = None
    if seen_fingerprints is not None:
        if fp in seen_fingerprints:
            duplicate_of = seen_fingerprints[fp]
            gate_passed = False
            reasons.append(f"Duplicate of '{duplicate_of}' (same type/target/endpoint/title).")
            for g in gate:
                if g["question"] == "Q5":
                    g["answer"] = False
                    g["passed"] = False
        else:
            seen_fingerprints[fp] = str(finding.get("title", ""))

    # --- Verdict ------------------------------------------------------------
    if not gate_passed:
        verdict = "KILL"
    elif confidence == "Low" or score < 4.0:
        verdict = "DOWNGRADE"
        reasons.append("Low confidence or sub-Medium score — downgrade, gather more evidence before submitting.")
    else:
        verdict = "REPORT-READY"

    return TriageResult(
        title=str(finding.get("title", "Untitled finding")),
        finding_type=ftype,
        vrt_category=VRT_CATEGORY[ftype],
        score=score,
        severity=severity_for(score),
        confidence=confidence,
        verdict=verdict,
        gate=gate,
        gate_passed=gate_passed,
        reasons=reasons,
        fingerprint=fp,
        duplicate_of=duplicate_of,
    )


def triage_file(path: str) -> dict:
    """Load findings JSON (list, or {"findings": [...]}) and triage all."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    findings = data.get("findings", data) if isinstance(data, dict) else data
    if not isinstance(findings, list):
        raise ValueError("findings file must be a JSON list or an object with a 'findings' list")
    seen: dict[str, str] = {}
    results = [score_finding(f, seen) for f in findings]
    summary = {
        "total": len(results),
        "report_ready": sum(1 for r in results if r.verdict == "REPORT-READY"),
        "downgrade": sum(1 for r in results if r.verdict == "DOWNGRADE"),
        "kill": sum(1 for r in results if r.verdict == "KILL"),
    }
    return {"summary": summary, "results": [r.to_dict() for r in results]}
