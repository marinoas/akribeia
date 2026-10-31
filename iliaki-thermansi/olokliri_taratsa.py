#!/usr/bin/env python3
"""Όλη η ταράτσα: PVT 24 m² (κλίση 40°) + επιπλέον Φ/Β 4,5 kWp (κλίση 15°, ~21 m²).
Αντλία θερμότητας νερού-νερού, πηγή η παλιά δεξαμενή 1 m³, buffer 1 m³ (δεύτερη δεξαμενή).
Τρόποι: (α) μόνο ηλιακό ρεύμα την ίδια ώρα, (β) ετήσιο ισοζύγιο: το δίκτυο ως εποχική μπαταρία."""
import copy, os
import sim, pvt_sim as pv
from report import fmt

L = pv.loads; Ltot = sum(L); OIL = pv.OIL; P = pv.P
Pflat = copy.deepcopy(P); Pflat["pv_tilt"] = 15.0
EXTRA_KWP = 4.5
HOUSE_KWH = 9000      # ρεύμα σπιτιού εκτός θέρμανσης (εκτίμηση, πριν βρεθεί ο κρυφός καταναλωτής)


def run(extra_kwp, grid, rad_frac=0.50, t_sup=55.0, area=24, buf_m3=1.0):
    kwp = area * pv.WP_PER_M2 / 1000
    capk, latent = 1.163, 93.0
    bcap = buf_m3 * 1.163; Tb = 40.0
    rad_cap = rad_frac * P["rad_cap"] / 0.50
    old_tsup = pv.T_SUP; pv.T_SUP = t_sup
    E = 10 * capk
    for _ in range(2):
        a = dict(heat=0.0, heat_solar=0.0, boiler=0.0, pv=0.0, pv_hp=0.0, hp_e=0.0, grid=0.0, export=0.0,
                 mon={m: [0.0, 0.0, 0.0, 0.0] for m in range(1, 13)})
        for hr, Lh in zip(pv.hours, L):
            ta = hr["ta"]; G = sim.poa(hr, P); G2 = sim.poa(hr, Pflat)
            Ts = E / capk if E > 0 else 0.0
            tm = Ts + 3
            q = max(0.0, area * (pv.ETA_TH0 * G - pv.UL * (tm - ta) - (pv.SKY if G < 50 else 0)) / 1000)
            q = min(q, max(0.0, 35 * capk - E))
            tcell = (tm + 5) if q > 0 else (ta + G / 800 * 25)
            e_pv = kwp * G / 1000 * pv.PR * (1 + pv.GAMMA * (tcell - 25))
            e_pv += extra_kwp * G2 / 1000 * pv.PR * (1 + pv.GAMMA * (ta + G2 / 800 * 25 - 25))
            a["pv"] += e_pv
            E += q
            heating = hr["m"] in P["heating_months"]
            need = Lh if heating else 0.0
            cop = pv.cop_ww(Ts)
            ok = E > -0.85 * latent
            h1 = min(need, e_pv * cop, pv.HP_KW, rad_cap) if ok else 0.0
            room = (60 - Tb) * bcap
            h2 = max(0.0, min((e_pv - h1 / cop) * cop, pv.HP_KW - h1, room)) if ok and heating else 0.0
            Tb += h2 / bcap
            h3 = 0.0
            if need - h1 > 0 and Tb > 40:
                h3 = max(0.0, min(need - h1, rad_cap - h1, (Tb - 40) * bcap)); Tb -= h3 / bcap
            h4 = 0.0
            if grid and ok and need - h1 - h3 > 0:
                h4 = max(0.0, min(need - h1 - h3, pv.HP_KW - h1 - h2, rad_cap - h1 - h3))
            E -= (h1 + h2 + h4) * (1 - 1 / cop)
            Tb -= 0.0015 * (Tb - 20) / bcap
            used_pv = (h1 + h2) / cop
            a["pv_hp"] += used_pv; a["hp_e"] += (h1 + h2 + h4) / cop; a["grid"] += h4 / cop
            a["export"] += e_pv - used_pv
            hh = h1 + h3 + h4
            a["heat"] += hh; a["heat_solar"] += h1 + h3; a["boiler"] += need - hh
            mm = a["mon"][hr["m"]]; mm[0] += need; mm[1] += h1 + h3; mm[2] += h4; mm[3] += need - hh
    pv.T_SUP = old_tsup
    return a


