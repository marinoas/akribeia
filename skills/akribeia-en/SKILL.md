---
name: akribeia-en
description: Use when changing an existing codebase that must not regress — the disciplined delivery loop. Covers additive-first, SSOT vs DRY, branch-per-bundle with a full gate, orchestrator+workers with no author self-review, separate simplify pass, diagnose-before-fix, audit-by-dimension, and a questionnaire whenever more than one option is defensible. Apply to feature work, bug fixes, refactors, and audits on any project.
---

# Akribeia — precision in delivery

Hardened on a production application where mistakes carry a real cost for real users: a silent bug is not an
annoyance, it is damage. The goal is **surgical, high-precision changes to code that is not allowed to break**.
It applies to any project and any language.

Every rule was born from an **incident that cost something** — **a rule without its incident becomes
superstition**. Here each incident is **one line** with its numbers; the full write-ups (I1–I17) are in
[references/incidents.md](references/incidents.md). The extended reasoning on model/effort and the list of what
was **not** adopted and why: [references/appendix.md](references/appendix.md).

> **Sibling skill:** `observe-before-concluding` — it governs how you **KNOW** what is true (observation scope,
> negative findings, the map of edges, calibrated certainty). When both apply, **that one comes first**: you do
> not correctly fix what you incorrectly diagnosed. Do not copy its rules in here.

## Checklist

- [ ] No existing functionality is affected; the solution is additive.
- [ ] Grepped for an existing helper before writing a new one.
- [ ] Its own branch; separate commits per logical step.
- [ ] Whatever the tests run against (build artifact) was rebuilt before running them.
- [ ] Full gate green, with the **real** summaries read.
- [ ] No cleanup change tangled with a functional change.
- [ ] Every red was diagnosed (regression vs stale test vs pre-existing) before being fixed.
- [ ] No test leaves residue for the next run.
- [ ] The report states, in its first line, whether a human decision is needed.
- [ ] Wherever **several defensible** options existed, a questionnaire with a recommendation was given, and the
      human's choice was recorded.
- [ ] State written to disk; tree clean, branch deleted.
- [ ] **§10**: did a lesson emerge that meets the bar? If so, it was written **with its incident**, checked for
      correlation-vs-cause, and anything redundant was pruned.

## 0. The rule that is never broken

