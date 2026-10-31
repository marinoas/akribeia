#!/usr/bin/env python3
"""
Ωριαία προσομοίωση ηλιακής θέρμανσης για σπίτι στην Κόρινθο.

Συγκρίνει, για έναν ολόκληρο χρόνο (8760 ώρες):
  S0  Μόνο λέβητας πετρελαίου (βάση σύγκρισης)
  S1  Κάτοπτρο 2 αξόνων -> αποθήκη άμμου -> απευθείας στα καλοριφέρ
  S2  Κάτοπτρο -> αποθήκη άμμου -> ΚΑΤΑΡΡΑΚΤΗΣ:
        άμμος > 200°C : κινεί αντλία θερμότητας απορρόφησης (NH3-H2O)
        άμμος 65-200°C: απευθείας στα καλοριφέρ
  S3  Φωτοβολταϊκό -> ηλεκτρική αντλία θερμότητας -> δεξαμενή νερού 1 m³
      (μόνο ηλιακό ρεύμα)
  S4  Όπως το S3, αλλά η αντλία θερμότητας παίρνει και ρεύμα δικτύου
      (υβριδικό με τον λέβητα)
Σε όλα, ό,τι δεν καλύπτεται το καλύπτει ο λέβητας.

Καιρός: συνθετικό τυπικό έτος για την Κόρινθο, βαθμονομημένο σε μηνιαίες
τιμές ακτινοβολίας και θερμοκρασίας. Αν κατεβάσεις αρχείο TMY από το PVGIS
(CSV), τρέξε:  python3 sim.py --pvgis tmy.csv
"""
import argparse, csv, math, os, random

# ----------------------------------------------------------------- ΠΑΡΑΜΕΤΡΟΙ
P = dict(
    lat=37.94,                       # Κόρινθος
    # Μηνιαία μέση ολική οριζόντια ακτινοβολία, kWh/m²/ημέρα (τυπικές τιμές περιοχής)
    ghi_month=[2.3, 3.1, 4.3, 5.6, 6.8, 7.6, 7.6, 6.9, 5.5, 3.9, 2.7, 2.1],
    # Μηνιαία μέση θερμοκρασία αέρα, °C, και ημερήσιο εύρος
    t_month=[10.0, 10.5, 12.5, 16.0, 20.5, 25.0, 27.5, 27.5, 23.5, 19.0, 14.5, 11.0],
    t_amp=[7, 7, 8, 9, 10, 10, 10, 10, 9, 8, 7, 7],
    seed=7,
    dni_scale=0.90,      # συντηρητική διόρθωση άμεσης ακτινοβολίας (βλ. README)

    # Σπίτι
    heating_months=[10, 11, 12, 1, 2, 3, 4],
    heat_annual_kwh=12500.0,         # 2.000 L × 10 kWh × 0,75 − ~2.500 kWh ζεστό νερό
    t_balance=17.0,                  # θερμοκρασία ισορροπίας (με εσωτερικά κέρδη)

    # Οικονομικά
    oil_eur_l=1.55, oil_kwh_l=10.0, boiler_eff=0.75,
    elec_eur_kwh=0.22,

    # Κάτοπτρο (σημειακής εστίασης, 2 αξόνων, κοιλότητα)
    conc_eta0=0.70,      # οπτική απόδοση (κάτοπτρο × στόχευση × απορρόφηση)
    conc_C=300.0,        # λόγος συγκέντρωσης
    conc_U=15.0,         # W/m²K απώλειες μεταφοράς δέκτη
    conc_eps=0.80,       # ισοδύναμη εκπεμψιμότητα κοιλότητας
    conc_dT=40.0,        # δέκτης πόσο θερμότερος από την άμμο
    transport_eff=0.92,  # κύκλωμα αέρα δέκτης→άμμος
    dni_min=150.0,       # W/m² κάτω από αυτό δεν λειτουργεί

    # Αποθήκη άμμου
    sand_rho=1600.0, sand_cp=0.90,   # kg/m³, kJ/kgK
    sand_tmax=550.0, t_direct_min=65.0, t_gen_min=200.0,
    ins_lambda=0.008, ins_t=0.20,    # μόνωση κενού με περλίτη
    bridge=1.25,                     # θερμογέφυρες, στηρίγματα, στόμιο
    hx_kw=12.0,                      # μέγιστη ισχύς απευθείας εκφόρτισης

    # Αντλία θερμότητας απορρόφησης (τύπου NH3-H2O, ~18 kW)
    ahp_kw=18.0, ahp_parasitic=0.04, # kWh ρεύματος ανά kWh θερμότητας

    # Φωτοβολταϊκό + ηλεκτρική αντλία θερμότητας
    pv_tilt=30.0, pv_pr=0.82, albedo=0.2,
    ehp_kw=10.0,
    tank_m3=1.0, tank_tmin=40.0, tank_tmax=60.0, tank_ua=1.6,  # W/K
    # Τα παλιά καλοριφέρ (σχεδιασμένα για 80/60°C) στους 55°C δίνουν ~50% της
    # ισχύος τους. Ό,τι ξεπερνά αυτό το όριο το καλύπτει νερό υψηλής θερμοκρασίας
    # (λέβητας, ή απευθείας η άμμος στο S1/S2).
    t_design=0.0, rad_lowtemp_frac=0.50,
)

