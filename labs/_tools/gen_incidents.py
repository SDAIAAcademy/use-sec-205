"""Incident part of the Rakb file pack: a synthetic year (2025) for 200 vehicles, one row per
vehicle and month, with kilometres, incidents and whether a Basar camera was fitted."""
import math
import random

from case import SEED

DEPOTS = [("الشمال", 70, 0.7), ("الشرق", 50, 1.0), ("الجنوب", 45, 1.1), ("الوسط", 35, 1.5)]
TYPES = {"شاحنة صغيرة": (3000, 45), "شاحنة خفيفة": (2300, 60), "دراجة نارية": (1500, 160)}
MIX = {"الشمال": (0.70, 0.25, 0.05), "الشرق": (0.60, 0.20, 0.20), "الجنوب": (0.60, 0.20, 0.20), "الوسط": (0.40, 0.10, 0.50)}
KM_FACTOR = {"الشمال": 1.3, "الشرق": 1.0, "الجنوب": 1.0, "الوسط": 0.8}
CAMERA_EFFECT = 0.9   # the true effect of the camera on the rate: a tenth fewer incidents
EQUIPPED = 20


def poisson(rng, lam):
    k, p, L = 0, 1.0, math.exp(-lam)
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def vehicles(rng):
    out, n = [], 0
    names = list(TYPES)
    for depot, count, _ in DEPOTS:
        shares = MIX[depot]
        kinds = []
        for name, share in zip(names, shares):
            kinds += [name] * round(share * count)
        kinds = (kinds + [names[0]] * count)[:count]
        for kind in kinds:
            n += 1
            out.append({"vehicle": f"R{n:03d}", "depot": depot, "type": kind,
                        "frailty": rng.gammavariate(4, 0.25)})
    return out


def year():
    rng = random.Random(SEED + 3)
    fleet = vehicles(rng)
    depot_risk = {d: f for d, _, f in DEPOTS}
    rows = {}
    km = {}
    for v in fleet:
        base_km, rate = TYPES[v["type"]]
        for m in range(1, 13):
            k = round(base_km * KM_FACTOR[v["depot"]] * max(0.4, rng.gauss(1, 0.15)))
            km[(v["vehicle"], m)] = k
    # Q1 decides who gets a camera; draw Q1 first, then the rest with the camera's true effect
    inc = {}
    for v in fleet:
        rate = TYPES[v["type"]][1] * depot_risk[v["depot"]] * v["frailty"]
        for m in (1, 2, 3):
            inc[(v["vehicle"], m)] = poisson(rng, rate * km[(v["vehicle"], m)] / 1e6)
    q1 = {v["vehicle"]: sum(inc[(v["vehicle"], m)] for m in (1, 2, 3)) for v in fleet}
    q1km = {v["vehicle"]: sum(km[(v["vehicle"], m)] for m in (1, 2, 3)) for v in fleet}
    ranked = sorted(fleet, key=lambda v: (-q1[v["vehicle"]], -q1km[v["vehicle"]], v["vehicle"]))
    equipped = {v["vehicle"] for v in ranked[:EQUIPPED]}
    comparison = {v["vehicle"] for v in ranked[EQUIPPED:2 * EQUIPPED]}
    for v in fleet:
        rate = TYPES[v["type"]][1] * depot_risk[v["depot"]] * v["frailty"]
        for m in range(4, 13):
            r = rate * (CAMERA_EFFECT if v["vehicle"] in equipped else 1.0)
            inc[(v["vehicle"], m)] = poisson(rng, r * km[(v["vehicle"], m)] / 1e6)
    table = []
    for v in fleet:
        for m in range(1, 13):
            table.append({"vehicle": v["vehicle"], "depot": v["depot"], "type": v["type"], "month": f"2025-{m:02d}",
                          "km": km[(v["vehicle"], m)], "incidents": inc[(v["vehicle"], m)],
                          "camera": int(v["vehicle"] in equipped and m >= 4)})
    return table, equipped, comparison, ranked


def quarter(table, ids, months):
    sel = [r for r in table if r["vehicle"] in ids and int(r["month"][5:]) in months]
    return sum(r["incidents"] for r in sel), sum(r["km"] for r in sel)


def summary(table, equipped, comparison):
    out = {"depot": {}, "type": {}}
    for key in ("depot", "type"):
        groups = {}
        for r in table:
            g = groups.setdefault(r[key], [0, 0, set()])
            g[0] += r["incidents"]
            g[1] += r["km"]
            g[2].add(r["vehicle"])
        for name, (i, k, vs) in groups.items():
            out[key][name] = {"vehicles": len(vs), "incidents": i, "million_km": round(k / 1e6, 2), "rate": round(i / k * 1e6, 1)}
    tot_i = sum(r["incidents"] for r in table)
    tot_k = sum(r["km"] for r in table)
    out["fleet"] = {"incidents": tot_i, "million_km": round(tot_k / 1e6, 2), "rate": round(tot_i / tot_k * 1e6, 1)}
    for name, ids in (("equipped", equipped), ("comparison", comparison)):
        a, ka = quarter(table, ids, (1, 2, 3))
        b, kb = quarter(table, ids, (4, 5, 6))
        out[name] = {"q1": a, "q2": b, "change_pct": round(100 * (b - a) / a), "q1_rate": round(a / ka * 1e6, 1), "q2_rate": round(b / kb * 1e6, 1)}
    return out
