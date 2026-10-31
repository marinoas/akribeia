#!/usr/bin/env python3
"""PVT στην ταράτσα -> δεξαμενή-πηγή (παλιά δεξαμενή, νερό/πάγος) -> αντλία θερμότητας
νερού-νερού -> καλοριφέρ (λέβητας σε σειρά για ό,τι δεν καλύπτεται).
Χρησιμοποιεί τον καιρό, τη ζήτηση και τις τιμές του sim.py."""
import copy, math
import sim

P = copy.deepcopy(sim.P)
P["pv_tilt"] = 40.0                       # συμβιβασμός χειμώνα / όλου του χρόνου
hours = sim.synthetic_weather(P)
loads, ua = sim.heating_loads(hours, P)
OIL = P["oil_eur_l"] / (P["oil_kwh_l"] * P["boiler_eff"])
EL = P["elec_eur_kwh"]

# PVT χωρίς τζάμι μπροστά (ανά μικτή επιφάνεια)
WP_PER_M2 = 215.0        # πάνελ ~430 W / 2,0 m²
PR = 0.86                # απώλειες inverter/καλωδίων (χωρίς θερμοκρασία)
GAMMA = -0.004           # απώλεια ισχύος ανά °C
ETA_TH0 = 0.50           # θερμική απόδοση στο μηδέν (μαζί με ρεύμα ~0,7 του φωτός)
UL = 25.0                # W/m²K ανταλλαγή με τον αέρα (πλάτη ΧΩΡΙΣ μόνωση: πιάνει και θερμότητα από τον αέρα)
SKY = 35.0               # W/m² απώλεια ακτινοβολίας προς τον ουρανό
HP_KW = 8.0              # θερμική ισχύς αντλίας θερμότητας νερού-νερού
T_SUP = 55.0


def cop_ww(t_src):
    te = t_src - 5 + 273.15
    tc = T_SUP + 273.15
    return min(5.5, max(2.0, 0.48 * tc / (tc - te)))


def run(area, src_m3, record=False):
    kwp = area * WP_PER_M2 / 1000
    capk = src_m3 * 1.163                 # kWh/K
    latent = src_m3 * 93.0                # kWh αν παγώσει όλο
    E = 10 * capk                         # ενέργεια πάνω από 0°C (αρνητικό = πάγος)
    for _ in range(2):
        a = dict(pv=0.0, pv_hp=0.0, grid=0.0, th=0.0, hp_heat=0.0, boiler=0.0,
                 frozen_h=0, minT=99.0)
        mon = {m: [0.0, 0.0, 0.0, 0.0, 0.0] for m in range(1, 13)}  # ανάγκη, δωρεάν, Φ/Β, δίκτυο, λέβητας
        for hr, L in zip(hours, loads):
            ta = hr["ta"]; G = sim.poa(hr, P)
            Ts = E / capk if E > 0 else 0.0
            # θερμική συλλογή (κυκλοφορητής τρέχει μόνο αν κερδίζουμε)
            tm = Ts + 3
            q = area * (ETA_TH0 * G - UL * (tm - ta) - (SKY if G < 50 else 0)) / 1000
            q = max(0.0, q)
            if E + q > 35 * capk:        # η δεξαμενή-πηγή δεν χρειάζεται πάνω από 35°C
                q = max(0.0, 35 * capk - E)
            pumping = q > 0
            tcell = (tm + 5) if pumping else (ta + G / 800 * 25)
            pv = kwp * G / 1000 * PR * (1 + GAMMA * (tcell - 25))
            E += q
            E -= 0.0006 * (Ts - ta)       # μικρές απώλειες μονωμένης δεξαμενής
            # αντλία θερμότητας
            hp = 0.0
            if L > 0 and E > -0.85 * latent:
                cop = cop_ww(Ts)
                hp = min(L, HP_KW, P["rad_cap"])
                ext = hp * (1 - 1 / cop)
                if E - ext < -0.85 * latent:
                    ext = max(0.0, E + 0.85 * latent)
                    hp = ext / (1 - 1 / cop)
                E -= ext
                e = hp / cop
                from_pv = min(e, pv)
                a["pv_hp"] += from_pv; a["grid"] += e - from_pv
                mon[hr["m"]][2] += from_pv; mon[hr["m"]][3] += e - from_pv
                mon[hr["m"]][1] += hp - e
            if E < 0:
                a["frozen_h"] += 1
            a["minT"] = min(a["minT"], E / capk if E > 0 else E / latent * 100)
            a["pv"] += pv; a["th"] += q; a["hp_heat"] += hp; a["boiler"] += L - hp
            mon[hr["m"]][0] += L; mon[hr["m"]][4] += L - hp
    a["kwp"] = kwp
    a["pv_other"] = a["pv"] - a["pv_hp"]
    oil_cost = a["boiler"] * OIL
    a["cost_heat"] = oil_cost + a["grid"] * EL
    a["save_heat"] = sum(loads) * OIL - a["cost_heat"]
    a["other_val"] = a["pv_other"] * 0.15
    a["oil_l"] = a["boiler"] / (P["oil_kwh_l"] * P["boiler_eff"])
    a["mon"] = mon
    return a


def baseline_pv_airhp(kwp):
    """Σύγκριση: απλά Φ/Β ίδιας ισχύος + αντλία αέρα-νερού + δίκτυο (το S4 του sim.py)."""
    q = copy.deepcopy(P); q["pv_tilt"] = 40.0
    r = sim.run_pv(hours, loads, q, kwp, True)
    oil_l = r["boiler"] / (P["oil_kwh_l"] * P["boiler_eff"])
    cost = r["boiler"] * OIL + r["grid_e"] * EL
    return dict(save_heat=sum(loads) * OIL - cost, other_val=r["pv_other"] * 0.15,
                oil_l=oil_l, cover=1 - r["boiler"] / sum(loads), pv=r["pv"], grid=r["grid_e"])


if __name__ == "__main__":
    print(f"Βάση: θέρμανση {sum(loads):.0f} kWh, {sum(loads)*OIL:.0f} €/έτος, όριο καλοριφέρ στους 55°C {P['rad_cap']:.1f} kW")
    for area in (10, 16, 24):
        for v in (1.0, 2.0):
            r = run(area, v)
            cov = r["hp_heat"] / sum(loads)
            print(f"PVT {area:>2} m² ({r['kwp']:.1f} kWp), πηγή {v:.0f} m³: Φ/Β {r['pv']:5.0f} kWh, θερμ. συλλογή {r['th']:5.0f}, "
                  f"αντλία {r['hp_heat']:5.0f} kWh ({100*cov:.0f}%), ρεύμα Φ/Β→αντλία {r['pv_hp']:4.0f}, δίκτυο {r['grid']:4.0f}, "
                  f"πετρέλαιο {r['oil_l']:4.0f} L, ώρες πάγου {r['frozen_h']:4d}, εξοικ. θέρμ. {r['save_heat']:5.0f} € + Φ/Β {r['other_val']:4.0f} €")
        b = baseline_pv_airhp(area * WP_PER_M2 / 1000)
        print(f"   σύγκριση: απλά Φ/Β {area*WP_PER_M2/1000:.1f} kWp + αντλία αέρα: κάλυψη {100*b['cover']:.0f}%, Φ/Β {b['pv']:.0f}, δίκτυο {b['grid']:.0f}, "
              f"πετρέλαιο {b['oil_l']:.0f} L, εξοικ. θέρμ. {b['save_heat']:.0f} € + Φ/Β {b['other_val']:.0f} €")
