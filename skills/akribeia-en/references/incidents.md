# Full incidents (I1–I12)

The incidents behind the rules in `SKILL.md`. There they are given in one line; here in full, with the
context that lets someone **judge whether the rule still holds**. A rule without its incident becomes
superstition.

---

## I1 — Four implementations of the same idea (§1, SSOT ≠ DRY)

The application's search had **four** separate implementations of text normalization — only one of them
complete. The result: **9 out of 10** search entry points failed to find a user's surname if you typed it
without the accent.

**Why it was not found earlier**: eight deep audits had walked past it, because no sweep had ever asked
"how many implementations of the same idea exist?". Each copy, read on its own, was correct code —
duplicated behaviour only shows up when you compare across the whole repo.

**The lesson**: `grep` for an existing helper **before** a new one is written; and one sweep dedicated
explicitly to the "duplicated behaviour" dimension.

---

## I2 — The worker that was not allowed to run its own tests (§3)

Two consecutive bundles went red at the final gate **only** in the worker's new specs. The constraint in
force at the time was "the worker does not run tests" — adopted so two processes would not collide on the
same port and the same test database.

The moment it was allowed to run **its own** specs, the **very first** run revealed a **real application
bug** that both the typecheck and the unit tests had walked past: a field never appeared in the edit form,
because an empty string is not nullish.

**The lesson**: the correct constraint is not "nobody else runs tests" but "nobody runs **the same** tests
at the same time". Without execution, the worker delivers unverified guesses about how the screen behaves.
And since flakiness is not disproved by one run: **0 failed / 0 flaky across two consecutive runs**.

---

## I3 — Gate 354/355: the red that was not ours (§5)

The gate reported **354 passed / 1 failed**. The single red looked like a regression from the day's
bundles, and the obvious move was to "fix" it there.

The experiment — `git stash`, then run the **same spec** against clean HEAD — showed it flaky **there
too**: a real, pre-existing UI race, a click lost silently inside a millisecond window.

**The lesson**: before you charge a red to your changes, prove it is yours. The pre-existing defect is
fixed as **its own bundle**, not tangled into the day's work.

---

## I4 — The "flaky" test that was a product defect (§5)

A test kept "losing" Escape on a modal — the classic flaky signature. It was not: the keyboard listener
was attached **3–7 ms after** the modal title appeared. Inside that window the form looked open to the
user, while Escape was **silently dropped** — **8 out of 8** times.

In other words, it was a real product defect, in the user's own words: "I pressed Escape and nothing
happened." Under load the window grew.

**The lesson**: "flaky test" → suspect the **application** first. Never a retry or a sleep to "stabilise"
it. Measure the race window, then write a deterministic test that fires at exactly that moment.

---

## I5 — Eight deep sweeps vs one new dimension (§6)

**Eight** deep but *generic* sweeps walked past the duplicated behaviour of I1. It was not a lack of
depth: none of them had asked "how many implementations of the same idea exist?". The **one** new
dimension found it immediately.

And then **only depth** answered what mattered: that the **wrong variant** had been picked, that **75**
rows in the database were **untouched** (so no data repair was needed), and that the timezone bug
reproduces under UTC — proven with a test at the New Year boundary.

**The lesson**: breadth and depth do not compete; they are sequential and unequally priced. Breadth
determines what you can find **at all**; depth determines whether the finding is **real and fully
resolved**.

---

## I6 — The finding that came from real use (§7)

The most valuable finding of an entire audit cycle did not come from a code sweep. It came because the
human opened a form, pressed Escape and opened it again — and saw that it did not close (the same defect
as I4). **Six** previous sweeps had not had that axis at all.

**The lesson**: in order of yield, problems are found by the **human who uses the application**, then by a
**new angle** of audit, then by **real execution**. "Think harder" does not make you notice something you
never looked at.

---

## I7 — 588 wrong date calculations (§7)

