#!/usr/bin/env python3
"""Inventor Matrix Zero MX290-12S (αέρα-νερού, R290, έως 75°C) στο σπίτι της Κορίνθου.
Τα COP βαθμονομήθηκαν στα στοιχεία του κατασκευαστή (A7/W35 4,8 και A7/W55 3,1).
Σενάρια: χωρίς Φ/Β | Φ/Β όλη η ταράτσα (μόνο ηλιακό) | Φ/Β όλη η ταράτσα + ετήσιο ισοζύγιο."""
import copy, os
import sim
from report import fmt

P = copy.deepcopy(sim.P)
hours = sim.synthetic_weather(P)
loads, ua = sim.heating_loads(hours, P)
Ltot = sum(loads)
OIL = P["oil_eur_l"] / (P["oil_kwh_l"] * P["boiler_eff"])
EL = P["elec_eur_kwh"]
P40 = copy.deepcopy(P); P40["pv_tilt"] = 40.0
P15 = copy.deepcopy(P); P15["pv_tilt"] = 15.0

ETA_C = 0.43                        # βαθμονόμηση στο product fiche (EN14825): A-7/W52 2,23 · A2/W42 3,52 · A7/W36 4,99 · A12/W30 6,41 · A-10/W55 2,05 · A2/W55 2,55 (απόκλιση ±8%)
T_MAX = 75.0
DESIGN = ua * (P["t_balance"] - 0.0)  # ~9,8 kW: φορτίο στους 0°C, για το οποίο υποθέτουμε ότι είναι διαστασιολογημένα τα καλοριφέρ (80/60)


def cop(t_out, t_sup):
    c = ETA_C * (t_sup + 273.15) / max(5.0, t_sup - t_out)   # οι τιμές του fiche περιλαμβάνουν ήδη την απόψυξη
    return min(6.5, c)


def capacity(t_out):
    """Από το fiche: ≥10,6 kW στους -7°C (νερό 52°C), 10,15 kW στους -10°C (55°C), 12 kW στους 7°C."""
    return 12.0 if t_out >= 7 else 12.0 - 0.106 * (7 - t_out)


def supply_needed(load):
    """Θερμοκρασία προσαγωγής που χρειάζονται τα καλοριφέρ για να δώσουν αυτό το φορτίο."""
    f = max(load / DESIGN, 0.0)
    return max(35.0, 20 + 50 * f ** (1 / 1.3) + 5)


def run(kwp40, kwp15, grid, buf_m3=1.0):
    bcap = buf_m3 * 1.163; Tb = 40.0
    a = dict(heat=0.0, boiler=0.0, e_hp=0.0, e_pv=0.0, e_grid=0.0, pv=0.0, export=0.0, short_h=0,
             mon={m: [0.0, 0.0, 0.0, 0.0] for m in range(1, 13)})
    for hr, L in zip(hours, loads):
        ta = hr["ta"]
        pv = (kwp40 * sim.poa(hr, P40) + kwp15 * sim.poa(hr, P15)) / 1000 * 0.84
        a["pv"] += pv
        heating = hr["m"] in P["heating_months"]
        need = L if heating else 0.0
        ts = supply_needed(need) if need > 0 else 35.0
        cap = capacity(ta)
        h_ok = need if ts <= T_MAX else need * ((T_MAX - 25) / 50) ** 1.3 / max(need / DESIGN, 1e-9) / 1.0
        h_ok = min(need, h_ok)
        c = cop(ta, min(ts, T_MAX))
        avail_pv = pv
        # 1) αντλία με ηλιακό ρεύμα
        h1 = min(h_ok, cap, avail_pv * c)
        avail_pv -= h1 / c
        # 2) buffer → σπίτι (αν είναι αρκετά ζεστό)
        h2 = 0.0
        if h_ok - h1 > 0 and Tb > ts:
            h2 = min(h_ok - h1, (Tb - max(ts, 40)) * bcap); h2 = max(0.0, h2); Tb -= h2 / bcap
        # 3) περίσσευμα ηλιακού → φόρτιση buffer έως 60°C
        h3 = 0.0
        if heating and avail_pv > 0 and Tb < 60:
            c60 = cop(ta, 62.0)
            h3 = min(avail_pv * c60, cap - h1, (60 - Tb) * bcap); h3 = max(0.0, h3)
            Tb += h3 / bcap; avail_pv -= h3 / c60; a["e_pv"] += h3 / c60; a["e_hp"] += h3 / c60
        # 4) δίκτυο
        h4 = 0.0
        if grid and h_ok - h1 - h2 > 0:
            h4 = min(h_ok - h1 - h2, cap - h1 - h3); h4 = max(0.0, h4)
        Tb -= 0.0015 * (Tb - 15) / bcap
        hh = h1 + h2 + h4
        a["e_hp"] += (h1 + h4) / c; a["e_pv"] += h1 / c; a["e_grid"] += h4 / c
        a["export"] += avail_pv
        a["heat"] += hh; a["boiler"] += need - hh
        if need - hh > 0.05:
            a["short_h"] += 1
        mm = a["mon"][hr["m"]]; mm[0] += need; mm[1] += h1 + h2; mm[2] += h4; mm[3] += need - hh
    a["scop"] = a["heat"] / a["e_hp"] if a["e_hp"] else 0
    return a


