"""Unit tests for gradebook.py
Run with:  python -m unittest test_gradebook -v
"""

import os
import tempfile
import unittest

import gradebook


def make_students():
    return {
        "1": {"name": "Asha", "marks": {s: 80 for s in gradebook.SUBJECTS}},
        "2": {"name": "Ravi", "marks": {s: 60 for s in gradebook.SUBJECTS}},
        "3": {"name": "Meena", "marks": {s: 90 for s in gradebook.SUBJECTS}},
    }


class TestCalculations(unittest.TestCase):

    def test_total_and_average(self):
        total, avg = gradebook.calculate_total_average({"a": 50, "b": 70})
        self.assertEqual(total, 120)
        self.assertEqual(avg, 60)

    def test_grade_boundaries(self):
        self.assertEqual(gradebook.calculate_grade(95), "A+")
        self.assertEqual(gradebook.calculate_grade(90), "A+")
        self.assertEqual(gradebook.calculate_grade(89.99), "A")
        self.assertEqual(gradebook.calculate_grade(50), "D")
        self.assertEqual(gradebook.calculate_grade(49.9), "F")
        self.assertEqual(gradebook.calculate_grade(0), "F")

    def test_result_pass_and_fail(self):
        good = {s: 70 for s in gradebook.SUBJECTS}
        bad = dict(good)
        bad["Maths"] = 39            # one subject below pass mark
        self.assertEqual(gradebook.get_result(good), "PASS")
        self.assertEqual(gradebook.get_result(bad), "FAIL")

    def test_name_validation(self):
        self.assertTrue(gradebook.is_valid_name("Asha Nair"))
        self.assertFalse(gradebook.is_valid_name(""))
        self.assertFalse(gradebook.is_valid_name("   "))
        self.assertFalse(gradebook.is_valid_name("R2D2"))


class TestRankingAndSummary(unittest.TestCase):

    def test_ranking_order(self):
        ranked = gradebook.rank_students(make_students())
        self.assertEqual([r["name"] for r in ranked], ["Meena", "Asha", "Ravi"])
        self.assertEqual([r["rank"] for r in ranked], [1, 2, 3])

    def test_tie_gets_same_rank(self):
        students = make_students()
        students["4"] = {"name": "Kiran", "marks": {s: 80 for s in gradebook.SUBJECTS}}
        ranked = gradebook.rank_students(students)
        ranks = {r["name"]: r["rank"] for r in ranked}
        self.assertEqual(ranks["Asha"], ranks["Kiran"])
        self.assertEqual(ranks["Ravi"], 4)

    def test_class_summary(self):
        summary = gradebook.class_summary(make_students())
        self.assertEqual(summary["count"], 3)
        self.assertAlmostEqual(summary["mean"], 76.6667, places=3)
        self.assertEqual(summary["median"], 80)
        self.assertEqual(summary["topper"]["name"], "Meena")
        self.assertEqual(summary["pass_percent"], 100)

    def test_summary_empty_and_single(self):
        self.assertIsNone(gradebook.class_summary({}))
        one = {"1": make_students()["1"]}
        self.assertEqual(gradebook.class_summary(one)["std_dev"], 0.0)

    def test_subject_stats(self):
        stats = gradebook.subject_stats(make_students())
        self.assertEqual(stats["Python"]["highest"], 90)
        self.assertEqual(stats["Python"]["lowest"], 60)


class TestFileHandling(unittest.TestCase):

    def test_save_and_load(self):
        students = make_students()
        folder = tempfile.mkdtemp()
        path = os.path.join(folder, "test.json")
        gradebook.save_data(students, path)
        self.assertEqual(gradebook.load_data(path), students)

    def test_missing_file_gives_empty_dict(self):
        self.assertEqual(gradebook.load_data("no_such_file.json"), {})

    def test_damaged_file_gives_empty_dict(self):
        folder = tempfile.mkdtemp()
        path = os.path.join(folder, "bad.json")
        with open(path, "w") as f:
            f.write("{ this is not json")
        self.assertEqual(gradebook.load_data(path), {})


if __name__ == "__main__":
    unittest.main()