# ----------------------------------------------------------------- ΚΑΙΡΟΣ
DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MONTH_OF_DAY = [m for m, n in enumerate(DAYS_IN_MONTH) for _ in range(n)]
SIGMA = 5.670e-8


def sun(lat, n, hour):
    """cos(ζενιθίου), ακτινοβολία εκτός ατμόσφαιρας σε οριζόντιο (W/m²), γωνίες."""
    d = math.radians(23.45 * math.sin(math.radians(360 * (284 + n) / 365)))
    w = math.radians(15 * (hour + 0.5 - 12))
    phi = math.radians(lat)
    cz = math.sin(phi) * math.sin(d) + math.cos(phi) * math.cos(d) * math.cos(w)
    g0 = 1367 * (1 + 0.033 * math.cos(math.radians(360 * n / 365)))
    return cz, g0 * max(cz, 0.0), d, w


def erbs(kt):
    if kt <= 0.22:
        return 1 - 0.09 * kt
    if kt <= 0.80:
        return 0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4
    return 0.165


def synthetic_weather(p):
    rnd = random.Random(p["seed"])
    lat = p["lat"]
    # εκτός ατμόσφαιρας ημερήσια
    h0 = []
    for n in range(1, 366):
        h0.append(sum(sun(lat, n, h)[1] for h in range(24)) / 1000.0)
    # μηνιαίο μέσο Kt
    kt_m = []
    for m in range(12):
        days = [i for i in range(365) if MONTH_OF_DAY[i] == m]
        kt_m.append(p["ghi_month"][m] / (sum(h0[i] for i in days) / len(days)))
    # ημερήσιο Kt με εμμονή (σειρές συννεφιασμένων ημερών)
    kt = []
    prev = 0.0
    for i in range(365):
        m = MONTH_OF_DAY[i]
        sd = 0.17 if m in (10, 11, 0, 1, 2) else 0.10
        prev = 0.6 * prev + sd * rnd.gauss(0, 1)
        kt.append(min(0.78, max(0.08, kt_m[m] + prev)))
    # επαναβαθμονόμηση ώστε να ταιριάζει ακριβώς ο μηνιαίος μέσος
    for m in range(12):
        days = [i for i in range(365) if MONTH_OF_DAY[i] == m]
        target = p["ghi_month"][m] * len(days)
        for _ in range(5):
            cur = sum(kt[i] * h0[i] for i in days)
            f = target / cur
            for i in days:
                kt[i] = min(0.80, max(0.05, kt[i] * f))
    # θερμοκρασία: μηνιαία κλιματολογία + ημερήσια ανωμαλία, πιο κρύες νύχτες με αίθριο
    hours = []
    tprev = 0.0
    for i in range(365):
        n = i + 1
        m = MONTH_OF_DAY[i]
        tsd = 2.6 if m in (10, 11, 0, 1, 2) else 1.6
        tprev = 0.75 * tprev + tsd * rnd.gauss(0, 1)
        amp = p["t_amp"][m] * (0.6 + 0.8 * (kt[i] - 0.3))
        for h in range(24):
            cz, g0h, d, w = sun(lat, n, h)
            ghi = kt[i] * g0h
            kd = erbs(kt[i])
            dhi = kd * ghi
            dni = p["dni_scale"] * (ghi - dhi) / cz if cz > 0.087 else 0.0
            ta = p["t_month"][m] + tprev + amp / 2 * math.cos(2 * math.pi * (h - 15) / 24)
            hours.append(dict(n=n, m=m + 1, h=h, ghi=ghi, dhi=dhi, dni=dni, cz=cz,
                              d=d, w=w, ta=ta))
    # ακριβής μηνιαία μέση θερμοκρασία
    for m in range(12):
        hs = [x for x in hours if x["m"] == m + 1]
        off = p["t_month"][m] - sum(x["ta"] for x in hs) / len(hs)
        for x in hs:
            x["ta"] += off
    return hours


