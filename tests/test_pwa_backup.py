import json
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_JS = PROJECT_ROOT / "pwa" / "app.js"
SERVICE_WORKER = PROJECT_ROOT / "pwa" / "service-worker.js"
INDEX_HTML = PROJECT_ROOT / "pwa" / "index.html"


class PwaBackupTest(unittest.TestCase):
    maxDiff = None

    def run_jxa(self, body):
        if not shutil.which("osascript"):
            self.skipTest("osascript 不可用，跳过前端纯函数测试")

        script = textwrap.dedent(
            f"""
            ObjC.import('Foundation');
            var globalThis = this;
            var console = {{ info: function() {{}}, warn: function() {{}} }};
            var navigator = {{}};
            var document = {{
              querySelector: function() {{ return null; }},
              querySelectorAll: function() {{ return []; }},
              createElement: function() {{
                return {{
                  click: function() {{}},
                  remove: function() {{}},
                  append: function() {{}},
                  appendChild: function() {{}},
                  setAttribute: function() {{}},
                  classList: {{ add: function() {{}}, remove: function() {{}} }},
                  style: {{ setProperty: function() {{}} }},
                }};
              }},
              body: {{ append: function() {{}} }},
            }};

            function printJson(value) {{
              $.NSFileHandle.fileHandleWithStandardOutput.writeData(
                $(JSON.stringify(value)).dataUsingEncoding($.NSUTF8StringEncoding)
              );
            }}

            var appJs = $.NSString.stringWithContentsOfFileEncodingError(
              $('{APP_JS}'),
              $.NSUTF8StringEncoding,
              null
            ).js;
            eval(appJs);
            {body}
            """
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = Path(temp_dir) / "pwa_test.js"
            script_path.write_text(script)
            result = subprocess.run(
                ["osascript", "-l", "JavaScript", str(script_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        return json.loads(result.stdout)

    @staticmethod
    def make_record(record_id, date, time, estimated_water_ml):
        return {
            "id": record_id,
            "date": date,
            "time": time,
            "category": "water",
            "meal": "none",
            "item_id": "water",
            "name": "白水",
            "quantity": estimated_water_ml / 250,
            "default_unit": "杯",
            "default_amount": 250,
            "base_type": "ml",
            "water_ratio": 1,
            "estimated_water_ml": estimated_water_ml,
            "note": "",
            "created_at": f"{date}T{time}:00.000Z",
        }

    def test_export_payload_structure_supports_empty_records(self):
        payload = self.run_jxa(
            "printJson(HydrationTrackerV3.buildExportPayload({schema_version: 1, records: []}, new Date('2026-07-01T08:00:00.000Z')));"
        )

        self.assertEqual(
            payload,
            {
                "app": "HydrationTracker",
                "export_version": 1,
                "schema_version": 1,
                "exported_at": "2026-07-01T08:00:00.000Z",
                "source": "pwa-localStorage",
                "storage_key": "hydration_tracker_v3_records",
                "records": [],
            },
        )

    def test_default_settings_use_2000ml_goal(self):
        payload = self.run_jxa(
            "printJson(HydrationTrackerV3.createDefaultSettings());"
        )

        self.assertEqual(
            payload,
            {
                "settings_version": 1,
                "daily_goal_ml": 2000,
            },
        )

    def test_valid_settings_are_loaded_from_storage(self):
        payload = self.run_jxa(
            "var storage = {getItem: function(key) { return key === HydrationTrackerV3.SETTINGS_KEY ? JSON.stringify({settings_version: 1, daily_goal_ml: 1800}) : null; }};"
            "printJson(HydrationTrackerV3.loadSettingsFromStorage(storage));"
        )

        self.assertEqual(payload["daily_goal_ml"], 1800)

    def test_invalid_settings_fall_back_to_default_goal(self):
        payload = self.run_jxa(
            "var storage = {getItem: function() { return JSON.stringify({settings_version: 1, daily_goal_ml: 'bad'}); }};"
            "printJson(HydrationTrackerV3.loadSettingsFromStorage(storage));"
        )

        self.assertEqual(payload["daily_goal_ml"], 2000)

    def test_missing_settings_fall_back_to_default_goal(self):
        payload = self.run_jxa(
            "var storage = {getItem: function() { return null; }};"
            "printJson(HydrationTrackerV3.loadSettingsFromStorage(storage));"
        )

        self.assertEqual(payload["daily_goal_ml"], 2000)

    def test_invalid_goal_value_is_rejected(self):
        payload = self.run_jxa(
            "try { HydrationTrackerV3.normalizeDailyGoalMl(499); printJson({ok: true}); }"
            "catch (error) { printJson({ok: false, message: String(error.message || error)}); }"
        )

        self.assertFalse(payload["ok"])
        self.assertIn("500", payload["message"])

    def test_goal_input_1800_builds_valid_settings(self):
        payload = self.run_jxa(
            "printJson(HydrationTrackerV3.buildDailyGoalSettings('1800'));"
        )

        self.assertEqual(
            payload,
            {
                "settings_version": 1,
                "daily_goal_ml": 1800,
            },
        )

    def test_goal_boundary_values_500_and_5000_are_valid(self):
        payload = self.run_jxa(
            "printJson({min: HydrationTrackerV3.normalizeDailyGoalMl('500'), max: HydrationTrackerV3.normalizeDailyGoalMl('5000')});"
        )

        self.assertEqual(payload["min"], 500)
        self.assertEqual(payload["max"], 5000)

    def test_goal_values_499_and_5001_are_invalid(self):
        payload = self.run_jxa(
            "var result = {};"
            "try { HydrationTrackerV3.normalizeDailyGoalMl('499'); result.low = 'ok'; }"
            "catch (error) { result.low = String(error.message || error); }"
            "try { HydrationTrackerV3.normalizeDailyGoalMl('5001'); result.high = 'ok'; }"
            "catch (error) { result.high = String(error.message || error); }"
            "printJson(result);"
        )

        self.assertIn("500", payload["low"])
        self.assertIn("5000", payload["high"])

    def test_goal_settings_auto_open_on_mobile_width(self):
        payload = self.run_jxa(
            "printJson({small: HydrationTrackerV3.shouldAutoOpenGoalSettings({innerWidth: 390}), large: HydrationTrackerV3.shouldAutoOpenGoalSettings({innerWidth: 900})});"
        )

        self.assertTrue(payload["small"])
        self.assertFalse(payload["large"])

    def test_valid_goal_value_is_saved_without_touching_records(self):
        payload = self.run_jxa(
            "var calls = [];"
            "var storage = {"
            "  setItem: function(key, value) { calls.push({key: key, value: JSON.parse(value)}); },"
            "  getItem: function() { return null; }"
            "};"
            "var settings = HydrationTrackerV3.writeSettingsToStorage(storage, {settings_version: 1, daily_goal_ml: 2500});"
            "printJson({settings: settings, calls: calls});"
        )

        self.assertEqual(payload["settings"]["daily_goal_ml"], 2500)
        self.assertEqual(len(payload["calls"]), 1)
        self.assertEqual(payload["calls"][0]["key"], "hydration_tracker_v4_settings")
        self.assertEqual(payload["calls"][0]["value"]["daily_goal_ml"], 2500)
        self.assertNotEqual(payload["calls"][0]["key"], "hydration_tracker_v3_records")

    def test_export_filename_contains_local_date(self):
        payload = self.run_jxa(
            "printJson({filename: HydrationTrackerV3.buildExportFilename(new Date('2026-07-01T08:00:00.000Z'))});"
        )

        self.assertEqual(payload["filename"], "hydration-tracker-backup-2026-07-01.json")

    def test_valid_backup_import_rebuilds_runtime_container(self):
        record = {
            "id": "rec_test_1",
            "date": "2026-07-01",
            "time": "08:30",
            "category": "water",
            "meal": "none",
            "item_id": "water",
            "name": "白水",
            "quantity": 1,
            "default_unit": "杯",
            "default_amount": 250,
            "base_type": "ml",
            "water_ratio": 1,
            "estimated_water_ml": 250,
            "note": "",
            "created_at": "2026-07-01T08:30:00.000Z",
        }
        backup = {
            "app": "HydrationTracker",
            "export_version": 1,
            "schema_version": 1,
            "exported_at": "2026-07-01T09:00:00.000Z",
            "source": "pwa-localStorage",
            "storage_key": "hydration_tracker_v3_records",
            "records": [record],
        }
        body = f"printJson(HydrationTrackerV3.buildDataFromBackupPayload({json.dumps(backup, ensure_ascii=False)}));"
        payload = self.run_jxa(body)

        self.assertEqual(payload, {"schema_version": 1, "records": [record]})

    def test_invalid_app_is_rejected_without_replacing_data(self):
        backup = {
            "app": "OtherApp",
            "export_version": 1,
            "schema_version": 1,
            "exported_at": "2026-07-01T09:00:00.000Z",
            "source": "pwa-localStorage",
            "storage_key": "hydration_tracker_v3_records",
            "records": [],
        }
        body = f"try {{ HydrationTrackerV3.buildDataFromBackupPayload({json.dumps(backup, ensure_ascii=False)}); printJson({{ok: true}}); }} catch (error) {{ printJson({{ok: false, message: String(error.message || error)}}); }}"
        payload = self.run_jxa(body)

        self.assertFalse(payload["ok"])
        self.assertIn("HydrationTracker", payload["message"])

    def test_invalid_schema_version_is_rejected(self):
        backup = {
            "app": "HydrationTracker",
            "export_version": 1,
            "schema_version": 99,
            "exported_at": "2026-07-01T09:00:00.000Z",
            "source": "pwa-localStorage",
            "storage_key": "hydration_tracker_v3_records",
            "records": [],
        }
        body = f"try {{ HydrationTrackerV3.buildDataFromBackupPayload({json.dumps(backup, ensure_ascii=False)}); printJson({{ok: true}}); }} catch (error) {{ printJson({{ok: false, message: String(error.message || error)}}); }}"
        payload = self.run_jxa(body)

        self.assertFalse(payload["ok"])
        self.assertIn("版本", payload["message"])

    def test_service_worker_does_not_touch_local_storage(self):
        source = SERVICE_WORKER.read_text()
        self.assertNotIn("localStorage", source)
        self.assertNotIn("localStorage.clear", source)

    def test_history_summary_is_empty_without_records(self):
        summaries = self.run_jxa(
            "printJson(HydrationTrackerV3.summarizeRecordsByDate({schema_version: 1, records: []}));"
        )

        self.assertEqual(summaries, [])

    def test_history_summary_includes_single_date(self):
        record = self.make_record("rec_today", "2026-07-01", "08:30", 250)
        body = f"printJson(HydrationTrackerV3.summarizeRecordsByDate({{schema_version: 1, records: {json.dumps([record], ensure_ascii=False)}}}));"
        summaries = self.run_jxa(body)

        self.assertEqual(
            summaries,
            [
                {
                    "date": "2026-07-01",
                    "totalWaterMl": 250,
                    "completionRate": 12.5,
                    "remainingMl": 1750,
                    "recordCount": 1,
                }
            ],
        )

    def test_history_summary_uses_custom_goal(self):
        record = self.make_record("rec_today", "2026-07-01", "08:30", 900)
        body = f"printJson(HydrationTrackerV3.summarizeRecordsByDate({{schema_version: 1, records: {json.dumps([record], ensure_ascii=False)}}}, 1800));"
        summaries = self.run_jxa(body)

        self.assertEqual(summaries[0]["completionRate"], 50)
        self.assertEqual(summaries[0]["remainingMl"], 900)

    def test_history_summary_groups_and_sorts_dates_descending(self):
        records = [
            self.make_record("rec_old", "2026-06-29", "12:00", 500),
            self.make_record("rec_new_1", "2026-07-01", "08:00", 250),
            self.make_record("rec_middle", "2026-06-30", "09:00", 1000),
            self.make_record("rec_new_2", "2026-07-01", "18:00", 750),
        ]
        body = f"printJson(HydrationTrackerV3.summarizeRecordsByDate({{schema_version: 1, records: {json.dumps(records, ensure_ascii=False)}}}));"
        summaries = self.run_jxa(body)

        self.assertEqual(
            [summary["date"] for summary in summaries],
            ["2026-07-01", "2026-06-30", "2026-06-29"],
        )
        self.assertEqual(summaries[0]["totalWaterMl"], 1000)
        self.assertEqual(summaries[0]["recordCount"], 2)
        self.assertEqual(summaries[0]["completionRate"], 50)

    def test_history_details_only_include_selected_date(self):
        selected = self.make_record("rec_selected", "2026-06-30", "09:00", 500)
        other = self.make_record("rec_other", "2026-07-01", "08:00", 250)
        records = [other, selected]
        body = f"printJson(HydrationTrackerV3.getRecordsForDate({{schema_version: 1, records: {json.dumps(records, ensure_ascii=False)}}}, '2026-06-30'));"
        details = self.run_jxa(body)

        self.assertEqual(details, [selected])

    def test_history_summary_does_not_change_exported_records(self):
        records = [
            self.make_record("rec_1", "2026-07-01", "08:00", 250),
            self.make_record("rec_2", "2026-06-30", "09:00", 500),
        ]
        data = {"schema_version": 1, "records": records}
        body = (
            f"var data = {json.dumps(data, ensure_ascii=False)};"
            "HydrationTrackerV3.summarizeRecordsByDate(data);"
            "printJson({data: data, exported: HydrationTrackerV3.buildExportPayload(data, new Date('2026-07-01T08:00:00.000Z')).records});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["data"], data)
        self.assertEqual(payload["exported"], records)

    def test_calendar_month_marks_recorded_dates(self):
        record = self.make_record("rec_calendar", "2026-07-15", "08:00", 1350)
        body = f"printJson(HydrationTrackerV3.buildCalendarMonth({{schema_version: 1, records: {json.dumps([record], ensure_ascii=False)}}}, 2026, 6, new Date('2026-07-01T12:00:00')));"
        calendar = self.run_jxa(body)

        self.assertEqual(calendar["label"], "2026年7月")
        self.assertEqual(len(calendar["days"]), 42)
        self.assertEqual(calendar["days"][0]["date"], "2026-06-29")
        recorded_day = next(day for day in calendar["days"] if day["date"] == "2026-07-15")
        empty_day = next(day for day in calendar["days"] if day["date"] == "2026-07-16")
        self.assertTrue(recorded_day["hasRecords"])
        self.assertEqual(recorded_day["totalWaterMl"], 1350)
        self.assertFalse(empty_day["hasRecords"])

    def test_recent_trend_has_seven_days_and_fills_missing_days_with_zero(self):
        records = [
            self.make_record("rec_early", "2026-06-26", "08:00", 500),
            self.make_record("rec_today", "2026-07-01", "09:00", 250),
        ]
        body = f"printJson(HydrationTrackerV3.buildRecentTrendData({{schema_version: 1, records: {json.dumps(records, ensure_ascii=False)}}}, new Date('2026-07-01T12:00:00'), 7));"
        trend = self.run_jxa(body)

        self.assertEqual(trend["targetMl"], 2000)
        self.assertEqual(
            [point["date"] for point in trend["points"]],
            [
                "2026-06-25",
                "2026-06-26",
                "2026-06-27",
                "2026-06-28",
                "2026-06-29",
                "2026-06-30",
                "2026-07-01",
            ],
        )
        self.assertEqual(
            [point["totalWaterMl"] for point in trend["points"]],
            [0, 500, 0, 0, 0, 0, 250],
        )

    def test_recent_trend_uses_custom_goal_line(self):
        records = [self.make_record("rec_today", "2026-07-01", "09:00", 250)]
        body = f"printJson(HydrationTrackerV3.buildRecentTrendData({{schema_version: 1, records: {json.dumps(records, ensure_ascii=False)}}}, new Date('2026-07-01T12:00:00'), 7, 1800));"
        trend = self.run_jxa(body)

        self.assertEqual(trend["targetMl"], 1800)

    def test_imported_records_are_available_to_calendar_and_history_summary(self):
        record = self.make_record("rec_imported", "2026-06-30", "10:00", 750)
        backup = {
            "app": "HydrationTracker",
            "export_version": 1,
            "schema_version": 1,
            "exported_at": "2026-07-01T09:00:00.000Z",
            "source": "pwa-localStorage",
            "storage_key": "hydration_tracker_v3_records",
            "records": [record],
        }
        body = (
            f"var data = HydrationTrackerV3.buildDataFromBackupPayload({json.dumps(backup, ensure_ascii=False)});"
            "printJson({summary: HydrationTrackerV3.summarizeRecordsByDate(data), calendar: HydrationTrackerV3.buildCalendarMonth(data, 2026, 5, new Date('2026-07-01T12:00:00'))});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["summary"][0]["date"], "2026-06-30")
        imported_day = next(
            day for day in payload["calendar"]["days"] if day["date"] == "2026-06-30"
        )
        self.assertTrue(imported_day["hasRecords"])
        self.assertEqual(imported_day["totalWaterMl"], 750)

    def test_today_view_is_default_and_other_views_start_hidden(self):
        source = INDEX_HTML.read_text()
        self.assertIn('id="nav-today" class="view-tab" type="button" role="tab" aria-selected="true"', source)
        self.assertIn('id="today-view" class="app-view" role="tabpanel"', source)
        self.assertIn('id="history-view" class="app-view" role="tabpanel" aria-labelledby="nav-history" hidden', source)
        self.assertIn('id="backup-view" class="app-view" role="tabpanel" aria-labelledby="nav-backup" hidden', source)

    def test_today_view_contains_daily_goal_settings_controls(self):
        source = INDEX_HTML.read_text()
        self.assertIn('id="goal-settings-title"', source)
        self.assertIn('id="goal-settings-toggle"', source)
        self.assertIn('id="daily-goal-input"', source)
        self.assertIn('id="current-daily-goal"', source)
        self.assertIn('id="goal-settings-save" type="button"', source)
        self.assertNotIn('goal-quick-button', source)

    def test_history_delete_matches_date_and_id_only(self):
        target = self.make_record("shared_id", "2026-06-30", "08:00", 250)
        same_date = self.make_record("same_date", "2026-06-30", "09:00", 500)
        same_id_other_date = self.make_record("shared_id", "2026-07-01", "10:00", 750)
        data = {"schema_version": 1, "records": [target, same_date, same_id_other_date]}
        body = (
            f"var result = HydrationTrackerV3.deleteRecordForDateById({json.dumps(data, ensure_ascii=False)}, 'shared_id', '2026-06-30');"
            "printJson(result);"
        )
        result = self.run_jxa(body)

        self.assertEqual(result["deletedCount"], 1)
        self.assertEqual(result["data"]["records"], [same_date, same_id_other_date])

    def test_cancelled_history_delete_does_not_change_data(self):
        record = self.make_record("rec_cancel", "2026-06-30", "08:00", 250)
        data = {"schema_version": 1, "records": [record]}
        body = (
            f"printJson(HydrationTrackerV3.resolveRecordDeletion({json.dumps(data, ensure_ascii=False)}, 'rec_cancel', '2026-06-30', false));"
        )
        result = self.run_jxa(body)

        self.assertTrue(result["cancelled"])
        self.assertEqual(result["deletedCount"], 0)
        self.assertEqual(result["data"], data)

    def test_history_delete_refresh_data_updates_calendar_trend_and_export(self):
        target = self.make_record("rec_delete", "2026-06-30", "08:00", 500)
        remaining = self.make_record("rec_keep", "2026-06-30", "09:00", 250)
        other_date = self.make_record("rec_other", "2026-07-01", "10:00", 750)
        data = {"schema_version": 1, "records": [target, remaining, other_date]}
        body = (
            f"var result = HydrationTrackerV3.deleteRecordForDateById({json.dumps(data, ensure_ascii=False)}, 'rec_delete', '2026-06-30');"
            "var nextData = result.data;"
            "printJson({"
            "summary: HydrationTrackerV3.calculateSummary(nextData, '2026-06-30'),"
            "calendar: HydrationTrackerV3.buildCalendarMonth(nextData, 2026, 5, new Date('2026-07-01T12:00:00')) ,"
            "trend: HydrationTrackerV3.buildRecentTrendData(nextData, new Date('2026-07-01T12:00:00'), 7),"
            "exported: HydrationTrackerV3.buildExportPayload(nextData, new Date('2026-07-01T12:00:00.000Z')).records"
            "});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["summary"]["recordCount"], 1)
        self.assertEqual(payload["summary"]["totalWaterMl"], 250)
        calendar_day = next(
            day for day in payload["calendar"]["days"] if day["date"] == "2026-06-30"
        )
        trend_day = next(
            day for day in payload["trend"]["points"] if day["date"] == "2026-06-30"
        )
        self.assertEqual(calendar_day["recordCount"], 1)
        self.assertEqual(calendar_day["totalWaterMl"], 250)
        self.assertEqual(trend_day["totalWaterMl"], 250)
        self.assertEqual(len(payload["exported"]), 2)

    def test_deleting_today_updates_today_summary(self):
        target = self.make_record("rec_today_delete", "2026-07-01", "08:00", 500)
        remaining_today = self.make_record("rec_today_keep", "2026-07-01", "09:00", 250)
        past = self.make_record("rec_past", "2026-06-30", "10:00", 750)
        data = {"schema_version": 1, "records": [target, remaining_today, past]}
        body = (
            f"var result = HydrationTrackerV3.deleteRecordForDateById({json.dumps(data, ensure_ascii=False)}, 'rec_today_delete', '2026-07-01');"
            "printJson({today: HydrationTrackerV3.calculateSummary(result.data, '2026-07-01'), past: HydrationTrackerV3.calculateSummary(result.data, '2026-06-30')});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["today"]["recordCount"], 1)
        self.assertEqual(payload["today"]["totalWaterMl"], 250)
        self.assertEqual(payload["past"]["recordCount"], 1)
        self.assertEqual(payload["past"]["totalWaterMl"], 750)

    def test_deleting_past_record_does_not_change_today_summary(self):
        today = self.make_record("rec_today", "2026-07-01", "08:00", 750)
        past = self.make_record("rec_past_delete", "2026-06-30", "09:00", 500)
        data = {"schema_version": 1, "records": [today, past]}
        body = (
            f"var data = {json.dumps(data, ensure_ascii=False)};"
            "var before = HydrationTrackerV3.calculateSummary(data, '2026-07-01');"
            "var result = HydrationTrackerV3.deleteRecordForDateById(data, 'rec_past_delete', '2026-06-30');"
            "var after = HydrationTrackerV3.calculateSummary(result.data, '2026-07-01');"
            "printJson({before: before, after: after});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["after"], payload["before"])

    def test_backfill_record_uses_selected_date_and_time(self):
        body = (
            "var record = HydrationTrackerV3.buildRecordForDate({"
            "item: HydrationTrackerV3.COMMON_ITEMS[0], quantity: 1, meal: 'none', note: '',"
            "date: '2026-06-28', time: '08:35', now: new Date('2026-07-01T12:00:00.000Z'), id: 'rec_backfill'"
            "});"
            "var data = {schema_version: 1, records: [record]};"
            "printJson({record: record, summary: HydrationTrackerV3.calculateSummary(data, '2026-06-28')});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["record"]["date"], "2026-06-28")
        self.assertEqual(payload["record"]["time"], "08:35")
        self.assertEqual(payload["record"]["estimated_water_ml"], 250)
        self.assertEqual(payload["summary"]["recordCount"], 1)
        self.assertEqual(payload["summary"]["totalWaterMl"], 250)

    def test_backfill_existing_date_updates_calendar_trend_and_export(self):
        existing = self.make_record("rec_existing", "2026-06-30", "08:00", 500)
        body = (
            f"var data = {{schema_version: 1, records: {json.dumps([existing], ensure_ascii=False)}}};"
            "var record = HydrationTrackerV3.buildRecordForDate({"
            "item: HydrationTrackerV3.COMMON_ITEMS[0], quantity: 1, meal: 'none', note: '补录',"
            "date: '2026-06-30', time: '18:20', now: new Date('2026-07-01T12:00:00.000Z'), id: 'rec_added'"
            "});"
            "var nextData = {schema_version: 1, records: data.records.concat([record])};"
            "printJson({"
            "summary: HydrationTrackerV3.calculateSummary(nextData, '2026-06-30'),"
            "calendar: HydrationTrackerV3.buildCalendarMonth(nextData, 2026, 5, new Date('2026-07-01T12:00:00')) ,"
            "trend: HydrationTrackerV3.buildRecentTrendData(nextData, new Date('2026-07-01T12:00:00'), 7),"
            "exported: HydrationTrackerV3.buildExportPayload(nextData, new Date('2026-07-01T12:00:00.000Z')).records"
            "});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["summary"]["recordCount"], 2)
        self.assertEqual(payload["summary"]["totalWaterMl"], 750)
        calendar_day = next(
            day for day in payload["calendar"]["days"] if day["date"] == "2026-06-30"
        )
        trend_day = next(
            day for day in payload["trend"]["points"] if day["date"] == "2026-06-30"
        )
        self.assertEqual(calendar_day["totalWaterMl"], 750)
        self.assertEqual(trend_day["totalWaterMl"], 750)
        self.assertEqual(len(payload["exported"]), 2)

    def test_backfill_today_updates_today_but_past_does_not(self):
        today = self.make_record("rec_today", "2026-07-01", "08:00", 500)
        body = (
            f"var data = {{schema_version: 1, records: {json.dumps([today], ensure_ascii=False)}}};"
            "var pastRecord = HydrationTrackerV3.buildRecordForDate({item: HydrationTrackerV3.COMMON_ITEMS[0], quantity: 1, meal: 'none', note: '', date: '2026-06-30', time: '10:00', now: new Date('2026-07-01T12:00:00.000Z'), id: 'rec_past'});"
            "var afterPast = {schema_version: 1, records: data.records.concat([pastRecord])};"
            "var todayRecord = HydrationTrackerV3.buildRecordForDate({item: HydrationTrackerV3.COMMON_ITEMS[0], quantity: 1, meal: 'none', note: '', date: '2026-07-01', time: '11:00', now: new Date('2026-07-01T12:00:00.000Z'), id: 'rec_today_added'});"
            "var afterToday = {schema_version: 1, records: afterPast.records.concat([todayRecord])};"
            "printJson({before: HydrationTrackerV3.calculateSummary(data, '2026-07-01'), afterPast: HydrationTrackerV3.calculateSummary(afterPast, '2026-07-01'), afterToday: HydrationTrackerV3.calculateSummary(afterToday, '2026-07-01')});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["afterPast"], payload["before"])
        self.assertEqual(payload["afterToday"]["recordCount"], 2)
        self.assertEqual(payload["afterToday"]["totalWaterMl"], 750)

    def test_backfill_rejects_invalid_quantity(self):
        body = (
            "try { HydrationTrackerV3.buildRecordForDate({item: HydrationTrackerV3.COMMON_ITEMS[0], quantity: 0, meal: 'none', note: '', date: '2026-06-30', time: '12:00', now: new Date('2026-07-01T12:00:00.000Z'), id: 'rec_invalid'}); printJson({ok: true}); }"
            "catch (error) { printJson({ok: false, message: String(error.message || error)}); }"
        )
        payload = self.run_jxa(body)

        self.assertFalse(payload["ok"])
        self.assertIn("数量", payload["message"])

    def test_backfill_rejects_invalid_time(self):
        body = (
            "try { HydrationTrackerV3.buildRecordForDate({item: HydrationTrackerV3.COMMON_ITEMS[0], quantity: 1, meal: 'none', note: '', date: '2026-06-30', time: '25:99', now: new Date('2026-07-01T12:00:00.000Z'), id: 'rec_invalid_time'}); printJson({ok: true}); }"
            "catch (error) { printJson({ok: false, message: String(error.message || error)}); }"
        )
        payload = self.run_jxa(body)

        self.assertFalse(payload["ok"])
        self.assertIn("时间", payload["message"])

    def test_clear_selected_date_matches_date_only(self):
        target_one = self.make_record("rec_target_1", "2026-06-30", "08:00", 250)
        target_two = self.make_record("rec_target_2", "2026-06-30", "09:00", 500)
        today = self.make_record("rec_today", "2026-07-01", "10:00", 750)
        data = {"schema_version": 1, "records": [target_one, target_two, today]}
        body = (
            f"printJson(HydrationTrackerV3.clearRecordsForDate({json.dumps(data, ensure_ascii=False)}, '2026-06-30'));"
        )
        result = self.run_jxa(body)

        self.assertEqual(result["deletedCount"], 2)
        self.assertEqual(result["data"]["records"], [today])

    def test_cancelled_selected_date_clear_does_not_change_data(self):
        record = self.make_record("rec_cancel", "2026-06-30", "08:00", 250)
        data = {"schema_version": 1, "records": [record]}
        body = (
            f"printJson(HydrationTrackerV3.resolveDateClear({json.dumps(data, ensure_ascii=False)}, '2026-06-30', false));"
        )
        result = self.run_jxa(body)

        self.assertTrue(result["cancelled"])
        self.assertEqual(result["deletedCount"], 0)
        self.assertEqual(result["data"], data)

    def test_clearing_past_date_does_not_change_today_summary(self):
        past = self.make_record("rec_past", "2026-06-30", "08:00", 500)
        today = self.make_record("rec_today", "2026-07-01", "09:00", 750)
        data = {"schema_version": 1, "records": [past, today]}
        body = (
            f"var data = {json.dumps(data, ensure_ascii=False)};"
            "var before = HydrationTrackerV3.calculateSummary(data, '2026-07-01');"
            "var result = HydrationTrackerV3.clearRecordsForDate(data, '2026-06-30');"
            "var after = HydrationTrackerV3.calculateSummary(result.data, '2026-07-01');"
            "printJson({before: before, after: after});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["after"], payload["before"])

    def test_clearing_today_updates_today_summary(self):
        today_one = self.make_record("rec_today_1", "2026-07-01", "08:00", 250)
        today_two = self.make_record("rec_today_2", "2026-07-01", "09:00", 500)
        past = self.make_record("rec_past", "2026-06-30", "10:00", 750)
        data = {"schema_version": 1, "records": [today_one, today_two, past]}
        body = (
            f"var result = HydrationTrackerV3.clearRecordsForDate({json.dumps(data, ensure_ascii=False)}, '2026-07-01');"
            "printJson({today: HydrationTrackerV3.calculateSummary(result.data, '2026-07-01'), past: HydrationTrackerV3.calculateSummary(result.data, '2026-06-30')});"
        )
        payload = self.run_jxa(body)

        self.assertEqual(payload["today"]["recordCount"], 0)
        self.assertEqual(payload["today"]["totalWaterMl"], 0)
        self.assertEqual(payload["past"]["recordCount"], 1)

    def test_clear_selected_date_updates_calendar_trend_and_export(self):
        target = self.make_record("rec_target", "2026-06-30", "08:00", 500)
        today = self.make_record("rec_today", "2026-07-01", "09:00", 750)
        data = {"schema_version": 1, "records": [target, today]}
        body = (
            f"var result = HydrationTrackerV3.clearRecordsForDate({json.dumps(data, ensure_ascii=False)}, '2026-06-30');"
            "var nextData = result.data;"
            "printJson({"
            "summary: HydrationTrackerV3.calculateSummary(nextData, '2026-06-30'),"
            "calendar: HydrationTrackerV3.buildCalendarMonth(nextData, 2026, 5, new Date('2026-07-01T12:00:00')) ,"
            "trend: HydrationTrackerV3.buildRecentTrendData(nextData, new Date('2026-07-01T12:00:00'), 7),"
            "exported: HydrationTrackerV3.buildExportPayload(nextData, new Date('2026-07-01T12:00:00.000Z')).records"
            "});"
        )
        payload = self.run_jxa(body)

        calendar_day = next(
            day for day in payload["calendar"]["days"] if day["date"] == "2026-06-30"
        )
        trend_day = next(
            day for day in payload["trend"]["points"] if day["date"] == "2026-06-30"
        )
        self.assertEqual(payload["summary"]["recordCount"], 0)
        self.assertFalse(calendar_day["hasRecords"])
        self.assertEqual(trend_day["totalWaterMl"], 0)
        self.assertEqual(len(payload["exported"]), 1)

    def test_pwa_never_calls_local_storage_clear(self):
        self.assertNotIn("localStorage.clear()", APP_JS.read_text())
        self.assertNotIn("localStorage.clear()", SERVICE_WORKER.read_text())

    def test_history_view_contains_clear_selected_date_button(self):
        source = INDEX_HTML.read_text()
        self.assertIn('id="history-clear-date"', source)
        self.assertIn("清空这一天", source)
        self.assertIn(
            "确定清空 ${targetDate} 的全部 ${recordCount} 条记录吗？",
            APP_JS.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
