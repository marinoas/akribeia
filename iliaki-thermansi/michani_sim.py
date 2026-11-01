#!/usr/bin/env python3
"""Μηχανή R1233zd(E) με πηγή: σωλήνες κενού + θερμικό λάδι -> δεξαμενή άμμου.
Ωριαία προσομοίωση ενός έτους (συνθετικός καιρός Κορίνθου από το sim.py).

Η μηχανή παίρνει 10 kW θερμότητας όποτε η άμμος είναι αρκετά ζεστή.
Συμπυκνωτής: στο σπίτι (55°C) όταν υπάρχει ζήτηση θέρμανσης, αλλιώς στη γείωση (22°C)."""
import copy, math
import CoolProp.CoolProp as CP
import sim

P = copy.deepcopy(sim.P)
P["pv_tilt"] = 60.0
HOURS = sim.synthetic_weather(P)
LOADS, _ = sim.heating_loads(HOURS, P)

F = "R1233zd(E)"
ETA0, A1, A2, FCOL = 0.45, 0.85, 0.004, 0.95   # σωλήνες κενού heat pipe, με θερμικό λάδι
SAND_C = 1600 * 0.80 / 3600                    # kWh/m³K (ξερή άμμος, φαινόμενη πυκνότητα 1600)
Q_ENG = 10.0                                   # kW θερμότητας στη μηχανή
DT_SAND_OIL = 10.0                             # άμμος -> λάδι (σωλήνες μέσα στην άμμο)
PINCH = 5.0                                    # λάδι -> R1233
TB_MIN = 60.0                                  # κατώτατη θερμοκρασία βρασμού R1233
TB_MAX = 150.0                                 # ανώτατη (κρίσιμο σημείο 166°C)
TC_GROUND, TC_HOUSE = 22.0, 55.0
ETA_EXP = 0.65


def eta_cycle(tb, tc):
    pc = CP.PropsSI("P", "T", tc + 273.15, "Q", 1, F)
    h1 = CP.PropsSI("H", "T", tb + 273.15, "Q", 1, F)
    s1 = CP.PropsSI("S", "T", tb + 273.15, "Q", 1, F)
    h2s = CP.PropsSI("H", "P", pc, "S", s1, F)
    h3 = CP.PropsSI("H", "T", tc + 273.15, "Q", 0, F)
    return ETA_EXP * (h1 - h2s) / (h1 - h3)


ETA_TAB = {tc: {tb: eta_cycle(tb, tc) for tb in range(int(TB_MIN), int(TB_MAX) + 1)}
           for tc in (TC_GROUND, TC_HOUSE)}


def eta_lookup(tb, tc):
    tb = max(TB_MIN, min(TB_MAX, tb))
    return ETA_TAB[tc][int(tb)]


def run(area, vol, tmax=180.0, insul_m=0.30):
    cap = SAND_C * vol
    d = (4 * vol / math.pi) ** (1 / 3)
    ua = 0.04 / insul_m * 1.5 * math.pi * (d + 2 * insul_m) ** 2 * 1.2 / 1000   # kW/K
    t_min_store = TB_MIN + PINCH + DT_SAND_OIL
    T = t_min_store
    for _ in range(2):                                     # δεύτερο πέρασμα: σωστή αρχική κατάσταση
        tot = dict(solar=0.0, loss=0.0, heat_in=0.0, elec=0.0, house=0.0, ground=0.0, run_h=0)
        mon = {m: dict(solar=0.0, elec=0.0, house=0.0, run_h=0, load=0.0) for m in range(1, 13)}
        for hr, L in zip(HOURS, LOADS):
            ta, m = hr["ta"], hr["m"]
            G = sim.poa(hr, P)
            q = 0.0
            if G > 50 and T < tmax:
                tm = T + 10
                eta = ETA0 - A1 * (tm - ta) / G - A2 * (tm - ta) ** 2 / G
                if eta > 0:
                    q = min(area * G * eta * FCOL / 1000, (tmax - T) * cap)
            T += q / cap
            ql = ua * (T - ta)
            T -= ql / cap
            if T > t_min_store:
                tb = min(TB_MAX, T - DT_SAND_OIL - PINCH)
                qin = min(Q_ENG, (T - t_min_store) * cap)
                tc = TC_HOUSE if L > 0 else TC_GROUND
                e = eta_lookup(tb, tc)
                w = qin * e
                rej = qin - w
                house = min(L, rej) if L > 0 else 0.0
                T -= qin / cap
                tot["heat_in"] += qin; tot["elec"] += w; tot["house"] += house
                tot["ground"] += rej - house; tot["run_h"] += qin / Q_ENG
                mon[m]["elec"] += w; mon[m]["house"] += house; mon[m]["run_h"] += qin / Q_ENG
            tot["solar"] += q; tot["loss"] += ql
            mon[m]["solar"] += q; mon[m]["load"] += L
    return tot, mon


if __name__ == "__main__":
    print(f"Ζήτηση θέρμανσης: {sum(LOADS):.0f} kWh/έτος")
    print("Απόδοση κύκλου (εκτονωτής 65%):",
          ", ".join(f"{tb}°C: {ETA_TAB[TC_GROUND][tb]*100:.1f}% / {ETA_TAB[TC_HOUSE][tb]*100:.1f}%"
                    for tb in (60, 90, 120, 150)), "(γείωση / σπίτι)")
    print()
    print("Επιφάνεια | Άμμος | Ήλιος  | Απώλ. | Ώρες λειτ. | Ρεύμα | Στο σπίτι | % θέρμ. | Ιαν ώρες/ημ | Ιουλ ώρες/ημ")
    for area in (25, 50, 100, 200):
        for vol in (5, 10, 20):
            t, mon = run(area, vol)
            print(f"{area:>6} m² | {vol:>3} m³ | {t['solar']:6.0f} | {t['loss']:5.0f} | {t['run_h']:7.0f} h | "
                  f"{t['elec']:5.0f} | {t['house']:6.0f} kWh | {t['house']/sum(LOADS)*100:4.0f}% | "
                  f"{mon[1]['run_h']/31:5.1f} | {mon[7]['run_h']/31:5.1f}")