cases = [
    ("1. PVT 24 m², μόνο ηλιακό ρεύμα την ίδια ώρα", 0.0, False, 0.50, 55.0, 15420),
    ("2. Όλη η ταράτσα (PVT 24 m² + Φ/Β 4,5 kWp), μόνο ηλιακό ρεύμα την ίδια ώρα", EXTRA_KWP, False, 0.50, 55.0, 15420 + 4000),
    ("3. Όλη η ταράτσα, ετήσιο ισοζύγιο, αντλία 55°C (λέβητας για τα πολύ κρύα)", EXTRA_KWP, True, 0.50, 55.0, 15420 + 4000 + 1000),
    ("4. Όλη η ταράτσα, ετήσιο ισοζύγιο, αντλία υψηλής θερμοκρασίας (65°C)", EXTRA_KWP, True, 0.75, 65.0, 15420 + 4000 + 1000 + 1500),
]
out = []; w = out.append
w("# Όλη η ταράτσα + ετήσιο ισοζύγιο")
w("")
w("Ταράτσα ~50 m²: **PVT 24 m² (5,2 kWp, κλίση 40°)** + **επιπλέον φωτοβολταϊκά 4,5 kWp** (~21 m², χαμηλή κλίση 15°, για λιγότερη σκίαση ανάμεσα στις σειρές). Σύνολο ~9,7 kWp. Αντλία θερμότητας νερού-νερού 8 kW, πηγή η παλιά δεξαμενή 1 m³, buffer 1 m³. Τρέχει με `python3 olokliri_taratsa.py`.")
w("")
w("**«Ετήσιο ισοζύγιο»:** η αντλία παίρνει ρεύμα από το δίκτυο όταν δεν φτάνει ο ήλιος, και το ηλιακό ρεύμα που περισσεύει (κυρίως άνοιξη-καλοκαίρι) πηγαίνει στο δίκτυο. Αν στο τέλος του χρόνου **τα πάνελ έχουν δώσει περισσότερο από όσο πήρε η αντλία**, η θέρμανση είναι **ηλιακή σε ετήσια βάση**. Το δίκτυο λειτουργεί ως εποχική μπαταρία.")
w("")
w("| Σενάριο | Θέρμανση από αντλία | Πετρέλαιο που μένει | Ρεύμα πάνελ τον χρόνο | Ρεύμα αντλίας (σύνολο) | Από αυτό, από δίκτυο | Πάνελ ÷ αντλία | Ηλιακή θέρμανση σε ετήσια βάση | Κόστος |")
w("|---|---|---|---|---|---|---|---|---|")
results = {}
for name, ex, g, rf, ts_, cx in cases:
    r = run(ex, g, rf, ts_)
    results[name] = (r, cx)
    ratio = r["pv"] / r["hp_e"] if r["hp_e"] else 0
    sol = r["heat"] if (g and ratio >= 1) else r["heat_solar"]
    w(f"| {name} | {fmt(r['heat'])} kWh (**{fmt(100*r['heat']/Ltot)}%**) | {fmt(r['boiler']/7.5)} L | {fmt(r['pv'])} kWh | {fmt(r['hp_e'])} kWh | {fmt(r['grid'])} kWh | {fmt(ratio,1)}× | **{fmt(100*sol/Ltot)}%** | ~{fmt(cx)} € |")
w("")
r3, c3 = results[cases[2][0]]; r4, c4 = results[cases[3][0]]; r2, c2 = results[cases[1][0]]
w("## Οικονομικά (σενάρια 3 και 4)")
w("")
w("Δύο εκδοχές, ανάλογα με το τι ισχύει για το ρεύμα που στέλνεις στο δίκτυο:")
w("")
w("| | Πλήρης συμψηφισμός (1 kWh που δίνεις = 1 kWh που παίρνεις) | Ταυτοχρονισμένος συμψηφισμός (ό,τι στέλνεις πληρώνεται ~0,06 €/kWh) |")
w("|---|---|---|")
for nm, r, cx in (("Σενάριο 3", r3, c3), ("Σενάριο 4", r4, c4)):
    oil_save = (Ltot - r["boiler"]) * OIL
    surplus = max(0.0, r["export"] - r["grid"])
    full = oil_save + min(surplus, HOUSE_KWH) * 0.20
    nb = oil_save - r["grid"] * pv.EL + r["export"] * 0.06
    w(f"| {nm}: εξοικονόμηση/έτος | ~{fmt(full)} € (θέρμανση + {fmt(min(surplus,HOUSE_KWH))} kWh περίσσευμα για το σπίτι) | ~{fmt(nb)} € |")
    w(f"| {nm}: απόσβεση | ~{fmt(cx/full,1)} χρόνια | ~{fmt(cx/nb,1)} χρόνια |")
w("")
w("## Από πού έρχεται η θέρμανση κάθε μήνα (σενάριο 4)")
w("")
w("| Μήνας | Ανάγκη | Ηλιακό ρεύμα την ίδια ώρα / buffer | Δίκτυο (επιστρέφεται από το καλοκαίρι) | Λέβητας |")
w("|---|---|---|---|---|")
for m in (10, 11, 12, 1, 2, 3, 4):
    v = r4["mon"][m]
    w(f"| {['Ιαν','Φεβ','Μαρ','Απρ','Μάι','Ιούν','Ιούλ','Αύγ','Σεπ','Οκτ','Νοέ','Δεκ'][m-1]} | {fmt(v[0])} | {fmt(v[1])} | {fmt(v[2])} | {fmt(max(0.0, v[3]))} |")
w("")
w("## Παραδοχές")
w("")
w(f"Ίδιο μοντέλο PVT με το `pvt_sim.py`. Επιπλέον Φ/Β: απόδοση χωρίς ψύξη (θερμοκρασία κυττάρου από τον αέρα και την ακτινοβολία). Αντλία 55°C: τα παλιά καλοριφέρ δίνουν ~50% της ισχύος τους. Αντλία υψηλής θερμοκρασίας 65°C (π.χ. με ψυκτικό R290): ~75% της ισχύος τους, αλλά χαμηλότερο COP. Ρεύμα σπιτιού εκτός θέρμανσης ~{fmt(HOUSE_KWH)} kWh/έτος (εκτίμηση). Κόστη: PVT DIY με δεύτερη δεξαμενή ~15.400 €, επιπλέον Φ/Β ~4.000 €, σύνδεση με δίκτυο και μεγαλύτερος inverter ~1.000 €, αντλία υψηλής θερμοκρασίας +1.500 €. **Οι όροι συμψηφισμού για νέα φωτοβολταϊκά έχουν αλλάξει στην Ελλάδα: έλεγξε τι ισχύει πριν αποφασίσεις.**")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "OLOKLIRI_TARATSA.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
