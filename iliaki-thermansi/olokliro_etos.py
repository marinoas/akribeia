#!/usr/bin/env python3
"""Ολόκληρη η διάταξη για ένα έτος: ήλιος (μέρα) + τζάκι (βράδυ) -> scroll R1233 -> ρεύμα + θέρμανση.
Ωριαίος καιρός και ζήτηση θέρμανσης από το sim.py (12.500 kWh/έτος, Κόρινθος).

Ήλιος: 5 m² επίπεδος + 45 m² σωλήνες κενού, 1 scroll (λόγος όγκων 3,5, 65 cc).
  Κάθε ώρα διαλέγει: υγροποίηση στα καλοριφέρ (50°C, η ζέστη πάει στο σπίτι) ή στα ψυγεία έξω (αέρας +20 K),
  όποιο έχει μεγαλύτερη αξία σε € (ρεύμα + πετρέλαιο που δεν καίγεται).
Τζάκι: Νοέ–Μάρ, καλύπτει ό,τι λείπει από τη θέρμανση της ημέρας, έως 6 ώρες × 10 kW στο λάδι.
  2 scroll σε σειρά, βρασμός 140°C, υγροποίηση στα καλοριφέρ. Υποθέτει δοχείο αδρανείας / θερμική μάζα
  σπιτιού που μεταφέρει τη ζέστη του βραδιού στη νύχτα.
Ό,τι λείπει ακόμα: ο υπάρχων λέβητας πετρελαίου."""
import copy
from collections import defaultdict
import CoolProp.CoolProp as CP
import sim
import scroll_sim as S

S.INTERNAL = 0.65                     # μέση περίπτωση για μετατρεπμένο συμπιεστή
P = copy.deepcopy(sim.P)
P["pv_tilt"] = 30
HOURS = sim.synthetic_weather(P)
LOADS, _ = sim.heating_loads(HOURS, P)

EL = P["elec_eur_kwh"]                                       # 0,22 €/kWh
OIL_HEAT = P["oil_eur_l"] / (P["oil_kwh_l"] * P["boiler_eff"])   # €/kWh θερμότητας από λέβητα
WOOD_KWH_KG = 3.0                                            # ωφέλιμα kWh στο λάδι ανά kg ξύλου
VR, DISP, A_FLAT, A_EVAC = 3.5, 65, 5, 45
FIRE_MONTHS = {11, 12, 1, 2, 3}
FIRE_KW, FIRE_HMAX = 10.0, 6


def solar_hour(G, ta, tc):
    """Καλύτερο σημείο λειτουργίας για υγροποίηση στους tc. Επιστρέφει (ρεύμα kW, θερμότητα στο ψυγείο kW)."""
    best = (0.0, 0.0)
    v_in = DISP / 1e6 / VR
    for tb in range(60, 141, 2):
        if tb <= tc + 10:
            continue
        s = S.scroll_state(tb, tc, VR, 0.7, 85)
        if s["w"] <= 0:
            continue
        qe = A_EVAC * G * max(0.0, S.eta(S.EVAC, tb + 5, ta, G)) / 1000
        if qe <= 0:
            continue
        qf = A_FLAT * G * max(0.0, S.eta(S.FLAT, (s["t4r"] + s["tp"]) / 2, ta, G)) / 1000
        dh_tot, dh_pre = s["h1"] - s["h4r"], s["hp"] - s["h4r"]
        m = (qe + qf) * 1000 / dh_tot if qf <= (qe + qf) * dh_pre / dh_tot else qe * 1000 / (s["h1"] - s["hp"])
        m = min(m, s["d1"] * v_in * S.VOL_EFF * 3000 / 60)
        rpm = m / (s["d1"] * v_in * S.VOL_EFF) * 60
        f_low = 1.0 if rpm >= 1500 else 0.5 + 0.5 * rpm / 1500
        el = m * (s["w"] * f_low * S.GEN - s["wp"]) / 1000 - 0.02
        rej = m * (dh_tot - s["w"] * f_low) / 1000
        if el > best[0]:
            best = (el, rej)
    return best


def fire_point():
    s = S.scroll_state(140, 50, VR * VR, 0.7, 140)
    q = s["h1"] - s["h4r"]
    el_frac = (s["w"] * S.GEN - s["wp"]) / q
    return el_frac, 1 - s["w"] / q


