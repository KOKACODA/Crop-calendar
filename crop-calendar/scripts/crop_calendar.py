#!/usr/bin/env python3
"""
crop-calendar — 作物种植日历生成器
输入地区 + 作物 → 生成全年种植管理日历，可导出 .ics 日历文件
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

# Windows GBK 终端兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── 数据加载 ──────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


CROPS = load_json("crops.json")
REGIONS = load_json("regions.json")


# ── 日期工具 ──────────────────────────────────────────────

def parse_date(date_str, year):
    """将 MM-DD 字符串转为当年 datetime"""
    month, day = map(int, date_str.split("-"))
    return datetime(year, month, day)


def date_range_text(start_str, end_str, year):
    """生成日期范围中文描述"""
    s = parse_date(start_str, year)
    e = parse_date(end_str, year)
    return f"{s.month}月{s.day}日 — {e.month}月{e.day}日"


# ── .ics 生成 ────────────────────────────────────────────

ICS_HEADER = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//crop-calendar//作物种植日历//CN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:作物种植日历
X-WR-TIMEZONE:Asia/Shanghai
"""

ICS_FOOTER = "END:VCALENDAR"

# 事件模板
EVENT_TEMPLATES = {
    "sow": {"prefix": "🌱 播种", "alarm_min": 3},
    "transplant": {"prefix": "🌾 移栽", "alarm_min": 3},
    "fertilizer": {"prefix": "🧪 追肥", "alarm_min": 1},
    "harvest": {"prefix": "🌾 收获", "alarm_min": 5},
}


def _dt_to_ical(dt):
    """datetime → iCal DTSTART/DTEND 格式"""
    return dt.strftime("%Y%m%dT080000")


def _uid(crop_key, season_type, event_type, idx, year):
    return f"crop-cal-{crop_key}-{season_type}-{event_type}-{idx}-{year}@crop-calendar"


def make_vevent(uid, summary, dt_start, dt_end, description="", alarm_min=None):
    """生成单个 VEVENT 块"""
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTART;TZID=Asia/Shanghai:{_dt_to_ical(dt_start)}",
        f"DTEND;TZID=Asia/Shanghai:{_dt_to_ical(dt_end)}",
        f"SUMMARY:{summary}",
    ]
    if description:
        lines.append(f"DESCRIPTION:{description}")
    if alarm_min is not None:
        lines += [
            "BEGIN:VALARM",
            "TRIGGER:-PT{}M".format(alarm_min * 24 * 60),  # days before → minutes
            "ACTION:DISPLAY",
            f"DESCRIPTION:{summary} 提醒",
            "END:VALARM",
        ]
    lines.append("END:VEVENT")
    return "\n".join(lines)


# ── 日历生成逻辑 ─────────────────────────────────────────

