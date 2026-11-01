#!/usr/bin/env python3
"""Ενοποιημένο σχέδιο με εκτονωτή scroll (συμπιεστής κλιματιστικού που δουλεύει ανάποδα).
5 m² επίπεδος (προθέρμανση) + 45 m² σωλήνες κενού (βρασμός) -> scroll 1500–3000 rpm με το ενσωματωμένο
μοτέρ ως γεννήτρια -> ανάκτηση εξαγωγής -> ψυγεία κλιματισμού σε σειρά -> αντλία.

Μοντέλο scroll (ημι-εμπειρικό, τύπου Lemort):
  ο ατμός μπαίνει από τη θυρίδα κατάθλιψης του συμπιεστή (όγκος θαλάμου = κυβισμός / λόγος όγκων),
  εκτονώνεται ισεντροπικά μέχρι τον ενσωματωμένο λόγο όγκων και μετά «αδειάζει» στην πίεση του ψυγείου.
  Αν η πίεση μέσα είναι ακόμα πάνω από του ψυγείου: απώλεια υπο-εκτόνωσης. Αν είναι κάτω: υπερ-εκτόνωση.
  Διαρροές, τριβή, μηχανικά: συντελεστής 0,75. Μοτέρ/γεννήτρια + μετατροπέας: 0,88."""
import copy
import CoolProp.CoolProp as CP
import sim

F = "R1233zd(E)"
P0 = copy.deepcopy(sim.P)
HOURS = sim.synthetic_weather(P0)
FLAT = (0.78, 3.8, 0.015)
EVAC = (0.45, 0.85, 0.004)
GEN = 0.88
INTERNAL = 0.75
VOL_EFF = 0.90
PUMP_ETA = 0.40
_c = {}


def scroll_state(tb, tc, vr, recup, tp_max):
    key = (tb, tc, vr, recup, tp_max)
    if key in _c:
        return _c[key]
    ph = CP.PropsSI("P", "T", tb + 273.15, "Q", 1, F)
    pc = CP.PropsSI("P", "T", tc + 273.15, "Q", 1, F)
    h1 = CP.PropsSI("H", "T", tb + 273.15, "Q", 1, F)
    s1 = CP.PropsSI("S", "T", tb + 273.15, "Q", 1, F)
    d1 = CP.PropsSI("D", "T", tb + 273.15, "Q", 1, F)
    d_int = d1 / vr
    p_int = CP.PropsSI("P", "D", d_int, "S", s1, F)
    h_int = CP.PropsSI("H", "D", d_int, "S", s1, F)
    w_ideal = (h1 - h_int) + (p_int - pc) / d_int          # >0 υπο-εκτόνωση, <0 μέρος όταν υπερ-εκτόνωση
    w_isen = h1 - CP.PropsSI("H", "P", pc, "S", s1, F)
    w = INTERNAL * w_ideal
    h2 = h1 - w
    hv = CP.PropsSI("H", "P", pc, "Q", 1, F)
    h3 = CP.PropsSI("H", "P", pc, "Q", 0, F)
    s3 = CP.PropsSI("S", "P", pc, "Q", 0, F)
    dh_p = CP.PropsSI("H", "P", ph, "S", s3, F) - h3
    h4 = h3 + dh_p
    h4r = h4 + recup * max(0.0, h2 - hv)
    t4r = CP.PropsSI("T", "P", ph, "H", h4r, F) - 273.15
    tp = max(min(tb - 5, tp_max), t4r)
    hp = CP.PropsSI("H", "P", ph, "T", tp + 273.15, F) if tp > t4r + 0.1 else h4r
    _c[key] = dict(h1=h1, hp=hp, h4r=h4r, t4r=t4r, tp=tp, w=w, wp=dh_p / PUMP_ETA, d1=d1,
                   eta_exp=w / w_isen, pr=ph / pc)
    return _c[key]


def eta(c, tm, ta, G):
    e0, a1, a2 = c
    d = tm - ta
    return e0 - a1 * d / G - a2 * d * d / G


