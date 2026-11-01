#!/usr/bin/env python3
"""Η μηχανή R1233 ως θερμική αντλία θερμότητας (ORC που κινεί απευθείας συμπιεστή).
Τον χειμώνα ο άξονας του scroll-εκτονωτή γυρίζει με ιμάντα έναν ανοιχτού τύπου συμπιεστή αυτοκινήτου.
Ο συμπιεστής παίρνει θερμότητα από τον έξω αέρα: τα ψυγεία κλιματισμού δουλεύουν τώρα ως εξατμιστής.
Και ο ατμός της εξαγωγής και ο ατμός του συμπιεστή υγροποιούνται στον ίδιο εναλλάκτη των καλοριφέρ.
Ένα υγρό, R1233zd, για όλα. Όταν το σπίτι δεν θέλει θέρμανση, ο συμπιεστής αποσυμπλέκεται και ο άξονας βγάζει ρεύμα."""
import copy
from collections import defaultdict
import CoolProp.CoolProp as CP
import sim
import scroll_sim as S
import olokliro_etos as O

F = "R1233zd(E)"
BELT = 0.95
ETA_C = 0.65


def cop_hp(ta, tc=52):
    te = ta - 6
    pe = CP.PropsSI("P", "T", te + 273.15, "Q", 1, F)
    pc = CP.PropsSI("P", "T", tc + 273.15, "Q", 1, F)
    h1 = CP.PropsSI("H", "T", te + 276.15, "P", pe, F)
    s1 = CP.PropsSI("S", "T", te + 276.15, "P", pe, F)
    h2 = h1 + (CP.PropsSI("H", "P", pc, "S", s1, F) - h1) / ETA_C
    h3 = CP.PropsSI("H", "T", tc + 273.15, "Q", 0, F)
    return (h2 - h3) / (h2 - h1)


_COP = {}


def cop(ta):
    k = int(round(ta))
    if k not in _COP:
        _COP[k] = cop_hp(k)
    return _COP[k]


def shaft_frac(tb, vr):
    st = S.scroll_state(tb, 50, vr, 0.7, tb)
    q = st["h1"] - st["h4r"]
    return (st["w"] - st["wp"] * S.PUMP_ETA / 0.5) / q, 1 - st["w"] / q


def main():
    fw, fr = shaft_frac(140, O.VR * O.VR)
    sw, sr = shaft_frac(100, O.VR)
    mon = defaultdict(lambda: defaultdict(float))
    deficit = defaultdict(float)
    hours_by_day = defaultdict(list)
    for hr, L in zip(O.HOURS, O.LOADS):
        m, G, ta = hr["m"], sim.poa(hr, O.P), hr["ta"]
        mm = mon[m]
        mm["load"] += L
        used = 0.0
        if G >= 150:
            el_out, _ = O.solar_hour(G, ta, int(round(min(60, ta + 20))))
            if L > 0:
                # ηλιακή θερμότητα στο λάδι/R1233 ~ ρεύμα εκτός θέρμανσης / απόδοση -> εκτίμηση από τη λειτουργία καλοριφέρ
                el_rad, rej_rad = O.solar_hour(G, ta, 50)
                q_in = rej_rad / sr if sr else 0
                heat = q_in * (sr + sw * BELT * cop(ta))
                used = min(L, heat)
                mm["heat_sun"] += used
            else:
                mm["el_sun"] += el_out
        deficit[(m, hr["n"])] += L - used
        hours_by_day[(m, hr["n"])].append(ta)
    for key, d in deficit.items():
        m = key[0]
        mm = mon[m]
        if m in O.FIRE_MONTHS and d > 0:
            ta_eve = sum(hours_by_day[key][17:23]) / 6
            f_heat = fr + fw * BELT * cop(ta_eve)
            q_oil = min(d / f_heat, O.FIRE_KW * O.FIRE_HMAX)
            mm["heat_fire"] += q_oil * f_heat; mm["wood"] += q_oil / O.WOOD_KWH_KG
            mm["from_air"] += q_oil * fw * BELT * cop(ta_eve) - q_oil * fw * BELT
            d -= q_oil * f_heat
        mm["boiler"] += max(0.0, d)
    return mon, fw, fr, sw, sr


if __name__ == "__main__":
    mon, fw, fr, sw, sr = main()
    print(f"Τζάκι (140°C): άξονας {fw*100:.1f}% της θερμότητας, κατευθείαν στα καλοριφέρ {fr*100:.1f}%")
    print(f"Ήλιος (100°C): άξονας {sw*100:.1f}%, κατευθείαν {sr*100:.1f}%")
    for ta in (10, 5, 0):
        print(f"  αέρας {ta:>2}°C: COP συμπιεστή {cop(ta):.2f}, θέρμανση τζακιού {(fr + fw*BELT*cop(ta))*100:.0f}% της θερμότητας του λαδιού")
    names = "Ιαν Φεβ Μαρ Απρ Μάι Ιούν Ιούλ Αύγ Σεπ Οκτ Νοέ Δεκ".split()
    tot = defaultdict(float)
    print(f"\n{'Μήνας':<5} {'Ζήτηση':>7} {'Θέρμ. ήλιος':>11} {'Θέρμ. τζάκι':>11} {'Λέβητας':>8} {'Ξύλα kg':>8} {'Ρεύμα ήλιος':>11}")
    for i, nm in enumerate(names, 1):
        mm = mon[i]
        for k in ("load", "heat_sun", "heat_fire", "boiler", "wood", "el_sun", "from_air"):
            tot[k] += mm[k]
        print(f"{nm:<5} {mm['load']:7.0f} {mm['heat_sun']:11.0f} {mm['heat_fire']:11.0f} {mm['boiler']:8.0f} {mm['wood']:8.0f} {mm['el_sun']:11.0f}")
    print(f"{'ΣΥΝ':<5} {tot['load']:7.0f} {tot['heat_sun']:11.0f} {tot['heat_fire']:11.0f} {tot['boiler']:8.0f} {tot['wood']:8.0f} {tot['el_sun']:11.0f}")
    print(f"Θερμότητα από τον αέρα (μέσω συμπιεστή, στο τζάκι): {tot['from_air']:.0f} kWh")
