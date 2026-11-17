"""Shared constants of the Rakb Urban Logistics case (USE-SEC-205). Standard library only."""
import random

SEED = 205
DEPOT = (24.6905, 46.7215)  # lat, lon: the Rakb depot, a point on OpenStreetMap roads of Riyadh
BOX = (24.635, 24.755, 46.640, 46.800)  # lat_min, lat_max, lon_min, lon_max of the delivery area
N_STOPS = 120


def stop_points():
    """The 120 delivery points: random positions in the box, fixed by the seed."""
    rng = random.Random(SEED)
    pts = []
    for _ in range(N_STOPS):
        lat = round(rng.uniform(BOX[0], BOX[1]), 5)
        lon = round(rng.uniform(BOX[2], BOX[3]), 5)
        pts.append((lat, lon))
    return pts
