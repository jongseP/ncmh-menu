"""국립정신건강센터 공지의 직원 식단표를 data/menu.json으로 만든다."""
import re

DEFAULT_HOURS = {"lunch_weekday": "11:30~13:00", "lunch_weekend": "11:30~12:20", "dinner": "16:20~17:10"}
KEYS = {"주메뉴": "main", "밥": "rice", "국 및 반찬": "sides", "PLUS 코너": "plus", "TAKE OUT": "takeout"}
DATE_RE = re.compile(r"^\[?(\d+)월 (\d+)일\([월화수목금토일]\)\]?$")
TIME = r"(\d{1,2}:\d{2}~\d{1,2}:\d{2})"


def parse_menu(text, title):
    m = re.search(r"(\d{4})년 (\d+)월", title)
    year, title_month = int(m.group(1)), int(m.group(2))

    hours = dict(DEFAULT_HOURS)
    if t := re.search(r"중식:.*?평일 " + TIME, text):
        hours["lunch_weekday"] = t.group(1)
    if t := re.search(r"중식:.*?주말 " + TIME, text):
        hours["lunch_weekend"] = t.group(1)
    if t := re.search(r"석식:\s*" + TIME, text):
        hours["dinner"] = t.group(1)

    days, cur = [], None
    for line in text.splitlines():
        line = line.strip()
        if dm := DATE_RE.match(line):
            month, day = int(dm.group(1)), int(dm.group(2))
            y = year + 1 if month < title_month else year
            cur = {"date": f"{y:04d}-{month:02d}-{day:02d}", "main": [], "rice": None,
                   "sides": [], "plus": None, "takeout": None}
            days.append(cur)
        elif line.startswith("["):
            cur = None  # [원산지 및 알레르기 안내] 이후는 메뉴가 아니다
        elif cur is not None and ":" in line:
            key, val = (s.strip() for s in line.split(":", 1))
            field = KEYS.get(key)
            if field == "main":
                cur["main"] = [s.strip() for s in val.split("/") if s.strip()]
            elif field == "sides":
                cur["sides"] = [s.strip() for s in val.split(",") if s.strip()]
            elif field:
                cur[field] = val or None
    return {"title": title, "hours": hours, "days": days}