def pvgis_weather(path, p):
    """Φορτώνει CSV TMY από PVGIS (στήλες time(UTC), T2m, G(h), Gb(n), Gd(h))."""
    rows = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("time(UTC)"))
    hdr = lines[start].split(",")
    for l in lines[start + 1:]:
        parts = l.split(",")
        if len(parts) != len(hdr) or not parts[0][:4].isdigit():
            continue
        rows.append(dict(zip(hdr, parts)))
    hours = []
    for k, r in enumerate(rows[:8760]):
        n = k // 24 + 1
        h = k % 24
        m = int(r["time(UTC)"][4:6])
        cz, _, d, w = sun(p["lat"], n, h)
        hours.append(dict(n=n, m=m, h=h, ghi=float(r["G(h)"]), dhi=float(r["Gd(h)"]),
                          dni=float(r["Gb(n)"]), cz=cz, d=d, w=w, ta=float(r["T2m"])))
    return hours


def poa(hr, p):
    """Ακτινοβολία σε κεκλιμένο νότιο επίπεδο (ισοτροπικό μοντέλο), W/m²."""
    if hr["ghi"] <= 0:
        return 0.0
    b = math.radians(p["pv_tilt"])
    phi = math.radians(p["lat"])
    d, w = hr["d"], hr["w"]
    ci = (math.sin(d) * math.sin(phi - b) +
          math.cos(d) * math.cos(phi - b) * math.cos(w))
    beam = hr["dni"] * max(ci, 0.0)
    diff = hr["dhi"] * (1 + math.cos(b)) / 2
    refl = hr["ghi"] * p["albedo"] * (1 - math.cos(b)) / 2
    return beam + diff + refl


def heating_loads(hours, p):
    raw = [max(0.0, p["t_balance"] - hr["ta"]) if hr["m"] in p["heating_months"] else 0.0
           for hr in hours]
    ua = p["heat_annual_kwh"] / sum(raw)       # kWh/K·h
    p["rad_cap"] = p["rad_lowtemp_frac"] * ua * (p["t_balance"] - p["t_design"])
    return [ua * x for x in raw], ua


# ----------------------------------------------------------------- ΣΕΝΑΡΙΑ
def cop_ahp(ta):
    return min(1.70, max(1.25, 1.50 + 0.012 * (ta - 7)))


def cop_ehp(ta):
    return min(4.0, max(1.8, 2.3 + 0.07 * ta))


def store_geom(v, p):
    d = (4 * v / math.pi) ** (1 / 3)
    t = p["ins_t"]
    a_in = 1.5 * math.pi * d**2
    a_out = 1.5 * math.pi * (d + 2 * t) ** 2
    a_mean = math.sqrt(a_in * a_out)
    ua_kw = p["ins_lambda"] * a_mean / t * p["bridge"] / 1000.0   # kW/K
    cap = v * p["sand_rho"] * p["sand_cp"] / 3600.0                # kWh/K
    return cap, ua_kw


