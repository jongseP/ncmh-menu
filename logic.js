// 화면 규칙(순수 함수). index.html과 tests/test_view.mjs가 같이 쓴다.
function findDay(weeks, iso) {
  for (const week of weeks) {
    const day = week.days.find(d => d.date === iso);
    if (day) return { week, day };
  }
  return null;
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
