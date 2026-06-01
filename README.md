# 🌿 crop-calendar — 作物种植日历生成器

> 输入地区 + 作物 → 生成全年种植管理日历（播种期/施肥期/收获期），可导出 .ics 到手机日历

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 功能特色

- 🗓️ **一键生成** — 输入地区和作物，自动生成全年种植管理日历
- 📱 **导出 .ics** — 导入手机日历（Apple Calendar / Google Calendar / Outlook），带提醒
- 📝 **导出 Markdown** — 生成漂亮的种植日历文档
- 🌾 **8 种作物** — 水稻/玉米/蔬菜/大豆/花生/甘薯/油菜/小麦
- 🗺️ **6 大地区** — 华南/华中/华东/华北/东北/西南
- 🧪 **智能施肥提醒** — 根据播种日自动推算追肥时间
- 💡 **农业建议** — 结合华南农业大学农艺与种业知识，提供种植要点

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/koka/crop-calendar.git
cd crop-calendar
# 无需安装依赖，纯 Python 标准库
```

### 命令行模式

```bash
# 生成华南地区2026年水稻种植日历
python scripts/crop_calendar.py --crop rice --region 华南 --year 2026 --output .

# 列出所有可用作物
python scripts/crop_calendar.py --list-crops

# 列出所有可用地区
python scripts/crop_calendar.py --list-regions

# 交互式模式（引导选择）
python scripts/crop_calendar.py --interactive
```

### 作为 Python 库使用

```python
from scripts.crop_calendar import generate_calendar

# 生成日历
events, ics_content, md_content = generate_calendar(
    crop_key="rice",
    region="华南",
    year=2026,
    output_path="./output"  # 可选，指定则自动写入文件
)

# 获取事件列表
for ev in events:
    print(f"{ev['label']}: {ev['start'].strftime('%m/%d')} - {ev['end'].strftime('%m/%d')}")

# 获取 .ics 内容（可直接写入文件或通过 API 发送）
with open("my_calendar.ics", "w", encoding="utf-8") as f:
    f.write(ics_content)
```

## 📱 导入手机日历

1. 运行命令生成 `.ics` 文件
2. **iPhone**: 通过 AirDrop / 邮件发送 → 点击打开 → 添加到日历
3. **Android**: 通过 Google Calendar 网页版 → 设置 → 导入日历 → 选择 .ics 文件
4. **Outlook**: 文件 → 打开和导出 → 导入日历

## 📋 可用作物

| 代码 | 作物 | 适种地区 |
|------|------|---------|
| `rice` | 水稻（早稻/晚稻） | 华南、华中、华东、西南 |
| `maize` | 玉米（春/夏） | 全国 |
| `vegetable` | 蔬菜-菜心（春/秋） | 华南 |
| `soybean` | 大豆 | 华南、华中、东北、华北 |
| `peanut` | 花生 | 华南、华中、华东 |
| `sweet_potato` | 甘薯 | 华南、华中、华北 |
| `rape` | 油菜 | 华中、华东、西南 |
| `wheat` | 小麦 | 华北、华中、西南 |

## 🗺️ 可用地区

| 代码 | 地区 | 气候特征 |
|------|------|---------|
| `华南` | 华南地区 | 亚热带，年均20-25°C，双季稻，台风季7-9月 |
| `华中` | 华中地区 | 亚热带，年均15-20°C，稻麦轮作 |
| `华东` | 华东地区 | 亚热带，年均14-20°C，梅雨和伏旱 |
| `华北` | 华北地区 | 温带，年均10-15°C，冬小麦-夏玉米轮作 |
| `东北` | 东北地区 | 温带，年均3-8°C，一年一熟 |
| `西南` | 西南地区 | 亚热带，立体气候，垂直农业 |

## 📂 项目结构

```
crop-calendar/
├── README.md
├── LICENSE
├── scripts/
│   └── crop_calendar.py    # 主脚本（CLI + 库）
├── data/
│   ├── crops.json          # 作物种植数据
│   └── regions.json        # 地区气候数据
└── output/                 # 生成文件输出目录（gitignore）
```

## 🧩 扩展数据

要添加新作物，编辑 `data/crops.json`：

```json
{
  "tomato": {
    "name_zh": "番茄",
    "name_en": "Tomato",
    "suitable_regions": ["华南", "华中"],
    "seasons": [
      {
        "type": "春番茄",
        "sow_start": "02-01",
        "sow_end": "03-15",
        "transplant_start": "03-15",
        "transplant_end": "04-15",
        "harvest_start": "06-01",
        "harvest_end": "08-31",
        "fertilizer_days_after_sow": [15, 45],
        "notes": "华南春番茄注意防青枯病"
      }
    ]
  }
}
```

## 📄 License

MIT License — 自由使用、修改、分发

## 🙏 致谢

- 种植数据参考华南农业大学农艺与种业专业教材
- 农业农村部《农作物种植区域划分》
- 各省农业技术推广中心种植历
