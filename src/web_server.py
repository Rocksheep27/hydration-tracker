"""Local web server for HydrationTracker V2.3."""

from __future__ import annotations

import json
import math
from datetime import date
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import hydration_tracker as tracker


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "web"
HOST = "127.0.0.1"
PORT = 8000
MAX_REQUEST_BODY_BYTES = 16_384
VALID_MEALS = {value for _, value in tracker.MEAL_OPTIONS}


def build_today_summary(
    data_file: Path = tracker.DATA_FILE,
    target_date: str | None = None,
) -> dict[str, int | float]:
    records = tracker.load_records(data_file)
    today = target_date or date.today().isoformat()
    daily_records = tracker.get_records_for_date(records, today)
    total = tracker.calculate_daily_total(records, today)
    target = tracker.DEFAULT_DAILY_GOAL_ML

    return {
        "total_water_ml": total,
        "target_ml": target,
        "completion_rate": tracker.calculate_completion_rate(total, target),
        "remaining_ml": tracker.calculate_remaining_ml(total, target),
        "record_count": len(daily_records),
    }


def get_api_response(
    path: str, data_file: Path = tracker.DATA_FILE
) -> tuple[int, dict[str, Any]] | None:
    try:
        if path == "/api/today":
            return 200, build_today_summary(data_file)
        if path == "/api/records/today":
            records = tracker.load_records(data_file)
            today = date.today().isoformat()
            return 200, {"records": tracker.get_records_for_date(records, today)}
        if path == "/api/common-items":
            return 200, {
                "items": [
                    {"name": name, **defaults}
                    for name, defaults in tracker.COMMON_ITEM_DEFAULTS.items()
                ]
            }
        return None
    except (OSError, ValueError):
        return 500, {"error": "无法读取本地记录。"}


def delete_api_response(
    path: str,
    data_file: Path = tracker.DATA_FILE,
) -> tuple[int, dict[str, Any]]:
    today = date.today().isoformat()

    if path == "/api/records/today":
        try:
            deleted_count = tracker.clear_records_for_date(today, data_file)
            return 200, {
                "message": "今日记录已清空。",
                "deleted_count": deleted_count,
            }
        except (OSError, ValueError):
            return 500, {"error": "无法清空今日记录。"}

    prefix = "/api/records/"
    if not path.startswith(prefix):
        return 404, {"error": "接口不存在。"}

    record_id = unquote(path[len(prefix) :])
    if not record_id or "/" in record_id or len(record_id) > 100:
        return 400, {"error": "记录 id 无效。"}

    try:
        records = tracker.load_records(data_file)
        matching_index = next(
            (
                index
                for index, record in enumerate(records)
                if record.get("date") == today and record.get("id") == record_id
            ),
            None,
        )
        if matching_index is None:
            return 404, {"error": "今天没有找到这条记录。"}

        removed = records.pop(matching_index)
        tracker.save_records(records, data_file)
        return 200, {
            "message": "记录已删除。",
            "deleted_record": removed,
        }
    except (OSError, ValueError):
        return 500, {"error": "无法删除本地记录。"}


def validate_record_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("请求内容必须是 JSON 对象。")

    category = payload.get("category")
    if not isinstance(category, str) or category not in tracker.VALID_CATEGORIES:
        raise ValueError("请选择有效的记录类型。")

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("请选择常用项目。")
    name = name.strip()
    defaults = tracker.COMMON_ITEM_DEFAULTS.get(name)
    if defaults is None:
        raise ValueError("所选项目不在常用项目库中。")
    if defaults["category"] != category:
        raise ValueError("项目与记录类型不匹配。")

    quantity = payload.get("quantity")
    if isinstance(quantity, bool) or not isinstance(quantity, (int, float)):
        raise ValueError("数量必须是大于 0 的数字。")
    try:
        quantity = float(quantity)
    except (OverflowError, ValueError):
        raise ValueError("数量必须是大于 0 的数字。") from None
    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError("数量必须是大于 0 的数字。")

    meal = payload.get("meal", "none")
    if not isinstance(meal, str) or meal not in VALID_MEALS:
        raise ValueError("请选择有效的餐次。")

    note = payload.get("note", "")
    if not isinstance(note, str):
        raise ValueError("备注必须是文字。")
    note = note.strip()
    if len(note) > 500:
        raise ValueError("备注不能超过 500 个字符。")

    return {
        "category": category,
        "name": name,
        "quantity": quantity,
        "meal": meal,
        "note": note,
    }


def post_api_response(
    path: str,
    payload: Any,
    data_file: Path = tracker.DATA_FILE,
) -> tuple[int, dict[str, Any]]:
    if path != "/api/records":
        return 404, {"error": "接口不存在。"}

    try:
        values = validate_record_payload(payload)
    except ValueError as error:
        return 400, {"error": str(error)}

    try:
        record = tracker.create_common_item_record(
            values["name"],
            values["quantity"],
            meal=values["meal"],
            note=values["note"],
        )
        tracker.add_record(record, data_file)
        return 201, {
            "message": "记录已保存。",
            "estimated_water_ml": record["estimated_water_ml"],
            "record": record,
        }
    except (OSError, ValueError):
        return 500, {"error": "无法保存本地记录。"}


class HydrationWebHandler(SimpleHTTPRequestHandler):
    """Serve the local pages and their JSON endpoints."""

    data_file = tracker.DATA_FILE

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        api_response = get_api_response(path, self.data_file)
        if api_response is not None:
            status, payload = api_response
            self.send_json(payload, status=status)
            return

        self.path = "/index.html" if path == "/" else path
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/records":
            self.send_json({"error": "接口不存在。"}, status=404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0 or content_length > MAX_REQUEST_BODY_BYTES:
            self.send_json({"error": "请求内容大小无效。"}, status=400)
            return

        try:
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json({"error": "请求内容不是有效 JSON。"}, status=400)
            return

        status, response = post_api_response(path, payload, self.data_file)
        self.send_json(response, status=status)

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        status, response = delete_api_response(path, self.data_file)
        self.send_json(response, status=status)

    def send_json(self, payload: dict[str, Any], status: int) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def create_server(
    host: str = HOST,
    port: int = PORT,
    data_file: Path = tracker.DATA_FILE,
) -> HTTPServer:
    class ConfiguredHydrationWebHandler(HydrationWebHandler):
        pass

    ConfiguredHydrationWebHandler.data_file = data_file
    handler = partial(ConfiguredHydrationWebHandler, directory=str(WEB_ROOT))
    return HTTPServer((host, port), handler)


def run_server() -> None:
    server = create_server()
    print(f"HydrationTracker V2.3 已启动：http://{HOST}:{PORT}")
    print("数据仅保存在本机，按 Control-C 停止。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止。")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
