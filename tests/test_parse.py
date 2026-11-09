import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fetch_menu import parse_menu  # noqa: E402

F = ROOT / "tests" / "fixtures"


def read(name):
    return (F / name).read_text(encoding="utf-8")


w2 = parse_menu(read("2026-11-w2.txt"), "2026년 11월 2주차 직원 식단표")
assert len(w2["days"]) == 7
d = w2["days"][0]
assert d == {"date": "2026-11-09", "main": ["어묵채잔치국수"], "rice": "흰쌀밥",
             "sides": ["임꺽정떡갈비", "청포묵김가루무침", "얼갈이겉절이", "깍두기"],
             "plus": "숭늉", "takeout": "감자샐러드"}, d
assert w2["days"][1]["main"] == ["A-고추장닭갈비", "B-치킨까스&머스타드"]
assert w2["days"][6]["date"] == "2026-11-15"
assert w2["hours"] == {"lunch_weekday": "11:30~13:00", "lunch_weekend": "11:30~12:20", "dinner": "16:20~17:10"}

w1 = parse_menu(read("2026-11-w1.txt"), "2026년 11월 1주차 직원 식단표")
assert w1["days"][0]["date"] == "2026-11-02"          # [11월 2일(월)] 형식
assert w1["days"][0]["rice"] is None                  # 밥: 줄 없음
assert "♥미니핫도그&케찹♥" in w1["days"][0]["sides"]   # 원문 그대로

dec = parse_menu("12월 31일(목)\n주메뉴: 떡국\n\n1월 1일(금)\n주메뉴: 만둣국\n", "2026년 12월 5주차 직원 식단표")
assert [x["date"] for x in dec["days"]] == ["2026-12-31", "2027-01-01"]
assert dec["hours"]["dinner"] == "16:20~17:10"         # 기본값
assert parse_menu("형식이 바뀐 파일", "2026년 11월 3주차 직원 식단표")["days"] == []

from fetch_menu import find_posts, find_txt_path, build  # noqa: E402

LIST = '<a class="bl_link" href="https://www.ncmh.go.kr/ncmh/board/boardView.do?no=10430&fno=37"\n title="">채용 공고</a>' \
       '<a class="bl_link" href="https://www.ncmh.go.kr/ncmh/board/boardView.do?no=10427&fno=37"\n title="">2026년 11월 2주차 직원 식단표</a>' \
       '<a class="bl_link" href="https://www.ncmh.go.kr/ncmh/board/boardView.do?no=10419&fno=37"\n title="">2026년 11월 1주차 직원 식단표</a>'
assert find_posts(LIST) == [(10427, "2026년 11월 2주차 직원 식단표"), (10419, "2026년 11월 1주차 직원 식단표")]
VIEW = "onclick=\"fn_fileDown('2026년 11월 2주차 직원 식단표_수정.jpg','/2026/11/x_1.jpg','10427','2');\" " \
       "onclick=\"fn_fileDown('2026년 11월 2주차 직원 식단표(텍스트파일)_수정.txt','/2026/11/x_2.txt','10427','1');\""
# 속성 순서·공백이 바뀌거나 title 속성이 없어도 찾는다
LIST2 = '<a title="" href="/ncmh/board/boardView.do?no=10500&amp;fno=37" class="x">\n  2026년 11월 3주차 직원 식단표 </a>' \
        '<a href="/ncmh/board/boardView.do?no=10499&fno=37">2026년 11월 2주차 직원 식단표</a>'
assert find_posts(LIST2) == [(10500, "2026년 11월 3주차 직원 식단표"), (10499, "2026년 11월 2주차 직원 식단표")]
assert find_txt_path(VIEW) == "/2026/11/x_2.txt"
assert find_txt_path("첨부 없음") is None
assert build([{"title": "t", "hours": {}, "days": []}])["weeks"] == []
assert [w["title"] for w in build([w2, w1])["weeks"]] == [w1["title"], w2["title"]]  # 날짜 오름차순
print("ok")

