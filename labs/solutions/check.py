# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["ortools==9.14.6206"]
# ///
"""Recomputes every number of the answer key from the files participants receive, and prints PASS
for each lab. Writes nothing and calls no model.
Usage: uv run labs/solutions/check.py            (every lab and the map)
       uv run labs/solutions/check.py 1.1 2.1    (some of them)"""
import csv
import datetime as dt
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parents[1] / "files"
sys.path.insert(0, str(FILES / "routing"))
sys.dont_write_bytecode = True


def lab_1_1():
    import rakb_routing as R
    case = R.load(FILES / "routing")
    assert len(case["stops"]) == 120 and sum(s["crates"] for s in case["stops"]) == 280
    manual = R.replay(case, R.read_plan(FILES / "routing" / "manual_plan.csv"))[1]
    ref = R.read_plan(FILES / "routing" / "solver_plan_reference.csv")
    first = R.solve(case, ())
    assert first == ref, "the solver no longer gives the reference plan"
    own = R.replay(case, first, rules=())[1]
    real = R.replay(case, first)[1]
    third = R.replay(case, R.solve(case, ("cold", "lift", "service")))[1]
    print("  manual     ", manual)
    print("  solver own ", own)
    print("  solver real", real)
    print("  solver +3  ", third)
    assert (manual["km"], manual["late_stops"], manual["late_minutes"]) == (565.0, 3, 84)
    assert manual["cold_breaches"] == manual["lift_breaches"] == 0
    assert (own["km"], own["late_stops"]) == (357.2, 0)
    assert (real["late_stops"], real["late_minutes"], real["cold_breaches"], real["lift_breaches"]) == (4, 23, 14, 6)
    assert (third["km"], third["late_stops"], third["late_minutes"], third["cold_breaches"], third["lift_breaches"]) == (450.5, 1, 14, 0, 0)
    assert sum(s["tower"] for s in case["stops"]) == 18
    seven = dict(case, fleet=case["fleet"][:7])
    try:
        s7 = R.replay(seven, R.solve(seven, ("cold", "lift", "service")))[1]
        print("  stretch, 7 vans:", s7)
    except RuntimeError as e:
        print("  stretch, 7 vans:", e)


