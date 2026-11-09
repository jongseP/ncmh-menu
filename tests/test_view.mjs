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
console.log("ok");
