#!/usr/bin/env python3
"""Σύγκριση Inventor MX290-12S με LG HM121HF (R290, 12 kW), με τα product fiche τους (EN14825)."""
import io, contextlib, os
with contextlib.redirect_stdout(io.StringIO()):
    import mx290_sim as m
from report import fmt

UNITS = [
    # όνομα, βαθμός Carnot (βαθμονόμηση στο fiche), ισχύς(t), SCOP 55 μέτριο / θερμό κλίμα, ηχητική ισχύς
    ("Inventor MX290-12S", 0.43, lambda t: 12.0 if t >= 7 else 12.0 - 0.106 * (7 - t), "3,62 / 4,45", "65 dB(A)"),
    ("Inventor MX290-10S", 0.44, lambda t: min(9.5, 7.4 + 0.095 * (t + 10)), "3,81 / 4,79", "61 dB(A)"),
    ("LG HM121HF", 0.46, lambda t: 9.3 + 0.05 * (t + 7) if t < 7 else 10.0, "3,97 / 4,85", "49 dB(A)"),
]
out = ["# Inventor MX290-12S, MX290-10S ή LG HM121HF", "",
       "Όλες: αέρα-νερού monoblock, R290 (10-12 kW), μονοφασικές, νερό έως 75°C. Μοντέλο βαθμονομημένο στο product fiche (EN14825) της καθεμίας. Ίδιο σπίτι, καιρός και καλοριφέρ με τα υπόλοιπα σενάρια. Τρέχει με `python3 lg_vs_mx290.py`.", "",
       "Τιμές: MX290-12S 4.800 €, MX290-10S 3.800 €, LG HM121HF + κιτ PHCS0 5.989 €.", "",
       "| Αντλία | SCOP 55°C (μέτριο / θερμό κλίμα) | Ηχητική ισχύς εξωτερικής | Κάλυψη | Πετρέλαιο | Ρεύμα αντλίας/έτος | Μέσο COP στο σπίτι | Εξοικονόμηση/έτος (χωρίς Φ/Β) |",
       "|---|---|---|---|---|---|---|---|"]
for name, eta, cap, scop, snd in UNITS:
    m.ETA_C = eta; m.capacity = cap
    r = m.run(0, 0, True)
    sv = r["heat"] * m.OIL - r["e_grid"] * m.EL
    out.append(f"| {name} | {scop} | {snd} | {fmt(100*r['heat']/m.Ltot)}% | {fmt(r['boiler']/7.5)} L | {fmt(r['e_hp'])} kWh | {fmt(r['scop'],2)} | {fmt(sv)} € |")
out += ["", "LG: βαθμονόμηση στα A-7/W52 2,54 · A2/W42 3,92 · A7/W36 5,22 · A-10/W55 2,36 · A2/W55 2,75 (θερμό κλίμα). Ισχύς (σελίδα προϊόντος, πλήρες φορτίο, νερό 55°C): 9,3 kW στους -7°C, 10 kW στους 7°C. Πλήρες φορτίο A7/W55: COP 3,10 και στις δύο αντλίες. A-7/W55: LG 2,32."]
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "LG_vs_MX290.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
