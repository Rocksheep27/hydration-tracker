from contextlib import redirect_stdout
from datetime import date
from io import StringIO
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import hydration_tracker as tracker


class HydrationTrackerTest(unittest.TestCase):
    def test_water_300ml_equals_300ml(self):
        result = tracker.calculate_estimated_water_ml("water", 300, "ml", 1.0)
        self.assertEqual(result, 300)

    def test_milk_250ml_uses_water_ratio(self):
        result = tracker.calculate_estimated_water_ml("beverage", 250, "ml", 0.87)
        self.assertEqual(result, 217.5)

    def test_cucumber_100g_uses_water_ratio(self):
        result = tracker.calculate_estimated_water_ml("food", 100, "g", 0.95)
        self.assertEqual(result, 95)

    def test_rice_150g_uses_water_ratio(self):
        result = tracker.calculate_estimated_water_ml("food", 150, "g", 0.60)
        self.assertEqual(result, 90)

    def test_daily_total(self):
        records = [
            {"date": "2026-06-26", "estimated_water_ml": 300},
            {"date": "2026-06-26", "estimated_water_ml": 217.5},
            {"date": "2026-06-26", "estimated_water_ml": 95},
            {"date": "2026-06-25", "estimated_water_ml": 1000},
        ]

        total = tracker.calculate_daily_total(records, "2026-06-26")

        self.assertEqual(total, 612.5)

    def test_completion_rate(self):
        rate = tracker.calculate_completion_rate(777.5, 2000)
        remaining = tracker.calculate_remaining_ml(777.5, 2000)

        self.assertEqual(rate, 38.88)
        self.assertEqual(remaining, 1222.5)

    def test_add_record_saves_to_local_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            record = tracker.create_record(
                category="water",
                name="白水",
                amount=300,
                unit="ml",
                record_date="2026-06-26",
                record_time="08:00",
            )

            tracker.add_record(record, data_file)
            records = tracker.load_records(data_file)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["estimated_water_ml"], 300)

    def test_common_beverage_uses_default_unit_and_ratio(self):
        with patch("builtins.input", side_effect=["1", "1", ""]):
            record = tracker.prompt_common_record("beverage")

        self.assertEqual(record["name"], "牛奶")
        self.assertEqual(record["amount"], 1)
        self.assertEqual(record["unit"], "杯")
        self.assertEqual(record["converted_amount"], 250)
        self.assertEqual(record["converted_unit"], "ml")
        self.assertEqual(record["water_ratio"], 0.87)
        self.assertEqual(record["estimated_water_ml"], 217.5)
        self.assertTrue(record["is_estimated"])

    def test_food_menu_maps_chinese_meal_and_uses_default_unit(self):
        with patch("builtins.input", side_effect=["1", "1", "2", ""]):
            record = tracker.prompt_common_record("food")

        self.assertEqual(record["name"], "苹果")
        self.assertEqual(record["amount"], 1)
        self.assertEqual(record["unit"], "个")
        self.assertEqual(record["converted_amount"], 180)
        self.assertEqual(record["converted_unit"], "g")
        self.assertEqual(record["meal"], "lunch")
        self.assertEqual(record["water_ratio"], 0.86)

    def test_precise_food_input_still_supports_grams(self):
        with patch(
            "builtins.input",
            side_effect=["0", "苹果", "200", "g", "", ""],
        ):
            record = tracker.prompt_common_record("food")

        self.assertEqual(record["amount"], 200)
        self.assertEqual(record["unit"], "g")
        self.assertEqual(record["converted_amount"], 200)
        self.assertEqual(record["converted_unit"], "g")
        self.assertEqual(record["estimated_water_ml"], 172)
        self.assertTrue(record["is_estimated"])

    def test_common_item_serving_estimates(self):
        cases = (
            ("苹果", 1, "个", 180, "g", 0.86, 154.8),
            ("鸡蛋", 2, "个", 100, "g", 0.75, 75),
            ("米饭", 1, "碗", 150, "g", 0.60, 90),
            ("西瓜", 1, "份", 300, "g", 0.91, 273),
            ("西红柿", 1, "个", 150, "g", 0.94, 141),
            ("青椒", 1, "个", 100, "g", 0.92, 92),
            ("橙子", 1, "个", 180, "g", 0.87, 156.6),
            ("汤", 1, "碗", 300, "ml", 0.95, 285),
            ("豆浆", 1, "杯", 250, "ml", 0.90, 225),
            ("馒头", 1, "个", 100, "g", 0.45, 45),
            ("香肠", 1, "根", 50, "g", 0.55, 27.5),
        )

        for name, quantity, unit, converted, converted_unit, ratio, water in cases:
            with self.subTest(name=name, quantity=quantity):
                record = tracker.create_common_item_record(name, quantity)
                self.assertEqual(record["amount"], quantity)
                self.assertEqual(record["unit"], unit)
                self.assertEqual(record["converted_amount"], converted)
                self.assertEqual(record["converted_unit"], converted_unit)
                self.assertEqual(record["water_ratio"], ratio)
                self.assertEqual(record["estimated_water_ml"], water)
                self.assertTrue(record["is_estimated"])

    def test_common_item_conversion_details_are_saved_to_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            record = tracker.create_common_item_record("苹果", 1)

            tracker.add_record(record, data_file)
            saved = tracker.load_records(data_file)[0]

            self.assertEqual(saved["name"], "苹果")
            self.assertEqual(saved["amount"], 1)
            self.assertEqual(saved["unit"], "个")
            self.assertEqual(saved["converted_amount"], 180)
            self.assertEqual(saved["converted_unit"], "g")
            self.assertEqual(saved["water_ratio"], 0.86)
            self.assertEqual(saved["estimated_water_ml"], 154.8)
            self.assertTrue(saved["is_estimated"])

    def test_format_number_uses_at_most_one_decimal_place(self):
        self.assertEqual(tracker.format_number(300), "300")
        self.assertEqual(tracker.format_number(217.5), "217.5")
        self.assertEqual(tracker.format_number(217.56), "217.6")

    def test_record_details_show_required_fields_and_support_old_records(self):
        records = [
            {
                "date": "2026-06-29",
                "time": "08:00",
                "name": "白水",
                "amount": 300,
                "unit": "ml",
                "water_ratio": 1.0,
                "estimated_water_ml": 300,
            },
            {
                "date": "2026-06-28",
                "time": "09:00",
                "name": "历史记录",
                "amount": 100,
                "unit": "ml",
                "water_ratio": 1.0,
                "estimated_water_ml": 100,
            },
        ]
        output = StringIO()

        with redirect_stdout(output):
            shown = tracker.display_records_for_date(records, "2026-06-29")

        text = output.getvalue()
        self.assertEqual(len(shown), 1)
        self.assertIn("1. 08:00", text)
        self.assertIn("白水", text)
        self.assertIn("原始：300 ml", text)
        self.assertIn("换算：约 300 ml", text)
        self.assertIn("含水率：1.00", text)
        self.assertIn("估算水分：300 ml", text)
        self.assertNotIn("历史记录", text)

    def test_delete_today_record_by_number_preserves_other_dates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            today = date.today().isoformat()
            records = [
                {"date": today, "name": "白水"},
                {"date": "2026-06-28", "name": "历史记录"},
                {"date": today, "name": "苹果"},
            ]
            tracker.save_records(records, data_file)

            with patch("builtins.input", side_effect=["2", "y"]):
                with redirect_stdout(StringIO()):
                    tracker.prompt_delete_today_record(data_file)

            saved = tracker.load_records(data_file)
            self.assertEqual(
                [(record["date"], record["name"]) for record in saved],
                [(today, "白水"), ("2026-06-28", "历史记录")],
            )

    def test_delete_today_record_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            today = date.today().isoformat()
            tracker.save_records([{"date": today, "name": "白水"}], data_file)

            with patch("builtins.input", side_effect=["1", "n"]):
                with redirect_stdout(StringIO()):
                    tracker.prompt_delete_today_record(data_file)

            self.assertEqual(len(tracker.load_records(data_file)), 1)

    def test_clear_today_records_preserves_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            today = date.today().isoformat()
            records = [
                {"date": today, "name": "白水"},
                {"date": "2026-06-28", "name": "历史记录"},
                {"date": today, "name": "苹果"},
            ]
            tracker.save_records(records, data_file)

            with patch("builtins.input", return_value="CLEAR"):
                with redirect_stdout(StringIO()):
                    tracker.prompt_clear_today_records(data_file)

            saved = tracker.load_records(data_file)
            self.assertEqual(saved, [{"date": "2026-06-28", "name": "历史记录"}])

    def test_clear_today_records_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            today = date.today().isoformat()
            tracker.save_records([{"date": today, "name": "白水"}], data_file)

            with patch("builtins.input", return_value="n"):
                with redirect_stdout(StringIO()):
                    tracker.prompt_clear_today_records(data_file)

            self.assertEqual(len(tracker.load_records(data_file)), 1)


if __name__ == "__main__":
    unittest.main()