def run_concentrator(hours, loads, p, area, vol, cascade, record=False):
    cap, ua = store_geom(vol, p)
    T = p["t_direct_min"]
    out = None
    for year in range(2):                 # 1ο έτος προθέρμανση, μετράμε το 2ο
        acc = dict(solar_in=0.0, loss=0.0, direct=0.0, ahp=0.0, boiler=0.0,
                   parasitic=0.0, monthly={m: [0.0, 0.0, 0.0, 0.0] for m in range(1, 13)},
                   T=[])
        for hr, L in zip(hours, loads):
            ta = hr["ta"]
            # --- φόρτιση από κάτοπτρο
            qin = 0.0
            if hr["dni"] > p["dni_min"] and T < p["sand_tmax"]:
                tr = T + p["conc_dT"] + 273.15
                tak = ta + 273.15
                dni = hr["dni"]
                eta = (p["conc_eta0"]
                       - p["conc_U"] * (tr - tak) / (p["conc_C"] * dni)
                       - p["conc_eps"] * SIGMA * (tr**4 - tak**4) / (p["conc_C"] * dni))
                if eta > 0:
                    qin = area * dni * eta * p["transport_eff"] / 1000.0
                    qin = min(qin, (p["sand_tmax"] - T) * cap)
            T += qin / cap
            # --- απώλειες
            ql = ua * (T - ta)
            T -= ql / cap
            # --- εκφόρτιση
            need = L
            q_ahp = q_dir = 0.0
            if need > 0 and cascade and T > p["t_gen_min"]:
                cop = cop_ahp(ta)
                avail_gen = (T - p["t_gen_min"]) * cap
                q_ahp = min(need, p["ahp_kw"], p["rad_cap"], avail_gen * cop)
                T -= (q_ahp / cop) / cap
                need -= q_ahp
            if need > 0 and T > p["t_direct_min"]:
                q_dir = min(need, p["hx_kw"], (T - p["t_direct_min"]) * cap)
                T -= q_dir / cap
                need -= q_dir
            acc["solar_in"] += qin
            acc["loss"] += ql
            acc["direct"] += q_dir
            acc["ahp"] += q_ahp
            acc["boiler"] += need
            acc["parasitic"] += q_ahp * p["ahp_parasitic"]
            mm = acc["monthly"][hr["m"]]
            mm[0] += L; mm[1] += q_ahp; mm[2] += q_dir; mm[3] += need
            if record:
                acc["T"].append(T)
        out = acc
    return out


def run_pv(hours, loads, p, kwp, grid):
    cap = p["tank_m3"] * 1000 * 4.186 / 3600.0   # kWh/K
    Tt = p["tank_tmin"]
    acc = dict(pv=0.0, pv_heat=0.0, pv_e_heat=0.0, grid_e=0.0, grid_heat=0.0,
               boiler=0.0, pv_other=0.0,
               monthly={m: [0.0, 0.0, 0.0, 0.0] for m in range(1, 13)})
    for hr, L in zip(hours, loads):
        ta = hr["ta"]
        e = kwp * poa(hr, p) / 1000.0 * p["pv_pr"]
        acc["pv"] += e
        cop = cop_ehp(ta)
        need = L
        heat_pv = 0.0
        e_used = 0.0
        lowcap = p["rad_cap"]          # ό,τι μπορούν να δώσουν τα καλοριφέρ στους 55°C
        if hr["m"] in p["heating_months"]:
            # απευθείας στο σπίτι
            q = min(need, e * cop, p["ehp_kw"], lowcap)
            heat_pv += q; need -= q; e_used += q / cop
            # περίσσευμα στη δεξαμενή
            room = (p["tank_tmax"] - Tt) * cap
            q2 = min((e - e_used) * cop, p["ehp_kw"] - q, room)
            if q2 > 0:
                Tt += q2 / cap; e_used += q2 / cop
            # δεξαμενή → σπίτι
            if need > 0 and Tt > p["tank_tmin"]:
                q3 = min(need, lowcap - heat_pv, (Tt - p["tank_tmin"]) * cap)
                q3 = max(q3, 0.0)
                Tt -= q3 / cap; need -= q3; heat_pv += q3
        acc["pv_other"] += e - e_used
        acc["pv_e_heat"] += e_used
        # απώλειες δεξαμενής
        Tt -= p["tank_ua"] * (Tt - ta) / 1000.0 / cap
        Tt = max(Tt, min(ta, p["tank_tmin"]))
        # ρεύμα δικτύου (S4)
        gh = 0.0
        if grid and need > 0:
            gh = max(0.0, min(need, p["ehp_kw"], lowcap - heat_pv))
            acc["grid_e"] += gh / cop
            need -= gh
        acc["grid_heat"] += gh
        acc["pv_heat"] += heat_pv
        acc["boiler"] += need
        mm = acc["monthly"][hr["m"]]
        mm[0] += L; mm[1] += heat_pv; mm[2] += gh; mm[3] += need
    return acc


# ----------------------------------------------------------------- ΚΟΣΤΗ (ενδεικτικά, € μέσες τιμές)
def capex_conc(area, vol, cascade):
    c = 350 * area + 3000 + 1200 * vol + 3000          # κάτοπτρο, αποθήκη, κύκλωμα αέρα/έλεγχος
    if cascade:
        c += 12000                                      # αντλία απορρόφησης + προσαρμογή
    return c


def capex_pv(kwp, grid):
    return 1100 * kwp + 1000 + 7000 + 1500              # Φ/Β, αντλία θερμότητας, δεξαμενή


