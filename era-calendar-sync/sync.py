#!/usr/bin/env python3
"""
Era Group ICS -> GHL Calendar Availability Sync
================================================
Mirrors read-only Microsoft 365 .ics busy blocks into a GHL round-robin
calendar as per-user "block slots", so the SynthFlow agent booking against
GHL only ever offers genuinely free times. Union model: a slot is offered
if at least one assigned rep is free.

Runs every 5 minutes via GitHub Actions (see .github/workflows/sync.yml).

SECRET: set repo secret GHL_PIT = the Era Group location Private Integration
Token (found in TGS: 05_GHL/41. Era Group GHL.txt). Never commit the token.

KEY GHL NUANCES (do not regress):
- GHL rejects Python's default User-Agent with Cloudflare 1010. A 'User-Agent'
  header is mandatory on every request.
- Block slots are created at LOCATION level with assignedUserId and NO
  calendarId (calendarId is rejected).
- Block slots are READ BACK from /calendars/blocked-slots, NOT /calendars/events.
"""
import icalendar, recurring_ical_events, urllib.request, urllib.error, json, os, sys
from datetime import datetime, timedelta
import zoneinfo

# ---- CONFIG -------------------------------------------------------------
SYD = zoneinfo.ZoneInfo("Australia/Sydney")
LOCATION_ID = "JqaksLDzySXCTQPHXNi3"
ROUND_ROBIN_CALENDAR_ID = "qZWZ7UOvoFeMaKRtYMiD"  # reference; blocks are user-level
WINDOW_DAYS = int(os.environ.get("SYNC_WINDOW_DAYS", "30"))
TAG = "[ICS-SYNC]"
PIT = os.environ.get("GHL_PIT")

# rep GHL userId -> (display name, read-only .ics feed)
REPS = {
    "h9n9IvKPFM91oD3T2cNl": ("Tarang",
        "https://outlook.office365.com/owa/calendar/86ba86595335472a984c4e848d3c48f1@eragroup.com/c2c4d7bde5f24ff2bd8ff2ff071c89db15375803323703129041/calendar.ics"),
    "nwHBlK7X2vRz3MdRtwFq": ("Amit",
        "https://outlook.office365.com/owa/calendar/044ae577d7d2404889ed1d69907bc66f@eragroup.com/f5e846746e884a3eaacff3bf9e94c7d54825808778541115669/calendar.ics"),
}
# -------------------------------------------------------------------------

HDRS = {
    "Authorization": f"Bearer {PIT}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "User-Agent": "curl/8.5.0",  # MANDATORY - default UA triggers Cloudflare 1010
}
BASE = "https://services.leadconnectorhq.com"


def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(body).encode() if body else None, headers=HDRS)
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        return {"_err": e.code, "_body": e.read().decode()[:200]}


def desired_blocks(ics_url):
    data = urllib.request.urlopen(
        urllib.request.Request(ics_url, headers={"User-Agent": "curl/8.5.0"}), timeout=30).read()
    cal = icalendar.Calendar.from_ical(data)
    now = datetime.now(SYD); end = now + timedelta(days=WINDOW_DAYS)
    out = {}
    for e in recurring_ical_events.of(cal).between(now, end):
        busy = str(e.get('X-MICROSOFT-CDO-BUSYSTATUS', 'BUSY'))
        if busy == 'FREE' or str(e.get('TRANSP', 'OPAQUE')) == 'TRANSPARENT':
            continue
        s = e.get('DTSTART').dt
        en = e.get('DTEND').dt if e.get('DTEND') else None
        if not isinstance(s, datetime):
            continue
        if s.tzinfo is None: s = s.replace(tzinfo=SYD)
        if en is None: en = s + timedelta(minutes=30)
        if en.tzinfo is None: en = en.replace(tzinfo=SYD)
        s = s.astimezone(SYD); en = en.astimezone(SYD)
        out[f"{s.isoformat()}|{en.isoformat()}"] = (s, en)
    return out


def existing_blocks(uid):
    now = datetime.now(SYD); end = now + timedelta(days=WINDOW_DAYS)
    r = api("GET", f"/calendars/blocked-slots?locationId={LOCATION_ID}&userId={uid}"
                   f"&startTime={int(now.timestamp()*1000)}&endTime={int(end.timestamp()*1000)}")
    ev = r.get("events", []) if isinstance(r, dict) else []
    mine = {}
    for x in ev:
        if x.get("title", "").startswith(TAG):
            try:
                s = datetime.fromisoformat(x["startTime"]).astimezone(SYD)
                e = datetime.fromisoformat(x["endTime"]).astimezone(SYD)
                mine[f"{s.isoformat()}|{e.isoformat()}"] = x["id"]
            except Exception:
                pass
    return mine


def main():
    if not PIT:
        print("FATAL: set GHL_PIT env var / repo secret"); sys.exit(1)
    summary = {}
    for uid, (name, url) in REPS.items():
        want = desired_blocks(url)
        have = existing_blocks(uid)
        add = [k for k in want if k not in have]
        rm = [have[k] for k in have if k not in want]
        added = deleted = 0
        for k in add:
            s, e = want[k]
            r = api("POST", "/calendars/events/block-slots", {
                "locationId": LOCATION_ID, "assignedUserId": uid,
                "startTime": s.isoformat(), "endTime": e.isoformat(),
                "title": f"{TAG} busy"})
            if r.get("id"): added += 1
        for eid in rm:
            api("DELETE", f"/calendars/events/{eid}"); deleted += 1
        summary[name] = {"desired": len(want), "added": added, "deleted": deleted}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
