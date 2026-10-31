"""Γραφήματα, πίνακες (Excel) και αναφορά (Markdown) από τα αποτελέσματα του sim.py."""
import copy
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook

import sim

# Παλέτα (επικυρωμένη για αχρωματοψία, 3 θέσεις, all-pairs) + ουδέτερο γκρι για τον λέβητα
BLUE, AQUA, ORANGE = "#2a78d6", "#1baf7a", "#eb6834"
GRAY = "#b5b3ad"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
RAMP = ["#86b6ef", "#2a78d6", "#104281"]          # διατακτική κλίμακα μπλε (όγκος αποθήκης)
MONTHS = ["Ιαν", "Φεβ", "Μαρ", "Απρ", "Μάι", "Ιούν", "Ιούλ", "Αύγ", "Σεπ", "Οκτ", "Νοέ", "Δεκ"]
SEASON = [10, 11, 12, 1, 2, 3, 4]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
    "legend.frameon": False,
})


def fmt(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ----------------------------------------------------------------- γραφήματα
def fig_monthly(res, out):
    ref, pv = res["ref"], res["ref_pv"]
    panels = [
        ("S1  Κάτοπτρο 40 m² + άμμος 3 m³", ref[False]["monthly"], "conc"),
        ("S2  ... + αντλία απορρόφησης", ref[True]["monthly"], "conc"),
        ("S4  Φ/Β 6 kWp + αντλία θερμότητας + δίκτυο", pv["monthly"], "pv"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, (title, mon, kind) in zip(axes, panels):
        xs = list(range(len(SEASON)))
        if kind == "conc":
            series = [("Ηλιακή θερμότητα μέσω αντλίας", BLUE, [mon[m][1] for m in SEASON]),
                      ("Ηλιακή θερμότητα απευθείας", AQUA, [mon[m][2] for m in SEASON]),
                      ("Λέβητας πετρελαίου", GRAY, [mon[m][3] for m in SEASON])]
        else:
            series = [("Ηλιακή θερμότητα μέσω αντλίας", BLUE, [mon[m][1] for m in SEASON]),
                      ("Ρεύμα δικτύου μέσω αντλίας", ORANGE, [mon[m][2] for m in SEASON]),
                      ("Λέβητας πετρελαίου", GRAY, [mon[m][3] for m in SEASON])]
        bottom = [0.0] * len(xs)
        for name, col, vals in series:
            ax.bar(xs, vals, bottom=bottom, width=0.62, color=col, edgecolor="#fcfcfb",
                   linewidth=1.5, label=name)
            bottom = [b + v for b, v in zip(bottom, vals)]
        ax.set_xticks(xs, [MONTHS[m - 1] for m in SEASON])
        ax.set_title(title, fontsize=10.5, color=INK, loc="left")
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("Θέρμανση (kWh/μήνα)")
    handles = {}
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            handles.setdefault(l, h)
    order = ["Ηλιακή θερμότητα μέσω αντλίας", "Ηλιακή θερμότητα απευθείας",
             "Ρεύμα δικτύου μέσω αντλίας", "Λέβητας πετρελαίου"]
    fig.legend([handles[k] for k in order], order, loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    path = os.path.join(out, "1_ana_mina.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig_store(res, out):
    fig, ax = plt.subplots(figsize=(12, 4))
    for cascade, col, name in ((False, BLUE, "S1 (χωρίς αντλία)"), (True, ORANGE, "S2 (με αντλία απορρόφησης)")):
        T = res["ref"][cascade]["T"]
        daily = [sum(T[d * 24:(d + 1) * 24]) / 24 for d in range(365)]
        ax.plot(range(365), daily, color=col, linewidth=2, label=name)
        ax.annotate(name, xy=(364, daily[-1]), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK2)
    for y, lab in ((200, "200°C: όριο λειτουργίας αντλίας απορρόφησης"),
                   (65, "65°C: όριο απευθείας θέρμανσης")):
        ax.axhline(y, color=INK2, linewidth=0.9, linestyle=(0, (4, 3)))
        ax.text(160, y + 8, lab, fontsize=8.5, color=INK2)
    starts = [0]
    for n in sim.DAYS_IN_MONTH[:-1]:
        starts.append(starts[-1] + n)
    ax.set_xticks([s + 14 for s in starts], MONTHS)
    ax.grid(axis="x", visible=False)
    ax.set_xlim(0, 365)
    ax.set_ylim(0, 580)
    ax.set_ylabel("Θερμοκρασία άμμου (°C, μέση ημέρας)")
    ax.set_title("Αποθήκη άμμου 3 m³ με κάτοπτρο 40 m²: θερμοκρασία μέσα στον χρόνο",
                 fontsize=11, color=INK, loc="left")
    ax.legend(loc="lower left", bbox_to_anchor=(0.36, 0.42), ncol=1)
    fig.tight_layout()
    path = os.path.join(out, "2_thermokrasia_ammou.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig_sweep(res, out):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for ax, sysname, title in ((axes[0], "S1", "S1  Κάτοπτρο + άμμος"),
                               (axes[1], "S2", "S2  Κάτοπτρο + άμμος + αντλία απορρόφησης")):
        for v, col in zip((1, 3, 8), RAMP):
            rows = sorted([r for r in res["rows"] if r["system"].startswith(sysname) and r["vol"] == v],
                          key=lambda r: r["area"])
            xs = [r["area"] for r in rows]
            ys = [100 * r["solar_frac"] for r in rows]
            ax.plot(xs, ys, color=col, linewidth=2, marker="o", markersize=5,
                    markeredgecolor="#fcfcfb", markeredgewidth=1.5, label=f"Άμμος {v} m³")
        ax.set_title(title, fontsize=10.5, color=INK, loc="left")
        ax.set_xlabel("Επιφάνεια κατόπτρου (m²)")
        ax.set_ylim(0, 100)
    axes[0].set_ylabel("Κάλυψη θέρμανσης από τον ήλιο (%)")
    axes[1].legend(loc="lower right")
    fig.tight_layout()
    path = os.path.join(out, "3_megethos.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def pick(res, system, size):
    return next(r for r in res["rows"] if r["system"].startswith(system) and r["size"] == size)


SELECTED = [("S4", "2 kWp"), ("S4", "6 kWp"), ("S3", "6 kWp"), ("S1", "20 m², 3 m³"),
            ("S1", "40 m², 3 m³"), ("S2", "40 m², 3 m³"), ("S2", "60 m², 3 m³")]


def fig_econ(res, out):
    rows = [pick(res, s, z) for s, z in SELECTED]
    rows.sort(key=lambda r: r["payback"])
    labels = [f"{r['system'].split()[0]}  {r['size']}" for r in rows]
    vals = [r["payback"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4))
    ys = list(range(len(rows)))[::-1]
    ax.barh(ys, vals, height=0.55, color=BLUE, edgecolor="#fcfcfb", linewidth=1.5)
    for y, v, r in zip(ys, vals, rows):
        ax.text(v + 0.3, y, f"{fmt(v, 1)} έτη   ({fmt(r['capex'])} € / {fmt(r['save'])} € τον χρόνο)",
                va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(ys, labels)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(vals) * 1.6)
    ax.set_xlabel("Απλή απόσβεση (έτη) = κόστος ÷ ετήσια εξοικονόμηση")
    ax.set_title("Απόσβεση επιλεγμένων διατάξεων (μέσες τιμές κόστους)", fontsize=11,
                 color=INK, loc="left")
    fig.tight_layout()
    path = os.path.join(out, "4_aposvesi.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# ----------------------------------------------------------------- ευαισθησία
def sensitivity(res, p):
    hours, loads = res["hours"], res["loads"]
    base_cost = res["base_cost"]
    cases = [
        ("Βασικό σενάριο", {}),
        ("Πιο απλό κάτοπτρο (οπτική 0,55, συγκέντρωση ×100)", dict(conc_eta0=0.55, conc_C=100.0)),
        ("Μόνωση πετροβάμβακα 30 cm αντί για κενό", dict(ins_lambda=0.07, ins_t=0.30)),
        ("Χωρίς διόρθωση άμεσης ακτινοβολίας (+11%)", dict(dni_scale=1.0)),
    ]
    out = []
    for name, ch in cases:
        q = copy.deepcopy(p)
        q.update(ch)
        hrs = hours
        if "dni_scale" in ch:
            hrs = sim.synthetic_weather(q)
        row = [name]
        for cascade in (False, True):
            r = sim.run_concentrator(hrs, loads, q, 40, 3, cascade)
            oil, cost = sim.econ(q, r["boiler"], r["parasitic"])
            row.append((1 - r["boiler"] / sum(loads), base_cost - cost))
        out.append(row)
    # τιμή πετρελαίου
    econ_cases = []
    for oil_price in (1.20, 1.55, 1.90):
        q = copy.deepcopy(p)
        q["oil_eur_l"] = oil_price
        bo, bc = sim.econ(q, sum(loads), 0)
        line = [oil_price]
        for s, z in (("S1", "40 m², 3 m³"), ("S2", "40 m², 3 m³"), ("S4", "6 kWp")):
            r = pick(res, s, z)
            cost = r["oil_l"] * oil_price + r["elec"] * q["elec_eur_kwh"]
            save = bc - cost + r.get("other_val", 0.0)
            line.append(r["capex"] / save if save > 0 else float("inf"))
        econ_cases.append(line)
    return out, econ_cases


# ----------------------------------------------------------------- Excel
def write_xlsx(res, p, out):
    wb = Workbook()
    ws = wb.active
    ws.title = "Αποτελέσματα"
    hdr = ["Σύστημα", "Μέγεθος", "Κάλυψη θέρμανσης από ήλιο (%)", "Κάλυψη χωρίς λέβητα (%)",
           "Πετρέλαιο που μένει (L/έτος)", "Εξοικονόμηση θέρμανσης (€/έτος)",
           "Αξία Φ/Β εκτός θέρμανσης (€/έτος)", "Συνολική εξοικονόμηση (€/έτος)",
           "Κόστος εγκατάστασης (€)", "Απόσβεση (έτη)"]
    ws.append(hdr)
    for r in res["rows"]:
        ws.append([r["system"], r["size"], round(100 * r["solar_frac"], 1),
                   round(100 * r.get("cover", r["solar_frac"]), 1), round(r["oil_l"]),
                   round(r["save_heat"]), round(r["other_val"]), round(r["save"]),
                   round(r["capex"]), round(r["payback"], 1)])
    for col, w in zip("ABCDEFGHIJ", (32, 14, 16, 16, 16, 18, 18, 18, 16, 12)):
        ws.column_dimensions[col].width = w
    ws2 = wb.create_sheet("Παράμετροι")
    ws2.append(["Παράμετρος", "Τιμή"])
    for k, v in p.items():
        ws2.append([k, str(v)])
    ws2.column_dimensions["A"].width = 22
    ws2.column_dimensions["B"].width = 80
    ws3 = wb.create_sheet("Καιρός ανά μήνα")
    ws3.append(["Μήνας", "Ολική οριζόντια (kWh/m²/ημέρα)", "Άμεση κάθετη (kWh/m²/ημέρα)",
                "Μέση θερμοκρασία (°C)", "Ανάγκη θέρμανσης (kWh)", "Φ/Β ανά kWp (kWh)"])
    for m, w in res["weather"].items():
        ws3.append([MONTHS[m - 1], round(w["ghi"], 2), round(w["dni"], 2), round(w["t"], 1),
                    round(w["load"]), round(w["pv1"])])
    path = os.path.join(out, "apotelesmata.xlsx")
    wb.save(path)
    return path


# ----------------------------------------------------------------- αναφορά
def write(res, out, p):
    figs = [fig_monthly(res, out), fig_store(res, out), fig_sweep(res, out), fig_econ(res, out)]
    xlsx = write_xlsx(res, p, out)
    sens, econ_sens = sensitivity(res, p)
    ref = res["ref"]

    L = []
    a = L.append
    a("# Ηλιακή θέρμανση με θερμική αποθήκη: αποτελέσματα προσομοίωσης")
    a("")
    a("Ωριαία προσομοίωση ενός έτους (8.760 ώρες) για σπίτι 100 m² στην Κόρινθο. "
      f"Καιρός: {res['source']}. Τρέχει με `python3 sim.py`.")
    a("")
    a("## Τι βγήκε, με μια ματιά")
    a("")
    s1 = pick(res, "S1", "40 m², 3 m³"); s2 = pick(res, "S2", "40 m², 3 m³")
    s4 = pick(res, "S4", "6 kWp"); s4s = pick(res, "S4", "2 kWp")
    s1in = ref[False]["solar_in"] - ref[False]["loss"]
    s2in = ref[True]["solar_in"] - ref[True]["loss"]
    mult = (s2["solar_frac"] * p["heat_annual_kwh"]) / s2in
    a(f"- **Σήμερα:** η θέρμανση (χωρίς το ζεστό νερό) κοστίζει ~{fmt(res['base_cost'])} €/έτος "
      f"(~{fmt(res['base_oil'])} L πετρέλαιο).")
    a(f"- **Κάτοπτρο 40 m² + άμμος 3 m³ (S1)** καλύπτει **{fmt(100*s1['solar_frac'])}%** της θέρμανσης. "
      f"Με την **αντλία απορρόφησης (S2)** φτάνει **{fmt(100*s2['solar_frac'])}%**.")
    a(f"- **Ο καταρράκτης δουλεύει, αλλά λιγότερο απ' όσο υπολόγισα στη συζήτηση.** Κάθε kWh που "
      f"βγαίνει από την άμμο γίνεται ~{fmt(mult, 2)} kWh θέρμανσης (όχι ~1,4 που είχα πει). "
      f"Όμως η αποθήκη μένει πιο ζεστή, οπότε το κάτοπτρο μαζεύει λιγότερο "
      f"({fmt(ref[True]['solar_in'])} αντί για {fmt(ref[False]['solar_in'])} kWh/έτος). "
      f"Το καθαρό κέρδος είναι +{fmt(100*(s2['solar_frac']-s1['solar_frac']))} μονάδες κάλυψης, "
      f"για ~12.000 € επιπλέον κόστος.")
    a(f"- **Φ/Β + ηλεκτρική αντλία θερμότητας + δίκτυο (S4)** καλύπτει ~{fmt(100*s4['cover'])}% χωρίς λέβητα "
      f"και αποσβένεται σε **~{fmt(s4['payback'], 1)} χρόνια**, έναντι **~{fmt(s1['payback'], 1)}** για το S1 "
      f"και **~{fmt(s2['payback'], 1)}** για το S2. Ακόμα και με μόλις 2 kWp: ~{fmt(s4s['payback'], 1)} χρόνια.")
    a("- **Συμπέρασμα:** ως οικονομική επένδυση κερδίζει καθαρά η ηλεκτρική αντλία θερμότητας. "
      "Το κάτοπτρο με την άμμο δουλεύει τεχνικά (74–82% κάλυψη) και έχει νόημα αν μετράει η "
      "ενεργειακή αυτονομία ή ως πειραματικό project. Η αντλία απορρόφησης δεν αξίζει το κόστος της "
      "με αυτή την αποθήκη.")
    a("")
    a("## 1. Από πού έρχεται η θέρμανση κάθε μήνα")
    a("")
    a("![Θέρμανση ανά μήνα](1_ana_mina.png)")
    a("")
    a("| Μήνας | Ανάγκη (kWh) | S1 ήλιος | S1 λέβητας | S2 ήλιος | S2 λέβητας | S4 Φ/Β | S4 δίκτυο | S4 λέβητας |")
    a("|---|---|---|---|---|---|---|---|---|")
    for m in SEASON:
        m1 = ref[False]["monthly"][m]; m2 = ref[True]["monthly"][m]; m4 = res["ref_pv"]["monthly"][m]
        a(f"| {MONTHS[m-1]} | {fmt(m1[0])} | {fmt(m1[1]+m1[2])} | {fmt(m1[3])} | {fmt(m2[1]+m2[2])} | "
          f"{fmt(m2[3])} | {fmt(m4[1])} | {fmt(m4[2])} | {fmt(m4[3])} |")
    a("")
    a("Ο Δεκέμβριος και ο Ιανουάριος είναι το «στενό»: λίγος ήλιος, μεγάλη ανάγκη. Τον Οκτώβριο, τον "
      "Μάρτιο και τον Απρίλιο ο ήλιος περισσεύει.")
    a("")
    a("## 2. Τι κάνει η αποθήκη μέσα στον χρόνο")
    a("")
    a("![Θερμοκρασία άμμου](2_thermokrasia_ammou.png)")
    a("")
    a(f"- Από τον Μάιο έως τον Σεπτέμβριο η άμμος μένει γεμάτη (550°C) και το κάτοπτρο απλώς "
      f"αναπληρώνει τις απώλειες. Ο χειμώνας ξεκινά με **γεμάτη μπαταρία**.")
    a(f"- Απώλειες αποθήκης με μόνωση κενού: ~{fmt(ref[False]['loss'])} kWh/έτος "
      f"(~{fmt(ref[False]['loss']/365, 1)} kWh/ημέρα).")
    a("- Τον Δεκέμβριο και τον Ιανουάριο η άμμος αδειάζει σε σειρές συννεφιασμένων ημερών και "
      "ξαναγεμίζει στις ηλιόλουστες. Εκεί δουλεύει ο λέβητας.")
    a("")
    a("## 3. Πόσο κάτοπτρο και πόση άμμος")
    a("")
    a("![Μέγεθος](3_megethos.png)")
    a("")
    a("| Κάτοπτρο | Άμμος 1 m³ | Άμμος 3 m³ | Άμμος 8 m³ | με απορρόφηση, 3 m³ |")
    a("|---|---|---|---|---|")
    for area in (10, 20, 30, 40, 60, 80, 100):
        vals = [pick(res, "S1", f"{area} m², {v} m³")["solar_frac"] for v in (1, 3, 8)]
        v2 = pick(res, "S2", f"{area} m², 3 m³")["solar_frac"]
        a(f"| {area} m² | {fmt(100*vals[0])}% | {fmt(100*vals[1])}% | {fmt(100*vals[2])}% | {fmt(100*v2)}% |")
    a("")
    a("- Μέχρι ~40 m² κάθε επιπλέον m² κατόπτρου προσθέτει πολλά. Μετά, η απόδοση φθίνει.")
    a("- Μεγαλύτερη αποθήκη από ~3 m³ προσθέτει λίγο: ο περιορισμός είναι **το κάτοπτρο τον χειμώνα**, όχι η αποθήκη.")
    a("- Ενδεικτικά, 40 m² είναι ένας δίσκος διαμέτρου ~7 m, ή π.χ. 4 δίσκοι των ~3,5 m.")
    a("")
    a("## 4. Οικονομικά")
    a("")
    a("![Απόσβεση](4_aposvesi.png)")
    a("")
    a("| Διάταξη | Κάλυψη χωρίς λέβητα | Πετρέλαιο που μένει | Εξοικονόμηση θέρμανσης | + Φ/Β εκτός θέρμανσης | Κόστος | Απόσβεση |")
    a("|---|---|---|---|---|---|---|")
    for s, z in SELECTED:
        r = pick(res, s, z)
        a(f"| {r['system']} {z} | {fmt(100*r.get('cover', r['solar_frac']))}% | {fmt(r['oil_l'])} L | "
          f"{fmt(r['save_heat'])} € | {fmt(r['other_val'])} € | {fmt(r['capex'])} € | {fmt(r['payback'], 1)} έτη |")
    a("")
    a("Το «Φ/Β εκτός θέρμανσης» είναι η αξία του ηλιακού ρεύματος που δεν πάει στη θέρμανση "
      "(καλοκαίρι, συσκευές), με 0,15 €/kWh. Το κάτοπτρο δεν έχει αντίστοιχο όφελος στο μοντέλο, αν και "
      "στην πράξη η αντλία απορρόφησης του S2 θα μπορούσε να κάνει και **ψύξη** το καλοκαίρι.")
    a("")
    a("## 5. Πόσο αξιόπιστα είναι τα νούμερα (ευαισθησία)")
    a("")
    a("Κάτοπτρο 40 m², άμμος 3 m³:")
    a("")
    a("| Σενάριο | S1 κάλυψη | S1 εξοικ./έτος | S2 κάλυψη | S2 εξοικ./έτος |")
    a("|---|---|---|---|---|")
    for name, (f1, e1), (f2, e2) in sens:
        a(f"| {name} | {fmt(100*f1)}% | {fmt(e1)} € | {fmt(100*f2)}% | {fmt(e2)} € |")
    a("")
    a("Απόσβεση (έτη) ανάλογα με την τιμή του πετρελαίου:")
    a("")
    a("| Πετρέλαιο | S1 40 m² | S2 40 m² | S4 6 kWp |")
    a("|---|---|---|---|")
    for price, b1, b2, b4 in econ_sens:
        a(f"| {fmt(price, 2)} €/L | {fmt(b1, 1)} | {fmt(b2, 1)} | {fmt(b4, 1)} |")
    a("")
    a("**Το πιο ευαίσθητο σημείο είναι το κάτοπτρο:** ένα απλούστερο, χειροποίητο κάτοπτρο "
      "με χαμηλότερη συγκέντρωση χάνει σημαντικό μέρος της απόδοσης στους 500°C. Η μόνωση "
      "κενού έναντι πετροβάμβακα επίσης μετράει.")
    a("")
    a("## 6. Παραδοχές και όρια του μοντέλου")
    a("")
    a("**Σπίτι:** 12.500 kWh θέρμανσης/έτος (2.000 L × 10 kWh × 0,75 απόδοση λέβητα, μείον ~2.500 kWh "
      "για ζεστό νερό, που πλέον το καλύπτει ο ηλιακός θερμοσίφωνας). Περίοδος Οκτώβριος–Απρίλιος. "
      f"Ζήτηση ανάλογη της διαφοράς από τους {fmt(p['t_balance'])}°C.")
    a("")
    a("**Καιρός:** συνθετικό τυπικό έτος, βαθμονομημένο σε τυπικές μηνιαίες τιμές ακτινοβολίας "
      "και θερμοκρασίας της περιοχής, με τυχαίες σειρές ηλιόλουστων και συννεφιασμένων ημερών. "
      "Η άμεση ακτινοβολία έχει μειωθεί 10% συντηρητικά (ετήσια ~1.810 kWh/m²). "
      "**Δεν είναι μετρήσεις για το σημείο σου.** Για ακριβέστερα αποτελέσματα κατέβασε από το "
      "[PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) → *TMY* → *csv* για τη θέση του σπιτιού και "
      "τρέξε `python3 sim.py --pvgis tmy.csv`.")
    a("")
    a(f"**Κάτοπτρο:** σημειακής εστίασης με παρακολούθηση 2 αξόνων, οπτική απόδοση {fmt(p['conc_eta0'], 2)}, "
      f"συγκέντρωση ×{fmt(p['conc_C'])}, δέκτης-κοιλότητα. Η απόδοση πέφτει όσο ανεβαίνει η θερμοκρασία "
      "(απώλειες ακτινοβολίας ∝ T⁴). Δεν λειτουργεί κάτω από 150 W/m² άμεσης ακτινοβολίας.")
    a("")
    a("**Αποθήκη:** κύλινδρος άμμου έξω από το σπίτι, μέγιστο 550°C, μόνωση κενού με περλίτη 20 cm "
      "(+25% για θερμογέφυρες). Οι απώλειες χάνονται (δεν ζεσταίνουν το σπίτι).")
    a("")
    a("**Αντλία απορρόφησης (S2):** τύπου αμμωνίας-νερού, απόδοση 1,25–1,70 ανάλογα με την εξωτερική "
      "θερμοκρασία, λειτουργεί όσο η άμμος είναι πάνω από 200°C, +4% ρεύμα για βοηθητικά.")
    a("")
    a("**Καλοριφέρ:** τα υπάρχοντα, σχεδιασμένα για 80/60°C. Στους 55°C (που δίνουν οι αντλίες "
      "θερμότητας) αποδίδουν ~50% της ισχύος τους. Ό,τι ξεπερνά αυτό το όριο το καλύπτει ο λέβητας, "
      "ή απευθείας η άμμος στο S1/S2, που μπορεί να δώσει νερό υψηλής θερμοκρασίας.")
    a("")
    a("**Φ/Β + αντλία θερμότητας (S3/S4):** νότια κλίση 30°, συντελεστής απόδοσης 0,82. Ηλεκτρική "
      "αντλία αέρα-νερού 10 kW, απόδοση 1,8–4,0 ανάλογα με την εξωτερική θερμοκρασία. Η παλιά δεξαμενή "
      "1 m³ ως buffer στους 40–60°C.")
    a("")
    a("**Τιμές:** πετρέλαιο 1,55 €/L, ρεύμα 0,22 €/kWh. **Κόστη εγκατάστασης (μέσες εκτιμήσεις, "
      "μεγάλη αβεβαιότητα):** κάτοπτρο 350 €/m², αποθήκη 3.000 € + 1.200 €/m³, κύκλωμα αέρα και αυτοματισμοί "
      "3.000 €, αντλία απορρόφησης με προσαρμογή 12.000 €. Φ/Β 1.100 €/kWp + 1.000 €, ηλεκτρική αντλία "
      "θερμότητας 7.000 €, μετατροπή δεξαμενής 1.500 €. Χωρίς επιδοτήσεις.")
    a("")
    a("**Τι ΔΕΝ μοντελοποιείται:** σκιάσεις, χιόνι ή σκόνη στο κάτοπτρο, βλάβες και συντήρηση, χρόνος "
      "προθέρμανσης του κατόπτρου, έξυπνος έλεγχος με πρόγνωση καιρού, ψύξη το καλοκαίρι, άδειες. "
      "Τα αποτελέσματα είναι **για σύγκριση διατάξεων**, όχι εγγυημένες αποδόσεις.")
    a("")
    a("## Αρχεία")
    a("")
    a("- `sim.py`: το μοντέλο. Όλες οι παράμετροι είναι στην αρχή του αρχείου (λεξικό `P`).")
    a("- `report.py`: παράγει αυτή την αναφορά, τα γραφήματα και το Excel.")
    a("- `apotelesmata.xlsx`: όλα τα σενάρια (" + str(len(res["rows"])) + " διατάξεις), οι παράμετροι και ο καιρός ανά μήνα.")
    a("- `1_ana_mina.png`, `2_thermokrasia_ammou.png`, `3_megethos.png`, `4_aposvesi.png`: τα γραφήματα.")
    path = os.path.join(out, "ANAFORA.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("Γράφτηκαν:", path, xlsx, *figs, sep="\n  ")
