# /// script
# requires-python = ">=3.11"
# ///
"""Run once: asks the public OSRM demo server (OpenStreetMap data) for the road distance and
driving time between the depot and the 120 delivery points, and writes the two matrices into
labs/files/routing/. The lab never calls the server: it reads the committed matrices.
Usage: uv run labs/_tools/fetch_matrix.py"""
import csv, json, pathlib, sys, time, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from case import DEPOT, stop_points

OUT = pathlib.Path(__file__).resolve().parents[1] / "files" / "routing"
pts = [DEPOT] + stop_points()
coords = ";".join(f"{lon},{lat}" for lat, lon in pts)
n = len(pts)
dist = [[None] * n for _ in range(n)]
dur = [[None] * n for _ in range(n)]
step = 20
for start in range(0, n, step):
    src = ";".join(str(i) for i in range(start, min(n, start + step)))
    url = f"https://router.project-osrm.org/table/v1/driving/{coords}?sources={src}&annotations=distance,duration"
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "academy-course-lab-matrix/1.0"})
            data = json.load(urllib.request.urlopen(req, timeout=120))
            assert data["code"] == "Ok", data.get("code")
            break
        except Exception as e:  # network: wait and retry
            print("retry", start, e)
            time.sleep(5 * (attempt + 1))
    else:
        raise SystemExit("server did not answer")
    for k, i in enumerate(range(start, min(n, start + step))):
        dist[i] = [round(x) for x in data["distances"][k]]
        dur[i] = [round(x) for x in data["durations"][k]]
    snapped = data["destinations"]
    time.sleep(1.5)
OUT.mkdir(parents=True, exist_ok=True)
ids = ["D0"] + [f"S{i:03d}" for i in range(1, n)]
for name, m in (("distance_m.csv", dist), ("duration_s.csv", dur)):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["from"] + ids)
        for i in range(n):
            w.writerow([ids[i]] + m[i])
with open(OUT / "snapped_points.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "lat", "lon", "snap_m"])
    for i, d in enumerate(snapped):
        w.writerow([ids[i], round(d["location"][1], 5), round(d["location"][0], 5), round(d["distance"])])
print("wrote", n, "x", n)
