import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

vm.runInThisContext(fs.readFileSync(new URL("../logic.js", import.meta.url), "utf8"));

const H = {lunch_weekday:"11:30~13:00", lunch_weekend:"11:30~12:20", dinner:"16:20~17:10"};
assert.equal(statusText({iso:"2026-11-09",hhmm:"12:00",weekend:false},H), "지금 중식 시간 · 13:00까지");
assert.equal(statusText({iso:"2026-11-14",hhmm:"12:00",weekend:true},H), "지금 중식 시간 · 12:20까지");
assert.equal(statusText({iso:"2026-11-09",hhmm:"09:00",weekend:false},H), "중식 11:30부터");
assert.equal(statusText({iso:"2026-11-09",hhmm:"14:00",weekend:false},H), "석식 16:20부터");
assert.equal(statusText({iso:"2026-11-09",hhmm:"16:30",weekend:false},H), "지금 석식 시간 · 17:10까지");
assert.equal(statusText({iso:"2026-11-09",hhmm:"18:00",weekend:false},H), null);
const weeks = [{title:"t", hours:H, days:[{date:"2026-11-09", main:["어묵채잔치국수"], rice:"흰쌀밥", sides:[], plus:null, takeout:null}]}];
assert.equal(findDay(weeks,"2026-11-09").day.main[0], "어묵채잔치국수");
assert.equal(findDay(weeks,"2030-01-01"), null);
// 경계값: 시작 시각은 "지금", 끝 시각은 다음 단계
const at = (hhmm, weekend=false) => statusText({iso:"2026-11-09", hhmm, weekend}, H);
assert.equal(at("11:29"), "중식 11:30부터");
assert.equal(at("11:30"), "지금 중식 시간 · 13:00까지");
assert.equal(at("12:59"), "지금 중식 시간 · 13:00까지");
assert.equal(at("13:00"), "석식 16:20부터");
assert.equal(at("16:20"), "지금 석식 시간 · 17:10까지");
assert.equal(at("17:09"), "지금 석식 시간 · 17:10까지");
assert.equal(at("17:10"), null);
assert.equal(at("12:19", true), "지금 중식 시간 · 12:20까지");
assert.equal(at("12:20", true), "석식 16:20부터");

// 처음 보여줄 날: 오늘이 있으면 오늘, 없으면 다가올 주 첫날(today=false), 그것도 없으면 null
const W = [{days:[{date:"2026-11-02"},{date:"2026-11-08"}]}, {days:[{date:"2026-11-09"},{date:"2026-11-10"},{date:"2026-11-15"}]}];
assert.deepEqual(pickStart(W, "2026-11-10"), {wi:1, sel:"2026-11-10", today:true});
assert.deepEqual(pickStart(W, "2026-10-30"), {wi:0, sel:"2026-11-02", today:false});
assert.equal(pickStart(W, "2026-11-16"), null);
console.log("ok");
