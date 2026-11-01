#!/usr/bin/env python3
"""Βελτιστοποίηση της διάταξης του χρήστη:
ηλιακός συλλέκτης (boiler, απευθείας βρασμός R1233) -> κινητήρας + turbo -> ψυγείο αυτοκινήτου με βεντιλατέρ
-> δοχείο -> αντλία από τον στρόφαλο -> συλλέκτης.
Ωριαία προσομοίωση ενός έτους (συνθετικός καιρός Κορίνθου, sim.py).
Κάθε ώρα επιλέγεται η θερμοκρασία βρασμού που δίνει το μέγιστο καθαρό ρεύμα."""
import copy
import CoolProp.CoolProp as CP
import sim

F = "R1233zd(E)"
P0 = copy.deepcopy(sim.P)
HOURS = sim.synthetic_weather(P0)

COLL = {   # (η0, a1, a2, μέγιστος βρασμός °C)
    "επίπεδος": (0.78, 3.8, 0.015, 95),      # χαλκός, δοκιμή 10 bar -> έως ~95°C (9,35 bar)
    "κενού":    (0.45, 0.85, 0.004, 140),     # heat pipe, ανά μικτή επιφάνεια (ίδιοι με michani_sim)
}
GEN = 0.90          # γεννήτρια
PUMP_ETA = 0.5      # αντλία τροφοδοσίας
TB_RANGE = range(40, 141, 2)
TC_RANGE = range(0, 61)
_cache = {}


def cycle(tb, tc, eta_exp, recup):
    """Έργο ανά kJ θερμότητας από τον συλλέκτη (καθαρό, μετά την αντλία) και κλάσμα αντλίας."""
    key = (tb, tc, eta_exp, recup)
    if key in _cache:
        return _cache[key]
    if tb <= tc + 5:
        _cache[key] = (0.0, 0.0)
        return _cache[key]
    ph = CP.PropsSI("P", "T", tb + 273.15, "Q", 1, F)
    pc = CP.PropsSI("P", "T", tc + 273.15, "Q", 1, F)
    h1 = CP.PropsSI("H", "T", tb + 273.15, "Q", 1, F)
    s1 = CP.PropsSI("S", "T", tb + 273.15, "Q", 1, F)
    h2 = h1 - eta_exp * (h1 - CP.PropsSI("H", "P", pc, "S", s1, F))
    hv = CP.PropsSI("H", "P", pc, "Q", 1, F)
    h3 = CP.PropsSI("H", "P", pc, "Q", 0, F)
    s3 = CP.PropsSI("S", "P", pc, "Q", 0, F)
    h4 = h3 + (CP.PropsSI("H", "P", ph, "S", s3, F) - h3) / PUMP_ETA
    rec = recup * (h2 - hv)                 # ανάκτηση από τον υπέρθερμο ατμό της εξαγωγής
    q = h1 - h4 - rec
    w = (h1 - h2) - (h4 - h3)
    _cache[key] = (w / q, (h4 - h3) / (h1 - h2))
    return _cache[key]


def run(area=50, coll="επίπεδος", tilt=45, qmax=10.0, eta_exp=0.65, recup=0.0,
        dt_cond=10.0, fan_w=120, g_min=150):
    p = copy.deepcopy(P0)
    p["pv_tilt"] = tilt
    e0, a1, a2, tbmax = COLL[coll]
    tot = dict(sun=0.0, heat=0.0, elec=0.0, rej=0.0, hours=0, clip=0.0)
    mon = {m: 0.0 for m in range(1, 13)}
    tbw = {m: [0.0, 0.0] for m in range(1, 13)}
    for hr in HOURS:
        G = sim.poa(hr, p)
        if G < g_min:
            continue
        ta = hr["ta"]
        tc = int(round(min(60, max(0, ta + dt_cond))))
        best = (0.0, 0.0, 0.0, 0.0, 0)
        for tb in TB_RANGE:
            if tb > tbmax:
                break
            tm = tb + 5 - ta
            eta = e0 - a1 * tm / G - a2 * tm * tm / G
            if eta <= 0:
                continue
            q_raw = area * G * eta / 1000
            q = min(q_raw, qmax)
            ec, _ = cycle(tb, tc, eta_exp, recup)
            el = q * ec * GEN - fan_w / 1000
            if el > best[0]:
                best = (el, q, q_raw - q, ec, tb)
        el, q, clip, ec, tbb = best
        if el > 0:
            tot["elec"] += el; tot["heat"] += q; tot["rej"] += q * (1 - ec)
            tot["hours"] += 1; tot["clip"] += clip; mon[hr["m"]] += el; tbw[hr["m"]][0] += tbb * el; tbw[hr["m"]][1] += el
        tot["sun"] += area * G / 1000
    tot["tb_month"] = {m: (tbw[m][0] / tbw[m][1] if tbw[m][1] else 0) for m in tbw}
    return tot, mon


if __name__ == "__main__":
    def show(label, **kw):
        t, mon = run(**kw)
        print(f"{label:<44} ρεύμα {t['elec']:6.0f} kWh/έτος | θερμότητα {t['heat']:6.0f} | "
              f"ώρες {t['hours']:4d} | κόπηκε {t['clip']:5.0f} | Ιαν {mon[1]:4.0f} Ιουλ {mon[7]:4.0f}")
        return t

    print("ΒΑΣΗ: 50 m² επίπεδος, κλίση 45°, μηχανή 10 kW θερμ., εκτονωτής 65%, ψυγείο αέρας+10 K, βεντιλατέρ 120 W")
    show("Βάση", )
    print("\n1. Είδος συλλέκτη")
    show("  σωλήνες κενού", coll="κενού")
    print("\n2. Κλίση συλλέκτη")
    for tl in (30, 60):
        show(f"  κλίση {tl}°", tilt=tl)
    print("\n3. Μέγεθος μηχανής (μέγιστη θερμότητα)")
    for qm in (15, 20, 30):
        show(f"  μηχανή {qm} kW θερμ.", qmax=qm)
    print("\n4. Ψυγείο αυτοκινήτου (διαφορά από τον αέρα)")
    for dt in (6, 15):
        show(f"  αέρας + {dt} K", dt_cond=dt)
    show("  χωρίς βεντιλατέρ, αέρας + 20 K", dt_cond=20, fan_w=0)
    print("\n5. Ανάκτηση θερμότητας εξαγωγής (recuperator)")
    show("  ανάκτηση 70% της υπερθέρμανσης", recup=0.7)
    print("\n6. Εκτονωτής")
    for ee in (0.50, 0.75):
        show(f"  απόδοση εκτονωτή {int(ee*100)}%", eta_exp=ee)
    print("\n7. Επιφάνεια")
    for a in (25, 100):
        show(f"  {a} m² (μηχανή αναλογικά {a/5:.0f} kW)", area=a, qmax=a / 5)
    print("\nΣΥΝΔΥΑΣΜΟΣ: 50 m² σωλήνες κενού, κλίση 30°, μηχανή 25 kW, αέρας+10 K με βεντιλατέρ 60 W, ανάκτηση 70%")
    for ee in (0.65, 0.75):
        t = show(f"  βελτιστοποιημένη, εκτονωτής {int(ee*100)}%", coll="κενού", tilt=30, qmax=25,
                 dt_cond=10, fan_w=60, recup=0.7, eta_exp=ee)
    print("  βέλτιστος βρασμός ανά μήνα:", " ".join(f"{m}:{t['tb_month'][m]:.0f}°C" for m in range(1, 13)))
    print(f"  θερμότητα στο ψυγείο αυτοκινήτου: {t['rej']:.0f} kWh/έτος (30–45°C)")
