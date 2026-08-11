---
name: observe-before-concluding-en
description: Use when investigating, diagnosing, auditing, or answering "does X exist / how does this work / is this configured" — before writing any conclusion, especially a NEGATIVE one or one that goes into a permanent record. Complements akribeia (which governs how you CHANGE things safely); this governs how you establish what is TRUE.
---

# Observe before you conclude

The sibling of `akribeia`: that one governs **how you change**, this one **how you know**. When both apply,
**this one comes first** — you do not correctly fix what you incorrectly diagnosed.

Every rule was born from a real mistake. The incidents (I1–I3) are **one line beside the rule** and in full at the
end of this file — a rule without its incident becomes superstition, and without them nobody can judge later
whether it still holds.

## Checklist

- [ ] Did I ask for the whole set, or justify why the filter is safe?
- [ ] Does every negative conclusion have a second observation **of a different shape**?
- [ ] Did I see one real execution, not just the code that permits it?
- [ ] Is there a map of edges, not only a list of nodes?
- [ ] Did I verify myself whatever I am passing on from someone else?
- [ ] Does the wording match the strength of the evidence (or say "unverified")?
- [ ] Before the permanent record: what would overturn it, and did I check?

---

## 0. The rule that is never broken

**A query answers about the QUERY, not about the world.** Every observation has a scope (a filter, a path, a time
window, a type). A conclusion **may never exceed the scope** of the observation supporting it.

## 1. Ask for the whole set, filter afterwards

When full enumeration costs the same or nearly the same, **take all of it** and filter locally. A filtered query
against an unfamiliar system proves something **about the filter** — never about the system.

> **I1** — a DNS zone queried with `type=TXT` ⇒ the conclusion "there is no DKIM", while the records were **CNAME**; the key that would have shown the entire zone had been available from the start.

## 2. A negative finding is a claim about your METHOD

"I did not find it" ≠ "it does not exist". **Before you write that something does not exist**, answer in writing:
*in what form could it exist that my query would not have caught?* — and make a **second observation of a different
shape**. Two sweeps of the same shape are not confirmation; they are the same blind spot, twice.

## 3. Observe the flow, do not infer it from the source

Code and configuration show what **can** happen; logs, traffic and the live response show what **does** happen. For
every "how does this work", find **one real execution**. The existence of a mechanism does not mean it is the
**active** one.

> **I2** — an MTA installed on the server was assumed to be sending the email; the real path was a site plugin → the provider's SMTP relay, found only because a log contradicted the assumption.

## 4. Map the EDGES, not the nodes

Before any audit or assessment, draw the map: **what flows from where to where** — inbound, outbound, webhooks,
email, data, third parties. Nodes (files, settings, individual records) are what is easy to read; **the edges are
where the defects live**.

> **I3** — an audit with **94** node-level findings had seen none of what **five minutes** on the edge map showed: an origin exposed outside the proxy (exactly where the scans were landing), a record pointing at a control panel that does not answer, and three records still pointing at the previous hosting provider.

## 5. Anything handed to you by someone else is a CLAIM

A sub-agent, documentation, a code comment, a previous session, your own earlier self: **verify before you pass it
on**, and certainly before you write it into a permanent record or state it to the human as fact. The cost of
verification is almost always lower than the cost of retraction.

## 6. The confidence of your wording = the strength of your evidence

Do not write in capitals what you checked **once, through one lens**. Every conclusion carries its evidence (the
command, file:line, the response) or the word "unverified". **The scale**: *verified* (I saw it happen) ·
*documented* (I saw it written) · *likely* · *unverified*. Never a silent promotion from the third to the first.

## 7. Before writing a conclusion into a permanent record

Two questions, in writing: **(a)** which observation would **REFUTE** it? **(b)** did I make it? If the answer to
(b) is no, the conclusion is written as a **hypothesis to be tested**, not as a finding. A mistake in a permanent
record **travels**: it generates requests for access that is not needed, work that is not needed, and it poisons
every decision that follows.

## 8. Inherited findings: ask what the previous work COULD NOT see

When you inherit a list of findings, do not blindly continue it — recognise **its shape**. An audit written from
reading code never contains infrastructure, network or flow findings; not because there are none, but because
nobody looked. **Your first contribution is the missing dimension**, not the 95th finding along the same one.

## 9. When the human contradicts your conclusion

That is a **finding**, not noise — and they almost always know something about the edges that you did not see. Stop
and verify **BEFORE** you defend or concede. Both reactions, without checking, are the same mistake.


## The incidents, in full

All three happened on the **same day**, in the same piece of work — an audit of an online shop. Their common root
is the reason this skill exists.

### I1 — The filtered query that became a conclusion (§0, §1, §2, §7)

The question was whether the domain had DKIM, so that it could be decided whether the DMARC policy could move to
enforcement. The DNS provider's API was asked for the zone's records **with a `type=TXT` filter**. No DKIM from the
email provider was found, and the **permanent status file** received, in capitals and with full reasoning: "THERE
IS NO DKIM — `p=quarantine` would send order confirmations to spam". A plan of action was proposed on top of it,
beginning with "I need access to the provider's dashboard".

**The DKIM was there.** It was two **CNAME** records (`..._domainkey`), and the filter had excluded them. The key
that would have read the **entire** zone had been available from the start; it was simply never used that way. The
mistake was caught by the human, asking why the paths had never been checked.

**Cost**: a wrong conclusion written into a permanent record, a request for credentials that were not needed, and
an exposed key the human pasted into the conversation to solve a problem **that did not exist**.

**The lesson**: when full enumeration costs the same, ask for the whole set. And every negative conclusion ("it
does not exist") is, first of all, a claim about your **method**.

### I2 — The mechanism that was not the active one (§3, §5)

In the same piece of work it was taken for granted that email left through the MTA installed on the server —
because one **was** installed. The real path was entirely different: a site plugin sending through the **provider's
SMTP relay**. It surfaced only because a log contradicted the assumption.

The same day, a sub-agent's finding about a discount label was passed on **unchecked** — and the human questioned
it, correctly.

**The lesson**: the existence of a mechanism does not prove it is the active one; that needs **one real
execution**. And anything handed to you — by a person, a tool or a sub-agent — is a claim until you verify it
yourself.

### I3 — Ninety-four findings about nodes, none about edges (§4, §8)

The audit had delivered **94** findings, all of them from reading code and configuration — that is, all of them
about **nodes**. When the map of **edges** was drawn (what flows from where to where: DNS, proxy, email, third
parties), **five minutes** surfaced three things no amount of code reading had produced:

- the site's origin did not go through the proxy — so **no edge defence at all**, and that was exactly where the
  remote-code-execution scans were landing;
- one record pointed at a control panel that **does not answer**;
- three records still pointed at the **previous hosting provider**.

**The lesson**: nodes are what is easy to read; the defects live on the edges. And when you inherit a list of
findings, the first question is not "what does it say" but **"what could its author not see"**.
