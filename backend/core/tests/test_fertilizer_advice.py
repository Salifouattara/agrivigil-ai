from django.test import SimpleTestCase

from core.crop_advice import get_crop_advice
from core.utils import calculate_fertilizer_detailed


class FertilizerDetailedTests(SimpleTestCase):
    def test_detailed_calc_includes_products_and_cost(self):
        result = calculate_fertilizer_detailed("cacao", "latéritique", 2.0)
        self.assertGreater(result["nitrogen_kg"], 0)
        self.assertGreater(result["total_cost_fcfa"], 0)
        self.assertTrue(len(result["products"]) >= 1)
        self.assertEqual(len(result["application_plan"]), 3)

    def test_crop_advice_returns_pesticides(self):
        advice = get_crop_advice("cacao")
        self.assertEqual(advice["crop_label"], "Cacao")
        self.assertTrue(len(advice["approved_pesticides"]) >= 1)
        self.assertTrue(len(advice["best_practices"]) >= 1)
