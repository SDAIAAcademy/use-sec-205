"""Routing part of the Rakb file pack: deliveries, fleet and the dispatcher's manual plan."""
import csv
import math
import random

from case import DEPOT, SEED

ORDER = "band_nn"
BANDS = [(0, 120), (60, 180), (120, 240), (240, 360), (300, 420)]


def deliveries(snapped):
    """snapped: list of (id, lat, lon) for D0 and the 120 stops, from snapped_points.csv."""
    rng = random.Random(SEED + 1)
    ids = [r[0] for r in snapped[1:]]
    order = ids[:]
    rng.shuffle(order)
    cold = set(order[:14])
    lift = set(order[14:20])
    tower = set(order[20:38])
    windowed = set(order[10:62])  # some cold and lift stops have windows too
    rows = []
    for sid, lat, lon in snapped[1:]:
        crates = rng.choice([1, 1, 2, 2, 2, 3, 3, 4])
        if sid in lift:
            crates = 4
        if sid in windowed:
            ws, we = rng.choice(BANDS)
        else:
            ws, we = 0, 480
        kind = "طرد"
        if sid in cold:
            kind = "بقالة مبرّدة"
        elif sid in lift:
            kind = "أثاث: يحتاج إلى شخصين"
        elif sid in tower:
            kind = "برج سكني"
        rows.append({"id": sid, "lat": lat, "lon": lon, "crates": crates, "win_start": ws, "win_end": we,
                     "cold": int(sid in cold), "lift": int(sid in lift), "tower": int(sid in tower), "kind": kind})
    return rows


FLEET = [
    {"id": f"V{k}", "capacity": 40, "kind": "شاحنة صغيرة"} for k in range(1, 9)
]
FLEET[1]["kind"] = "شاحنة صغيرة مع مساعد للحمل"
FLEET[7]["kind"] = "شاحنة صغيرة مبرّدة"


def manual_plan(stops, case):
    """Ayed Qutb's plan: cold stops on V8, lifts on V2, the rest swept by direction around the
    depot into the vans, each route ordered by window end, then by the nearest next stop."""
    lat0, lon0 = DEPOT

    def angle(s):
        return math.atan2(float(s["lat"]) - lat0, float(s["lon"]) - lon0)

    plan = {v["id"]: [] for v in FLEET}
    load = {v["id"]: 0 for v in FLEET}
    for s in stops:
        if s["cold"]:
            plan["V8"].append(s)
            load["V8"] += s["crates"]
        elif s["lift"]:
            plan["V2"].append(s)
            load["V2"] += s["crates"]
    rest = sorted([s for s in stops if not s["cold"] and not s["lift"]], key=angle)
    vans = ["V1", "V3", "V4", "V5", "V6", "V7"]
    per_van = math.ceil(sum(s["crates"] for s in rest) / len(vans))
    k = 0
    for s in rest:
        if k < len(vans) - 1 and load[vans[k]] + s["crates"] > per_van:
            k += 1
        van = vans[k]
        if load[van] + s["crates"] > 40:
            van = "V2" if load["V2"] + s["crates"] <= 40 else "V8"
        plan[van].append(s)
        load[van] += s["crates"]
    pos = {sid: i for i, sid in enumerate(case["ids"])}
    out = {}
    for van, lst in plan.items():
        route, here = [], 0
        left = lst[:]
        while left:
            if ORDER == "window_nn":
                first_end = min(s["win_end"] for s in left)
                pool = [s for s in left if s["win_end"] == first_end]
            elif ORDER == "band_nn":
                first_end = min(s["win_end"] for s in left)
                pool = [s for s in left if s["win_end"] <= first_end + 120]
            else:
                pool = left
            nxt = min(pool, key=lambda s: case["dist"][here][pos[s["id"]]])
            route.append(nxt["id"])
            left.remove(nxt)
            here = pos[nxt["id"]]
        out[van] = route
    return out


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})
