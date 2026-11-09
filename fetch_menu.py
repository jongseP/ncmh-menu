"""국립정신건강센터 공지의 직원 식단표를 data/menu.json으로 만든다."""
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = "https://www.ncmh.go.kr"
LIST_URL = BASE + "/ncmh/board/boardList.do?fno=37&menu_cd=01_01"
VIEW_URL = BASE + "/ncmh/board/boardView.do?no={no}&fno=37&menu_cd=01_01&bn=newsView"
FILE_URL = BASE + "/static/jsp/download_image.jsp?physical_name={path}"
OUT = Path(__file__).resolve().parent / "data" / "menu.json"
KST = timezone(timedelta(hours=9))

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


def find_posts(list_html, limit=2):
    posts = re.findall(r'<a\b[^>]*boardView\.do\?no=(\d+)[^>]*>([^<]*직원 식단표[^<]*)</a>', list_html)
    return [(int(no), title.strip()) for no, title in posts][:limit]


def find_txt_path(view_html):
    m = re.search(r"fn_fileDown\('[^']*\.txt','([^']+)'", view_html)
    return m.group(1) if m else None


def build(weeks):
    weeks = sorted((w for w in weeks if w["days"]), key=lambda w: w["days"][0]["date"])
    return {"updated": datetime.now(KST).isoformat(timespec="seconds"), "source": LIST_URL, "weeks": weeks}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ncmh-menu-bot"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def main():
    weeks = []
    for no, title in find_posts(get(LIST_URL)):
        path = find_txt_path(get(VIEW_URL.format(no=no)))
        if path:
            weeks.append(parse_menu(get(FILE_URL.format(path=path)), title))
    data = build(weeks)
    if not data["weeks"]:
        print("식단을 찾지 못함 — menu.json을 그대로 둔다", file=sys.stderr)
        return 1
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("weeks") == data["weeks"]:
            print("변경 없음")
            return 0
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"저장: {[w['title'] for w in data['weeks']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
