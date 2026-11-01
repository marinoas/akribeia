#!/usr/bin/env python3
"""Παραβολικό κάτοπτρο + Stirling + αποθήκη Al-Si (577°C) + δεξαμενή οξικού νατρίου (58°C).
Ωριαία προσομοίωση ενός έτους με τον συνθετικό καιρό του sim.py (άμεση ακτινοβολία DNI, Κόρινθος)."""
import copy, math
import sim

P = copy.deepcopy(sim.P)
HOURS = sim.synthetic_weather(P)
SIGMA = 5.67e-8

# --- Κάτοπτρο ---
D = 4.0                                   # m διάμετρος
RIM = math.radians(45)                    # γωνία χείλους
A = math.pi * D * D / 4                   # m²
F = D / (4 * math.tan(RIM / 2))           # εστιακή απόσταση
DEPTH = D * D / (16 * F)
REFL, INTERCEPT = 0.92, 0.95              # καθρέφτης (γυαλί με ασήμι) / πόσο φως μπαίνει στο άνοιγμα
SLOPE_ERR = 0.004                         # rad, σφάλμα επιφάνειας + στόχευσης (DIY)

# --- Δέκτης (κοιλότητα) ---
T_REC = 650 + 273.15
spread = 0.00465 + 2 * SLOPE_ERR          # ημι-γωνία: ήλιος + σφάλματα
d_ap = 2 * (F / math.cos(RIM / 2) ** 2) * spread * 1.1
A_AP = math.pi * d_ap * d_ap / 4
Q_RAD = 0.9 * SIGMA * T_REC ** 4 * A_AP   # ακτινοβολία από το άνοιγμα
Q_CONV = 0.6 * Q_RAD                      # συναγωγή (εκτίμηση)

# --- Αποθήκη Al-Si ---
STORE_KWH = 40.0
STORE_LOSS = 0.22                         # kW (20 cm μικροπορώδης μόνωση)

# --- Stirling ---
T_HOT = 560 + 273.15                      # κεφαλή (αποθήκη 577°C μείον σωλήνα νατρίου)
T_COLD = 55 + 273.15                      # κρύα άκρη -> οξικό νάτριο
FRAC_CARNOT = 0.50
ETA_ENG = FRAC_CARNOT * (1 - T_COLD / T_HOT)
GEN = 0.92
Q_ENG_MAX, Q_ENG_MIN = 4.0, 1.2           # kW θερμότητας στην κεφαλή


def run(q_eng_max=Q_ENG_MAX, store_kwh=STORE_KWH, d=D):
    a = math.pi * d * d / 4
    s = store_kwh * 0.2                   # ξεκινά λίγο φορτισμένη
    tot = dict(dni=0, rec=0, el=0, heat=0, spill=0, hours=0)
    mon = {m: dict(el=0.0, heat=0.0) for m in range(1, 13)}
    for _ in range(2):
        for k in tot: tot[k] = 0
        for m in mon: mon[m] = dict(el=0.0, heat=0.0)
        for hr in HOURS:
            dni = hr["dni"] if hr["dni"] > 150 else 0.0
            q_in = a * dni * REFL * INTERCEPT / 1000
            q_rec = max(0.0, q_in - (Q_RAD + Q_CONV) / 1000) if q_in > 0 else 0.0
            s = s + q_rec - STORE_LOSS
            s = max(0.0, s)
            q_eng = min(q_eng_max, s)
            if q_eng < Q_ENG_MIN:
                q_eng = 0.0
            s -= q_eng
            if s > store_kwh:
                tot["spill"] += s - store_kwh; s = store_kwh
            el = q_eng * ETA_ENG * GEN
            heat = q_eng * (1 - ETA_ENG)
            tot["dni"] += a * dni / 1000; tot["rec"] += q_rec; tot["el"] += el; tot["heat"] += heat
            tot["hours"] += q_eng > 0
            mon[hr["m"]]["el"] += el; mon[hr["m"]]["heat"] += heat
    return tot, mon


if __name__ == "__main__":
    print(f"Κάτοπτρο: D {D} m, επιφάνεια {A:.2f} m², εστιακή {F:.2f} m (f/D {F/D:.2f}), βάθος {DEPTH:.2f} m")
    print(f"Δέκτης: άνοιγμα {d_ap*100:.1f} cm, συγκέντρωση {A/A_AP:.0f}x, απώλειες στους 650°C {(Q_RAD+Q_CONV)/1000:.2f} kW")
    print(f"Στο μεσημέρι (DNI 900): στο κάτοπτρο {A*0.9:.1f} kW, στον δέκτη {A*0.9*REFL*INTERCEPT-(Q_RAD+Q_CONV)/1000:.1f} kW")
    print(f"Stirling: Carnot {(1-T_COLD/T_HOT)*100:.1f}%, απόδοση {ETA_ENG*100:.1f}%, ρεύμα στο max {Q_ENG_MAX*ETA_ENG*GEN:.2f} kW")
    t, mon = run()
    print(f"\nΈτος: DNI στο κάτοπτρο {t['dni']:.0f} kWh, στην αποθήκη {t['rec']:.0f}, ρεύμα {t['el']:.0f} kWh, "
          f"ζέστη 55°C {t['heat']:.0f} kWh, χαμένα (γεμάτη αποθήκη) {t['spill']:.0f}, ώρες λειτουργίας {t['hours']}")
    print("Ήλιος -> ρεύμα:", f"{t['el']/t['dni']*100:.1f}%")
    names = "Ιαν Φεβ Μαρ Απρ Μάι Ιούν Ιούλ Αύγ Σεπ Οκτ Νοέ Δεκ".split()
    print(" ".join(f"{n}:{mon[i+1]['el']:.0f}" for i, n in enumerate(names)))
    print("\nΜέγεθος μηχανής / αποθήκης:")
    for qm in (3, 4, 6, 9):
        for st in (20, 40, 80):
            t, _ = run(qm, st)
            print(f"  μηχανή {qm} kW θερμ. ({qm*ETA_ENG*GEN:.2f} kW ρεύμα), αποθήκη {st} kWh: ρεύμα {t['el']:.0f} kWh/έτος, χαμένα {t['spill']:.0f}")