def lab_1_2():
    with open(FILES / "forecast" / "trips_daily.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    y = {dt.date.fromisoformat(r["date"]): int(r["trips"]) for r in rows}
    out = {}
    for period in ("عادية", "عطلات"):
        acc = {"mawsim": [], "lag7": [], "lag364": []}
        for r in rows:
            if r["period"] != period:
                continue
            d = dt.date.fromisoformat(r["date"])
            a = y[d]
            for k, v in (("mawsim", int(r["mawsim_forecast"])), ("lag7", y[d - dt.timedelta(days=7)]), ("lag364", y[d - dt.timedelta(days=364)])):
                acc[k].append((abs(a - v), abs(a - v) / a))
        out[period] = {k: (round(sum(e for e, _ in v) / len(v)), round(100 * sum(p for _, p in v) / len(v), 1), len(v)) for k, v in acc.items()}
    for p, v in out.items():
        print("  ", "ordinary" if p == "عادية" else "holidays", v)
    assert out["عادية"] == {"mawsim": (622, 3.2, 42), "lag7": (1184, 6.0, 42), "lag364": (1619, 8.4, 42)}
    assert out["عطلات"] == {"mawsim": (3768, 35.5, 42), "lag7": (4754, 36.5, 42), "lag364": (2014, 14.6, 42)}
    xmas = dt.date(2025, 12, 25)
    m = int(next(r["mawsim_forecast"] for r in rows if r["date"] == xmas.isoformat()))
    print("   Christmas 2025: actual", y[xmas], "| mawsim", m, "| lag364", y[xmas - dt.timedelta(days=364)], "| same date 2024", y[dt.date(2024, 12, 25)])
    assert (y[xmas], y[dt.date(2024, 12, 25)]) == (5220, 5326)


def lab_2_1():
    with open(FILES / "incidents" / "fleet_year_2025.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["km"], r["incidents"], r["camera"] = int(r["km"]), int(r["incidents"]), int(r["camera"])
    assert len(rows) == 2400

    def rate(sel):
        i, k = sum(r["incidents"] for r in sel), sum(r["km"] for r in sel)
        return i, round(k / 1e6, 2), round(i / k * 1e6, 1)

    depots = {d: rate([r for r in rows if r["depot"] == d]) for d in ("الشمال", "الشرق", "الجنوب", "الوسط")}
    types = {t: rate([r for r in rows if r["type"] == t]) for t in ("شاحنة صغيرة", "شاحنة خفيفة", "دراجة نارية")}
    print("   depots", depots)
    print("   types ", types)
    assert depots == {"الشمال": (114, 3.0, 38.0), "الشرق": (85, 1.54, 55.3), "الجنوب": (86, 1.38, 62.2), "الوسط": (85, 0.75, 113.4)}
    assert types == {"شاحنة صغيرة": (197, 4.76, 41.4), "شاحنة خفيفة": (72, 1.25, 57.5), "دراجة نارية": (101, 0.65, 154.3)}
    assert rate(rows) == (370, 6.67, 55.5)
    q = lambda r, ms: int(r["month"][5:]) in ms
    equipped = {r["vehicle"] for r in rows if r["camera"]}
    q1 = {}
    for r in rows:
        if q(r, (1, 2, 3)):
            a = q1.setdefault(r["vehicle"], [0, 0])
            a[0] += r["incidents"]
            a[1] += r["km"]
    ranked = sorted(q1, key=lambda v: (-q1[v][0], -q1[v][1], v))
    assert set(ranked[:20]) == equipped, "the equipped vehicles are not the 20 worst of Q1"
    comparison = set(ranked[20:40])
    for name, ids in (("equipped", equipped), ("comparison", comparison)):
        a = rate([r for r in rows if r["vehicle"] in ids and q(r, (1, 2, 3))])
        b = rate([r for r in rows if r["vehicle"] in ids and q(r, (4, 5, 6))])
        print(f"   {name}: Q1 {a} | Q2 {b} | change {round(100 * (b[0] - a[0]) / a[0])}%")
    eq1 = rate([r for r in rows if r["vehicle"] in equipped and q(r, (1, 2, 3))])
    eq2 = rate([r for r in rows if r["vehicle"] in equipped and q(r, (4, 5, 6))])
    co1 = rate([r for r in rows if r["vehicle"] in comparison and q(r, (1, 2, 3))])
    co2 = rate([r for r in rows if r["vehicle"] in comparison and q(r, (4, 5, 6))])
    assert (eq1[0], eq2[0], co1[0], co2[0]) == (41, 13, 20, 9)
    later = rate([r for r in rows if r["vehicle"] in equipped and q(r, range(4, 13))])
    print("   equipped, April to December:", later)


CLAIMS_KEY = {"C1": 2, "C2": 4, "C3": 3, "C4": 1, "C5": 2, "C6": 0, "C7": 4, "C8": 5}


def lab_2_2():
    text = (FILES / "claims" / "claims_8.txt").read_text(encoding="utf-8")
    for c in CLAIMS_KEY:
        assert f"{c} ·" in text, c
    card = (FILES / "claims" / "levels_card.txt").read_text(encoding="utf-8")
    for level in range(6):
        assert f"المستوى {level}" in card
    print("   key:", CLAIMS_KEY, "| LO1 evidence: six of eight rows right")


REFERENCE_MAP = {  # value, readiness, safety impact, likelihood, impact
    "U01": (4, 3, "غير مباشر", 2, 2), "U02": (4, 3, "غير مباشر", 3, 2), "U03": (3, 2, "مباشر", 2, 3),
    "U04": (3, 3, "مباشر", 2, 4), "U05": (3, 4, "لا", 3, 1), "U06": (4, 2, "غير مباشر", 3, 2),
    "U07": (4, 2, "مباشر", 2, 3), "U08": (3, 1, "غير مباشر", 3, 2), "U09": (1, 1, "مباشر", 2, 3),
    "U10": (3, 4, "لا", 3, 1), "U11": (2, 3, "غير مباشر", 2, 2), "U12": (4, 3, "لا", 3, 1),
    "U13": (4, 1, "مباشر", 3, 3), "U14": (2, 3, "لا", 2, 1),
}


def tier(score):
    return "منخفض" if score <= 2 else "متوسط" if score <= 6 else "مرتفع" if score <= 12 else "كارثي"


def lab_map():
    text = (FILES / "map" / "use_cases_14.txt").read_text(encoding="utf-8")
    for u in REFERENCE_MAP:
        assert f"{u} ·" in text, u
    rows = []
    for u, (v, r, s, lk, im) in REFERENCE_MAP.items():
        rows.append((v * r, u, s, lk * im, tier(lk * im)))
    rows.sort(key=lambda x: (-x[0], x[1]))
    for vr, u, s, sc, t in rows:
        print(f"   {u}  value x readiness {vr:2}  safety {s:9}  risk {sc:2} {t}")
    tiers = [t for *_, t in rows]
    assert tiers.count("مرتفع") == 2 and tiers.count("منخفض") == 1
    takeover = [u for u, x in REFERENCE_MAP.items() if x[2] != "لا"]
    assert len(takeover) == 10, takeover


LABS = {"1.1": lab_1_1, "1.2": lab_1_2, "2.1": lab_2_1, "2.2": lab_2_2, "map": lab_map}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    chosen = sys.argv[1:] or list(LABS)
    for name in chosen:
        print(f"lab {name}")
        LABS[name]()
        print(f"PASS {name}")