HP = 4800 + 1600; BUF = 1500; INT = 1250; PV = 10500
HOUSE = 9000
S = [
    ("Α. Μόνο αντλία (ρεύμα δικτύου), χωρίς φωτοβολταϊκά", 0.0, 0.0, True, HP + BUF + INT),
    ("Β. Αντλία + Φ/Β 9,7 kWp, μόνο ηλιακό ρεύμα την ίδια ώρα", 5.2, 4.5, False, HP + BUF + INT + PV),
    ("Γ. Αντλία + Φ/Β 9,7 kWp, ετήσιο ισοζύγιο", 5.2, 4.5, True, HP + BUF + INT + PV),
]
out = []; w = out.append
w("# Inventor Matrix Zero MX290-12S στο σπίτι σου")
w("")
w("Αντλία αέρα-νερού monoblock, R290, έως 75°C, 12 kW. Τα COP και η ισχύς του μοντέλου βαθμονομήθηκαν στο **επίσημο product fiche** του κατασκευαστή (EN14825, ±8%). Η θερμοκρασία νερού ακολουθεί αυτό που χρειάζονται τα καλοριφέρ κάθε ώρα (αντιστάθμιση εξωτερικής θερμοκρασίας). Η παλιά δεξαμενή 1 m³ είναι buffer. Ίδιος καιρός και ζήτηση με τα υπόλοιπα σενάρια. Τρέχει με `python3 mx290_sim.py`.")
w("")
w("| Σενάριο | Θέρμανση από αντλία | Πετρέλαιο που μένει | Ώρες που δεν φτάνει η αντλία | Ρεύμα αντλίας | από Φ/Β | από δίκτυο | Μέσο COP | Ρεύμα Φ/Β τον χρόνο |")
w("|---|---|---|---|---|---|---|---|---|")
R = {}
for n, k40, k15, g, cx in S:
    r = run(k40, k15, g); R[n] = (r, cx)
    w(f"| {n} | **{fmt(100*r['heat']/Ltot)}%** | {fmt(r['boiler']/7.5)} L | {r['short_h']} | {fmt(r['e_hp'])} kWh | {fmt(r['e_pv'])} | {fmt(r['e_grid'])} | {fmt(r['scop'],1)} | {fmt(r['pv'])} kWh |")
w("")
w("## Οικονομικά")
w("")
w("| Σενάριο | Κόστος | Εξοικονόμηση/έτος | Απόσβεση |")
w("|---|---|---|---|")
for n, (r, cx) in R.items():
    oil_save = r["heat"] * OIL
    if r["pv"] == 0:
        sv = oil_save - r["e_grid"] * EL
        w(f"| {n} | ~{fmt(cx)} € | ~{fmt(sv)} € | ~{fmt(cx/sv,1)} χρόνια |")
    elif n.startswith("Β"):
        sv = oil_save + min(r["export"], HOUSE) * 0.20 * 0.5
        w(f"| {n} | ~{fmt(cx)} € | ~{fmt(sv)} € (με ~50% του υπόλοιπου ηλιακού ρεύματος να καλύπτει το σπίτι) | ~{fmt(cx/sv,1)} χρόνια |")
    else:
        full = oil_save + min(max(0, r["export"] - r["e_grid"]), HOUSE) * 0.20
        nb = oil_save - r["e_grid"] * EL + r["export"] * 0.06
        w(f"| {n}, πλήρης συμψηφισμός | ~{fmt(cx)} € | ~{fmt(full)} € | ~{fmt(cx/full,1)} χρόνια |")
        w(f"| {n}, ταυτοχρονισμένος συμψηφισμός (έγχυση 0,06 €/kWh) | ~{fmt(cx)} € | ~{fmt(nb)} € | ~{fmt(cx/nb,1)} χρόνια |")
w("")
rA = R[S[0][0]][0]
w("## Ανά μήνα (σενάριο Α, μόνο αντλία)")
w("")
w("| Μήνας | Ανάγκη | Αντλία | Λέβητας |")
w("|---|---|---|---|")
for m in (10, 11, 12, 1, 2, 3, 4):
    v = rA["mon"][m]
    w(f"| {['Ιαν','Φεβ','Μαρ','Απρ','Μάι','Ιούν','Ιούλ','Αύγ','Σεπ','Οκτ','Νοέ','Δεκ'][m-1]} | {fmt(v[0])} | {fmt(v[1]+v[2])} | {fmt(max(0,v[3]))} |")
w("")
w("## Παραδοχές")
w("")
w(f"COP = 0,43 × Carnot (προσαγωγή/εξωτερική), βαθμονομημένο στα σημεία του product fiche (A-7/W52: 2,23, A2/W42: 3,52, A7/W36: 4,99, A12/W30: 6,41, A-10/W55: 2,05, A2/W55: 2,55), μέγιστο 6,5. Ισχύς 12 kW στους 7°C, 10,6 kW στους −7°C, 10,15 kW στους −10°C (από το fiche, για νερό έως 55°C. Σε 65-75°C η ισχύς είναι πιθανότατα λίγο μικρότερη). Καλοριφέρ διαστασιολογημένα για 80/60°C στους 0°C ({fmt(DESIGN,1)} kW). Η θερμοκρασία νερού που χρειάζεται υπολογίζεται κάθε ώρα από το φορτίο. Buffer 1 m³, φόρτιση έως 60°C με το ηλιακό που περισσεύει. Φ/Β: 5,2 kWp σε 40° + 4,5 kWp σε 15°. Κόστη: αντλία 4.800 € + εγκατάσταση ~1.600 €, buffer ~1.500 €, σύνδεση με λέβητα και αυτοματισμοί ~1.250 €, Φ/Β ~10.500 €. Πετρέλαιο 1,55 €/L, λέβητας 75%, ρεύμα 0,22 €/kWh.")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MX290.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
