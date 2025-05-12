import random, heapq, pandas as pd
 

# ------------------------------------------------------------
# 1) Road network and POIs
# ------------------------------------------------------------
base_graph = {
    'A': [('B', 3.0), ('C', 5.0)],
    'B': [('A', 3.0), ('C', 2.0), ('D', 4.0)],
    'C': [('A', 5.0), ('B', 2.0), ('D', 3.0), ('E', 4.0)],
    'D': [('B', 4.0), ('C', 3.0), ('E', 2.0)],
    'E': [('C', 4.0), ('D', 2.0)]
}

restaurants = {'Resto1': 'B', 'Resto2': 'C', 'Resto3': 'D'}
customers   = {'customerA': 'A', 'customerB': 'C',
               'customerC': 'D', 'customerD': 'E'}

BASE_SPEED_MPH = 40.0
SPEED_VARIATION = 0.30


# ------------------------------------------------------------
# 2) Helpers
# ------------------------------------------------------------
def gen_time(km):
    speed = BASE_SPEED_MPH * random.uniform(1-SPEED_VARIATION, 1+SPEED_VARIATION)
    return km / speed * 60.0      # minutes

def snapshot():
    """Return a fresh traffic snapshot with time‑dependent edge weights."""
    return {u: [(v, gen_time(l)) for v, l in nbrs]
            for u, nbrs in base_graph.items()}

def dijkstra(g, s, t):
    dist, prev = {v: float('inf') for v in g}, {}
    dist[s] = 0.0
    pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t: break
        if d != dist[u]: continue
        for v, w in g[u]:
            alt = d + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))
    path, n = [], t
    while n in prev: path.append(n); n = prev[n]
    path.append(s); path.reverse()
    return path, dist[t]

def edge_time(g, u, v):
    for nbr, w in g[u]:
        if nbr == v: return w
    raise ValueError("edge missing")


# ------------------------------------------------------------
# 3) Simulation
# ------------------------------------------------------------
def compare_dynamic_vs_static(start='A', resto='Resto1', cust='customerD',
                              seed=42):
    random.seed(seed)

    # ---------- original plan on a single snapshot ----------
    first = snapshot()
    leg1, eta1 = dijkstra(first, start, restaurants[resto])
    leg2, eta2 = dijkstra(first, restaurants[resto], customers[cust])
    orig_path = leg1 + leg2[1:]
    orig_eta  = eta1 + eta2

    # ---------- dynamic replanning & static replay ----------
    stage, dest = "to_restaurant", restaurants[resto]
    dyn_curr, dyn_total = start, 0.0
    stat_idx, stat_total = 0, 0.0          # index into orig_path
    prev_remain = None
    log_rows, driven_path = [], [start]

    while True:
        live = snapshot()                  # same snapshot for *both* couriers

        # ---- dynamic decision ----
        dyn_path, dyn_eta = dijkstra(live, dyn_curr, dest)
        changed = prev_remain is not None and dyn_path != prev_remain
        prev_remain = dyn_path
        dyn_next = dyn_path[1] if len(dyn_path) > 1 else dyn_curr
        dyn_edge = 0.0
        if dyn_next != dyn_curr:
            dyn_edge = edge_time(live, dyn_curr, dyn_next)

        # ---- static courier takes next edge of original path ----
        if stat_idx < len(orig_path) - 1:
            stat_u = orig_path[stat_idx]
            stat_v = orig_path[stat_idx + 1]
            stat_edge = edge_time(live, stat_u, stat_v)
            stat_total += stat_edge
            stat_idx  += 1
        else:
            stat_edge = 0.0  # already delivered

        # ---- log the step ----
        log_rows.append({
            "stage": stage,
            "dyn_curr": dyn_curr,
            "dyn_next": dyn_next,
            "dyn_remain": " ➔ ".join(dyn_path),
            "dyn_edge_time": round(dyn_edge, 2),
            "dyn_cum": round(dyn_total, 2),
            "static_curr": orig_path[stat_idx-1] if stat_idx else start,
            "static_edge_time": round(stat_edge, 2),
            "static_cum": round(stat_total, 2),
            "changed": "★" if changed else ""
        })

        # ---- advance dynamic courier ----
        if dyn_next == dyn_curr:
            if stage == "to_restaurant":
                stage, dest = "to_customer", customers[cust]
            else:
                # dynamic courier delivered
                delivered = True
                break
        else:
            dyn_total += dyn_edge
            dyn_curr = dyn_next
            driven_path.append(dyn_next)

        # stop when both couriers are done
        if stat_idx >= len(orig_path) and dyn_next == dyn_curr == dest:
            break

    df = pd.DataFrame(log_rows)
    return (df, orig_path, driven_path,
            orig_eta, stat_total, dyn_total)

def benchmark_routing(
        n_runs=1000,
        start='A',
        resto='Resto1',
        cust='customerD',
        seed_base=100):
    """
    Run compare_dynamic_vs_static n_runs times and print:
      • best single time saved   (most‑negative Δ)
      • worst single time lost   (most‑positive Δ)
      • net total Δ over all runs (dyn − stat, minutes; <0 ⇒ net saved)
      • average Δ
      • win counts
    """
    
    deltas = []  # Δ = dynamic_time − static_time
    for i in range(n_runs):
        seed = seed_base + i
        (_,_, _, _, stat_t, dyn_t) = compare_dynamic_vs_static(
            start, resto, cust, seed)
        deltas.append(dyn_t - stat_t)

    df = pd.DataFrame(deltas, columns=["delta"])

    max_saved = df["delta"].min()           # most‑negative
    max_lost  = df["delta"].max()           # most‑positive
    net_total = df["delta"].sum()           # one value: <0 means net saved
    avg_delta = df["delta"].mean()
    wins_dyn  = (df["delta"] < 0).sum()
    wins_stat = n_runs - wins_dyn

    print(f"Simulations run            : {n_runs}")
    print(f"Dynamic routing won        : {wins_dyn} times")
    print(f"Static routing won         : {wins_stat} times")
    print(f"Average Δ (dyn‑stat)       : {avg_delta:+.2f} min")
    print(f"Maximum single save        : {abs(max_saved):.2f} min")
    print(f"Maximum single loss        : {max_lost:.2f} min")
    print(f"Net total time (dyn‑stat)  : {net_total:+.2f} min "
          f"({'saved' if net_total < 0 else 'lost'})")

    return df


# ------------------------------------------------------------
# 4) Run demo
# ------------------------------------------------------------

log, orig_path, dyn_path, eta_orig, eta_static, eta_dyn = compare_dynamic_vs_static()

print("\n==== ORIGINAL PLAN (frozen at t 0) ====")
print("Path :", " ➔ ".join(orig_path))
print(f"ETA  : {eta_orig:.2f} min")

print("\n==== STEP‑BY‑STEP LOG (★ = route changed) ====")
print(log.to_string(index=False))

print("\n==== FINAL OUTCOME ====")
print("Dynamic driven route   :", " ➔ ".join(dyn_path))
print(f"Static‑path time       : {eta_static:.2f} min   "
    "(following the original path but live weights)")
print(f"Dynamic‑replan time    : {eta_dyn:.2f} min")
print(f"Δ vs. static path      : {abs(eta_static - eta_dyn):.2f} min "
    f"({'saved' if eta_static > eta_dyn else 'lost'})")
print("===========================")

benchmark_routing()
