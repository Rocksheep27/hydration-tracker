"""V1 hydration tracker prototype using only the Python standard library."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "hydration_log.json"
CUP_TO_ML = 250
DEFAULT_DAILY_GOAL_ML = 2000

CATEGORY_WATER = "water"
CATEGORY_BEVERAGE = "beverage"
CATEGORY_FOOD = "food"

WATER_RATIOS = {
    "白水": 1.00,
    "牛奶": 0.87,
    "豆浆": 0.90,
    "咖啡": 0.98,
    "茶": 0.99,
    "汤": 0.95,
    "苹果": 0.86,
    "香蕉": 0.75,
    "桃子": 0.89,
    "西瓜": 0.91,
    "橙子": 0.87,
    "橘子": 0.87,
    "黄瓜": 0.95,
    "西红柿": 0.94,
    "青椒": 0.92,
    "米饭": 0.60,
    "面包": 0.35,
    "馒头": 0.45,
    "鸡蛋": 0.75,
    "鸡胸肉": 0.65,
    "香肠": 0.55,
}

VALID_CATEGORIES = {CATEGORY_WATER, CATEGORY_BEVERAGE, CATEGORY_FOOD}
VALID_UNITS = {"ml", "g", "cup"}

COMMON_ITEM_DEFAULTS = {
    "白水": {
        "category": CATEGORY_WATER,
        "unit": "杯",
        "base_amount": 250,
        "base_unit": "ml",
        "water_ratio": 1.00,
    },
    "牛奶": {
        "category": CATEGORY_BEVERAGE,
        "unit": "杯",
        "base_amount": 250,
        "base_unit": "ml",
        "water_ratio": 0.87,
    },
    "豆浆": {
        "category": CATEGORY_BEVERAGE,
        "unit": "杯",
        "base_amount": 250,
        "base_unit": "ml",
        "water_ratio": 0.90,
    },
    "咖啡": {
        "category": CATEGORY_BEVERAGE,
        "unit": "杯",
        "base_amount": 250,
        "base_unit": "ml",
        "water_ratio": 0.98,
    },
    "茶": {
        "category": CATEGORY_BEVERAGE,
        "unit": "杯",
        "base_amount": 250,
        "base_unit": "ml",
        "water_ratio": 0.99,
    },
    "汤": {
        "category": CATEGORY_BEVERAGE,
        "unit": "碗",
        "base_amount": 300,
        "base_unit": "ml",
        "water_ratio": 0.95,
    },
    "苹果": {
        "category": CATEGORY_FOOD,
        "unit": "个",
        "base_amount": 180,
        "base_unit": "g",
        "water_ratio": 0.86,
    },
    "香蕉": {
        "category": CATEGORY_FOOD,
        "unit": "根",
        "base_amount": 120,
        "base_unit": "g",
        "water_ratio": 0.75,
    },
    "桃子": {
        "category": CATEGORY_FOOD,
        "unit": "个",
        "base_amount": 150,
        "base_unit": "g",
        "water_ratio": 0.89,
    },
    "西瓜": {
        "category": CATEGORY_FOOD,
        "unit": "份",
        "base_amount": 300,
        "base_unit": "g",
        "water_ratio": 0.91,
    },
    "橙子": {
        "category": CATEGORY_FOOD,
        "unit": "个",
        "base_amount": 180,
        "base_unit": "g",
        "water_ratio": 0.87,
    },
    "橘子": {
        "category": CATEGORY_FOOD,
        "unit": "个",
        "base_amount": 100,
        "base_unit": "g",
        "water_ratio": 0.87,
    },
    "黄瓜": {
        "category": CATEGORY_FOOD,
        "unit": "根",
        "base_amount": 200,
        "base_unit": "g",
        "water_ratio": 0.95,
    },
    "西红柿": {
        "category": CATEGORY_FOOD,
        "unit": "个",
        "base_amount": 150,
        "base_unit": "g",
        "water_ratio": 0.94,
    },
    "青椒": {
        "category": CATEGORY_FOOD,
        "unit": "个",
        "base_amount": 100,
        "base_unit": "g",
        "water_ratio": 0.92,
    },
    "米饭": {
        "category": CATEGORY_FOOD,
        "unit": "碗",
        "base_amount": 150,
        "base_unit": "g",
        "water_ratio": 0.60,
    },
    "面包": {
        "category": CATEGORY_FOOD,
        "unit": "片",
        "base_amount": 30,
        "base_unit": "g",
        "water_ratio": 0.35,
    },
    "馒头": {
        "category": CATEGORY_FOOD,
        "unit": "个",
        "base_amount": 100,
        "base_unit": "g",
        "water_ratio": 0.45,
    },
    "鸡蛋": {
        "category": CATEGORY_FOOD,
        "unit": "个",
        "base_amount": 50,
        "base_unit": "g",
        "water_ratio": 0.75,
    },
    "鸡胸肉": {
        "category": CATEGORY_FOOD,
        "unit": "份",
        "base_amount": 100,
        "base_unit": "g",
        "water_ratio": 0.65,
    },
    "香肠": {
        "category": CATEGORY_FOOD,
        "unit": "根",
        "base_amount": 50,
        "base_unit": "g",
        "water_ratio": 0.55,
    },
}

COMMON_ITEM_GROUPS = {
    CATEGORY_WATER: (("饮品/液体", ("白水",)),),
    CATEGORY_BEVERAGE: (
        ("饮品/液体", ("牛奶", "豆浆", "咖啡", "茶", "汤")),
    ),
    CATEGORY_FOOD: (
        ("水果", ("苹果", "香蕉", "桃子", "西瓜", "橙子", "橘子")),
        ("蔬菜", ("黄瓜", "西红柿", "青椒")),
        ("主食", ("米饭", "面包", "馒头")),
        ("蛋白质", ("鸡蛋", "鸡胸肉", "香肠")),
    ),
}

DEFAULT_UNITS = {
    CATEGORY_WATER: "ml",
    CATEGORY_BEVERAGE: "ml",
    CATEGORY_FOOD: "g",
}

MEAL_OPTIONS = (
    ("早餐", "breakfast"),
    ("午餐", "lunch"),
    ("晚餐", "dinner"),
    ("加餐", "snack"),
    ("无餐次", "none"),
)


def ensure_data_file(data_file: Path = DATA_FILE) -> None:
    """Create the local JSON data file if it does not exist."""
    data_file.parent.mkdir(parents=True, exist_ok=True)
    if not data_file.exists():
        save_records([], data_file)


def load_records(data_file: Path = DATA_FILE) -> list[dict[str, Any]]:
    ensure_data_file(data_file)
    with data_file.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("本地数据文件格式不正确，预期为记录列表。")
    return data


def save_records(records: list[dict[str, Any]], data_file: Path = DATA_FILE) -> None:
    data_file.parent.mkdir(parents=True, exist_ok=True)
    with data_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)
        file.write("\n")


def get_default_water_ratio(name: str, category: str) -> float | None:
    if category == CATEGORY_WATER:
        return 1.0
    return WATER_RATIOS.get(name)


def convert_amount_to_base_unit(amount: float, unit: str, category: str) -> float:
    if amount < 0:
        raise ValueError("数量不能为负数。")
    if unit not in VALID_UNITS:
        raise ValueError("单位只支持 ml、g、cup。")

    if unit == "cup":
        return amount * CUP_TO_ML
    if unit == "g" and category != CATEGORY_FOOD:
        raise ValueError("g 单位只适合食物记录。")
    if unit == "ml" and category == CATEGORY_FOOD:
        raise ValueError("食物记录请使用 g，或先按饮料记录液体食物。")
    return amount


def calculate_estimated_water_ml(
    category: str,
    amount: float,
    unit: str,
    water_ratio: float | None,
) -> float:
    if category not in VALID_CATEGORIES:
        raise ValueError("摄入类型只支持 water、beverage、food。")

    base_amount = convert_amount_to_base_unit(amount, unit, category)

    if category == CATEGORY_WATER:
        if unit == "g":
            raise ValueError("白水记录请使用 ml 或 cup。")
        return round(base_amount, 2)

    if water_ratio is None:
        raise ValueError("缺少含水率，请手动输入。")
    if water_ratio < 0 or water_ratio > 1:
        raise ValueError("含水率必须在 0 到 1 之间。")

    return round(base_amount * water_ratio, 2)


def create_record(
    *,
    category: str,
    name: str,
    amount: float,
    unit: str,
    meal: str = "none",
    water_ratio: float | None = None,
    converted_amount: float | None = None,
    converted_unit: str | None = None,
    is_estimated: bool = False,
    note: str = "",
    record_date: str | None = None,
    record_time: str | None = None,
) -> dict[str, Any]:
    if category not in VALID_CATEGORIES:
        raise ValueError("摄入类型只支持 water、beverage、food。")

    ratio = water_ratio
    if ratio is None:
        ratio = get_default_water_ratio(name, category)

    calculation_amount = converted_amount if converted_amount is not None else amount
    calculation_unit = converted_unit or unit
    estimated_water_ml = calculate_estimated_water_ml(
        category=category,
        amount=calculation_amount,
        unit=calculation_unit,
        water_ratio=ratio,
    )

    now = datetime.now()
    return {
        "id": f"rec_{uuid4().hex[:8]}",
        "date": record_date or date.today().isoformat(),
        "time": record_time or now.strftime("%H:%M"),
        "category": category,
        "meal": meal,
        "name": name,
        "amount": amount,
        "unit": unit,
        "converted_amount": calculation_amount,
        "converted_unit": calculation_unit,
        "water_ratio": ratio,
        "estimated_water_ml": estimated_water_ml,
        "is_estimated": is_estimated,
        "note": note,
    }


def create_common_item_record(
    name: str,
    quantity: float,
    *,
    meal: str = "none",
    note: str = "",
    record_date: str | None = None,
    record_time: str | None = None,
) -> dict[str, Any]:
    defaults = COMMON_ITEM_DEFAULTS.get(name)
    if defaults is None:
        raise ValueError("未找到常用项目的估算数据。")

    converted_amount = round(quantity * defaults["base_amount"], 2)
    return create_record(
        category=defaults["category"],
        name=name,
        amount=quantity,
        unit=defaults["unit"],
        meal=meal,
        water_ratio=defaults["water_ratio"],
        converted_amount=converted_amount,
        converted_unit=defaults["base_unit"],
        is_estimated=True,
        note=note,
        record_date=record_date,
        record_time=record_time,
    )


def add_record(record: dict[str, Any], data_file: Path = DATA_FILE) -> dict[str, Any]:
    records = load_records(data_file)
    records.append(record)
    save_records(records, data_file)
    return record


def get_records_for_date(
    records: list[dict[str, Any]], target_date: str
) -> list[dict[str, Any]]:
    return [record for record in records if record.get("date") == target_date]


def delete_record_for_date(
    target_date: str,
    record_number: int,
    data_file: Path = DATA_FILE,
) -> dict[str, Any]:
    records = load_records(data_file)
    matching_positions = [
        index
        for index, record in enumerate(records)
        if record.get("date") == target_date
    ]
    if record_number < 1 or record_number > len(matching_positions):
        raise ValueError("记录序号不存在。")

    removed = records.pop(matching_positions[record_number - 1])
    save_records(records, data_file)
    return removed


def clear_records_for_date(
    target_date: str, data_file: Path = DATA_FILE
) -> int:
    records = load_records(data_file)
    kept_records = [
        record for record in records if record.get("date") != target_date
    ]
    removed_count = len(records) - len(kept_records)
    if removed_count:
        save_records(kept_records, data_file)
    return removed_count


def calculate_daily_total(records: list[dict[str, Any]], target_date: str) -> float:
    total = 0.0
    for record in records:
        if record.get("date") == target_date:
            estimated = record.get("estimated_water_ml", 0)
            if isinstance(estimated, (int, float)):
                total += estimated
    return round(total, 2)


def calculate_completion_rate(total_ml: float, goal_ml: float) -> float:
    if goal_ml <= 0:
        raise ValueError("目标水量必须大于 0。")
    return round((total_ml / goal_ml) * 100, 2)


def calculate_remaining_ml(total_ml: float, goal_ml: float) -> float:
    if goal_ml <= 0:
        raise ValueError("目标水量必须大于 0。")
    return round(max(goal_ml - total_ml, 0), 2)


def prompt_float(prompt: str, default: float | None = None) -> float:
    while True:
        value = input(prompt).strip()
        if not value and default is not None:
            return default
        try:
            return float(value)
        except ValueError:
            print("请输入数字。")


def prompt_water_ratio() -> float:
    while True:
        value = prompt_float("含水率估算值（0 到 1，例如 0.87）：")
        if 0 <= value <= 1:
            return value
        print("含水率必须在 0 到 1 之间。")


def prompt_common_item(category: str) -> tuple[str, bool]:
    items = []
    print("常用项目（默认重量、容量和含水率均为估算值）：")
    for group_name, group_items in COMMON_ITEM_GROUPS[category]:
        print(f"[{group_name}]")
        for item in group_items:
            items.append(item)
            defaults = COMMON_ITEM_DEFAULTS[item]
            amount = format_number(defaults["base_amount"])
            print(
                f"{len(items)}. {item}"
                f"（1 {defaults['unit']}约 {amount} {defaults['base_unit']}）"
            )
    print("0. 精确输入（手动输入名称和 g/ml）")

    while True:
        choice = input("请选择（直接回车选择 1）：").strip()
        if not choice:
            return items[0], True
        if choice == "0":
            while True:
                name = input("名称：").strip()
                if name:
                    return name, False
                print("名称不能为空。")
        if choice.isdigit() and 1 <= int(choice) <= len(items):
            return items[int(choice) - 1], True
        print(f"请输入 0 到 {len(items)}。")


def prompt_unit(category: str) -> str:
    default_unit = DEFAULT_UNITS[category]
    while True:
        unit = input(
            f"单位（ml/g/cup，直接回车使用 {default_unit}）："
        ).strip().lower()
        unit = unit or default_unit
        try:
            convert_amount_to_base_unit(0, unit, category)
        except ValueError as error:
            print(error)
            continue
        return unit


def prompt_meal() -> str:
    print("餐次：")
    for index, (label, _) in enumerate(MEAL_OPTIONS, start=1):
        print(f"{index}. {label}")

    while True:
        choice = input("请选择餐次（直接回车选择无餐次）：").strip()
        if not choice:
            return "none"
        if choice.isdigit() and 1 <= int(choice) <= len(MEAL_OPTIONS):
            return MEAL_OPTIONS[int(choice) - 1][1]
        print(f"请输入 1 到 {len(MEAL_OPTIONS)}。")


def format_number(value: float) -> str:
    rounded = round(float(value), 1)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.1f}"


def format_water_ratio(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return "未知"


def display_records_for_date(
    records: list[dict[str, Any]], target_date: str
) -> list[dict[str, Any]]:
    daily_records = get_records_for_date(records, target_date)
    print(f"\n{target_date} 记录明细")
    if not daily_records:
        print("今天还没有记录。")
        return []

    for index, record in enumerate(daily_records, start=1):
        amount = record.get("amount", 0)
        unit = record.get("unit", "未知")
        converted_amount = record.get("converted_amount", amount)
        converted_unit = record.get("converted_unit", unit)
        estimated_water = record.get("estimated_water_ml", 0)
        print(
            f"{index}. {record.get('time', '--:--')} | "
            f"{record.get('name', '未命名')} | "
            f"原始：{format_number(amount)} {unit} | "
            f"换算：约 {format_number(converted_amount)} {converted_unit} | "
            f"含水率：{format_water_ratio(record.get('water_ratio'))} | "
            f"估算水分：{format_number(estimated_water)} ml"
        )
    return daily_records


def show_today_records(data_file: Path = DATA_FILE) -> list[dict[str, Any]]:
    records = load_records(data_file)
    return display_records_for_date(records, date.today().isoformat())


def prompt_delete_today_record(data_file: Path = DATA_FILE) -> None:
    daily_records = show_today_records(data_file)
    if not daily_records:
        return

    choice = input("请输入要删除的记录序号（直接回车取消）：").strip()
    if not choice:
        print("已取消删除。")
        return
    if not choice.isdigit() or not 1 <= int(choice) <= len(daily_records):
        print("记录序号不存在，未删除任何记录。")
        return

    selected = daily_records[int(choice) - 1]
    confirm = input(
        f"确认删除“{selected.get('name', '未命名')}”？输入 y 确认："
    ).strip().lower()
    if confirm != "y":
        print("已取消删除。")
        return

    removed = delete_record_for_date(
        date.today().isoformat(), int(choice), data_file
    )
    print(f"已删除：{removed.get('name', '未命名')}。")


def prompt_clear_today_records(data_file: Path = DATA_FILE) -> None:
    records = load_records(data_file)
    today = date.today().isoformat()
    daily_records = get_records_for_date(records, today)
    if not daily_records:
        print("今天还没有记录，无需清空。")
        return

    print(f"今天共有 {len(daily_records)} 条记录。")
    confirm = input("确认清空今天全部记录？输入 CLEAR 确认：").strip()
    if confirm != "CLEAR":
        print("已取消清空。")
        return

    removed_count = clear_records_for_date(today, data_file)
    print(f"已清空今天的 {removed_count} 条记录。")


def prompt_common_record(category: str) -> dict[str, Any]:
    name, uses_common_estimate = prompt_common_item(category)
    if uses_common_estimate:
        defaults = COMMON_ITEM_DEFAULTS[name]
        amount = prompt_float(
            f"数量（{defaults['unit']}，直接回车使用 1）：",
            default=1,
        )
    else:
        amount = prompt_float("精确数量：")
        unit = prompt_unit(category)

    meal = "none"
    if category == CATEGORY_FOOD:
        meal = prompt_meal()
    note = input("备注（可直接回车跳过）：").strip()

    if uses_common_estimate:
        return create_common_item_record(
            name,
            amount,
            meal=meal,
            note=note,
        )

    ratio = get_default_water_ratio(name, category)
    if ratio is None:
        ratio = prompt_water_ratio()

    return create_record(
        category=category,
        name=name,
        amount=amount,
        unit=unit,
        meal=meal,
        water_ratio=ratio,
        is_estimated=category != CATEGORY_WATER,
        note=note,
    )


def show_today_progress(data_file: Path = DATA_FILE) -> None:
    records = load_records(data_file)
    today = date.today().isoformat()
    total = calculate_daily_total(records, today)
    rate = calculate_completion_rate(total, DEFAULT_DAILY_GOAL_ML)
    remaining = calculate_remaining_ml(total, DEFAULT_DAILY_GOAL_ML)

    print("\n今日进度")
    print(f"日期：{today}")
    print(f"今日总水分摄入（估算）：{format_number(total)} ml")
    print(f"目标完成率：{format_number(rate)}%")
    print(f"还差：{format_number(remaining)} ml")
    print("可选择“查看今日记录明细”核对每条数据。")


def run_menu() -> None:
    ensure_data_file()

    while True:
        print("\nHydrationTracker V1")
        print("1. 添加白水记录")
        print("2. 添加饮料记录")
        print("3. 添加食物记录")
        print("4. 查看今日进度")
        print("5. 查看今日记录明细")
        print("6. 删除某条记录")
        print("7. 清空今日记录")
        print("8. 退出")

        choice = input("请选择：").strip()

        try:
            if choice == "1":
                record = prompt_common_record(CATEGORY_WATER)
                add_record(record)
                water_ml = format_number(record["estimated_water_ml"])
                print(f"已添加，估算水分：{water_ml} ml（估算值）")
            elif choice == "2":
                record = prompt_common_record(CATEGORY_BEVERAGE)
                add_record(record)
                water_ml = format_number(record["estimated_water_ml"])
                print(f"已添加，估算水分：{water_ml} ml（估算值）")
            elif choice == "3":
                record = prompt_common_record(CATEGORY_FOOD)
                add_record(record)
                water_ml = format_number(record["estimated_water_ml"])
                print(f"已添加，估算水分：{water_ml} ml（估算值）")
            elif choice == "4":
                show_today_progress()
            elif choice == "5":
                show_today_records()
            elif choice == "6":
                prompt_delete_today_record()
            elif choice == "7":
                prompt_clear_today_records()
            elif choice == "8":
                print("已退出。")
                break
            else:
                print("请输入 1 到 8。")
        except ValueError as error:
            print(f"无法保存记录：{error}")


if __name__ == "__main__":
    run_menu()
