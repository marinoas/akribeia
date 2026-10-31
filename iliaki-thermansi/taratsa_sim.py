#!/usr/bin/env python3
"""Σωλήνες κενού στην ταράτσα (κλίση 60°, νότια) -> αποθήκη στο έδαφος -> καλοριφέρ.
Β: drainback νερό (έως 90°C) | Α: αέρας + πέτρες (έως 150°C) | Γ: θερμέλαιο + βασάλτης (έως 180°C)
Χρησιμοποιεί τον καιρό και τη ζήτηση του sim.py."""
import copy, math
import sim

P = copy.deepcopy(sim.P)
P["pv_tilt"] = 60.0
hours = sim.synthetic_weather(P)
loads, ua = sim.heating_loads(hours, P)
OIL = P["oil_eur_l"] / (P["oil_kwh_l"] * P["boiler_eff"])     # €/kWh θερμότητας λέβητα

# Σωλήνες κενού heat pipe, συντελεστές ανά μικτή επιφάνεια (τυπικές τιμές)
ETA0, A1, A2 = 0.45, 0.85, 0.004

STORES = {
    # όνομα: (θερμοχωρ. kWh/m³K, Tmax, Tmin παράδοσης, συντελ. συλλέκτη, παρασιτικά kWh/kWh)
    "Β νερό drainback":      (1.16, 90.0, 45.0, 1.00, 0.010),
    "Α αέρας + πέτρες":      (0.45, 150.0, 55.0, 0.85, 0.040),   # κενά ~40%, αέρας μεταφέρει χειρότερα
    "Γ θερμέλαιο + βασάλτης": (0.70, 180.0, 55.0, 0.95, 0.012),
}


def run(area, name, vol):
    c, tmax, tmin, fcol, para = STORES[name]
    cap = c * vol                              # kWh/K
    d = (4 * vol / math.pi) ** (1 / 3)
    ua_store = 0.04 / 0.20 * 1.5 * math.pi * (d + 0.4) ** 2 * 1.2 / 1000   # πετροβάμβακας 20 cm
    T = tmin
    for _ in range(2):
        tot = dict(solar=0.0, used=0.0, loss=0.0, boiler=0.0, para=0.0)
        mon = {m: [0.0, 0.0] for m in range(1, 13)}
        for hr, L in zip(hours, loads):
            ta = hr["ta"]
            G = sim.poa(hr, P)
            q = 0.0
            if G > 50 and T < tmax:
                tm = T + 10
                eta = ETA0 - A1 * (tm - ta) / G - A2 * (tm - ta) ** 2 / G
                if eta > 0:
                    q = min(area * G * eta * fcol / 1000, (tmax - T) * cap)
            T += q / cap
            ql = ua_store * (T - ta)
            T -= ql / cap
            use = 0.0
            if L > 0 and T > tmin:
                use = min(L, (T - tmin) * cap, 12.0)
                T -= use / cap
            tot["solar"] += q; tot["loss"] += ql; tot["used"] += use
            tot["boiler"] += L - use; tot["para"] += q * para
            mon[hr["m"]][0] += L; mon[hr["m"]][1] += use
    return tot, mon, cap * (tmax - tmin)


jan_kw = sum(L for hr, L in zip(hours, loads) if hr["m"] == 1) / (31 * 24)
print(f"Ζήτηση Ιανουαρίου: μέση {jan_kw:.1f} kW = {jan_kw*24:.0f} kWh/ημέρα. Σήμερα θέρμανση {sum(loads):.0f} kWh, {sum(loads)*OIL:.0f} €/έτος")
for area in (15, 25):
    for name, vols in (("Β νερό drainback", (1, 2, 4, 6)), ("Α αέρας + πέτρες", (3, 5, 8)),
                       ("Γ θερμέλαιο + βασάλτης", (2, 3, 4))):
        for v in vols:
            t, mon, emax = run(area, name, v)
            frac = t["used"] / sum(loads)
            save = t["used"] * OIL - t["para"] * P["elec_eur_kwh"]
            jan = mon[1][1] / mon[1][0]
            print(f"{area:>3} m² | {name:<24} {v:>2} m³ | γεμάτη: {emax:4.0f} kWh = {emax/jan_kw:4.0f} ώρες Ιαν | "
                  f"κάλυψη έτους {100*frac:4.1f}% | Ιαν {100*jan:4.1f}% | εξοικ. {save:5.0f} €")