In an **answered** verification sheet, the domain expert had written — as an aside next to a "YES" — that
a particular day is a public holiday. The information sat in the repo **for days**: nobody read anything
but the yes/no.

The holiday was missing from the table in the code. Cost: **588 wrong dates** in production. The gap
finally surfaced not from a code sweep, but from **cross-checking the code against the expert's own
words**.

**A second lesson from the same incident**: every verification sheet used scenarios from the **same
year** — and it was the one year in which the missing holiday fell on a weekend, so it changed no result
at all. **Test scenarios that share a hidden constant hide the defects OF that constant.** Every rule is
checked with **two scenarios that differ along the dimension that could be hiding the bug** — here, the
year.

---

## I8 — The report that did not say whether a decision was needed (§8b)

A red-gate report, with a complete and correct technical diagnosis — but nowhere stating that **no**
decision from the human was pending. The human (not a developer) asked: "so what am I supposed to say
now?".

Cost here: one round trip. **The real danger is the reverse** — a request for a decision buried inside a
technical report, which goes unnoticed and stalls the work for hours or days.

**The lesson**: every report opens by saying "no decision needed from you" or "I need a decision on X" —
and in the second case the question comes **first**, before the documentation.

---

## I9 — The silently chosen interpretation (§8c)

A calculation rule admitted, in **two** specific cases, **more than one defensible reading**: there was no
single right answer with the rest wrong — there were versions that all stood up, each with a different
source and a different result.

Until then the system **picked one silently**. That is: an interpretation the human had never approved was
being applied invisibly — and they had no way of even learning that a choice existed. This had already
cost.

The solution that worked: the system **computes ALL versions**, **displays them with each one's source**,
**recommends the conservative one with reasons**, and **records** the human's choice. Where the preference
proved stable, it became a **setting with a default** so it is never asked again.

**The lesson**: when there is one right option, do it and don't ask. When there are several defensible
ones, **the machine does not choose silently**: it composes a questionnaire in plain words, recommends
one, and the final choice belongs to the human.

---

## I10 — The memory that said two opposite things (§9)

The project's memory was scattered across **dozens** of files — one per session, per topic, per finding.
The result: it simultaneously held **two opposite decisions** on the same topic, and **three "unresolved
contradictions"** were presented to the human — **all three of which they had already resolved**.

Worse: one file had the **correct** decision in its body, but its **summary** — the one loaded into every
session — still said the opposite.

**The lesson**: **ONE** memory file per project, **updated** rather than accumulated; every decision in one
place, edited in place; anything disproved is **deleted**. And: **as many layers, as many chances to
diverge** — when you change content, change in the same motion every summary, title and index that points
at it.

---

## I11 — The queue that was worse than no queue (§9)

One sweep of the work queue, cross-checked against the **sources** (what the human had actually asked
for), found: **15** explicit requests that had **never** been entered, **6** half-entered, and **8 of the
21** "pending" items that **had already been done**. In parallel, **16** loose ends lived only as "⚠️
TODO" comments inside source files, where whoever decides what happens next never sees them.

A queue that says "done" for something that does not exist, or "pending" for something finished, leads to
the **wrong assignment** — which makes it **worse than no queue at all**, exactly like the stale rule in
§10.

**The lesson**: the queue is written from the **sources**, not from the session. Every request is recorded
**the moment it is heard**; every completed item is **moved** with its proof; every loose end inside a code
comment is **promoted** to the queue.

---

## I12 — A near-superstition: "lower effort, more bugs found" (§10)

It was observed that during a period of **lower** effort, **more** bugs were found. The correlation was
real and measurable, and it was nearly recorded as a rule.

The cause was elsewhere: the findings of that period came from **real use** of the application, from a
**new audit dimension**, and from **real execution** — not from less thinking.

**The lesson**: never record **correlation as cause**. Before writing a rule, ask *is there another
explanation for what I saw?* Had this rule been written, it would have degraded the work **permanently**.
