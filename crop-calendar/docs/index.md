# 🌿 作物种植日历下载

> 2026年预生成日历文件，可直接下载 .ics 导入手机日历

| 作物 | 地区 | .ics 日历文件 | .md 日历文件 |
|:-----|:-----|:-------------|:------------|
| 水稻 | 华南地区 | [📥 下载](rice_华南_2026.ics) | [📄 查看](rice_华南_2026.md) |
| 水稻 | 华中地区 | [📥 下载](rice_华中_2026.ics) | [📄 查看](rice_华中_2026.md) |
| 玉米 | 华南地区 | [📥 下载](maize_华南_2026.ics) | [📄 查看](maize_华南_2026.md) |
| 玉米 | 华北地区 | [📥 下载](maize_华北_2026.ics) | [📄 查看](maize_华北_2026.md) |
| 蔬菜（以菜心为例） | 华南地区 | [📥 下载](vegetable_华南_2026.ics) | [📄 查看](vegetable_华南_2026.md) |
| 大豆 | 东北地区 | [📥 下载](soybean_东北_2026.ics) | [📄 查看](soybean_东北_2026.md) |
| 花生 | 华南地区 | [📥 下载](peanut_华南_2026.ics) | [📄 查看](peanut_华南_2026.md) |
| 甘薯 | 华南地区 | [📥 下载](sweet_potato_华南_2026.ics) | [📄 查看](sweet_potato_华南_2026.md) |
| 油菜 | 华中地区 | [📥 下载](rape_华中_2026.ics) | [📄 查看](rape_华中_2026.md) |
| 小麦 | 华北地区 | [📥 下载](wheat_华北_2026.ics) | [📄 查看](wheat_华北_2026.md) |

---

## 📱 导入方法

1. 点击 **📥 下载** 获取 .ics 文件
2. **iPhone**: 通过 AirDrop/邮件发送 → 点击 → 添加到日历
3. **Android**: Google Calendar → 设置 → 导入日历 → 选择 .ics
4. **Outlook**: 文件 → 打开和导出 → 导入日历

## 🛠️ 自定义生成

如果上面的预生成文件不满足需求，可以自行生成：

```bash
git clone https://github.com/koka/crop-calendar.git
cd crop-calendar
python scripts/crop_calendar.py --crop rice --region 华南 --year 2026 --output .
```

支持 8 种作物 × 6 大地区，详见 [README](../README.md)