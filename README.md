# Akribeia

**Precision delivery discipline for AI-assisted coding.**

*Ακρίβεια* (akribeia) is the Greek word for precision, exactness — the quality you need when the changes are
surgical and the code is not allowed to break.

Τέσσερα skills για Claude Code: πώς **ξέρεις** τι ισχύει, πώς **αλλάζεις** κώδικα που δεν επιτρέπεται να χαλάσει,
πώς **αποδεικνύεις** ότι παρέδωσες — και οι παγίδες των ελληνικών, οριζόντια.

Four Claude Code skills: how you **know** what is true, how you **change** code that is not allowed to break, how
you **prove** you delivered — plus the Greek-text traps, horizontally.

[Ελληνικά](#ελληνικά) · [English](#english)

---

## Ελληνικά

### Τι είναι

Μια **οικογένεια τεσσάρων skills** που φορτώνονται από το Claude Code και αλλάζουν τον τρόπο που δουλεύει σε
υπάρχοντα κώδικα: προσθετικές λύσεις αντί για μετατροπές, ξεχωριστό branch και πλήρες gate ανά δέσμη, διάγνωση πριν
από διόρθωση, έλεγχοι κατά διάσταση, ερωτηματολόγιο στον άνθρωπο όταν υπάρχουν πολλές υποστηρίξιμες επιλογές, και
αναφορές που δεν λένε ψέματα.

Δεν είναι θεωρία. **Κάθε κανόνας μέσα τους γεννήθηκε από περιστατικό που κόστισε** — κόκκινο gate, σφάλμα που
πέρασε στην παραγωγή, χαμένη μέρα, ένα κατάστημα εκτός λειτουργίας. Τα περιστατικά είναι γραμμένα δίπλα στους
κανόνες, γιατί κανόνας χωρίς περιστατικό γίνεται δεισιδαιμονία και κανείς δεν μπορεί να κρίνει αργότερα αν ισχύει
ακόμη.

### Η οικογένεια

| Skill | Η ουσία σε μία γραμμή |
|---|---|
| **akribeia** | Ο πειθαρχημένος βρόχος **αλλαγής** κώδικα που δεν επιτρέπεται να χαλάσει: προσθετικές λύσεις, branch + πλήρες gate ανά δέσμη, συντονιστής και εργάτες χωρίς αυτο-έλεγχο, διάγνωση πριν από διόρθωση, ειλικρινείς αναφορές. |
| **observe-before-concluding** | Πώς τεκμηριώνεις **τι ισχύει** πριν το γράψεις: εμβέλεια παρατήρησης, αρνητικά ευρήματα με δεύτερη ματιά άλλου σχήματος, χάρτης **ακμών** (ροές) και όχι μόνο κόμβων, διαβάθμιση βεβαιότητας. |
| **verified-delivery** | Παράδοση **με απόδειξη**: κόκκινο-πριν, ωμές γραμμές εξόδου αντί για πίνακες από μνήμης, λίστες ΠΑΓΩΜΕΝΩΝ σε κάθε ανάθεση, τι επιβιώνει της ακύρωσης, το εύρημα του χρήστη ως **κατηγορία**. |
| **greek-text-pitfalls** | Οι παγίδες των **ελληνικών** σε κώδικα: κεφαλαία με τόνους και διαλυτικά, τελικό σίγμα (U+03C2/U+03C3), το `\w` που δεν πιάνει ελληνικά, αναζήτηση χωρίς τόνους, προσβάσιμα ονόματα, εγκλείσεις όρων, ζώνη ώρας. |

### Πώς συνδέονται

**`observe-before-concluding` (πώς ΞΕΡΕΙΣ) → `akribeia` (πώς ΑΛΛΑΖΕΙΣ) → `verified-delivery` (πώς ΑΠΟΔΕΙΚΝΥΕΙΣ)** —
και το **`greek-text-pitfalls` οριζόντια**, όπου υπάρχει ελληνικό κείμενο.

Η σειρά δεν είναι διακοσμητική: **δεν διορθώνεις σωστά ό,τι διέγνωσες λάθος**. Όταν ισχύουν και τα δύο πρώτα, το
`observe-before-concluding` προηγείται. Και τα τέσσερα δουλεύουν και **μόνα τους**· δεν εξαρτώνται μεταξύ τους.

### Η δομή

```
skills/
├── akribeia/                       # EL — ο βρόχος αλλαγής (§0–§10)
│   ├── SKILL.md                    #   οι κανόνες, πυκνά· κάθε περιστατικό σε μία γραμμή
│   └── references/
│       ├── incidents.md            #   τα πλήρη περιστατικά (Π1–Π17)
│       └── appendix.md             #   μοντέλο & effort · τι ΔΕΝ υιοθετήθηκε και γιατί
├── observe-before-concluding/      # EL — πώς ξέρεις τι ισχύει (περιστατικά μέσα στο SKILL.md)
├── verified-delivery/              # EL — παράδοση με απόδειξη
├── greek-text-pitfalls/            # EL — ελληνικά σε κώδικα
└── *-en/                           # τα ίδια, στα αγγλικά
```

Το `SKILL.md` είναι αυτό που διαβάζεται κάθε φορά — γι' αυτό κρατιέται σύντομο. Τα `references/` φορτώνονται
μόνο όταν χρειαστούν. **Τίποτα δεν λείπει· απλώς δεν είναι όλα στην ίδια σελίδα.**

### Σε ποιον απευθύνεται

- Σε ομάδες και μόνους developers που δουλεύουν με Claude Code πάνω σε **υπάρχον** σύστημα με πραγματικούς
  χρήστες και πραγματικά δεδομένα.
- Σε όποιον τρέχει **πολλαπλούς agents** (συντονιστή + εργάτες) και έχει ήδη πληρώσει το τίμημα των
  συγκρούσεων, των ψευδώς πράσινων τεστ και των αναφορών «όλα καλά».
- Σε μη-developers που κατευθύνουν τεχνική δουλειά: οι §8β και §8γ υπάρχουν ακριβώς γι' αυτό — κάθε αναφορά
  δηλώνει από την πρώτη γραμμή αν χρειάζεται απόφασή σου, και καμία διφορούμενη επιλογή δεν γίνεται σιωπηλά
  στη θέση σου.

Δεν απευθύνεται σε greenfield prototypes που θα πεταχτούν. Εκεί οι μισοί κανόνες είναι τροχοπέδη.

### Τι ΔΕΝ είναι

- **Δεν είναι εργαλείο.** Δεν εγκαθίσταται, δεν τρέχει, δεν έχει CLI.
- **Δεν είναι εξάρτηση.** Καμία βιβλιοθήκη, κανένα πακέτο, κανένα MCP server. Σκέτο markdown.
- **Δεν είναι framework.** Δεν σου επιβάλλει δομή repo, εργαλεία τεστ ή CI.
- **Δεν είναι πλήρες.** Είναι ό,τι έχει αποδειχθεί μέχρι σήμερα σε πραγματική δουλειά. Ο ίδιος ο §10 του
  `akribeia` λέει πώς κλαδεύεται όταν κάτι διαψευστεί.

### Η ιστορία

Γεννήθηκε χτίζοντας με το Claude Code μια production εφαρμογή σε πεδίο όπου μια λάθος ημερομηνία ή μια λάθος
τιμή έχει σοβαρές συνέπειες για πραγματικούς ανθρώπους — εκεί ένα σιωπηλό σφάλμα δεν είναι ενόχληση, είναι
ζημιά. Δεν γράφτηκε ως «best practices»: **γράφτηκε ανάποδα**, κάθε φορά που κάτι κόστισε και ένας γραπτός
κανόνας θα το είχε αποτρέψει. Και **κλαδεύεται** με τον ίδιο τρόπο — ό,τι διαψεύστηκε από τη μετέπειτα
εμπειρία σβήνεται (§10), γιατί ένας ξεπερασμένος κανόνας είναι χειρότερος από ανύπαρκτο.

Τα τρία νεότερα μέλη βγήκαν από την ίδια πορεία: το `verified-delivery` όταν φάνηκε ότι μια αναφορά μπορεί να
είναι **σωστή και ταυτόχρονα ανεπαλήθευτη**, το `greek-text-pitfalls` από ελαττώματα που περνούσαν σιωπηλά μέσα
από πράσινα τεστ, και το `observe-before-concluding` όταν ένα φιλτραρισμένο ερώτημα έγινε **αρνητικό πόρισμα σε
μόνιμο αρχείο** — και ήταν λάθος.

### Τα κεφάλαια του `akribeia`

| § | Ο κανόνας σε μία γραμμή |
|---|---|
| **0** | Η υπάρχουσα λειτουργικότητα δεν πειράζεται — προσθετική λύση ή σταμάτα και ρώτα. |
| **1** | SSOT ≠ DRY: το πρώτο αφορά πού ζουν τα δεδομένα, το δεύτερο πού ζει η συμπεριφορά. |
| **2** | Δέσμη = branch· πλήρες gate πριν από κάθε merge· διάβασε το πραγματικό summary, όχι το exit code. |
| **2β** | Αλλαγή credential: πρώτα το σύστημα και απόδειξη με πραγματική κλήση, μετά το config. |
| **3** | Συντονιστής που αναθέτει και δεν αυτο-ελέγχεται· παράλληλα ό,τι διαβάζει, στη σειρά ό,τι γράφει. |
| **4** | Υλοποίηση και απλοποίηση ποτέ στο ίδιο diff. |
| **5** | Διάγνωση πριν από διόρθωση· το τεστ πρέπει να το δεις κόκκινο πριν το πιστέψεις. |
| **6** | Πρώτα πλάτος (νέα διάσταση), μετά βάθος — και μέτρα το **παραδοτέο**, όχι μόνο τον κώδικα. |
| **6β** | Τα σχόλια του κώδικα είναι ισχυρισμοί, όχι τεκμήρια — ό,τι περιγράφει κατάσταση επαληθεύεται. |
| **7** | Τα προβλήματα τα βρίσκει η πραγματική χρήση, η νέα οπτική γωνία και η πραγματική εκτέλεση. |
| **8** | Ειλικρίνεια αναφοράς· κάθε αναφορά δηλώνει αν χρειάζεται απόφαση· και όπου οι επιλογές είναι πολλές και υποστηρίξιμες, αποφασίζει ο άνθρωπος με ερωτηματολόγιο. |
| **9** | Αντοχή σε διακοπή: ΕΝΑ αρχείο μνήμης που επικαιροποιείται, ουρά γραμμένη από τις πηγές, αρχείο που απαντά ο άνθρωπος = παγωμένο. |
| **10** | Το ίδιο το πρωτόκολλο ενημερώνεται και **κλαδεύεται** από τη χρήση του, με πήχη δύο όρων. |

Στην κορυφή του `SKILL.md` υπάρχει λίστα ελέγχου· στο `references/appendix.md` το **τι δεν υιοθετήθηκε και
γιατί** (π.χ. το δημοφιλές «σβήσε τα παλιά μονοπάτια αντί για migrations» — επικίνδυνο όταν στη βάση υπάρχουν
δεδομένα ανθρώπων).

### Εγκατάσταση

Κάθε skill είναι ένας φάκελος. Τον αντιγράφεις — τίποτε άλλο.

**Ολόκληρη η οικογένεια, για όλα σου τα projects** (user scope — συνιστάται):

```bash
git clone https://github.com/marinoas/akribeia.git /tmp/akribeia
mkdir -p ~/.claude/skills
cp -R /tmp/akribeia/skills/akribeia \
      /tmp/akribeia/skills/observe-before-concluding \
      /tmp/akribeia/skills/verified-delivery \
      /tmp/akribeia/skills/greek-text-pitfalls \
      ~/.claude/skills/
```

**Μόνο για ένα repo** (repo scope — μπαίνει στο git του project και το μοιράζεται η ομάδα):

```bash
mkdir -p .claude/skills
cp -R /tmp/akribeia/skills/akribeia .claude/skills/
```

**Αγγλική έκδοση**: αντιγράψτε τους φακέλους με την κατάληξη `-en` (`akribeia-en`,
`observe-before-concluding-en`, `verified-delivery-en`, `greek-text-pitfalls-en`). Εγκαταστήστε **μία γλώσσα ανά
skill** — αν μπουν και οι δύο, ενεργοποιούνται και οι δύο και διπλασιάζεις άσκοπα το context.

**Μπορείς να πάρεις και ένα μόνο**: τα skills δεν εξαρτώνται μεταξύ τους. Αν κρατήσεις ένα, κράτα το `akribeia`.

Έλεγχος ότι φορτώθηκαν: `/skills` μέσα στο Claude Code, ή απλά ζήτησέ του «διόρθωσε αυτό το bug χωρίς να
χαλάσει τίποτα» και δες αν τα επικαλείται.

### Πώς φαίνεται στην πράξη

Τα skills ενεργοποιούνται μόνα τους όταν η δουλειά αφορά αλλαγή σε υπάρχοντα κώδικα ή διερεύνηση. Δεν χρειάζεται
να τα αναφέρεις.

**Χωρίς αυτά**, ένα τυπικό «διόρθωσε το bug στη λίστα» παράγει: μια αλλαγή, ένα «έτοιμο, θα έπρεπε να δουλεύει
τώρα», συχνά και έναν καλλωπισμό δίπλα.

**Με αυτά**, η ίδια εντολή παράγει:

1. **Διάγνωση πρώτα** — τι ακριβώς φταίει, και αν το κόκκινο προϋπήρχε (`git stash` και τρέξιμο στο καθαρό
   HEAD) πριν χρεωθεί στην τρέχουσα δουλειά.
2. **grep πριν γραφτεί οποιοσδήποτε helper** — υπάρχει ήδη κάτι που κάνει το ίδιο; (Ο κανόνας αυτός γεννήθηκε
   από τέσσερις παράλληλες υλοποιήσεις της ίδιας συνάρτησης, από τις οποίες μόνο μία ήταν σωστή.)
3. **Τεστ που το είδες κόκκινο** πριν από τη διόρθωση — αλλιώς δεν ξέρεις αν ελέγχει το σφάλμα.
4. **Δικό του branch**, καθαρά commits, πλήρες gate, και το **πραγματικό** summary στην αναφορά («347 passed,
   1 failed» — όχι «πέρασαν τα τεστ»).
5. **Αναφορά που ξεκινά λέγοντας αν χρειάζεται απόφασή σου** — και αν οι εύλογες επιλογές είναι περισσότερες
   από μία, ερωτηματολόγιο με τις συνέπειες της καθεμίας και αιτιολογημένη σύσταση.

Και στα ερωτήματα του τύπου «υπάρχει το Χ; πώς δουλεύει αυτό;»: **καμία αρνητική απάντηση χωρίς δεύτερη
παρατήρηση άλλου σχήματος**, και καμία «σιγουριά» που δεν αντιστοιχεί στην απόδειξη που την στηρίζει.

Το ορατό κόστος: πιο αργή απάντηση. Το αόρατο όφελος: δεν ξοδεύεις τη μεθεπόμενη μέρα ψάχνοντας τι χάλασε.

### CodeGraph

Αν το repo σου έχει δείκτη [CodeGraph](https://github.com/colbymchenry/codegraph), το `akribeia` γίνεται πιο
αποδοτικό σε τρία σημεία — χαρτογράφηση blast radius πριν από παράλληλες αναθέσεις, μονοπάτια που το grep δεν
ακολουθεί, και οικονομία context στον προσανατολισμό.

Δεν είναι εξάρτηση, και οι υπερβολές δεν βοηθούν κανέναν: τι κάνει και τι **δεν** κάνει, με το ίδιο μέτρο
ειλικρίνειας που απαιτεί η §8, στο [docs/codegraph-integration.md](docs/codegraph-integration.md).

### Εκδόσεις

- **v3** — από ένα skill σε **οικογένεια τεσσάρων**: νέα μέλη `observe-before-concluding`, `verified-delivery`,
  `greek-text-pitfalls` (EL + EN). Το `akribeia` συγχρονίστηκε: νέοι κανόνες §2β (σειρά αλλαγής credential) και
  §6β (τα σχόλια είναι ισχυρισμοί), ντετερμινιστικός εντοπισμός σε e2e λίστες (§5), «μέτρα το παραδοτέο» (§6),
  η αντίφαση ανθρώπου-κώδικα ως εύρημα (§7), αρχείο-ΠΑΓΩΜΕΝΟ (§9), ρητή σήμανση ΑΞΙΩΜΑΤΟΣ (§0/§10), λίστα
  ελέγχου στην κορυφή, περιστατικά Π13–Π17.
- **v2** — δίγλωσσο (EL + EN), περιστατικά δίπλα στους κανόνες, `references/` για τα πλήρη.
- **v1** — η πρώτη δημόσια παγίωση του πρωτοκόλλου.

### Συνεισφορά

Ο πήχης του §10 ισχύει και για τα PRs: ένας νέος κανόνας μπαίνει μόνο αν (α) **κόστισε πραγματικά** κάπου, και
(β) ένας γραπτός κανόνας θα το είχε αποτρέψει. Στείλε το **περιστατικό** μαζί με τον κανόνα — χωρίς αυτό δεν
μπορεί να αξιολογηθεί. Διορθώσεις που **αφαιρούν** κανόνα τον οποίο διέψευσε η εμπειρία σου είναι εξίσου
ευπρόσδεκτες με τις προσθήκες.

### Άδεια

MIT — δες [LICENSE](LICENSE). Αντίγραψέ το, κόψ' το, προσάρμοσέ το στο δικό σου project.

---

*Γράφτηκε σε συνεργασία ανθρώπου και Claude, πάνω σε πραγματικά περιστατικά από πραγματική δουλειά. Οι αριθμοί
μέσα στα skills (588 λανθασμένοι υπολογισμοί, 9 στα 10 σημεία αναζήτησης, 354/355 στο gate, 13,3 MB ανά επίσκεψη)
είναι μετρημένοι, όχι σχήματα λόγου.*

---
---

## English

### What it is

A **family of four Claude Code skills** that change how it works on existing code: additive solutions instead of
conversions, a branch and a full gate per bundle, diagnosis before fixing, audits by dimension, a questionnaire for
the human whenever several options are defensible, and reports that do not lie.

It is not theory. **Every rule in them was born from an incident that cost something** — a red gate, a bug that
reached production, a lost day, a shop taken offline. The incidents are written next to the rules, because a rule
without its incident becomes superstition and nobody can later judge whether it still holds.

### The family

| Skill | The point, in one line |
|---|---|
| **akribeia** | The disciplined loop for **changing** code that is not allowed to break: additive solutions, branch + full gate per bundle, orchestrator and workers with no self-review, diagnosis before fixing, honest reports. |
| **observe-before-concluding** | How you establish **what is true** before you write it down: observation scope, negative findings backed by a second look of a different shape, a map of **edges** (flows) and not just nodes, calibrated certainty. |
| **verified-delivery** | Delivery **with proof**: red-before-green, raw output lines instead of tables written from memory, a FROZEN list in every assignment, what survives a cancellation, the user's finding as a **category**. |
| **greek-text-pitfalls** | The traps of **Greek text** in code: uppercase with accents and diaereses, final sigma (U+03C2/U+03C3), `\w` that does not match Greek, accent-insensitive search, accessible names, term containment, time zone. |

### How they connect

**`observe-before-concluding` (how you KNOW) → `akribeia` (how you CHANGE) → `verified-delivery` (how you PROVE)** —
with **`greek-text-pitfalls` horizontally**, wherever there is Greek text.

The order is not decorative: **you do not correctly fix what you incorrectly diagnosed.** When the first two both
apply, `observe-before-concluding` comes first. All four also work **on their own**; they do not depend on each
other.

### The structure

```
skills/
├── akribeia/                       # EL — the change loop (§0–§10)
│   ├── SKILL.md                    #   the rules, dense; each incident in one line
│   └── references/
│       ├── incidents.md            #   the full incidents (I1–I17)
│       └── appendix.md             #   model & effort · what was NOT adopted, and why
├── observe-before-concluding/      # EL — how you know what is true (incidents inside SKILL.md)
├── verified-delivery/              # EL — delivery with proof
├── greek-text-pitfalls/            # EL — Greek text in code
└── *-en/                           # the same, in English
```

`SKILL.md` is what gets read every time — which is why it is kept short. The `references/` are loaded only when
needed. **Nothing is missing; it is simply not all on one page.**

### Who it is for

- Teams and solo developers working with Claude Code on an **existing** system with real users and real data.
- Anyone running **multiple agents** (orchestrator + workers) who has already paid the price of collisions,
  falsely green tests, and "all good" reports.
- Non-developers directing technical work: §8b and §8c exist exactly for that — every report states in its
  first line whether a decision from you is needed, and no ambiguous choice is made silently on your behalf.

It is not for greenfield prototypes that will be thrown away. There, half of these rules are friction.

### What it is NOT

- **Not a tool.** Nothing to install, nothing to run, no CLI.
- **Not a dependency.** No library, no package, no MCP server. Plain markdown.
- **Not a framework.** It imposes no repo layout, test runner or CI.
- **Not complete.** It is what has been proven so far in real work. `akribeia`'s own §10 describes how it gets
  pruned when something is disproved.

### The story

It came out of building, with Claude Code, a production application in a field where a wrong date or a wrong
figure has serious consequences for real people — where a silent error is not an annoyance but damage. It was
not written as "best practices": it was **written backwards**, each time something cost us and a written rule
would have prevented it. And it is **pruned** the same way — whatever later experience disproves gets deleted
(§10), because a stale rule is worse than no rule at all.

The three newer members came out of the same road: `verified-delivery` when it turned out that a report can be
**correct and unverified at the same time**, `greek-text-pitfalls` from defects that slipped silently through green
tests, and `observe-before-concluding` when one filtered query became a **negative conclusion in a permanent
record** — and was wrong.

### The chapters of `akribeia`

| § | The rule in one line |
|---|---|
| **0** | Working functionality is not touched — find an additive solution, or stop and ask. |
| **1** | SSOT ≠ DRY: the first is about where data lives, the second about where behaviour lives. |
| **2** | Bundle = branch; full gate before every merge; read the real summary, not the exit code. |
| **2b** | Changing a credential: the system first, proven by a real call, then the config. |
| **3** | An orchestrator that delegates and never self-reviews; parallel for reads, serial for writes. |
| **4** | Implementation and simplification never in the same diff. |
| **5** | Diagnose before fixing; you must see the test red before you believe it. |
| **6** | Breadth first (a new dimension), then depth — and measure the **deliverable**, not only the code. |
| **6b** | Code comments are claims, not evidence — anything describing state must be verified. |
| **7** | Problems are found by real use, a new angle of audit, and real execution. |
| **8** | Honest reporting; every report states whether a decision is needed; and where several options are defensible, the human decides via a questionnaire. |
| **9** | Surviving interruption: ONE memory file that is updated, a queue written from the sources, a file the human is answering is frozen. |
| **10** | The protocol itself is updated and **pruned** by its own use, against a two-part bar. |

`SKILL.md` opens with a checklist; `references/appendix.md` holds **what was not adopted and why** (e.g. the
popular "delete old paths instead of adding migrations" — dangerous once there is human data in the database).

### Installation

Each skill is a folder. You copy it — that is all.

**The whole family, for all your projects** (user scope — recommended):

```bash
git clone https://github.com/marinoas/akribeia.git /tmp/akribeia
mkdir -p ~/.claude/skills
cp -R /tmp/akribeia/skills/akribeia-en \
      /tmp/akribeia/skills/observe-before-concluding-en \
      /tmp/akribeia/skills/verified-delivery-en \
      /tmp/akribeia/skills/greek-text-pitfalls-en \
      ~/.claude/skills/
```

**For one repo only** (repo scope — committed to the project, shared with the team):

```bash
mkdir -p .claude/skills
cp -R /tmp/akribeia/skills/akribeia-en .claude/skills/
```

**Greek version**: copy the folders without the `-en` suffix. Install **one language per skill** — if both are
present, both trigger and you double the context for nothing.

**You can also take just one**: the skills do not depend on each other. If you keep one, keep `akribeia`.

To confirm they loaded: run `/skills` inside Claude Code, or simply ask it to "fix this bug without breaking
anything" and watch whether it invokes them.

### What it looks like in practice

The skills trigger on their own whenever the work involves changing existing code, or an investigation. You do not
need to mention them.

**Without them**, a typical "fix the bug in the list view" produces: one change, a "done, this should work now",
and often an unrelated bit of cleanup alongside.

**With them**, the same instruction produces:

1. **Diagnosis first** — what exactly is wrong, and whether the red pre-existed (`git stash` and run against
   clean HEAD) before it is charged to the current work.
2. **A grep before any helper is written** — does something already do this? (That rule was born from four
   parallel implementations of the same function, only one of which was correct.)
3. **A test you have seen red** before the fix — otherwise you do not know it tests the bug.
4. **Its own branch**, clean commits, the full gate, and the **real** summary in the report ("347 passed, 1
   failed" — not "tests pass").
5. **A report that opens by saying whether it needs a decision from you** — and if more than one option is
   defensible, a questionnaire with each option's consequences and a reasoned recommendation.

And for questions of the "does X exist / how does this work" kind: **no negative answer without a second
observation of a different shape**, and no confidence in the wording that the evidence does not support.

The visible cost: a slower answer. The invisible benefit: you do not spend the day after tomorrow hunting for
what broke.

### CodeGraph

If your repo has a [CodeGraph](https://github.com/colbymchenry/codegraph) index, `akribeia` gets more efficient
in three places — mapping the blast radius before parallel assignments, following paths grep cannot, and saving
context during orientation.

It is not a dependency, and inflated claims help nobody: what it does and what it does **not**, held to the same
honesty §8 demands, is in [docs/codegraph-integration.md](docs/codegraph-integration.md).

### Versions

- **v3** — from one skill to a **family of four**: new members `observe-before-concluding`, `verified-delivery`,
  `greek-text-pitfalls` (EL + EN). `akribeia` was synced: new rules §2b (the order of a credential change) and
  §6b (comments are claims), deterministic targeting in e2e lists (§5), "measure the deliverable" (§6), the
  human-vs-code contradiction as a finding (§7), the FROZEN answer file (§9), explicit AXIOM marking (§0/§10),
  the checklist moved to the top, incidents I13–I17.
- **v2** — bilingual (EL + EN), incidents next to the rules, `references/` for the full write-ups.
- **v1** — the first public hardening of the protocol.

### Contributing

The §10 bar applies to pull requests too: a new rule goes in only if (a) it **actually cost** something
somewhere, and (b) a written rule would have prevented it. Send the **incident** together with the rule —
without it, the rule cannot be evaluated. Changes that **remove** a rule your experience has disproved are as
welcome as additions.

### License

MIT — see [LICENSE](LICENSE). Copy it, cut it down, adapt it to your own project.

---

*Written by a human and Claude together, on top of real incidents from real work. The numbers inside the skills
(588 wrong calculations, 9 out of 10 search entry points, 354/355 at the gate, 13.3 MB per visit) are measured, not
figures of speech.*
