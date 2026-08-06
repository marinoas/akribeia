# Appendix

Two sections kept out of `SKILL.md` to hold its size down, with nothing lost: the full reasoning on model
and effort (§3), and the list of what was **not** adopted and why.

---

## A. Model and effort — recommend, don't make the human guess (§3)

The orchestrator **explicitly recommends** which model and which effort level each role needs — at the
start of the session and **whenever the kind of work changes**. The decision belongs to the human; the
recommendation is an obligation. Without it, the human either guesses or pays top price for every task.

**The allocation principle: the expensive model goes on the LOW-VOLUME side.** The orchestrator runs
**continuously** and re-reads its whole context every turn; the workers run in **bursts** but burn many
times more tokens (measured: **160k–260k** each per assignment). So **implementation** gets the best coding
model at high effort; **orchestration** needs sufficient judgement with economy — not the most expensive
thing available.

**Exception**: when the human is **away** and leaves one large, well-specified goal, the top model pays for
itself as orchestrator (long autonomy, many agents to coordinate). In **interactive** work its multi-minute
turns are a drawback, not an advantage.

**Two traps that cost invisibly:**

- **Switching models mid-session invalidates the prompt cache** (it is per model). With a large context, an
  "upgrade" pays for a full re-read for zero benefit.
- **High effort does not improve judgement in a long session**: it lengthens the analyses, fills the
  context faster, and it is **context exhaustion** that ruins decisions later on. For long orchestration,
  medium effort produces a better FINAL result.

**What actually matters**: the quality of the **brief** counts for more than the model tier. Findings come
from narrow assignment, independent verification and real execution — not from a more expensive model with
a loose instruction.

---

## B. What was NOT adopted, and why

Popular lists of agent principles circulate. Most of their points coincide with `SKILL.md`. **Three,
however, need a boundary**, and it is worth saying so explicitly so they are not argued again:

1. *"Do not maintain backwards compatibility; delete old paths instead of adding compatibility layers,
   fallbacks or migrations."* That was written for products **with no real users**. When there is human
   data in the database, the opposite holds: old rows are left **dormant** rather than deleted, and old
   record types still open correctly. It contradicts §0 head-on. What is **genuinely dead code** goes —
   that is a different thing.
2. *"Never use a stopgap."* This contradicts "build in layers" from the same list. The temporary solution
   is sometimes the correct step; the rule that stands is "never an **unrecorded** stopgap" (§9) — every
   stopgap in the queue **together with its exit condition**.
3. *"Prefer existing libraries."* Generally true (§1) — but not where the problem is local or specialised
   (text transformations for one specific language, one industry's date-calculation rules, national
   holidays): there is no library there, and every new dependency is extra risk surface in a system holding
   confidential data.
