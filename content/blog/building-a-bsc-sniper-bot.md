---
title: "I Built a Liquidity Sniper Bot for BNB Chain — and It Proved a Losing Game"
date: 2026-06-09
draft: false
description: "I built a complete, real-time DeFi sniper bot in Go, took it live with real money on BSC, and let the data answer one honest question: can a retail bot win at sniping new token launches? It can't — and the why is more interesting than a profit chart."
subtitle: "What four nights of live trading, ~$10 of real losses, and an adversary that adapted to every defense taught me about DeFi"
tags:
  - Golang
  - Blockchain
  - BSC
  - DeFi
  - Ethereum
  - SmartContracts
  - PancakeSwap
  - Web3
  - TradingBots
  - Engineering
---

# I Built a Liquidity Sniper Bot for BNB Chain — and It Proved a Losing Game

I built a crypto trading bot.

Not to get rich. I went in fairly sure that "easy money" bots are mostly a fantasy.

I built it to **find out for myself** — with code, with real money, with data instead of opinions.

And it gave me a clean answer.

> The bot works flawlessly. The market is the problem.
> The tokens that survive every defense you build are the ones *engineered* to survive every defense you build, and then trap you.

This is the story of that project: what it does, how I took it all the way to live trading, and the exact mechanism by which it lost. The engineering was the easy part. The honesty was the point.

---

# The idea I started with (and why it was wrong)

My first instinct was the one almost everyone has: **arbitrage**.

A liquidity pool prices BNB against USDT by a simple formula. When the price drifts a little — buy low here, sell high there, pocket the difference. A fast bot should print money on those gaps, right?

It took very little reading to see why that's the *hardest* game in crypto, not the easiest:

> Established pairs are efficiently priced. Any deviation is closed in the **same block** by professional MEV bots running on private mempools and co-located infrastructure. By the time a retail bot sees the gap in the public mempool — a second or two later — it's gone, and your transaction is visible to everyone, so you get front-run too.

Efficient markets have no retail edge. That edge was captured years ago by people with infrastructure and capital I can't match.

So I reasoned my way to the one corner that *might* still be inefficient:

> Brand-new token launches have **no price discovery yet**. The gap between the launch price and where the market settles is the only mispricing a small bot could theoretically capture.

That's "sniping." And it led me straight into the most adversarial environment I've ever written software for.

---

# What I built

I wrote it in **Go**, as a clean, staged pipeline. The shape matters, because each stage is a defense, and the story is really about defenses being defeated one by one.

```
WebSocket (PairCreated event)
   → listener     receive raw logs
   → pipeline     a funnel of gates, cheap → expensive:
        decode → reserve → token → score → lp/pre-arm → honeypot → output → trade
   → monitor      track each position, run the exit strategy, execute sells
   → executor     sign & submit real swaps (live mode)
   → store        SQLite record of every position and sell
```

A few pieces I'm genuinely proud of as engineering:

- **A pure-Go honeypot simulator.** Before buying, it runs a full *buy → sell* round-trip against the real token using `eth_simulateV1` — one RPC call, state carried between calls, a fabricated wallet funded by overriding a storage slot. If the simulated sell reverts, it's a honeypot, and we never touch it. No deployed helper contract, no Solidity.
- **AMM-accurate paper trading.** The sandbox prices fills along the real constant-product curve, so a rugged pool fills near zero. Paper P&L *cannot* hide a loss the way naive backtests do — which turned out to matter enormously.
- **A real on-chain executor.** Encrypted keystore wallet (passphrase from the environment, never disk), a capital ledger that gates buys on balance + a gas reserve, real V2 swaps that measure tokens received from the actual `balanceOf` delta, a deployer blocklist that learns from rugs, and restart-liquidation so a crash never strands a position.
- **Chain- and DEX-general.** Router, wrapped-native, chain id, and fees all come from config. The same binary runs any Uniswap-V2-style DEX on any EVM chain.

It's a complete, working system. That's important, because it means when it lost, it wasn't losing because of a bug.

---

# Then I did the thing most people don't: I went live

Paper trading looked *great*. In the sandbox, most tokens showed a profit.

I almost stopped there. I'm glad I didn't, because the gap between paper and live is the first real lesson:

> Paper exits are instant, free, and never fail. Live exits are a transaction that takes ~3 seconds to mine, into a market that is actively trying to trap you. **Paper profitability does not transfer to live for this strategy.**

So I funded a throwaway wallet with a few dollars, set the trade size tiny (~$0.60 a pop), flipped the safety switch off, and let it run for real.

Here is exactly what happened, defense by defense.

---

# The field report

