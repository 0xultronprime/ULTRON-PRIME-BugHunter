"""Unit tests for ultron.triage — VRT scoring, gate, duplicates. Stdlib only."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultron.triage import (  # noqa: E402
    GATE_QUESTIONS,
    finding_fingerprint,
    score_finding,
    severity_for,
    triage_file,
)

SAMPLE = {
    "title": "Stored XSS in profile bio",
    "type": "xss-stored",
    "target": "example.com",
    "endpoint": "/profile/bio",
    "evidence": ["POST /profile/bio with <script>alert(1)</script>", "Response reflects payload on victim profile page"],
    "impact": "Stored XSS executes for every user viewing the profile",
    "reproducible": True,
    "in_scope": True,
    "accepted_impact": True,
}


class TestSeverity(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(severity_for(9.8), "Critical")
        self.assertEqual(severity_for(7.5), "High")
        self.assertEqual(severity_for(5.0), "Medium")
        self.assertEqual(severity_for(2.0), "Low")
        self.assertEqual(severity_for(0.0), "Informational")

    def test_gate_has_seven_questions(self):
        self.assertEqual(len(GATE_QUESTIONS), 7)


class TestScoring(unittest.TestCase):
    def test_good_finding_is_report_ready(self):
        r = score_finding(dict(SAMPLE))
        self.assertEqual(r.verdict, "REPORT-READY")
        self.assertTrue(r.gate_passed)
        self.assertEqual(r.severity, "High")
        self.assertEqual(r.confidence, "High")
        self.assertGreaterEqual(r.score, 7.0)

    def test_no_evidence_downgrades(self):
        f = dict(SAMPLE, evidence=[])
        r = score_finding(f)
        self.assertIn(r.verdict, ("DOWNGRADE", "KILL"))
        self.assertEqual(r.confidence, "Low")

    def test_out_of_scope_kills(self):
        f = dict(SAMPLE, in_scope=False)
        r = score_finding(f)
        self.assertEqual(r.verdict, "KILL")
        self.assertFalse(r.gate_passed)

    def test_explicit_gate_answer_kills(self):
        f = dict(SAMPLE, gate_answers={"Q1": False})
        r = score_finding(f)
        self.assertEqual(r.verdict, "KILL")

    def test_unknown_type_falls_back(self):
        f = dict(SAMPLE, type="something-made-up")
        r = score_finding(f)
        self.assertEqual(r.finding_type, "other")
        self.assertEqual(r.vrt_category, "Other")


class TestDuplicates(unittest.TestCase):
    def test_same_finding_same_fingerprint(self):
        self.assertEqual(finding_fingerprint(SAMPLE), finding_fingerprint(dict(SAMPLE)))

    def test_duplicate_second_finding_killed(self):
        seen: dict = {}
        first = score_finding(dict(SAMPLE), seen)
        second = score_finding(dict(SAMPLE), seen)
        self.assertEqual(first.verdict, "REPORT-READY")
        self.assertEqual(second.verdict, "KILL")
        self.assertIsNotNone(second.duplicate_of)


class TestTriageFile(unittest.TestCase):
    def test_sample_file(self):
        sample = Path(__file__).resolve().parent.parent / "sample-findings.json"
        result = triage_file(str(sample))
        self.assertEqual(result["summary"]["total"], 3)
        self.assertEqual(result["summary"]["report_ready"], 2)
        self.assertEqual(result["summary"]["kill"], 1)


if __name__ == "__main__":
    unittest.main()
