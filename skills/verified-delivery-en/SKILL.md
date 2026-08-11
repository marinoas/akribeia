---
name: verified-delivery-en
description: Use when implementing or delegating any code change that must not break existing behaviour — enforces red-before-green proof, real gate summaries, adversarial checks before deciding, visual verification, and frozen-list briefs. Especially for long autonomous sessions with subagents on a shared working tree.
---

# Delivery with proof, not with reassurance

Every rule here earned its place: it caught a real defect that had passed through "green tests". Do not skip them
because "it is obvious that it works".

## 1. RED FIRST — non-negotiable

Before you write the fix, **prove by execution** that the new test fails against today's code. Quote the actual
failure message in your report.

**Why**: a test you have never seen red, you do not know what it checks. In one case an e2e test used a **fake**
rule identifier, so it confirmed that "the human-readable label is displayed" and passed — while the application
was showing the user the internal identifier `pricing-rule-override-17`. The test was hiding the defect instead of
catching it.

Always add a **negative assertion** too: not only "the right thing is shown" but also "the wrong thing is **not**".

## 2. Read the REAL summary, not the exit code

Pipes swallow exit codes (`playwright | grep` → always 0). Read "X passed / Y failed" with your own eyes. A merge
has already gone through a red gate exactly this way.

Run the checks **synchronously**. Do not "wait for an event" that never comes.

**Quote the RAW OUTPUT LINES, never a formatted table.** A table can be written from memory or from expectation; a
line of output cannot. Real incident: a worker wrote "e2e: 14 passed, exit 0" while the run **was still going** and
they had not seen the output. The number **turned out correct** — which is why it went unnoticed, and why it is
worse: **a correct prediction is not verification**. In practice the report also hid a `1 skipped` that nobody saw.

This applies to the **recipient** of the report as well: if you merge on the basis of a table instead of output,
the gap is yours, not the worker's. **Ask for the lines.**

## 3. Instructions are hypotheses — test them adversarially before executing

If the instruction you were given breaks something, **measure it and deviate with documentation** — do not execute
it blindly, and do not silently ignore it.

**Example**: the instruction was "use a layout effect". The worker tried it, saw an existing test go red (React
runs all layout effects before passive ones, so the modal stole focus back), used a different solution, and **wrote
the reasoning into the code** so that nobody would later "fix" it.

## 4. Stop and ask when the spec collides with reality

Define **explicit STOP conditions** in every assignment: "if you find an existing test that depends on this
behaviour, stop and report". Better one question than a silent choice made inside an ambiguity.

The same goes for **interpretations that belong to the user** (regulatory, accounting, operational): note the
convention in the code as "to be confirmed" and ask. That is how an expiry date computed **wrong by one day**, in
the dangerous direction, was caught — the code had flagged it, the user confirmed it.

When the user gives two inconsistent versions (e.g. a weekday and a date that do not match), **do not choose** —
quote both and ask for confirmation.

## 5. Look at the screen

A code review does not catch: wrong text shown to the user, elements outside their container, jumping heights,
touch target sizes. Open the application.

- Use **exact viewport sizes** (Playwright viewport), not window resizing — browsers have a minimum width and you
  will be measuring the wrong thing.
- Measure instead of estimating: `document.scrollWidth − clientWidth` for overflow, `getBoundingClientRect()` for
  touch sizes.
- A "green" test asserting that "something is displayed" says nothing about **what**.

## 6. A double implementation is a suspected defect, not just untidiness

Every single time duplicated logic was unified in this work, a **real bug** was found in one of the versions: a
list filtering by name instead of by identity (and showing someone else's data), a button sending the wrong text,
a component breaking the page because 5 of the 7 pages had each fixed the same thing on their own.

Before writing a helper: **search** for an existing one. If you find something similar, unify. If it cannot be
unified, write down **why** — and the next person will not try again.

## 7. A "nothing was lost" table

When you replace a screen or a flow, require a table of **action × where it was before × where it is now**.
Without it, the losses are discovered by the user, weeks later.

## 8. A FROZEN list in every assignment

Write down explicitly what is **not** to be touched: verified domain logic, texts that belong to the user, recent
correctness fixes. And add **guards**: "these N tests must stay green without being weakened".

Never "fix the test so it passes". If an assertion was checking real behaviour, it must keep checking it — just
deterministically.

## 9. One writer at a time; merge only after completion

In a shared working tree: never two sub-workers writing at the same time, and **no branch switching while a gate is
running** — the results would be invalid without showing it.

Reading in parallel with writing is fine. Use it: while the writer runs, prepare the next assignment with read-only
analysis.

## 10. Measure, do not guess

"It probably happens rarely" is not an answer. Asked "what happens when the date shifts?", the worker swept 41,146
combinations and found 8.2% landing on a holiday and 29.1% diverging. That turned a suspicion into a documented
priority.

## 11. Check what SURVIVES a cancellation

Audits usually look at "what happens when the user completes". Almost never at "what is left when the user
**cancels**". An entire family of defects lives there:

- A dialog closed with Escape/X that **keeps** the previous selection — reopening it shows data unrelated to the
  current task (a real user finding: a form that cleared itself **only after a successful submit**, so cancelling
  left a customer selected and loaded their data the next time round).
- Filters/searches/sortings that survive navigation without being visible.
- Half-filled fields, uploaded files, temporary reservations.

**The test that catches it**: open → fill in → **cancel** → reopen → assert it is clean. Write it for every
creation form, not for one.

## 12. A user's finding is a CATEGORY, not an incident

When the user reports a bug from real use, do not fix it where they saw it. Ask **two** things:
1. **Where else does the same category live?** (grep for the pattern, not for the symptom)
2. **Why did my audit not catch it?** The answer is always an axis you did not examine — add it to the next sweep.

Real use finds what sweeps miss, because the user does things nobody thought to try. Treat every such report as a
**sample**.

## 13. One visible queue

The user does not see your notes. Keep **one** queue file that you update and send them. If they ask "what else do
we have?" and you have to go looking, the queue is broken.
