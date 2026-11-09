"""국립정신건강센터 공지의 직원 식단표를 data/menu.json으로 만든다."""
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE = "https://www.ncmh.go.kr"
LIST_URL = BASE + "/ncmh/board/boardList.do?fno=37&menu_cd=01_01"
VIEW_URL = BASE + "/ncmh/board/boardView.do?no={no}&fno=37&menu_cd=01_01&bn=newsView"
FILE_URL = BASE + "/static/jsp/download_image.jsp?physical_name={path}"
OUT = Path(__file__).resolve().parent / "data" / "menu.json"
KST = timezone(timedelta(hours=9))

DEFAULT_HOURS = {"lunch_weekday": "11:30~13:00", "lunch_weekend": "11:30~12:20", "dinner": "16:20~17:10"}
# 키는 공백을 뺀 모양으로 비교한다 ("PLUS코너"도 "PLUS 코너"로 본다)
KEYS = {"주메뉴": "main", "밥": "rice", "국및반찬": "sides", "PLUS코너": "plus", "TAKEOUT": "takeout"}
# "11월 9일(월)", "[11월 2일(월)]", "11월 9일 (월)", "11월 10일(화) 메뉴"
DATE_RE = re.compile(r"^\[?(\d+)월\s*(\d+)일\s*\([월화수목금토일]\)\]?(?:\s.*)?$")
COLON = "[:：]"
TIME = r"(\d{1,2}:\d{2}~\d{1,2}:\d{2})"


def closest_year(year, title_month, month, day):
    mid = date(year, title_month, 15)
    cands = []
    for c in (year - 1, year, year + 1):
        try:
            cands.append((abs((date(c, month, day) - mid).days), c))
        except ValueError:  # 2월 29일이 없는 해
            pass
    return min(cands)[1]


def parse_menu(text, title):
    m = re.search(r"(\d{4})년 (\d+)월", title)
    year, title_month = int(m.group(1)), int(m.group(2))

    hours = dict(DEFAULT_HOURS)
    if t := re.search(r"중식" + COLON + r".*?평일 " + TIME, text):
        hours["lunch_weekday"] = t.group(1)
    if t := re.search(r"중식" + COLON + r".*?주말 " + TIME, text):
        hours["lunch_weekend"] = t.group(1)
    if t := re.search(r"석식" + COLON + r"\s*" + TIME, text):
        hours["dinner"] = t.group(1)

    days, cur = [], None
    for line in text.splitlines():
        line = line.strip()
        if dm := DATE_RE.match(line):
            month, day = int(dm.group(1)), int(dm.group(2))
            # 제목 연도 ±1 중 제목의 달에 가장 가까운 해 (12월 글의 1월, 1월 글의 12월)
            y = closest_year(year, title_month, month, day)
            cur = {"date": f"{y:04d}-{month:02d}-{day:02d}", "main": [], "rice": None,
                   "sides": [], "plus": None, "takeout": None}
            days.append(cur)
        elif line.startswith("["):
            cur = None  # [원산지 및 알레르기 안내] 이후는 메뉴가 아니다
        elif cur is not None and re.search(COLON, line):
            key, val = (s.strip() for s in re.split(COLON, line, maxsplit=1))
            field = KEYS.get(re.sub(r"\s+", "", key))
            if field == "main":
                cur["main"] = [s.strip() for s in re.split(r"/|\s또는\s", val) if s.strip()]
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
        # 한 주라도 못 읽으면 실패로 끝낸다. 남은 주만 저장하면 빈 날이 조용히 생긴다.
        path = find_txt_path(get(VIEW_URL.format(no=no)))
        week = parse_menu(get(FILE_URL.format(path=path)), title) if path else None
        if not week or not week["days"]:
            print(f"읽지 못함: {title} — menu.json을 그대로 둔다", file=sys.stderr)
            return 1
        weeks.append(week)
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