def generate_calendar(crop_key, region, year, output_path=None):
    """生成种植日历，返回 (events_list, ics_content, markdown_content)"""

    if crop_key not in CROPS:
        available = ", ".join(f"{k}({v['name_zh']})" for k, v in CROPS.items())
        print(f"❌ 未知作物: {crop_key}", file=sys.stderr)
        print(f"   可用作物: {available}", file=sys.stderr)
        sys.exit(1)

    if region not in REGIONS:
        available = ", ".join(f"{k}({v['name_zh']})" for k, v in REGIONS.items())
        print(f"❌ 未知地区: {region}", file=sys.stderr)
        print(f"   可用地区: {available}", file=sys.stderr)
        sys.exit(1)

    crop = CROPS[crop_key]
    region_info = REGIONS[region]

    # 检查作物是否适合该地区
    if region not in crop["suitable_regions"]:
        print(f"⚠️  {crop['name_zh']}主要适种区域为{'、'.join(crop['suitable_regions'])}，{region_info['name_zh']}可能不是最佳选择")

    events = []
    vevents = []

    for season in crop["seasons"]:
        season_type = season["type"]

        # 1) 播种期
        sow_start = parse_date(season["sow_start"], year)
        sow_end = parse_date(season["sow_end"], year)
        events.append({
            "type": "sow", "label": f"🌱 {crop['name_zh']}（{season_type}）播种期",
            "start": sow_start, "end": sow_end,
            "desc": f"{crop['name_zh']}（{season_type}）播种窗口期"
        })

        # 2) 移栽期（如果有）
        if "transplant_start" in season:
            tp_start = parse_date(season["transplant_start"], year)
            tp_end = parse_date(season["transplant_end"], year)
            events.append({
                "type": "transplant", "label": f"🌾 {crop['name_zh']}（{season_type}）移栽期",
                "start": tp_start, "end": tp_end,
                "desc": f"{crop['name_zh']}（{season_type}）移栽窗口期"
            })

        # 3) 追肥日期（基于播种日推算）
        for i, days in enumerate(season.get("fertilizer_days_after_sow", [])):
            f_date = sow_start + timedelta(days=days)
            f_end = f_date + timedelta(days=1)
            nth = ["第一次", "第二次", "第三次", "第四次"][i] if i < 4 else f"第{i+1}次"
            events.append({
                "type": "fertilizer", "label": f"🧪 {crop['name_zh']}（{season_type}）{nth}追肥",
                "start": f_date, "end": f_end,
                "desc": f"播种后{days}天，{crop['name_zh']}（{season_type}）{nth}追肥"
            })

        # 4) 收获期
        hv_start = parse_date(season["harvest_start"], year)
        hv_end = parse_date(season["harvest_end"], year)
        events.append({
            "type": "harvest", "label": f"🌾 {crop['name_zh']}（{season_type}）收获期",
            "start": hv_start, "end": hv_end,
            "desc": f"{crop['name_zh']}（{season_type}）收获窗口期"
        })

    # 按日期排序
    events.sort(key=lambda e: e["start"])

    # 生成 .ics
    for i, ev in enumerate(events):
        tpl = EVENT_TEMPLATES.get(ev["type"], {"prefix": "", "alarm_min": None})
        vevents.append(make_vevent(
            uid=_uid(crop_key, ev["type"], ev["type"], i, year),
            summary=ev["label"],
            dt_start=ev["start"],
            dt_end=ev["end"],
            description=ev.get("desc", ""),
            alarm_min=tpl.get("alarm_min"),
        ))

    ics_content = ICS_HEADER + "\n".join(vevents) + "\n" + ICS_FOOTER

    # 生成 Markdown
    md_lines = [
        f"# {crop['name_zh']}（{crop['name_en']}）种植日历",
        f"",
        f"**地区：** {region_info['name_zh']}（{region_info['climate']}）",
        f"**年份：** {year}年",
        f"",
        f"---",
        f"",
    ]

    for season in crop["seasons"]:
        season_type = season["type"]
        md_lines.append(f"## {season_type}")
        md_lines.append("")
        sow_range = date_range_text(season["sow_start"], season["sow_end"], year)
        hv_range = date_range_text(season["harvest_start"], season["harvest_end"], year)

        md_lines.append(f"| 事项 | 时间 |")
        md_lines.append(f"|:-----|:-----|")
        md_lines.append(f"| 🌱 播种期 | {sow_range} |")

        if "transplant_start" in season:
            tp_range = date_range_text(season["transplant_start"], season["transplant_end"], year)
            md_lines.append(f"| 🌾 移栽期 | {tp_range} |")

        for i, days in enumerate(season.get("fertilizer_days_after_sow", [])):
            f_date = parse_date(season["sow_start"], year) + timedelta(days=days)
            nth = ["第一次", "第二次", "第三次", "第四次"][i] if i < 4 else f"第{i+1}次"
            md_lines.append(f"| 🧪 {nth}追肥 | {f_date.month}月{f_date.day}日（播种后{days}天） |")

        md_lines.append(f"| 🌾 收获期 | {hv_range} |")
        md_lines.append(f"| 💡 备注 | {season.get('notes', '')} |")
        md_lines.append("")

    md_lines += [
        "---",
        "",
        f"> 📌 数据来源：华南农业大学农艺与种业知识库",
        f"> 📌 生成工具：[crop-calendar](https://github.com/koka/crop-calendar)",
        f"> 📌 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]

    md_content = "\n".join(md_lines)

    # 写文件
    if output_path:
        os.makedirs(output_path, exist_ok=True)

        ics_file = os.path.join(output_path, f"{crop_key}_{region}_{year}.ics")
        with open(ics_file, "w", encoding="utf-8") as f:
            f.write(ics_content)
        print(f"✅ .ics 日历文件: {ics_file}")

        md_file = os.path.join(output_path, f"{crop_key}_{region}_{year}.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"✅ .md 日历文件: {md_file}")

    return events, ics_content, md_content


# ── 命令行交互 ────────────────────────────────────────────

def list_crops():
    print("\n📋 可用作物列表：")
    print("-" * 50)
    for key, crop in CROPS.items():
        regions = "、".join(crop["suitable_regions"])
        print(f"  {key:15s} {crop['name_zh']:8s} 适种: {regions}")
    print()


def list_regions():
    print("\n🗺️  可用地区列表：")
    print("-" * 50)
    for key, region in REGIONS.items():
        print(f"  {key:6s} {region['name_zh']:8s} {region['climate']}")
    print()


def interactive_mode():
    """交互式选择模式"""
    print("=" * 50)
    print("  🌿 crop-calendar — 作物种植日历生成器")
    print("  输入地区 + 作物，生成全年种植管理日历")
    print("=" * 50)

    list_regions()
    region = input("👉 请选择地区（如 华南）: ").strip()
    if region not in REGIONS:
        print(f"❌ 未知地区: {region}")
        return

    list_crops()
    crop_key = input("👉 请选择作物（如 rice）: ").strip()
    if crop_key not in CROPS:
        print(f"❌ 未知作物: {crop_key}")
        return

    year = input("👉 请输入年份（默认2026）: ").strip()
    if not year:
        year = "2026"
    year = int(year)

    output = input("👉 输出目录（留空=当前目录）: ").strip() or "."

    generate_calendar(crop_key, region, year, output)


def main():
    parser = argparse.ArgumentParser(
        description="🌿 crop-calendar — 作物种植日历生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python crop_calendar.py --crop rice --region 华南 --year 2026 --output .
  python crop_calendar.py --list-crops
  python crop_calendar.py --interactive
        """,
    )
    parser.add_argument("--crop", "-c", help="作物代码（如 rice, maize, vegetable）")
    parser.add_argument("--region", "-r", help="地区（如 华南, 华中, 华北）")
    parser.add_argument("--year", "-y", type=int, default=2026, help="年份（默认2026）")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--list-crops", action="store_true", help="列出所有可用作物")
    parser.add_argument("--list-regions", action="store_true", help="列出所有可用地区")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")

    args = parser.parse_args()

    if args.list_crops:
        list_crops()
        return
    if args.list_regions:
        list_regions()
        return
    if args.interactive:
        interactive_mode()
        return

    if not args.crop or not args.region:
        parser.print_help()
        print("\n⚠️  --crop 和 --region 为必填参数，或使用 --interactive 进入交互模式")
        sys.exit(1)

    generate_calendar(args.crop, args.region, args.year, args.output)


if __name__ == "__main__":
    main()
