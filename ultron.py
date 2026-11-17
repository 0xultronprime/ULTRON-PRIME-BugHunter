"""ULTRON PRIME BugHunter — `ultron` CLI.

Commands:
  ultron scan --target <domain> --scope <file>   authorized-scope recon checklist (no network scan; see scope file)
  ultron triage <findings.json>                  VRT-aware scoring + 7-Question Gate
  ultron report <findings.json> --out report.html  single-file ULTRON PRIME HTML report
  ultron skills                                  list all skills (83 original + 3 ULTRON PRIME)
  ultron version

Stdlib only. AUTHORIZED USE ONLY — see README.md / SECURITY.md.
The `cbh` CLI from the original project still works unchanged.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

import ultron.report as report_mod  # noqa: E402
import ultron.triage as triage_mod  # noqa: E402

VERSION = "1.0.0-ultron"
BANNER = r"""
\033[1;31m██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗\033[0m
\033[1;37m██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║\033[0m
\033[1;31m██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║\033[0m
\033[1;37m██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║\033[0m
\033[1;31m╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║\033[0m
\033[1;37m ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝\033[0m
\033[1;31m  P R I M E  —  B U G H U N T E R  v1.0.0\033[0m
\033[0;37m  Fork of elementalsouls/Claude-BugHunter · Authorized testing only.\033[0m
"""

PLAIN_BANNER = """
██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗
██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║
██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║
██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║
╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
  P R I M E  —  B U G H U N T E R  v1.0.0
  Fork of elementalsouls/Claude-BugHunter · Authorized testing only.
"""


def print_banner() -> None:
    print(BANNER if sys.stdout.isatty() else PLAIN_BANNER)


def list_skills() -> list[dict]:
    """Read every skills/*/SKILL.md frontmatter name + description."""
    skills_dir = REPO_ROOT / "skills"
    out = []
    for skill_dir in sorted(skills_dir.iterdir()) if skills_dir.is_dir() else []:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue
        name = skill_dir.name
        desc = ""
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---"):
            front = text.split("---", 2)[1]
            for line in front.splitlines():
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
        out.append({"name": name, "description": desc, "path": str(skill_dir)})
    return out


def cmd_scan(args) -> int:
    """Authorized-scope checklist. Deliberately NO network scanning here:
    the original `cbh recon` owns recon; `ultron scan` is the pre-flight
    scope/authorization gate — it refuses to proceed without a scope file
    that names the target as in-scope."""
    scope_path = Path(args.scope) if args.scope else None
    target = args.target
    print(f"[ULTRON] Pre-flight scope check for target: {target}")
    if scope_path is None or not scope_path.is_file():
        print("[!] No --scope file given or file not found.")
        print("    Create a scope file listing in-scope domains (one per line), e.g.:")
        print("      example.com")
        print("      *.example.com")
        print("    Then re-run: ultron scan --target <domain> --scope scope.txt")
        return 2
    entries = [ln.strip() for ln in scope_path.read_text(encoding="utf-8").splitlines()
               if ln.strip() and not ln.strip().startswith("#")]
    in_scope = target in entries or any(
        e.startswith("*.") and target.endswith(e[1:]) for e in entries
    )
    print(f"[ULTRON] Scope file: {scope_path} ({len(entries)} entries)")
    for e in entries:
        print(f"    - {e}")
    if not in_scope:
        print(f"[KILL] {target} is NOT in the scope file. Do not test it.")
        print("       Testing an out-of-scope target is unauthorized — stop here.")
        return 1
    print(f"[OK] {target} is in scope. Authorization confirmed by scope file.")
    print("[OK] Next: run recon with the original engine — `cbh recon <target>`")
    print("     or open the matching hunt-* skill (see `ultron skills`).")
    print("[OK] Remember: stay inside the scope file. One out-of-scope host = stop.")
    return 0


def cmd_triage(args) -> int:
    try:
        result = triage_mod.triage_file(args.findings)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[!] Could not triage {args.findings}: {exc}", file=sys.stderr)
        return 2
    s = result["summary"]
    print(f"[ULTRON] Triaged {s['total']} finding(s): "
          f"{s['report_ready']} report-ready, {s['downgrade']} downgrade, {s['kill']} kill")
    for r in result["results"]:
        print(f"\n— {r['title']}")
        print(f"  {r['severity']} {r['score']:.1f}/10 · {r['vrt_category']} · "
              f"confidence {r['confidence']} · verdict: {r['verdict']}")
        for reason in r["reasons"]:
            print(f"  · {reason}")
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\n[ULTRON] Triage JSON written to {args.out}")
    return 0 if s["kill"] == 0 else 1


def cmd_report(args) -> int:
    try:
        out = report_mod.report_from_file(args.findings, args.out)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[!] Could not build report from {args.findings}: {exc}", file=sys.stderr)
        return 2
    print(f"[ULTRON] Report written to {out}")
    print("[ULTRON] Open it in a browser — black/red ULTRON PRIME theme, "
          "findings table, severity badges, evidence + authorization statement included.")
    return 0


def cmd_skills(args) -> int:
    skills = list_skills()
    print(f"[ULTRON] {len(skills)} skills installed:")
    for s in skills:
        desc = f" — {s['description'][:110]}" if s["description"] else ""
        print(f"  • {s['name']}{desc}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ultron",
        description="ULTRON PRIME BugHunter — fork of elementalsouls/Claude-BugHunter. Authorized testing only.",
    )
    sub = parser.add_subparsers(dest="command")

    p_scan = sub.add_parser("scan", help="Pre-flight authorized-scope check for a target")
    p_scan.add_argument("--target", required=True, help="Target domain, e.g. example.com")
    p_scan.add_argument("--scope", required=True, help="Scope file: in-scope domains, one per line")
    p_scan.set_defaults(func=cmd_scan)

    p_triage = sub.add_parser("triage", help="Score findings JSON with the 7-Question Gate")
    p_triage.add_argument("findings", help="Path to findings JSON (list or {\"findings\": [...]})")
    p_triage.add_argument("--out", help="Optional path to write triage JSON")
    p_triage.set_defaults(func=cmd_triage)

    p_report = sub.add_parser("report", help="Build a single-file HTML report from findings JSON")
    p_report.add_argument("findings", help="Path to findings JSON")
    p_report.add_argument("--out", default="report.html", help="Output HTML path (default: report.html)")
    p_report.set_defaults(func=cmd_report)

    p_skills = sub.add_parser("skills", help="List all installed skills")
    p_skills.set_defaults(func=cmd_skills)

    p_version = sub.add_parser("version", help="Print version")
    p_version.set_defaults(func=lambda a: print(f"ultron {VERSION} (ULTRON PRIME BugHunter)"))

    print_banner()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
