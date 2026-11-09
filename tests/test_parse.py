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
print("ok")
