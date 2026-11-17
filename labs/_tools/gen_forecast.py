"""Forecast part of the Rakb file pack: Chicago daily taxi trips with Mawsim's week-ahead forecast."""
import csv
import datetime as dt
import pathlib
import random

from case import SEED

SRC = pathlib.Path(__file__).parent / "source" / "chicago_taxi_daily.csv"
FIRST = dt.date(2024, 10, 1)        # first row in the lab file: enough history for a lag of 364 days
TEST_FROM = dt.date(2025, 10, 6)     # Mawsim's forecast starts here
LAST = dt.date(2026, 1, 4)
ORDINARY = (dt.date(2025, 10, 6), dt.date(2025, 11, 16))   # six ordinary weeks
HOLIDAY = (dt.date(2025, 11, 24), dt.date(2026, 1, 4))      # six weeks: Thanksgiving to New Year
HOLIDAYS = {
    dt.date(2024, 11, 28): "عيد الشكر", dt.date(2025, 11, 27): "عيد الشكر",
    dt.date(2024, 12, 24): "ليلة عيد الميلاد", dt.date(2025, 12, 24): "ليلة عيد الميلاد",
    dt.date(2024, 12, 25): "عيد الميلاد", dt.date(2025, 12, 25): "عيد الميلاد",
    dt.date(2024, 12, 31): "ليلة رأس السنة", dt.date(2025, 12, 31): "ليلة رأس السنة",
    dt.date(2025, 1, 1): "رأس السنة", dt.date(2026, 1, 1): "رأس السنة",
}
WEEKDAYS = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


def load():
    with open(SRC, encoding="utf-8") as f:
        return {dt.date.fromisoformat(r["day"]): int(r["trips"]) for r in csv.DictReader(f)}


def calendar_blind(d):
    """The days a forecast without a holiday calendar gets wrong: Thanksgiving week and the
    stretch from the week before Christmas to the second of January."""
    return dt.date(2025, 11, 26) <= d <= dt.date(2025, 11, 30) or dt.date(2025, 12, 22) <= d <= dt.date(2026, 1, 3)


def mawsim(y):
    """Synthetic stand-in for the vendor's week-ahead forecast: close to the actual (a model that
    knows weather, weekday and trend) on ordinary days, and the median of the same weekday over the
    last four weeks on the days a calendar-blind model gets wrong."""
    rng = random.Random(SEED + 2)
    out = {}
    d = TEST_FROM
    while d <= LAST:
        if calendar_blind(d):
            lags = sorted(y[d - dt.timedelta(days=7 * k)] for k in (1, 2, 3, 4))
            out[d] = round((lags[1] + lags[2]) / 2 * (1 + rng.gauss(0, 0.03)))
        else:
            out[d] = round(y[d] * (1 + rng.gauss(0, 0.045)))
        d += dt.timedelta(days=1)
    return out


def table():
    y = load()
    forecast = mawsim(y)
    rows = []
    d = FIRST
    while d <= LAST:
        fc = ""
        if d >= TEST_FROM:
            fc = forecast[d]
        period = ""
        if ORDINARY[0] <= d <= ORDINARY[1]:
            period = "عادية"
        elif HOLIDAY[0] <= d <= HOLIDAY[1]:
            period = "عطلات"
        rows.append({"date": d.isoformat(), "weekday": WEEKDAYS[d.weekday()], "trips": y[d],
                     "mawsim_forecast": fc, "period": period, "holiday": HOLIDAYS.get(d, "")})
        d += dt.timedelta(days=1)
    return rows


def errors(rows):
    """MAE and MAPE per period for Mawsim, last week (lag 7) and last year (lag 364)."""
    by = {r["date"]: r for r in rows}
    out = {}
    for period in ("عادية", "عطلات"):
        acc = {"mawsim": [], "lag7": [], "lag364": []}
        for r in rows:
            if r["period"] != period:
                continue
            d = dt.date.fromisoformat(r["date"])
            a = r["trips"]
            f = {"mawsim": r["mawsim_forecast"],
                 "lag7": by[(d - dt.timedelta(days=7)).isoformat()]["trips"],
                 "lag364": by[(d - dt.timedelta(days=364)).isoformat()]["trips"]}
            for k, v in f.items():
                acc[k].append((abs(a - v), abs(a - v) / a))
        out[period] = {k: {"mae": round(sum(e for e, _ in v) / len(v)), "mape": round(100 * sum(p for _, p in v) / len(v), 1),
                           "days": len(v)} for k, v in acc.items()}
    return out
