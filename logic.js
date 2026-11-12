// 화면 규칙(순수 함수). index.html과 tests/test_view.mjs가 같이 쓴다.
function findDay(weeks, iso) {
  for (const week of weeks) {
    const day = week.days.find(d => d.date === iso);
    if (day) return { week, day };
  }
  return null;
}

// 처음 보여줄 날. 오늘이 있으면 오늘, 없으면 다가올 주 첫날(today:false), 그것도 없으면 null
function pickStart(weeks, iso) {
  const hit = findDay(weeks, iso);
  if (hit) return { wi: weeks.indexOf(hit.week), sel: iso, today: true };
  const next = weeks.findIndex(w => w.days[0].date > iso);
  return next < 0 ? null : { wi: next, sel: weeks[next].days[0].date, today: false };
}

// now: {iso, hhmm:"HH:MM", weekend}, hours: {lunch_weekday, lunch_weekend, dinner} ("11:30~13:00")
function statusText(now, hours) {
  const [ls, le] = (now.weekend ? hours.lunch_weekend : hours.lunch_weekday).split("~");
  const [ds, de] = hours.dinner.split("~");
  const t = now.hhmm, pad = s => s.padStart(5, "0"); // "9:00" 같은 한 자리 시각도 비교되게
  if (t < pad(ls)) return `중식 ${ls}부터`;
  if (t < pad(le)) return `지금 중식 시간 · ${le}까지`;
  if (t < pad(ds)) return `석식 ${ds}부터`;
  if (t < pad(de)) return `지금 석식 시간 · ${de}까지`;
  return null;
}

// 중식이 끝나면 "저녁", 그 전은 "점심" (중·석식 같은 메뉴)
function mealWord(now, hours) {
  const le = (now.weekend ? hours.lunch_weekend : hours.lunch_weekday).split("~")[1];
  return now.hhmm < le.padStart(5, "0") ? "점심" : "저녁";
}
