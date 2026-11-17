"""Rakb Urban Logistics: the routing helpers of lab 1.1 (USE-SEC-205).

Reads the delivery files, runs the OR-Tools solver with the rules you switch on, and replays any
plan under the dispatcher's four rules, so that two plans are compared under the same rules.
Times are minutes from the start of the shift. Distances are metres from OpenStreetMap roads.
"""
import csv
import pathlib

SHIFT = 480          # minutes in a shift
BASE_SERVICE = 5     # minutes per stop that the first solver run assumes
TOWER_SERVICE = 15   # minutes per stop in a tower: lift, concierge, signature
REST = 30            # minutes of rest
REST_FROM, REST_TO = 210, 270   # the rest starts between these minutes of the shift
COLD_VAN, LIFT_VAN = "V8", "V2"
ALL_RULES = ("cold", "lift", "service", "rest")


def load(folder="."):
    folder = pathlib.Path(folder)
    with open(folder / "deliveries_120.csv", encoding="utf-8") as f:
        stops = list(csv.DictReader(f))
    for s in stops:
        for k in ("crates", "win_start", "win_end", "cold", "lift", "tower"):
            s[k] = int(s[k])
    with open(folder / "fleet.csv", encoding="utf-8") as f:
        fleet = list(csv.DictReader(f))
    for v in fleet:
        v["capacity"] = int(v["capacity"])

    def matrix(name):
        with open(folder / name, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        ids = rows[0][1:]
        return ids, [[int(x) for x in r[1:]] for r in rows[1:]]

    ids, dist = matrix("distance_m.csv")
    _, dur = matrix("duration_s.csv")
    return {"stops": stops, "fleet": fleet, "ids": ids, "dist": dist, "dur": dur}


def service_minutes(stop, rules):
    if "service" in rules and stop["tower"]:
        return TOWER_SERVICE
    return BASE_SERVICE


def travel_minutes(case, a, b):
    return case["dur"][a][b] / 60.0


def solve(case, rules=(), seconds=60):
    """Runs OR-Tools on the vehicle routing problem with capacities and time windows.
    rules: any of "cold", "lift", "service" to add that dispatcher's rule to the model. The rest
    rule is not modelled here: replay() shows what it does to a plan.
    The search stops at a local optimum (greedy descent), so the same files give the same plan."""
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2

    stops, fleet = case["stops"], case["fleet"]
    n = len(stops) + 1
    nv = len(fleet)
    manager = pywrapcp.RoutingIndexManager(n, nv, 0)
    routing = pywrapcp.RoutingModel(manager)
    service = [0] + [service_minutes(s, rules) for s in stops]

    def dist_cb(i, j):
        return case["dist"][manager.IndexToNode(i)][manager.IndexToNode(j)]

    def time_cb(i, j):
        a, b = manager.IndexToNode(i), manager.IndexToNode(j)
        return int(round(case["dur"][a][b] / 60.0)) + service[a]

    def demand_cb(i):
        node = manager.IndexToNode(i)
        return 0 if node == 0 else stops[node - 1]["crates"]

    d_idx = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(d_idx)
    t_idx = routing.RegisterTransitCallback(time_cb)
    routing.AddDimension(t_idx, SHIFT, SHIFT, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    q_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(q_idx, 0, [v["capacity"] for v in fleet], True, "Load")

    for node in range(1, n):
        s = stops[node - 1]
        idx = manager.NodeToIndex(node)
        time_dim.CumulVar(idx).SetRange(s["win_start"], s["win_end"])
        allowed = None
        if "cold" in rules and s["cold"]:
            allowed = [k for k, v in enumerate(fleet) if v["id"] == COLD_VAN]
        if "lift" in rules and s["lift"]:
            allowed = [k for k, v in enumerate(fleet) if v["id"] == LIFT_VAN]
        if allowed is not None:
            routing.SetAllowedVehiclesForIndex(allowed, idx)
    for k in range(nv):
        time_dim.CumulVar(routing.Start(k)).SetRange(0, 0)
        time_dim.CumulVar(routing.End(k)).SetRange(0, SHIFT)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT
    params.time_limit.seconds = seconds
    sol = routing.SolveWithParameters(params)
    if sol is None:
        raise RuntimeError("the solver found no plan that keeps every rule switched on")
    plan = {}
    for k, v in enumerate(fleet):
        idx = routing.Start(k)
        route = []
        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            if node:
                route.append(stops[node - 1]["id"])
            idx = sol.Value(routing.NextVar(idx))
        plan[v["id"]] = route
    return plan


def replay(case, plan, rules=ALL_RULES):
    """Drives a plan under the rules: each van leaves at minute 0 and waits when it is early.
    The rest: before leaving a stop, a driver who has not rested rests now if the clock has passed
    minute 210, or waits for minute 210 and rests then if the next drive would end after minute
    270. Returns (rows, summary). A breach is a stop on a van the rule forbids, or a rest that
    could only start after minute 270."""
    pos = {sid: k for k, sid in enumerate(case["ids"])}
    by_id = {s["id"]: s for s in case["stops"]}
    rows, km, late_stops, late_min, overtime = [], 0.0, 0, 0.0, 0
    breaches = {r: 0 for r in ALL_RULES}
    for van, route in plan.items():
        t, here, rested = 0.0, 0, False
        legs = route + [None]
        for seq, sid in enumerate(legs):
            j = 0 if sid is None else pos[sid]
            if "rest" in rules and not rested and seq > 0:
                drive = travel_minutes(case, here, j)
                finish = t + drive
                if sid is not None:
                    nxt = by_id[sid]
                    finish = max(finish, nxt["win_start"]) + service_minutes(nxt, rules)
                if t >= REST_FROM or finish > REST_TO:
                    if t > REST_TO:
                        breaches["rest"] += 1
                        rows[-1]["rest_after"] = "late rest"
                    else:
                        rows[-1]["rest_after"] = "rest"
                    t = max(t, REST_FROM) + REST
                    rested = True
            km += case["dist"][here][j] / 1000.0
            t += travel_minutes(case, here, j)
            if sid is None:
                break
            s = by_id[sid]
            arrive = t
            start = max(t, s["win_start"])
            late = max(0.0, start - s["win_end"])
            wrong = []
            if "cold" in rules and s["cold"] and van != COLD_VAN:
                wrong.append("cold")
            if "lift" in rules and s["lift"] and van != LIFT_VAN:
                wrong.append("lift")
            for w in wrong:
                breaches[w] += 1
            t = start + service_minutes(s, rules)
            if late > 0.5:
                late_stops += 1
                late_min += late
            rows.append({"van": van, "seq": seq + 1, "stop": sid, "arrive": round(arrive), "start": round(start),
                         "win_start": s["win_start"], "win_end": s["win_end"], "late_min": round(late),
                         "breach": " ".join(wrong), "rest_after": ""})
            here = j
        if route and t > SHIFT + 0.5:
            overtime += 1
    summary = {"vans_used": sum(1 for r in plan.values() if r), "km": round(km, 1), "late_stops": late_stops,
               "late_minutes": round(late_min), "vans_overtime": overtime,
               "cold_breaches": breaches["cold"], "lift_breaches": breaches["lift"], "late_rests": breaches["rest"]}
    return rows, summary


def read_plan(path):
    plan = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            plan.setdefault(r["van"], []).append((int(r["seq"]), r["stop"]))
    return {v: [sid for _, sid in sorted(lst)] for v, lst in plan.items()}


def write_plan(path, plan):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["van", "seq", "stop"])
        for van, route in plan.items():
            for k, sid in enumerate(route, 1):
                w.writerow([van, k, sid])