# --- 검증 에이전트 지적 사항 ---
import json  # noqa: E402
import tempfile  # noqa: E402
import fetch_menu  # noqa: E402

# Minor 3: "A-… 또는 B-…"도 두 줄
d = parse_menu("11월 5일(목)\n주메뉴: A-고등어무조림 또는 B-순살안동찜닭\n", "2026년 11월 1주차 직원 식단표")
assert d["days"][0]["main"] == ["A-고등어무조림", "B-순살안동찜닭"], d["days"][0]["main"]

# Minor 4: 제목 월과 다른 달 날짜는 가장 가까운 해
jan = parse_menu("12월 28일(월)\n주메뉴: 떡국\n\n1월 1일(금)\n주메뉴: 만둣국\n", "2027년 1월 1주차 직원 식단표")
assert [x["date"] for x in jan["days"]] == ["2026-12-28", "2027-01-01"], jan
nov = parse_menu("10월 26일(월)\n주메뉴: 국수\n", "2026년 11월 1주차 직원 식단표")
assert nov["days"][0]["date"] == "2026-10-26", nov
leap = parse_menu("2월 29일(화)\n주메뉴: 국수\n", "2028년 3월 1주차 직원 식단표")
assert leap["days"][0]["date"] == "2028-02-29", leap   # 윤년이 아닌 후보 해에서 오류가 나면 안 됨

# Minor 5: 형식이 조금 달라도 읽기
loose = parse_menu("11월 9일 (월)\n주메뉴： 잔치국수\nPLUS코너: 숭늉\n\n11월 10일(화) 메뉴\n주메뉴: 카레\n", "2026년 11월 2주차 직원 식단표")
assert [x["date"] for x in loose["days"]] == ["2026-11-09", "2026-11-10"], loose
assert loose["days"][0]["main"] == ["잔치국수"] and loose["days"][0]["plus"] == "숭늉", loose["days"][0]
assert parse_menu("기간: 11월 9일(월) ~ 11월 15일(일)\n", "2026년 11월 2주차 직원 식단표")["days"] == []

# Important 1 + 테스트 빈 곳: 글 하나라도 못 읽으면 종료코드 1, 파일은 그대로
W2 = read("2026-11-w2.txt")
LIST_OK = LIST.replace("https://www.ncmh.go.kr", "")
VIEW_TXT = "fn_fileDown('a.txt','/p/{n}.txt','1','1');"


def run_main(pages):
    tmp = Path(tempfile.mkdtemp()) / "menu.json"
    tmp.write_text('{"weeks": "old"}', encoding="utf-8")
    fetch_menu.OUT, orig_get = tmp, fetch_menu.get
    fetch_menu.get = lambda url: pages(url)
    try:
        rc = fetch_menu.main()
    finally:
        fetch_menu.get = orig_get
    return rc, json.loads(tmp.read_text(encoding="utf-8"))


def pages_with(second_txt):
    def get(url):
        if "boardList" in url:
            return LIST_OK
        if "boardView" in url:
            return VIEW_TXT.format(n=url.split("no=")[1].split("&")[0])
        return W2 if "10427" in url else second_txt
    return get


rc, data = run_main(pages_with(read("2026-11-w1.txt")))
assert rc == 0 and [w["title"] for w in data["weeks"]] == [w1["title"], w2["title"]], (rc, data)
rc, data = run_main(pages_with("형식이 바뀐 파일"))
assert rc == 1 and data == {"weeks": "old"}, (rc, data)          # 한 주만 깨져도 실패, 파일 유지
rc, data = run_main(lambda url: LIST_OK if "boardList" in url else ("첨부 없음" if "boardView" in url else W2))
assert rc == 1 and data == {"weeks": "old"}, (rc, data)          # txt 첨부가 없어도 실패
print("ok2")