| The bot, at each stage | What real money did | Verdict |
|---|---|---|
| Detection + honeypot sim | **12 / 12 losses, −83%.** Every token went flat, then rugged in 10–18s. | rugs dominate |
| **+ LP lock/burn check** | One whole night: **0 buys.** 66 launches skipped for unlocked liquidity. | the safe ones are rare |
| **+ recursive pre-arm** | Finally fired buys — on confirmed-locked, sim-passing tokens. | the strategy *functions* |
| The result of those buys | 4 tokens passed **everything**, the buys worked, prices even **rose**… then every sell reverted. | **−100% each** |

Let me unpack the two findings that actually matter.

## Finding 1: a rug is not a price crash

The first run was carnage. Twelve trades, twelve losses. I added an exit strategy with a stop-loss and a trailing stop — and it didn't help at all. Why?

Because a **rug pull is not a price movement.** The deployer doesn't sell the token down; they call `removeLiquidity` and pull the entire pool in one transaction. The *price ratio* barely moves — so a stop-loss watching price never triggers. One block there's liquidity; the next block the pool is empty and your tokens are unsellable.

> You cannot out-*exit* a rug. There's nothing to sell into. The only defense is to never enter — which means proving the liquidity is locked *before* you buy.

So I built that. The pair contract *is* the liquidity token; if enough of its supply sits in a burn address or a known locker, the deployer can't pull it. I made the check recursive — it polls for a window and buys the instant a token proves it's locked.

That stopped the rugs cold. An entire night with zero losses, because it correctly refused every ruggable launch.

It also revealed Finding 2.

## Finding 2: the survivors are engineered to be traps

When the bot finally bought tokens that had locked their liquidity *and* passed the honeypot simulation, four of them did something I'll never forget:

```
14:05  BUY VIT      (passed LP lock + honeypot sim, real buy succeeded)
14:08  VIT +16.7%   (it went UP — sellable a moment ago)
14:08  SELL reverts. retry. reverts. ×5. unsellable. −100%.
```

Same for three others, all dressed as fake stablecoins — `USDM`, `PUSD`, `USDTR` — to look legitimate.

These are **switchable honeypots**, and they are beautiful, evil engineering:

> The token is genuinely sellable at the instant the simulator checks it — so it passes. The bot buys. The deployer lets bots accumulate for a few minutes, then flips a switch (`setMaxSell(0)`, a blacklist, a pause) and freezes every buyer.

A honeypot simulation is a **point-in-time** check. It cannot see a *future* state change. There is no pre-buy filter for "the deployer will disable sells three minutes from now," because that information does not exist when you have to decide.

---

# The structural conclusion

After all of it, BSC launches sort into exactly three buckets:

| Token type | My defense | Outcome |
|---|---|---|
| no liquidity lock | LP check | skipped |
| static honeypot | sell simulation | skipped |
| **switchable honeypot** | **none possible** | **−100%** |

And here's the part that makes it unwinnable, not just hard:

> The tokens that survive your funnel are precisely the ones *built* to survive your funnel. Every filter you add doesn't reduce your losses — it **selects** for a more sophisticated adversary. You're not fighting bad luck. You're fighting someone who adapts to your exact defenses and keeps the timing advantage.

Total cost of learning this, for real, on-chain, with data I can point to: about **$10**. The entire "buy my sniper bot" industry is built on never telling you this.

---

# What I actually took away

The losses were tiny. The lessons were not.

**On engineering.** This is the kind of project I value most — the one where I didn't already know the domain (MEV, AMM math, `eth_simulateV1`, honeypot mechanics) and had to decompose it fast enough to build something real. The bot is genuinely good: a clean staged pipeline, honest AMM-accurate accounting, a full live-execution engine, chain-agnostic by config. None of that was the hard part.

> Engineering is rarely about already knowing the technology. It's about decomposing an unfamiliar, adversarial system fast enough to get a true answer out of it.

**On markets.** Both ends of what I tried are losing games for retail, for opposite reasons. Efficient markets (arbitrage) have *no* edge — taken by faster, richer players. Inefficient markets (new launches) have an edge that exists *because* the place is a minefield. The scams live exactly where the only opportunity is. There is no permissionless venue that's both active and clean — that's not a config you can find, it's the structure of the thing.

**On honesty.** I could have stopped at the green paper-trading numbers and written a very different, much more flattering post. The whole point was to not do that. I built an instrument precise enough to tell me the truth, and then I believed it.

A bot that loses $10 and hands you a correct, hard-won conclusion is worth more than one that shows you a fake profit chart and quietly drains your wallet.

I'm calling this project finished. It did exactly what I built it to do: it answered the question honestly.

The code is a complete, working liquidity sniper. The result is a clear "no." Both of those are, to me, a success.

---

The full source is open (GPL-3.0): **[github.com/jeyem/lqsniper](https://github.com/jeyem/lqsniper)** — read the field report in the README, and please remember the disclaimer.