**Working functionality is not touched.** If there is *any suspicion* that a change affects it: stop (not "let's
see if it passes"), look for an **additive** solution (a new layer alongside, not a conversion), and if there is
none, report it in plain words — what is at risk, what the options are; the human decides. Always prefer **new
files / new columns / new layers** over converting what exists.

*This rule is an **AXIOM**, not an induction from an incident — it is explicitly exempt from §10's incident
requirement: in a system holding real people's data you do not wait for it to cost something before you believe it.*

## 1. SSOT ≠ DRY — two different rules

**SSOT** = where the **data** lives (one authoritative source). **DRY** = where the **behaviour** lives (one
implementation per idea). The second is forgotten more easily: duplicated behaviour is **invisible when you read
file by file** — each copy, on its own, is correct code; it only shows up when you compare across the whole repo.

- **Checkable procedure**: before writing *any* helper, `grep` for something that already does the same or nearly
  the same thing. If you find one, **unify**; if it cannot be unified, write down **why**.
- **And outside the repo**: does a dependency **you already have** do this? Do not assume a library lacks a
  feature without reading its docs and types. *Boundary*: this does not mean "add new packages" — a new dependency
  is extra risk surface and is the human's decision.
- **The goal is NOT zero duplication.** Things that change for different reasons stay separate; forced unification
  creates coupling, which is worse than repetition. Where duplication is unavoidable (e.g. two bundles that cannot
  share code), **write a test that locks their equivalence**, and keep an explicit "FROZEN — do not unify" list
  with reasons.

> **I1** — four separate implementations of text normalization, only one of them complete → **9 out of 10** search entry points failed; **eight** deep audits had walked past it.

## 2. Bundles, branches, the gate

- Every bundle on **its own branch**; every logical step in **its own commit** (so it can be reverted on its own).
  After the merge: **clean** tree, branch deleted, pushed.
- **Full gate before every merge**: typecheck → unit → e2e. Never merge without green.
- **Read the actual summary** (X passed / Y failed), never just the exit code — pipes mask it, and the report says
  "passed" while the run blew up.
- **Step 0 wherever a build artifact exists**: if the tests run against compiled output (`dist/`, a bundle, an
  image), **rebuild before you run** — otherwise they come back **falsely green** and an entire day's work can
  "pass" without a single line of it having executed.

## 2b. Changing a credential: the SYSTEM first, the config second

Change the secret **at its source** (the database user, the provider's dashboard, the secret store), **prove with
a real call that the new one works**, and only then write it into the configuration files — with a backup
**outside** the web root. Never both steps in one script without checking that the first succeeded. When a secret
has two sides, accept a few seconds of mismatch but keep that window inside **one** command. This is neither a code
change (§0) nor a red test (§5) — which is exactly why no other rule catches it.

> **I13** — a script wrote the new password into the config file **before** confirming the change on the database user; the change had failed **silently** (missing privilege) and the shop was down for **~90 seconds**, restored from backup.

## 3. Orchestrator and workers

- The orchestrator **does not write** the bulk of the code; it delegates with an **explicit, narrow brief** and
  keeps its own context for judgement, the gate, and the merge. **NEVER "do a self-review"**: the author judges by
  the same criteria that led to the mistake — review needs an independent pair of eyes.
- A brief contains: the **goal** (in the human's own words, verbatim), the **already diagnosed cause**, **what you
  already know** (files, lines, flows) so it does not burn context, the **non-negotiables**, explicitly what it
  must **not** touch, the **checks** it runs itself, and the **deliverable**: what was done, what was **not** done
  and why, what is left open.
- **Parallel for everything that reads, serial for everything that writes.** When two must write, split them **by
  file area**; where you genuinely need parallel writing, the way out is **a separate working tree per writer**
  (e.g. `git worktree`) — not two hands in the same tree.
- **The worker runs ITS OWN new tests — never the full suite.** Without that it delivers **unverified guesses**.
  The constraint you need is not "nobody else runs tests", it is "nobody runs **the same** tests at the same time"
  (shared port, shared test database). Require **0 failed / 0 flaky across TWO consecutive runs**.
- **Model and effort: recommend, don't make the human guess.** The orchestrator **explicitly** recommends model and
  effort per role, at the start and whenever the kind of work changes; the human decides. Allocation principle:
  **the expensive model goes on the LOW-VOLUME side**. Measurements, the exception and the two invisible traps:
  [references/appendix.md](references/appendix.md).

> **I2** — two consecutive bundles went red at the gate only in the worker's new specs; the moment it was allowed to run them, the very first run revealed a **real application bug**.

## 4. Implementation ≠ simplification

Never in the same diff — mixed together, when the gate goes red you cannot tell whether the feature or the cleanup
broke it. **Prevention** inside every brief: "search before you write" (§1). **Cleanup** as a separate pass, with
fresh eyes, **delegated to a different worker**, over the *accumulated* surface after merging — never per task (a
small diff does not reveal patterns). High-volume, zero-functional-benefit changes (e.g. "unify 21 labels") **do
not get their own branch**: they happen whenever the file is open anyway.

## 5. Diagnose before you fix

- Is it a **regression** or a **stale test expectation**? If the behaviour changed legitimately, update the test —
  and make it **stricter**, don't loosen it to get green. **Cross-test contamination**? Run the suspect spec alone.
- Is it even **yours**? `git stash` and run the same spec against clean HEAD; if it fails there too, it is a
  pre-existing defect — its own bundle, not tangled into yours.
- **"Flaky test" = suspect the APPLICATION first.** Never a retry or a sleep to "stabilise" it; measure the race
  window and write a deterministic test that fires at exactly that moment.
- **e2e over lists: deterministic targeting, never "whatever shows up".** An assertion against a general list
  (`.first()`, "contains X") passes on an empty database and blows up in the full suite, where the row falls
  **outside the pagination window**. Filter server-side by the **test's own unique key**.
- **Test hygiene**: a test that passes once and kills the suite on the next run is **worse than no test**; if a
  spec leaves residue, rewrite it so it proves the same thing **without leaving traces**. Leave a "DO NOT REPEAT"
  comment with the explanation, not just the fix.
- **The test must BITE.** Write it first and see it **red** before you fix. If that is impossible (a new feature)
  and it passes first try, **break the implementation on purpose**, watch it fall, then restore. A test you have
  never seen red is not proof; it is decoration.

> **I3** — a gate at **354/355**; the single red looked like a regression from the day's bundles, but it was flaky **on clean HEAD too**: a pre-existing UI race.
> **I4** — the keyboard listener was attached **3–7 ms after** the modal title appeared; inside that window Escape was silently dropped (**8 out of 8**) — a defect, not flakiness.
> **I14** — a spec green on its own **×2**, red **×2** inside the full suite of **494**: the page shows a 200-row window over the whole database and the new row fell outside it. Cost: one full gate cycle.

## 6. Audits: breadth first, then depth

- **Breadth determines what you can find at all**: if the question is never asked, no amount of depth surfaces it.
  Repeated *generic* sweeps have **diminishing returns**; a new **dimension** has fresh ones.
- **Depth determines whether the finding is real and fully resolved** — whether it is the wrong variant, whether it
  has already corrupted data, whether it is provable by a test.
- **The cost is unequal**: breadth is cheap (one read-only explorer per dimension, all **in parallel**), depth is
  expensive. So **wide and shallow first, deep only on what survived the triage**.
- **Depth must REFUTE, not confirm**: deep analysis on a wrong premise produces *confident* wrong answers — what
  survives an attempt to falsify it is real.
- **MEASURE THE DELIVERABLE, not just the code**: page weight, response time, what the live installation actually
  serves. One `curl` sees what no amount of code reading can.
- Dimensions that pay off: duplicated behaviour · dates and timezones · money · text transformations · permissions
  and multi-tenancy · audit logging · messages and labels · navigation · types · test helpers · **what the user
  actually receives**. Always separate **CRITICAL** (security hole, data loss) from **cleanliness**, and rank:
  first what produces wrong output **today**, then what will silently drift **tomorrow**, last the bulk.

> **I5** — **eight** deep generic sweeps walked past the duplication of §1; the **one** new dimension found it, and only depth showed the wrong variant had been picked and that **75** rows were untouched.
> **I15** — **11** parallel audit dimensions and **12** red-team agents never measured the page itself; one `curl` found **13.3 MB** per visit to an online shop, for months — an 80% cut with zero new infrastructure.

## 6b. Code comments are CLAIMS, not evidence

A comment stating an **environmental fact** ("we're on the free tier", "the images are already compressed") was
true when it was written and nobody ever rechecked it — **verify it before you rely on it** (one `curl`, one `ls`).
What describes *intent* is useful; what describes *state* is suspect. **The tell**: a comment that justifies an
*omission* ("we don't optimise because X") — X is precisely the thing you must verify.

> **I16** — the human had explicitly said "we are on a **paid** plan"; the config file said "we're on the **free** tier". Both were in front of the audit and were never connected. The same comment hid a second error ("already compressed"), which was the cause of I15's 13.3 MB.

## 7. What actually finds the problems

In order of yield: **the human who uses the application** · a **new angle** of audit · **real execution** and
reading the real output. "Think harder" helps where the difficulty is in the thinking — it does **not** make you
notice something you never looked at.

**And one source that is systematically forgotten: what the human has ALREADY told or written to you** — one idea,
two triggers: *when reading their answers*, read their **comments**, not only the yes/no; *when reading code*, if
something they said **contradicts** the code, the contradiction is a **FINDING** — do not silently pick which of
the two holds.

> **I6** — the most valuable finding of an entire audit cycle came from real use: the human opened a form, pressed Escape, opened it again; **six** sweeps had not had that axis.
> **I7** — **588** wrong date calculations in production: the domain expert had noted in a parenthesis next to a "YES" that a particular day is a public holiday, and nobody read anything but the yes/no.

**A second rule from I7: test scenarios that share a hidden constant hide the defects OF that constant.** Every
sheet used scenarios from the same year — the one year in which the missing holiday fell on a weekend, so it
changed no result at all. **Every rule is checked with two scenarios that differ along the dimension that could be
hiding the bug** (here: the year).

## 8. Honest reporting

Never "perfect", never "should pass" — only documented coverage with numbers. If something was not done, say so. If
something is truncated (top-N, a sample), declare it: a silent truncation reads as full coverage. A counter that hit
a cap is reported as "20+", never as "20".

**8b. Every report states whether a decision is needed.** The human on the other side is often **not a developer**;
a technical report does not, by itself, tell them whether you are **informing** or **asking**. So every report opens
by saying which: **"No decision needed from you"** → then the update; or **"I need a decision on X"** → the question
**first**, clearly, before the documentation. And do not ask for a decision you will make better yourself later with
more information — that transfers burden, not control.

**8c. Between several reasonable options, the HUMAN decides — via a questionnaire.** When there is **one right**
option and the others are wrong, do the right one and don't ask. But when there are **more than one defensible**
options, the machine **does not choose silently**: it composes a **questionnaire** of the available options, explains
in **plain words** what each one does and implies, **recommends one with reasons** — and the final choice always
belongs to the human. The choice is **recorded**; a preference that proves stable becomes a **setting with a
default**, so it is never asked again. This does not contradict §8b's "a recommendation, not a menu": there the
question is *what should I do next* (you know that better); here it is *which reading applies* — and that belongs to
the human, with your recommendation beside it.

> **I8** — a red-gate report with a complete diagnosis, without stating that no decision was pending; the human asked "so what am I supposed to say now?".
> **I9** — for two cases with multiple defensible readings of a calculation rule, the system computed ALL versions with each one's source and recommended the conservative one; the silent automatic choice had already cost — an interpretation the human had never approved was being applied invisibly.

## 9. Surviving interruption — and memory that does not lie

Context is the resource that runs out first. Write the state **to disk** as you go (what was done, what comes next
in order, the human's decisions, the "never again" lessons); no work is left half-finished on a branch without a
written diagnosis.

**ONE memory file per project — one that is UPDATED, not accumulated.** Not one per session, per topic or per
finding. Every decision lives in one place and is **edited in place**; anything proven wrong is **deleted**, not
annotated as "old" (§1's DRY). **As many layers, as many chances to diverge**: when you change content, change **in
the same motion** every summary, title and index that points at it.

**The work queue is written from the SOURCES, not from the session.** Every explicit request is recorded **the
moment it is heard**, before implementation starts; every completed item is **moved** with its proof (a commit or
file:line). **Loose ends born inside code comments are promoted to the queue** — a "⚠️ TODO" living only in a source
file will never be seen by whoever decides what happens next. And **never an unrecorded stopgap**: "never use a
stopgap" is wrong as an absolute rule (we build in layers) — the dangerous one is the stopgap nobody remembers
exists, so every temporary solution goes into the queue **with its exit condition**.

**A file the human is answering is FROZEN.** From the moment they get the go-ahead to write inside a file,
**NOBODY** touches it until they say "done" — and the go-ahead is given **ONLY** when every task on that file is
finished. Answers in progress live only in their editor; they cannot be recovered from anywhere.

> **I10** — scattered across dozens of files, the memory held two opposite decisions at once, **three "unresolved contradictions"** were presented that the human had already resolved, and one file's **summary** said the opposite of its body.
> **I11** — a queue with **15** requests never entered, **6** half-entered, **8 of the 21** "pending" already done, and **16** loose ends hidden in code comments: worse than no queue at all.
> **I17** — the go-ahead was given for the "final" sections of a sheet while a worker was still rewriting two of them; the human's handwritten answers were lost **twice**, unrecoverably.

## 10. Self-improvement of this protocol

This file **is updated by its own use**: at the end of every piece of work, ask *did something come up that, had it
been written here, would have prevented it?* **The bar — both conditions together**: (1) **it actually cost
something** (time lost, a bug shipped, the gate went red, a revert was needed) and (2) **a written rule would have
prevented it**. Anything not meeting both **does not go in**: a protocol that bloats stops being read carefully —
and **if it grows past what you would read before starting, it has already failed**.

**Entry format**: the rule **together with its incident** (one line here, the full write-up in `references/`).
**Prune, don't only add**: two rules saying the same thing → **unify them**; a rule that later experience disproved
→ **delete it** (a stale rule is **worse than no rule**: it costs attention and leads to a wrong decision,
confidently). **The superstition guard**: never record **correlation as cause** — ask first, *is there another
explanation for what I saw?* **A rule with no genuine incident is declared an AXIOM — you do not manufacture an
incident for it**: if the rule was always followed, there is no incident, and a stretched or retrofitted "fitting"
one contaminates precisely the file that decides whether the remaining rules still hold; an axiom is stated with its
source (who set it, when, why) — see §0. **When to ask the human**: if a new rule contradicts an existing one or
changes how you work together, propose it — do not write it on your own; anything else (a technical lesson, a tool
trap, test hygiene) is written autonomously, with a note.

> **I12** — it was nearly recorded that "with lower effort, more bugs get found": the correlation was real, the cause was elsewhere (real use, a new audit dimension, real execution).
