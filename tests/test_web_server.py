import json
import sys
import tempfile
import unittest
from datetime import date
from io import BytesIO
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import hydration_tracker as tracker
import web_server


class WebApiTest(unittest.TestCase):
    def call_get(self, path, data_file):
        response = {}
        handler = object.__new__(web_server.HydrationWebHandler)
        handler.path = path
        handler.data_file = data_file
        handler.send_json = lambda payload, status: response.update(
            {"status": status, "payload": payload}
        )
        handler.do_GET()
        return response["status"], response["payload"]

    def call_post(self, payload, data_file):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        response = {}
        handler = object.__new__(web_server.HydrationWebHandler)
        handler.path = "/api/records"
        handler.data_file = data_file
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile = BytesIO(body)
        handler.send_json = lambda payload, status: response.update(
            {"status": status, "payload": payload}
        )
        handler.do_POST()
        return response["status"], response["payload"]

    def call_delete(self, path, data_file):
        response = {}
        handler = object.__new__(web_server.HydrationWebHandler)
        handler.path = path
        handler.data_file = data_file
        handler.send_json = lambda payload, status: response.update(
            {"status": status, "payload": payload}
        )
        handler.do_DELETE()
        return response["status"], response["payload"]

    def fetch_today(self, records):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records(records, data_file)
            status, payload = self.call_get("/api/today", data_file)

        self.assertEqual(status, 200)
        return payload

    def test_today_api_returns_zero_for_no_records(self):
        payload = self.fetch_today([])

        self.assertEqual(
            payload,
            {
                "total_water_ml": 0.0,
                "target_ml": 2000,
                "completion_rate": 0.0,
                "remaining_ml": 2000,
                "record_count": 0,
            },
        )

    def test_today_api_summarizes_only_today_records(self):
        today = date.today().isoformat()
        records = [
            {"date": today, "estimated_water_ml": 300},
            {"date": today, "estimated_water_ml": 217.5},
            {"date": "2026-06-28", "estimated_water_ml": 1000},
        ]

        payload = self.fetch_today(records)

        self.assertEqual(payload["total_water_ml"], 517.5)
        self.assertEqual(payload["target_ml"], 2000)
        self.assertEqual(payload["completion_rate"], 25.87)
        self.assertEqual(payload["remaining_ml"], 1482.5)
        self.assertEqual(payload["record_count"], 2)

    def test_common_items_api_reuses_v1_library(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records([], data_file)
            status, payload = self.call_get("/api/common-items", data_file)

        self.assertEqual(status, 200)
        self.assertEqual(
            {item["name"] for item in payload["items"]},
            set(tracker.COMMON_ITEM_DEFAULTS),
        )

    def test_post_records_adds_common_servings(self):
        cases = (
            ("water", "白水", 1, "杯", 250, "ml", 1.00, 250),
            ("beverage", "豆浆", 0.5, "杯", 125, "ml", 0.90, 112.5),
            ("food", "苹果", 1, "个", 180, "g", 0.86, 154.8),
            ("food", "鸡蛋", 2, "个", 100, "g", 0.75, 75),
        )

        for category, name, quantity, unit, converted, base_unit, ratio, water in cases:
            with self.subTest(name=name, quantity=quantity):
                with tempfile.TemporaryDirectory() as temp_dir:
                    data_file = Path(temp_dir) / "hydration_log.json"
                    tracker.save_records([], data_file)
                    status, payload = self.call_post(
                        {
                            "category": category,
                            "name": name,
                            "quantity": quantity,
                            "meal": "none",
                            "note": "网页测试",
                        },
                        data_file,
                    )
                    saved = tracker.load_records(data_file)

                self.assertEqual(status, 201)
                self.assertEqual(payload["estimated_water_ml"], water)
                self.assertEqual(len(saved), 1)
                self.assertEqual(saved[0]["name"], name)
                self.assertEqual(saved[0]["amount"], quantity)
                self.assertEqual(saved[0]["unit"], unit)
                self.assertEqual(saved[0]["converted_amount"], converted)
                self.assertEqual(saved[0]["converted_unit"], base_unit)
                self.assertEqual(saved[0]["water_ratio"], ratio)
                self.assertEqual(saved[0]["estimated_water_ml"], water)
                self.assertEqual(saved[0]["note"], "网页测试")

    def test_invalid_item_name_does_not_write_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            original = [{"date": "2026-06-28", "name": "历史记录"}]
            tracker.save_records(original, data_file)

            status, payload = self.call_post(
                {
                    "category": "food",
                    "name": "不存在的项目",
                    "quantity": 1,
                    "meal": "none",
                    "note": "",
                },
                data_file,
            )

            self.assertEqual(status, 400)
            self.assertIn("error", payload)
            self.assertEqual(tracker.load_records(data_file), original)

    def test_invalid_quantity_does_not_write_data(self):
        invalid_quantities = (0, -1, "1", None)
        for quantity in invalid_quantities:
            with self.subTest(quantity=quantity):
                with tempfile.TemporaryDirectory() as temp_dir:
                    data_file = Path(temp_dir) / "hydration_log.json"
                    tracker.save_records([], data_file)

                    status, payload = self.call_post(
                        {
                            "category": "water",
                            "name": "白水",
                            "quantity": quantity,
                            "meal": "none",
                            "note": "",
                        },
                        data_file,
                    )

                    self.assertEqual(status, 400)
                    self.assertIn("error", payload)
                    self.assertEqual(tracker.load_records(data_file), [])

    def test_category_mismatch_does_not_write_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records([], data_file)

            status, _ = self.call_post(
                {
                    "category": "beverage",
                    "name": "苹果",
                    "quantity": 1,
                    "meal": "none",
                    "note": "",
                },
                data_file,
            )

            self.assertEqual(status, 400)
            self.assertEqual(tracker.load_records(data_file), [])

    def test_today_api_updates_after_post(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records([], data_file)
            self.call_post(
                {
                    "category": "water",
                    "name": "白水",
                    "quantity": 1,
                    "meal": "none",
                    "note": "",
                },
                data_file,
            )
            self.call_post(
                {
                    "category": "food",
                    "name": "苹果",
                    "quantity": 1,
                    "meal": "snack",
                    "note": "",
                },
                data_file,
            )

            status, payload = self.call_get("/api/today", data_file)

            self.assertEqual(status, 200)
            self.assertEqual(payload["total_water_ml"], 404.8)
            self.assertEqual(payload["completion_rate"], 20.24)
            self.assertEqual(payload["remaining_ml"], 1595.2)
            self.assertEqual(payload["record_count"], 2)

    def test_today_records_api_returns_only_today_records(self):
        today = date.today().isoformat()
        records = [
            {"id": "rec_today_1", "date": today, "name": "白水"},
            {"id": "rec_old_1", "date": "2026-06-28", "name": "历史记录"},
            {"id": "rec_today_2", "date": today, "name": "苹果"},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records(records, data_file)

            status, payload = self.call_get("/api/records/today", data_file)

        self.assertEqual(status, 200)
        self.assertEqual(
            [record["id"] for record in payload["records"]],
            ["rec_today_1", "rec_today_2"],
        )

    def test_today_records_api_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records(
                [{"id": "rec_old", "date": "2026-06-28", "name": "历史记录"}],
                data_file,
            )

            status, payload = self.call_get("/api/records/today", data_file)

        self.assertEqual(status, 200)
        self.assertEqual(payload["records"], [])

    def test_delete_record_by_id_preserves_other_records(self):
        today = date.today().isoformat()
        records = [
            {"id": "rec_delete", "date": today, "name": "白水"},
            {"id": "rec_keep", "date": today, "name": "苹果"},
            {"id": "rec_old", "date": "2026-06-28", "name": "历史记录"},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records(records, data_file)

            status, payload = self.call_delete(
                "/api/records/rec_delete", data_file
            )
            saved = tracker.load_records(data_file)

        self.assertEqual(status, 200)
        self.assertEqual(payload["deleted_record"]["id"], "rec_delete")
        self.assertEqual(
            [record["id"] for record in saved],
            ["rec_keep", "rec_old"],
        )

    def test_delete_historical_record_id_is_rejected(self):
        records = [
            {"id": "rec_old", "date": "2026-06-28", "name": "历史记录"},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records(records, data_file)

            status, payload = self.call_delete("/api/records/rec_old", data_file)

            self.assertEqual(status, 404)
            self.assertIn("error", payload)
            self.assertEqual(tracker.load_records(data_file), records)

    def test_delete_missing_record_id_returns_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records([], data_file)

            status, payload = self.call_delete(
                "/api/records/rec_missing", data_file
            )

            self.assertEqual(status, 404)
            self.assertIn("error", payload)
            self.assertEqual(tracker.load_records(data_file), [])

    def test_clear_today_records_preserves_other_dates(self):
        today = date.today().isoformat()
        records = [
            {"id": "rec_today_1", "date": today, "name": "白水"},
            {"id": "rec_old", "date": "2026-06-28", "name": "历史记录"},
            {"id": "rec_today_2", "date": today, "name": "苹果"},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records(records, data_file)

            status, payload = self.call_delete("/api/records/today", data_file)
            saved = tracker.load_records(data_file)

        self.assertEqual(status, 200)
        self.assertEqual(payload["deleted_count"], 2)
        self.assertEqual(saved, [records[1]])

    def test_today_summary_updates_after_delete_and_clear(self):
        today = date.today().isoformat()
        records = [
            {
                "id": "rec_today_1",
                "date": today,
                "name": "白水",
                "estimated_water_ml": 300,
            },
            {
                "id": "rec_today_2",
                "date": today,
                "name": "豆浆",
                "estimated_water_ml": 225,
            },
            {
                "id": "rec_old",
                "date": "2026-06-28",
                "name": "历史记录",
                "estimated_water_ml": 1000,
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "hydration_log.json"
            tracker.save_records(records, data_file)

            self.call_delete("/api/records/rec_today_1", data_file)
            _, after_delete = self.call_get("/api/today", data_file)
            self.call_delete("/api/records/today", data_file)
            _, after_clear = self.call_get("/api/today", data_file)

            self.assertEqual(after_delete["total_water_ml"], 225)
            self.assertEqual(after_delete["record_count"], 1)
            self.assertEqual(after_clear["total_water_ml"], 0)
            self.assertEqual(after_clear["record_count"], 0)
            self.assertEqual(
                tracker.load_records(data_file),
                [records[2]],
            )


if __name__ == "__main__":
    unittest.main()
