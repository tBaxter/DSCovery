import unittest

from jobsearch.models import Company


class CompanyClassificationTest(unittest.TestCase):

    def test_leading_practice(self):
        company = Company(
            importer_name="Test Co",
            overall_score=20,
            viability_score=4,
            delivery_score=6,
            reputation_score=6,
        )
        self.assertEqual(company.classification, "leading_practice")

    def test_strong_practice(self):
        company = Company(
            importer_name="Test Co",
            overall_score=12,
            viability_score=2,
            reputation_score=4,
        )
        self.assertEqual(company.classification, "strong_practice")

    def test_watch(self):
        company = Company(
            importer_name="Test Co",
            overall_score=5,
            viability_score=6,
            reputation_score=0,
        )
        self.assertEqual(company.classification, "watch")
        self.assertIsNone(company.display_classification)

    def test_remove(self):
        company = Company(
            importer_name="Test Co",
            overall_score=1,
            viability_score=2,
            reputation_score=-2,
        )
        self.assertEqual(company.classification, "remove")
        self.assertIsNone(company.display_classification)

    def test_display_classification_for_leading_and_demonstrated(self):
        company = Company(
            importer_name="Test Co",
            overall_score=20,
            viability_score=4,
            delivery_score=6,
            reputation_score=6,
        )
        self.assertEqual(company.display_classification, "leading_practice")

        company = Company(
            importer_name="Test Co",
            overall_score=12,
            viability_score=2,
            reputation_score=4,
        )
        self.assertEqual(company.display_classification, "strong_practice")