def econ(p, boiler_kwh, elec_kwh, extra_value=0.0):
    oil_l = boiler_kwh / (p["oil_kwh_l"] * p["boiler_eff"])
    cost = oil_l * p["oil_eur_l"] + elec_kwh * p["elec_eur_kwh"] - extra_value
    return oil_l, cost


# ----------------------------------------------------------------- MAIN
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pvgis", help="CSV TMY από PVGIS (προαιρετικό)")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    p = P
    hours = pvgis_weather(args.pvgis, p) if args.pvgis else synthetic_weather(p)
    loads, ua = heating_loads(hours, p)
    src = "PVGIS" if args.pvgis else "συνθετικό τυπικό έτος"

    base_oil, base_cost = econ(p, sum(loads), 0)
    res = dict(source=src, ua=ua, base_oil=base_oil, base_cost=base_cost, rows=[])

    # ---- έλεγχος καιρού
    mon = {m: dict(ghi=0.0, dni=0.0, t=[], load=0.0, pv=0.0) for m in range(1, 13)}
    for hr, L in zip(hours, loads):
        mm = mon[hr["m"]]
        mm["ghi"] += hr["ghi"] / 1000; mm["dni"] += hr["dni"] / 1000
        mm["t"].append(hr["ta"]); mm["load"] += L
        mm["pv"] += poa(hr, p) / 1000 * p["pv_pr"]
    res["weather"] = {m: dict(ghi=v["ghi"] / DAYS_IN_MONTH[m - 1],
                              dni=v["dni"] / DAYS_IN_MONTH[m - 1],
                              t=sum(v["t"]) / len(v["t"]),
                              load=v["load"], pv1=v["pv"]) for m, v in mon.items()}

    # ---- σάρωση κατόπτρου
    areas = [10, 20, 30, 40, 60, 80, 100]
    vols = [1, 2, 3, 5, 8]
    for cascade in (False, True):
        for a in areas:
            for v in vols:
                r = run_concentrator(hours, loads, p, a, v, cascade)
                oil, cost = econ(p, r["boiler"], r["parasitic"])
                capex = capex_conc(a, v, cascade)
                save = base_cost - cost
                res["rows"].append(dict(
                    save_heat=save, other_val=0.0, elec=r["parasitic"],
                    system="S2 κάτοπτρο+άμμος+απορρόφηση" if cascade else "S1 κάτοπτρο+άμμος",
                    size=f"{a} m², {v} m³", area=a, vol=v, kwp=None,
                    solar_frac=1 - r["boiler"] / sum(loads),
                    solar_in=r["solar_in"], loss=r["loss"],
                    oil_l=oil, cost=cost, save=save, capex=capex,
                    payback=capex / save if save > 0 else float("inf")))
    # ---- σάρωση φωτοβολταϊκού
    for grid in (False, True):
        for k in [2, 4, 6, 8, 10, 12]:
            r = run_pv(hours, loads, p, k, grid)
            other_val = r["pv_other"] * 0.15   # Φ/Β εκτός θέρμανσης: ιδιοκατανάλωση/έγχυση
            oil, cost = econ(p, r["boiler"], r["grid_e"])
            capex = capex_pv(k, grid)
            save_heat = base_cost - cost
            save = save_heat + other_val
            res["rows"].append(dict(
                system="S4 Φ/Β+αντλία θερμ.+δίκτυο" if grid else "S3 Φ/Β+αντλία θερμ.",
                size=f"{k} kWp", area=None, vol=None, kwp=k,
                solar_frac=r["pv_heat"] / sum(loads),
                cover=1 - r["boiler"] / sum(loads),
                pv=r["pv"], pv_other=r["pv_other"], grid_e=r["grid_e"],
                save_heat=save_heat, other_val=other_val, elec=r["grid_e"],
                oil_l=oil, cost=cost, save=save, capex=capex,
                payback=capex / save if save > 0 else float("inf")))

    # ---- αναφορά: 40 m², 3 m³
    ref = {}
    for cascade in (False, True):
        ref[cascade] = run_concentrator(hours, loads, p, 40, 3, cascade, record=True)
    ref_pv = run_pv(hours, loads, p, 6, True)
    res["ref"] = ref
    res["ref_pv"] = ref_pv
    res["loads"] = loads
    res["hours"] = hours
    return res, args.out, p


if __name__ == "__main__":
    import report
    res, out, p = main()
    report.write(res, out, p)
