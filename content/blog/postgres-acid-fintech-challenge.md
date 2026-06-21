---
title: "A Small Fintech Challenge, and Why I Let Postgres Hold the Money"
slug: "a-small-fintech-challenge-and-why-i-let-postgres-hold-the-money"
date: 2026-06-21
draft: false
description: "I took a small fintech-style coding challenge — a marketplace where players buy and auction items with in-game gold — and treated it as one question: how do you keep money correct when many people act at once? The answer wasn't a clever lock in my code. It was leaning on what Postgres already guarantees."
subtitle: "How ACID transactions and row-level serialization turned a hard concurrency problem into a boring one"
tags:
  - Postgres
  - Golang
  - Fintech
  - Concurrency
  - Databases
  - ACID
  - Backend
  - Engineering
---

# A Small Fintech Challenge, and Why I Let Postgres Hold the Money

I picked up a small backend challenge recently: build a marketplace where guilds buy and auction items using in-game gold. Listings, auctions, bids, a price oracle, automatic settlement. On the surface it's a CRUD app.

The full source is on GitHub: [github.com/jeyem/dragon-market](https://github.com/jeyem/dragon-market).

It isn't. The moment money moves and two people act at the same time, it becomes the only problem that matters:

> A marketplace can lose a feature and survive. It cannot lose a coin and survive.

Two guilds bid on the same auction in the same millisecond. A buyer spends gold they already spent on something else a microsecond earlier. An auction settles twice because a retry fired. Every one of these is a money bug, and every one of them is a *race*.

The interesting part of the project wasn't the API. It was deciding **who is responsible for correctness**. I decided it shouldn't be my Go code. It should be Postgres.

---

# The temptation, and why I skipped it

The instinct is to reach for application-level concurrency control: a mutex around the bid handler, an in-memory queue per auction, a distributed lock in Redis. It feels like control.

It's also a trap. App-level locks don't survive a second instance of your service. They don't survive a crash mid-operation. They don't roll back. And they sit *outside* the system that actually stores the truth, so they're always one deploy away from being bypassed.

Postgres already solves this, and it solves it with guarantees that have been hardened for decades. So the whole design became one sentence: **every operation that touches money is a single database transaction, and the database serializes the parts that conflict.**

---

# Balances you can't corrupt because they don't exist

The first decision was to not store balances at all.

There's no `balance` column anywhere. A wallet is *derived* from an append-only ledger:

```
total     = sum(grant, credit) - sum(debit)
reserved  = sum(reserve)       - sum(release)
available = total - reserved
```

This sounds like a performance compromise. It's actually a correctness gift. A mutable balance column is the classic lost-update bug waiting to happen: read 100, read 100, both subtract 30, both write 70, and 30 gold just evaporated. You cannot have that bug against a number you never update. You only ever *append* a fact — "reserved 50 for this bid" — and the balance is whatever the facts add up to. Every coin is traceable to a row.

---

# Letting the database serialize the race

The bids are where concurrency gets real. A new bid has to be at least 5% above the current highest, and the bidder has to actually have the funds. Both checks are meaningless if another bid lands between the read and the write.

So the transaction takes a **row lock** on the auction before it reads anything:

```sql
SELECT ... FROM auctions WHERE id = $1 FOR UPDATE;
```

`FOR UPDATE` makes Postgres serialize every bid on that one auction. The second bidder simply *waits* — inside the database, holding a real lock — until the first transaction commits or rolls back. By the time they read the highest bid, it's the truth, not a stale snapshot. The 5% rule and the funds check are evaluated against reality and can't be undercut by a concurrent writer.

The same pattern guards a buyer's wallet: lock the guild row, then check available funds and the daily spend cap. No two purchases can both believe the same gold is available.

This is a deliberate trade. Bids on a *single* auction now run one at a time, so a wildly hot auction is a throughput hotspot. I kept it anyway and wrote the trade-off down: it's per-row, so different auctions still run fully in parallel, and I'd take "slower but always correct" over "fast and occasionally wrong" with money every single time. Consistency first; throughput is an optimization you can do later with a clear conscience.

---

# The bug the tests caught (and what it taught me)

I wrapped the database calls in a circuit breaker, and my first version counted *business* rejections — "bid too low", "insufficient funds" — as breaker failures. A burst of perfectly valid rejections tripped the breaker, and the next legitimate request got a 500.

The end-to-end tests caught it immediately: a buy that should have returned `200` came back `500`. The fix was a one-line distinction — only real infrastructure faults (a failed begin or commit) trip the breaker; a rolled-back business rule counts as a *success*, because the system did exactly what it should. The transaction had already protected the data. The breaker just had the wrong opinion about what "failure" means.

---

# The takeaway

The lesson I keep relearning: **the database is not just where data rests, it's a correctness engine, and most of the time it's a better one than the code you'd write to replace it.**

ACID transactions gave me atomicity for free — debit the buyer, credit the seller, transfer the item, all or nothing. Row-level locking gave me serialization exactly where conflicts happen and nowhere else. An append-only ledger made an entire category of bug structurally impossible.

I wrote less concurrency code, not more. The hard part — making races safe — I handed to the system designed for it. That's not laziness. On anything that touches money, it's the most senior decision in the whole project.

The code, the migrations, and the end-to-end tests are all here: [github.com/jeyem/dragon-market](https://github.com/jeyem/dragon-market).
