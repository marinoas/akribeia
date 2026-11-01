#!/usr/bin/env python3
"""Ενοποιημένο σχέδιο:
  επίπεδος ηλιακός συλλέκτης (προθέρμανση υγρού R1233, μέσω κυκλώματος νερού και πλακοειδούς)
  -> σωλήνες κενού (βρασμός R1233)
  -> στρόβιλος δύο βαθμίδων: 2 turbo μεταβλητής γεωμετρίας σε σειρά, το καθένα με γεννήτρια υψηλών στροφών
  -> ανάκτηση θερμότητας εξαγωγής -> ψυγεία κλιματισμού αυτοκινήτου σε σειρά (χωρίς βεντιλατέρ)
  -> δοχείο -> ηλεκτρική αντλία τροφοδοσίας -> πίσω στον επίπεδο.
Ωριαία προσομοίωση ενός έτους (συνθετικός καιρός Κορίνθου, sim.py)."""
import copy
import CoolProp.CoolProp as CP
import sim

F = "R1233zd(E)"
P0 = copy.deepcopy(sim.P)
HOURS = sim.synthetic_weather(P0)
FLAT = (0.78, 3.8, 0.015)
EVAC = (0.45, 0.85, 0.004)
GEN = 0.90
PUMP_ETA = 0.40           # ηλεκτρική αντλία (μοτέρ + αντλία)
_c = {}


def state(tb, tc, eta_t, recup, tp_max):
    key = (tb, tc, eta_t, recup, tp_max)
    if key in _c:
        return _c[key]
    ph = CP.PropsSI("P", "T", tb + 273.15, "Q", 1, F)
    pc = CP.PropsSI("P", "T", tc + 273.15, "Q", 1, F)
    h1 = CP.PropsSI("H", "T", tb + 273.15, "Q", 1, F)
    s1 = CP.PropsSI("S", "T", tb + 273.15, "Q", 1, F)
    h2 = h1 - eta_t * (h1 - CP.PropsSI("H", "P", pc, "S", s1, F))
    hv = CP.PropsSI("H", "P", pc, "Q", 1, F)
    h3 = CP.PropsSI("H", "P", pc, "Q", 0, F)
    s3 = CP.PropsSI("S", "P", pc, "Q", 0, F)
    h4 = h3 + (CP.PropsSI("H", "P", ph, "S", s3, F) - h3) / PUMP_ETA * 0.0 + \
        (CP.PropsSI("H", "P", ph, "S", s3, F) - h3)            # η ενθαλπία ανεβαίνει με το ισεντροπικό έργο
    w_pump_el = (CP.PropsSI("H", "P", ph, "S", s3, F) - h3) / PUMP_ETA
    h4r = h4 + recup * (h2 - hv)                                 # μετά την ανάκτηση
    t4r = CP.PropsSI("T", "P", ph, "H", h4r, F) - 273.15
    tp = min(tb - 5, tp_max)
    hp = CP.PropsSI("H", "P", ph, "T", tp + 273.15, F) if tp > t4r else h4r
    tp = max(tp, t4r)
    _c[key] = dict(h1=h1, hp=hp, h4r=h4r, t4r=t4r, tp=tp, w=h1 - h2, wp=w_pump_el)
    return _c[key]


def eta(c, tm, ta, G):
    e0, a1, a2 = c
    d = tm - ta
    return e0 - a1 * d / G - a2 * d * d / G


def run(a_flat=15, a_evac=35, tilt=30, eta_t=0.70, recup=0.7, dt_cond=20, tp_max=85,
        parasitic_w=150, qmax=25, g_min=150):
    p = copy.deepcopy(P0)
    p["pv_tilt"] = tilt
    tot = dict(sun=0.0, elec=0.0, heat=0.0, flat_used=0.0, flat_surplus=0.0, rej=0.0, hours=0)
    mon = {m: 0.0 for m in range(1, 13)}
    for hr in HOURS:
        G = sim.poa(hr, p)
        tot["sun"] += (a_flat + a_evac) * G / 1000
        if G < g_min:
            continue
        ta = hr["ta"]
        tc = int(round(min(60, max(0, ta + dt_cond))))
        best = None
        for tb in range(60, 141, 2):
            if tb <= tc + 10:
                continue
            s = state(tb, tc, eta_t, recup, tp_max)
            qe = a_evac * G * max(0.0, eta(EVAC, tb + 5, ta, G)) / 1000
            qf = a_flat * G * max(0.0, eta(FLAT, (s["t4r"] + s["tp"]) / 2, ta, G)) / 1000 if a_flat else 0.0
            dh_tot = s["h1"] - s["h4r"]
            dh_pre = s["hp"] - s["h4r"]
            if qe <= 0:
                continue
            if qf <= (qe + qf) * dh_pre / dh_tot:          # ο επίπεδος χρησιμοποιείται όλος
                m = (qe + qf) / dh_tot
                qf_used = qf
            else:                                          # περισσεύει επίπεδος (πάει π.χ. σε ζεστό νερό χρήσης)
                m = qe / (s["h1"] - s["hp"])
                qf_used = m * dh_pre
            q = qe + qf_used
            if q > qmax:
                m *= qmax / q; qf_used *= qmax / q; q = qmax
            el = m * (s["w"] * GEN - s["wp"]) - parasitic_w / 1000
            if best is None or el > best[0]:
                best = (el, q, qf_used, qf - qf_used, m * s["w"])
        if best and best[0] > 0:
            el, q, qfu, qfs, w = best
            tot["elec"] += el; tot["heat"] += q; tot["flat_used"] += qfu; tot["flat_surplus"] += qfs
            tot["rej"] += q - w; tot["hours"] += 1; mon[hr["m"]] += el
        elif a_flat:
            tot["flat_surplus"] += a_flat * G * max(0.0, eta(FLAT, 50, ta, G)) / 1000
    return tot, mon


if __name__ == "__main__":
    def show(lbl, **kw):
        t, m = run(**kw)
        print(f"{lbl:<40} ρεύμα {t['elec']:5.0f} kWh/έτος | Ιαν {m[1]:4.0f} Ιουλ {m[7]:4.0f} | "
              f"ώρες {t['hours']:4d} | επίπεδος σε χρήση {t['flat_used']:5.0f}, περίσσευμα {t['flat_surplus']:5.0f} | "
              f"ψυγεία {t['rej']:6.0f}")
        return t
    print("Επιφάνεια 50 m² συνολικά, κλίση 30°, στρόβιλος 2 βαθμίδων 70%, ανάκτηση 70%, ψυγεία κλιμ. χωρίς βεντιλατέρ (αέρας+20 K),")
    print("παρασιτικά (λάδι ρουλεμάν turbo, έλεγχος) 150 W όσο λειτουργεί, ηλεκτρική αντλία 40%\n")
    print("1. Μοιρασιά επίπεδου / σωλήνων κενού")
    for af in (0, 5, 10, 15, 20, 30):
        show(f"  επίπεδος {af} m² + κενού {50-af} m²", a_flat=af, a_evac=50 - af)
    print("\n2. Απόδοση στροβίλου (2 turbo μεταβλητής γεωμετρίας)")
    for et in (0.60, 0.65, 0.75):
        show(f"  στρόβιλος {int(et*100)}%", a_flat=10, a_evac=40, eta_t=et)
    print("\n3. Παρασιτικά turbo")
    for pw in (50, 300):
        show(f"  παρασιτικά {pw} W", a_flat=10, a_evac=40, parasitic_w=pw)