def run(disp_cc=65, vr=3.0, stages=1, rpm_min=1500, rpm_max=3000, a_flat=5, a_evac=45, tilt=30,
        recup=0.7, dt_cond=20, tp_max=85, parasitic_w=20, g_min=150):
    p = copy.deepcopy(P0)
    p["pv_tilt"] = tilt
    vr_tot = vr ** stages
    v_in = disp_cc / 1e6 / vr                                 # m³ ανά στροφή, θάλαμος εισόδου
    tot = dict(elec=0.0, heat=0.0, hours=0, clip=0.0, eta_w=0.0, low=0)
    mon = {m: 0.0 for m in range(1, 13)}
    for hr in HOURS:
        G = sim.poa(hr, p)
        if G < g_min:
            continue
        ta = hr["ta"]
        tc = int(round(min(60, max(0, ta + dt_cond))))
        best = None
        for tb in range(60, 141, 2):
            if tb <= tc + 10:
                continue
            s = scroll_state(tb, tc, vr_tot, recup, tp_max)
            if s["w"] <= 0:
                continue
            qe = a_evac * G * max(0.0, eta(EVAC, tb + 5, ta, G)) / 1000
            if qe <= 0:
                continue
            qf = a_flat * G * max(0.0, eta(FLAT, (s["t4r"] + s["tp"]) / 2, ta, G)) / 1000 if a_flat else 0.0
            dh_tot = s["h1"] - s["h4r"]
            dh_pre = s["hp"] - s["h4r"]
            if qf <= (qe + qf) * dh_pre / dh_tot:
                m = (qe + qf) * 1000 / dh_tot                  # kg/s (q σε kW, h σε J/kg)
            else:
                m = qe * 1000 / (s["h1"] - s["hp"])
            m_max = s["d1"] * v_in * VOL_EFF * rpm_max / 60
            clip = max(0.0, m - m_max)
            m = min(m, m_max)
            rpm = m / (s["d1"] * v_in * VOL_EFF) * 60
            f_low = 1.0 if rpm >= rpm_min else max(0.0, 0.5 + 0.5 * rpm / rpm_min)   # περισσότερη διαρροή σε χαμηλές στροφές
            el = m * (s["w"] * f_low * GEN - s["wp"]) / 1000 - parasitic_w / 1000     # kW
            if best is None or el > best[0]:
                best = (el, m * dh_tot / 1000, clip * dh_tot / 1000, s["eta_exp"] * f_low, rpm < rpm_min)
        if best and best[0] > 0:
            el, q, clip, e_exp, low = best
            tot["elec"] += el; tot["heat"] += q; tot["hours"] += 1; tot["clip"] += clip
            tot["eta_w"] += e_exp * el; tot["low"] += int(low); mon[hr["m"]] += el
    tot["eta_mean"] = tot["eta_w"] / tot["elec"] if tot["elec"] else 0
    return tot, mon


if __name__ == "__main__":
    def show(lbl, **kw):
        t, m = run(**kw)
        print(f"{lbl:<46} ρεύμα {t['elec']:5.0f} kWh/έτος | Ιαν {m[1]:4.0f} Ιουλ {m[7]:4.0f} | "
              f"μέση απόδοση εκτονωτή {t['eta_mean']*100:4.1f}% | ώρες {t['hours']:4d} (κάτω από 1500 rpm: {t['low']:4d}) | "
              f"κόπηκε {t['clip']:5.0f} kWh θερμ.")
    print("5 m² επίπεδος + 45 m² σωλήνες κενού, κλίση 30°, ψυγεία κλιμ. χωρίς βεντιλατέρ (αέρας+20 K), ανάκτηση 70%\n")
    print("Λόγος πιέσεων και όγκων στη διάταξη:")
    for tb, tc in ((86, 30), (100, 40), (115, 50)):
        s = scroll_state(tb, tc, 1.0, 0.0, 85)
        d2 = CP.PropsSI("D", "P", CP.PropsSI("P", "T", tc + 273.15, "Q", 1, F), "S",
                        CP.PropsSI("S", "T", tb + 273.15, "Q", 1, F), F)
        print(f"  βρασμός {tb}°C / υγροποίηση {tc}°C: λόγος πιέσεων {s['pr']:.1f}, λόγος όγκων για πλήρη εκτόνωση {s['d1']/d2:.1f}")
    print("\n1. Ένα scroll, ενσωματωμένος λόγος όγκων (κυβισμός 65 cc/στροφή)")
    for vr in (2.5, 3.0, 3.5):
        show(f"  λόγος όγκων {vr}", vr=vr)
    print("\n2. Δύο scroll σε σειρά (λόγος όγκων 3,0 το καθένα -> 9 συνολικά)")
    show("  2 scroll σε σειρά", vr=3.0, stages=2)
    print("\n3. Μέγεθος (κυβισμός ως συμπιεστή), λόγος όγκων 3,0")
    for d in (30, 45, 100):
        show(f"  {d} cc/στροφή", disp_cc=d)
    print("\n4. Εύρος στροφών")
    show("  1500–3600 rpm", rpm_max=3600)
    show("  1000–3000 rpm (χωρίς ποινή ως 1000)", rpm_min=1000)
