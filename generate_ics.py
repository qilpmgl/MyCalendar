#!/usr/bin/env python3
"""
中国黄历 ICS 日历生成器

生成一个 .ics 文件，每天一个全天事件，包含完整的黄历信息。
可直接导入或订阅到 iPhone 系统日历。

数据来源：cnlunar 库（基于《钦定协纪辨方书》）
"""

import cnlunar
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from hashlib import md5
import argparse
import sys


def get_lunar_info(dt: datetime) -> dict:
    """获取指定日期的全部黄历信息"""
    a = cnlunar.Lunar(dt)

    # 农历月份：去掉"大/小"后缀，保留简洁名称
    lunar_month = a.lunarMonthCn.replace("大", "").replace("小", "")
    leap_prefix = "闰" if a.isLunarLeapMonth else ""
    lunar_date_str = f"{leap_prefix}{lunar_month}{a.lunarDayCn}"

    # 节气
    solar_term = a.todaySolarTerms if a.todaySolarTerms != "无" else ""

    # 宜忌：取前几个核心项，避免标题过长
    yi_list = a.goodThing or []
    ji_list = a.badThing or []
    yi_short = " ".join(yi_list[:4])
    ji_short = " ".join(ji_list[:4])
    yi_full = " ".join(yi_list)
    ji_full = " ".join(ji_list)

    return {
        "lunar_date": lunar_date_str,
        "year_ganzhi": a.year8Char,
        "month_ganzhi": a.month8Char,
        "day_ganzhi": a.day8Char,
        "zodiac": a.chineseYearZodiac,
        "solar_term": solar_term,
        "yi_short": yi_short,
        "ji_short": ji_short,
        "yi_full": yi_full,
        "ji_full": ji_full,
        "good_gods": a.goodGodName or [],
        "bad_gods": a.badGodName or [],
        "zodiac_clash": a.chineseZodiacClash,
        "day_officer": a.today12DayOfficer,
        "star28": a.today28Star,
        "phase_of_moon": a.phaseOfMoon,
        "level_name": a.todayLevelName,
        "next_solar_term": a.nextSolarTerm,
        "next_solar_term_date": a.nextSolarTermDate,
    }


def build_summary(info: dict) -> str:
    """构建日历事件标题（简洁版，系统日历列表视图可读）"""
    parts = [info["lunar_date"], info["day_ganzhi"]]
    if info["solar_term"]:
        parts.append(f"【{info['solar_term']}】")
    if info["yi_short"]:
        parts.append(f"宜:{info['yi_short']}")
    return " ".join(parts)


def build_description(info: dict, solar_date: datetime) -> str:
    """构建日历事件详细描述"""
    lines = [
        f"📅 公历：{solar_date.strftime('%Y年%m月%d日')}",
        f"🌙 农历：{info['year_ganzhi']}年（{info['zodiac']}年）{info['lunar_date']}",
        f"🔄 干支：{info['year_ganzhi']}年 {info['month_ganzhi']}月 {info['day_ganzhi']}日",
        "",
    ]

    if info["solar_term"]:
        lines.append(f"🌿 节气：{info['solar_term']}")
        lines.append("")

    lines.append(f"✅ 宜：{info['yi_full'] or '无'}")
    lines.append(f"❌ 忌：{info['ji_full'] or '无'}")
    lines.append("")
    lines.append(f"⚔️ 冲煞：{info['zodiac_clash']}")
    lines.append(f"📋 建除：{info['day_officer']}")
    lines.append(f"⭐ 二十八宿：{info['star28']}")
    lines.append(f"🌓 月相：{info['phase_of_moon']}")
    lines.append("")

    if info["good_gods"]:
        lines.append(f"🙏 吉神：{'、'.join(info['good_gods'])}")
    if info["bad_gods"]:
        lines.append(f"👹 凶煞：{'、'.join(info['bad_gods'])}")

    lines.append("")
    lines.append(f"⏭️ 下一节气：{info['next_solar_term']}（{info['next_solar_term_date'][0]}月{info['next_solar_term_date'][1]}日）")
    lines.append("")
    lines.append("📖 数据来源：《钦定协纪辨方书》/ cnlunar")
    lines.append("⚠️ 仅供参考")

    return "\n".join(lines)


def generate_ics(start_year: int, end_year: int, output_path: str):
    """生成 ICS 日历文件"""
    cal = Calendar()
    cal.add("prodid", "-//Chinese Almanac//yellow-calender//CN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", "中国黄历")
    cal.add("x-wr-caldesc", "每日黄历：农历、干支、节气、宜忌")
    cal.add("x-wr-timezone", "Asia/Shanghai")
    # 订阅刷新间隔：每天
    cal.add("refresh-interval;value=duration", "P1D")

    start_date = datetime(start_year, 1, 1, 8, 0)
    end_date = datetime(end_year, 12, 31, 8, 0)
    current = start_date
    total_days = (end_date - start_date).days + 1
    count = 0

    print(f"正在生成 {start_year}-{end_year} 年黄历数据（共 {total_days} 天）...")

    while current <= end_date:
        info = get_lunar_info(current)

        event = Event()
        summary = build_summary(info)
        description = build_description(info, current)

        event.add("summary", summary)
        event.add("description", description)
        event.add("dtstart", current.date())
        event.add("dtend", current.date())
        event.add("transp", "TRANSPARENT")  # 不占用时间块

        # 用日期生成稳定的 UID，避免重复导入时产生重复事件
        uid = md5(f"yellow-cal-{current.strftime('%Y%m%d')}".encode()).hexdigest()
        event.add("uid", f"{uid}@yellow-calender")

        cal.add_component(event)

        count += 1
        if count % 100 == 0:
            print(f"  已处理 {count}/{total_days} 天...")

        current += timedelta(days=1)

    with open(output_path, "wb") as f:
        f.write(cal.to_ical())

    print(f"\n✅ 完成！共生成 {count} 天黄历数据")
    print(f"📄 文件：{output_path}")
    print(f"\n📱 使用方法：")
    print(f"  方法一：AirDrop 发送 .ics 文件到 iPhone，打开即可导入")
    print(f"  方法二：把文件放到 HTTPS 服务器上，iPhone 系统日历订阅该 URL")
    print(f"  方法三：邮件发送 .ics 文件到自己的邮箱，iPhone 打开附件即可导入")


def main():
    parser = argparse.ArgumentParser(description="中国黄历 ICS 日历生成器")
    parser.add_argument(
        "--start", type=int, default=2026, help="起始年份（默认 2026）"
    )
    parser.add_argument(
        "--end", type=int, default=2028, help="结束年份（默认 2028）"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="chinese_almanac.ics",
        help="输出文件名（默认 chinese_almanac.ics）",
    )
    args = parser.parse_args()

    if args.start < 1900 or args.end > 2100:
        print("年份范围应在 1900-2100 之间", file=sys.stderr)
        sys.exit(1)
    if args.start > args.end:
        print("起始年份不能大于结束年份", file=sys.stderr)
        sys.exit(1)

    generate_ics(args.start, args.end, args.output)


if __name__ == "__main__":
    main()
