#!/usr/bin/env python3
"""
预生成常见作物×地区的日历文件，放到 docs/ 目录供 GitHub Pages 展示
也可以直接放在 release 里供下载
"""

import os
import sys

# Windows GBK 兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crop_calendar import generate_calendar, CROPS, REGIONS

YEAR = 2026
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")

# 预设组合：最常用的地区+作物搭配
PRESETS = [
    ("rice", "华南"),
    ("rice", "华中"),
    ("maize", "华南"),
    ("maize", "华北"),
    ("vegetable", "华南"),
    ("soybean", "东北"),
    ("peanut", "华南"),
    ("sweet_potato", "华南"),
    ("rape", "华中"),
    ("wheat", "华北"),
]

# 生成索引页
index_lines = [
    "# 🌿 作物种植日历下载",
    "",
    f"> {YEAR}年预生成日历文件，可直接下载 .ics 导入手机日历",
    "",
    "| 作物 | 地区 | .ics 日历文件 | .md 日历文件 |",
    "|:-----|:-----|:-------------|:------------|",
]


def main():
    global index_lines
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for crop_key, region in PRESETS:
        try:
            generate_calendar(crop_key, region, YEAR, OUTPUT_DIR)
            crop_name = CROPS[crop_key]["name_zh"]
            region_name = REGIONS[region]["name_zh"]
            ics_name = f"{crop_key}_{region}_{YEAR}.ics"
            md_name = f"{crop_key}_{region}_{YEAR}.md"
            index_lines.append(
                f"| {crop_name} | {region_name} | [📥 下载]({ics_name}) | [📄 查看]({md_name}) |"
            )
            print(f"  ✅ {crop_name} × {region_name}")
        except Exception as e:
            print(f"  ❌ {crop_key} × {region}: {e}")

    # 写索引页
    index_lines += [
        "",
        "---",
        "",
        "## 📱 导入方法",
        "",
        "1. 点击 **📥 下载** 获取 .ics 文件",
        "2. **iPhone**: 通过 AirDrop/邮件发送 → 点击 → 添加到日历",
        "3. **Android**: Google Calendar → 设置 → 导入日历 → 选择 .ics",
        "4. **Outlook**: 文件 → 打开和导出 → 导入日历",
        "",
        "## 🛠️ 自定义生成",
        "",
        "如果上面的预生成文件不满足需求，可以自行生成：",
        "",
        "```bash",
        "git clone https://github.com/koka/crop-calendar.git",
        "cd crop-calendar",
        f"python scripts/crop_calendar.py --crop rice --region 华南 --year {YEAR} --output .",
        "```",
        "",
        "支持 8 种作物 × 6 大地区，详见 [README](../README.md)",
    ]

    index_path = os.path.join(OUTPUT_DIR, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))
    print(f"\n✅ 索引页: {index_path}")


if __name__ == "__main__":
    main()