def main():
    fe, fr = fire_point()
    mon = defaultdict(lambda: defaultdict(float))
    day_deficit = defaultdict(float)
    for hr, L in zip(HOURS, LOADS):
        m, G, ta = hr["m"], sim.poa(hr, P), hr["ta"]
        mm = mon[m]
        mm["load"] += L
        heat_used = 0.0
        if G >= 150:
            el_out, rej_out = solar_hour(G, ta, int(round(min(60, ta + 20))))
            el_rad, rej_rad = solar_hour(G, ta, 50) if L > 0 else (0.0, 0.0)
            v_out = el_out * EL
            v_rad = el_rad * EL + min(L, rej_rad) * OIL_HEAT
            if L > 0 and v_rad > v_out:
                heat_used = min(L, rej_rad)
                mm["el_sun"] += el_rad; mm["heat_sun"] += heat_used; mm["sun_out"] += rej_rad - heat_used
            else:
                mm["el_sun"] += el_out; mm["sun_out"] += rej_out
        day_deficit[(m, hr["n"])] += L - heat_used
    for (m, n), deficit in day_deficit.items():
        mm = mon[m]
        if m in FIRE_MONTHS and deficit > 0:
            q_oil = min(deficit / fr, FIRE_KW * FIRE_HMAX)       # θερμότητα στο λάδι
            mm["fire_in"] += q_oil; mm["el_fire"] += q_oil * fe; mm["heat_fire"] += q_oil * fr
            mm["wood"] += q_oil / WOOD_KWH_KG
            deficit -= q_oil * fr
        mm["boiler"] += max(0.0, deficit)
    return mon, fe, fr


if __name__ == "__main__":
    mon, fe, fr = main()
    names = "Ιαν Φεβ Μαρ Απρ Μάι Ιούν Ιούλ Αύγ Σεπ Οκτ Νοέ Δεκ".split()
    keys = ["load", "el_sun", "el_fire", "heat_sun", "heat_fire", "boiler", "wood"]
    print(f"Τζάκι: {fe*100:.1f}% ρεύμα, {fr*100:.1f}% θερμότητα στα καλοριφέρ (της θερμότητας στο λάδι)\n")
    print(f"{'Μήνας':<5} {'Ζήτηση':>7} {'Ρεύμα ήλιος':>11} {'Ρεύμα τζάκι':>11} {'Θέρμ. ήλιος':>11} {'Θέρμ. τζάκι':>11} {'Λέβητας':>8} {'Ξύλα kg':>8}")
    tot = defaultdict(float)
    for i, nm in enumerate(names, 1):
        mm = mon[i]
        for k in keys + ["sun_out"]:
            tot[k] += mm[k]
        print(f"{nm:<5} {mm['load']:7.0f} {mm['el_sun']:11.0f} {mm['el_fire']:11.0f} {mm['heat_sun']:11.0f} "
              f"{mm['heat_fire']:11.0f} {mm['boiler']:8.0f} {mm['wood']:8.0f}")
    print(f"{'ΣΥΝ':<5} {tot['load']:7.0f} {tot['el_sun']:11.0f} {tot['el_fire']:11.0f} {tot['heat_sun']:11.0f} "
          f"{tot['heat_fire']:11.0f} {tot['boiler']:8.0f} {tot['wood']:8.0f}")
    print(f"\nΘερμότητα ήλιου που έφυγε από τα ψυγεία έξω: {tot['sun_out']:.0f} kWh (διαθέσιμη για ζεστό νερό χρήσης)")
    el = tot["el_sun"] + tot["el_fire"]
    oil_saved_kwh = tot["heat_sun"] + tot["heat_fire"]
    oil_l = oil_saved_kwh / (P["oil_kwh_l"] * P["boiler_eff"])
    print(f"Ρεύμα συνολικά: {el:.0f} kWh/έτος  -> {el*EL:.0f} €/έτος (στα {EL} €/kWh)")
    print(f"Θέρμανση από τη διάταξη: {oil_saved_kwh:.0f} kWh = {oil_l:.0f} L πετρέλαιο λιγότερο -> {oil_l*P['oil_eur_l']:.0f} €/έτος")
    print(f"Ξύλα: {tot['wood']/1000:.1f} τόνοι/έτος")
