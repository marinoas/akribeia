#!/usr/bin/env python3
"""Καθαρή σύγκριση: μόνο θέρμανση που προέρχεται από τον ήλιο (χωρίς ρεύμα δικτύου,
χωρίς πίστωση για ρεύμα εκτός θέρμανσης). Ό,τι λείπει το καλύπτει ο λέβητας."""
import copy
import sim, pvt_sim as pv, taratsa_sim as ts
from report import fmt

L = pv.loads; Ltot = sum(L); OIL = pv.OIL
P = pv.P


def pvt_solar_only(area, buf_m3=0.3):
    """PVT + αντλία νερού-νερού που δουλεύει ΜΟΝΟ με το ρεύμα των πάνελ.
    Περίσσευμα ρεύματος → η αντλία φορτίζει buffer (40-60°C) για το βράδυ."""
    kwp = area * pv.WP_PER_M2 / 1000
    capk, latent = 1.163, 93.0               # παλιά δεξαμενή 1 m³ ως πηγή
    bcap = buf_m3 * 1.163; Tb = 40.0
    E = 10 * capk
    for _ in range(2):
        heat = 0.0; elec = 0.0; pvsum = 0.0
        for hr, Lh in zip(pv.hours, L):
            ta = hr["ta"]; G = sim.poa(hr, P)
            Ts = E / capk if E > 0 else 0.0
            tm = Ts + 3
            q = max(0.0, area * (pv.ETA_TH0 * G - pv.UL * (tm - ta) - (pv.SKY if G < 50 else 0)) / 1000)
            q = min(q, max(0.0, 35 * capk - E))
            tcell = (tm + 5) if q > 0 else (ta + G / 800 * 25)
            e_pv = kwp * G / 1000 * pv.PR * (1 + pv.GAMMA * (tcell - 25))
            pvsum += e_pv
            E += q
            need = Lh if hr["m"] in P["heating_months"] else 0.0
            cop = pv.cop_ww(Ts)
            ok = E > -0.85 * latent
            # 1) αντλία απευθείας με ηλιακό ρεύμα
            h1 = min(need, e_pv * cop, pv.HP_KW, P["rad_cap"]) if ok else 0.0
            # 2) περίσσευμα → buffer
            room = (60 - Tb) * bcap
            h2 = min((e_pv - h1 / cop) * cop, pv.HP_KW - h1, room) if ok and hr["m"] in P["heating_months"] else 0.0
            h2 = max(0.0, h2)
            Tb += h2 / bcap
            E -= (h1 + h2) * (1 - 1 / cop)
            # 3) buffer → σπίτι
            h3 = 0.0
            if need - h1 > 0 and Tb > 40:
                h3 = min(need - h1, P["rad_cap"] - h1, (Tb - 40) * bcap); h3 = max(0.0, h3)
                Tb -= h3 / bcap
            Tb -= 0.0015 * (Tb - 20) / bcap
            heat += h1 + h3; elec += (h1 + h2) / cop
    return heat, pvsum, kwp


def s3(kwp, tank):
    q = copy.deepcopy(P); q["tank_m3"] = tank; q["tank_ua"] = 1.6 * tank ** (2 / 3)
    r = sim.run_pv(pv.hours, L, q, kwp, False)
    return r["pv_heat"], r["pv"]


res, _, _ = sim.main()
pick = lambda sy, sz: next(x for x in res["rows"] if x["system"].startswith(sy) and x["size"] == sz)
rows = []
# συλλέκτες ταράτσας (εφικτά στο σπίτι)
t_et, _, _ = ts.run(25, "Β νερό drainback", 2)
rows.append(("Σωλήνες κενού 25 m² + νερό 2 m³", 25, t_et["used"], 11000, "ναι"))
h, pvs, k = pvt_solar_only(24, 0.3)
rows.append((f"PVT 24 m² ({k:.1f} kWp) + αντλία νερού-νερού, buffer 300 L", 24, h, 15020 - 1800 + 1200, "ναι"))
h, _, _ = pvt_solar_only(24, 1.0)
rows.append(("PVT 24 m² + αντλία νερού-νερού, buffer 1 m³ (+ δεύτερη δεξαμενή)", 24, h, 15020 - 1800 + 1200 + 1000, "ναι"))
h, _ = s3(24 * 0.215, 0.3)
rows.append(("Φ/Β 24 m² (5,2 kWp) + αντλία αέρα-νερού, buffer 300 L", 24, h, 1100 * 5.2 + 1000 + 7000 + 800, "ναι"))
h, _ = s3(24 * 0.215, 1.0)
rows.append(("Φ/Β 24 m² (5,2 kWp) + αντλία αέρα-νερού, παλιά δεξαμενή 1 m³", 24, h, 1100 * 5.2 + 1000 + 7000 + 1500, "ναι"))
h, _ = s3(6.0, 1.0)
rows.append(("S3 του GitHub: Φ/Β 6 kWp (~28 m²) + αντλία αέρα-νερού, 1 m³", 28, h, pick("S3", "6 kWp")["capex"], "ναι"))
# μεγάλα κάτοπτρα (όχι εφικτά)
for sy, name in (("S1", "S1: κάτοπτρο 40 m² + άμμος 3 m³"), ("S2", "S2: + αντλία απορρόφησης")):
    r = pick(sy, "40 m², 3 m³")
    rows.append((name, 40, r["solar_frac"] * Ltot, r["capex"], "όχι"))

out = []
print = lambda x: out.append(x)
print("| Σύστημα | Επιφάνεια | Θέρμανση ΜΟΝΟ από ήλιο | Κάλυψη | kWh θέρμανσης ανά m² | Πετρέλαιο που γλιτώνεις | Εξοικονόμηση | Κόστος | Απόσβεση | Εφικτό |")
print("|---|---|---|---|---|---|---|---|---|---|")
for n, A, h, cx, ok in rows:
    sv = h * OIL
    print(f"| {n} | {A} m² | {fmt(h)} kWh | {fmt(100*h/Ltot)}% | {fmt(h/A)} | {fmt(h/7.5)} L | {fmt(sv)} € | {fmt(cx)} € | {fmt(cx/sv,1)} έτη | {ok} |")

import os
md = ["# Καθαρή σύγκριση: μόνο θέρμανση από τον ήλιο", "",
      "Μετράει **μόνο** τη θέρμανση που προέρχεται από τον ήλιο: απευθείας ηλιακή θερμότητα, ή αντλία θερμότητας που δουλεύει **μόνο με ηλιακό ρεύμα** (μαζί με τη δωρεάν θερμότητα που τραβάει από τον αέρα ή τα πάνελ εκείνη την ώρα). **Χωρίς ρεύμα δικτύου** και **χωρίς πίστωση** για ρεύμα που πάει εκτός θέρμανσης. Ό,τι λείπει το καλύπτει ο λέβητας. Εξοικονόμηση = πετρέλαιο που γλιτώνεις × 1,55 €/L. Όλα τα συστήματα με φωτοβολταϊκά περιλαμβάνουν inverter για να κινηθεί η αντλία θερμότητας.", ""] + out + ["",
      "Τρέχει με `python3 kathari_sygkrisi.py`."]
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "KATHARI_SYGKRISI.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
__builtins__.print("\n".join(out))
