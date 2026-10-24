import unittest

from src.maintainerkit import fallback_triage, render_comment, safe_text, similarity


class MaintainerKitTests(unittest.TestCase):
    def test_security_issues_get_security_category(self):
        issue = {"number": 4, "title": "Security vulnerability: leaked credential", "body": "Credential leak"}
        result = fallback_triage(issue, ["security", "bug"], [])
        self.assertEqual(result["category"], "security")
        self.assertIn("security", result["recommended_labels"])

    def test_bug_issue_gets_bug_category(self):
        issue = {"number": 5, "title": "Crash when opening file", "body": "The app crashes."}
        result = fallback_triage(issue, ["bug", "documentation"], [])
        self.assertEqual(result["category"], "bug")
        self.assertEqual(result["recommended_labels"], ["bug"])

    def test_only_existing_labels_are_recommended(self):
        issue = {"number": 5, "title": "Crash when opening file", "body": "The app crashes."}
        result = fallback_triage(issue, ["priority: low"], [])
        self.assertEqual(result["recommended_labels"], [])

    def test_similar_titles_score_higher(self):
        same = similarity("Crash when saving a project", "Crash when saving project")
        different = similarity("Crash when saving a project", "Add dark mode theme")
        self.assertGreater(same, different)

    def test_duplicate_candidates_are_limited_and_exclude_self(self):
        issue = {"number": 1, "title": "Crash when saving project", "body": "saving crashes"}
        candidates = [
            {"number": 1, "title": "Crash when saving project"},
            {"number": 2, "title": "Crash when saving project file"},
            {"number": 3, "title": "Add a new color theme"},
        ]
        result = fallback_triage(issue, [], candidates)
        self.assertNotIn(1, result["duplicate_issue_numbers"])
        self.assertIn(2, result["duplicate_issue_numbers"])

    def test_rendered_comment_contains_idempotency_marker(self):
        body = render_comment({"category": "bug", "summary": "Save failed", "recommended_labels": [],
                              "clarification_question": "Steps to reproduce?", "duplicate_issue_numbers": [12]},
                             "sample/project", "test mode")
        self.assertIn("<!-- maintainerkit:triage -->", body)
        self.assertIn("https://github.com/sample/project/issues/12", body)

    def test_safe_text_limits_and_escapes_html(self):
        self.assertEqual(safe_text("<script>alert(1)</script>"), "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertLessEqual(len(safe_text("x" * 100, 10)), 10)


if __name__ == "__main__":
    unittest.main()
