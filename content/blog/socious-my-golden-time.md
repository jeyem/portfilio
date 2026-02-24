---
title: "My Golden Time, Tied to Projects That Wanted to Make a Difference"
description: "A detailed account of my years at Socious — the rewrites, the Cardano escrow, the digital identity work, and what it felt like when the mission slowly stopped being real."
date: 2026-02-19
tags:
  - Cardano
  - Blockchain
  - Ethereum
  - Golang
  - Nodejs
  - Postgres
  - AWS
  - GCP
  - Docker
  - CI/CD
  - Career
  - Socious
draft: false
subtitle: "Rebuilding a Startup Backend, Two Blockchain Contracts, and What Happens When a Mission Runs Out of Runway"
---

This post is a technical and personal record of almost three years at Socious — what I built, what the team went through, and what I learned about engineering inside a mission-driven startup. If you're a recruiter or engineer, the technical decisions are in here. If you've worked at a startup that ran on belief longer than the runway warranted, the rest will feel familiar.

## Part I — The Trial and the Rewrite

### The Trial, the Chaos, and a Month That Was Never Realistic

The first call didn't go well. July 2022 — I had a meeting with Seira Yun, CEO of Socious, and within a day or two I got rejected. Stack mismatch, they said. My background didn't line up with what they were looking for on paper. That should have been the end of it.

But apparently one of the technical consultants on the project saw something worth a second look. I got pulled back in — not as a full hire, just a trial assignment. No onboarding call, no walkthrough, no "here's how we work." Just a folder of docs and a codebase. The docs were dense and mostly dead ends, the kind that tell you what something is called but not how it actually behaves. So I did what I always do: I ignored them and went straight to the code.

PHP wasn't my core language — it still isn't — but that never really mattered to me. Code follows logic. You read the models, you trace the conditions, you follow the data. In some ways it's cleaner than reading a requirements doc written by someone three steps removed from the actual system. Within a day or two I had a working picture of what Socious was: a simple hiring platform. Organizations posted projects or job positions, contributors found them and applied, and the app handled the connection flow. No payments, no complex state — just people and opportunities finding each other. The product was lean, but the network Seira had built around it on LinkedIn and social media was already real. That part was working.

### Working with Japanese for the First Time — and a Timeline That Made No Sense

This was my first time working closely with Japanese people. My impression of Seira was immediate: the guy was a hard worker. Always online, always responsive — despite a massive time zone difference between Tehran and Tokyo, replies came fast. That part genuinely impressed me.

But there was one thing that bothered me from early on. Seira had strong opinions about how things worked technically. Not wrong opinions necessarily, but confident ones — the kind that come from someone who has built products, moved fast, shipped things, but hasn't spent years deep inside an engineering process. There was a subtle sense that the development side of things was underestimated. Like it should move as fast as a decision in a meeting.

He had brought in a person named Lalo as CTO — and after a few sessions with Lalo, the picture got clearer. The existing PHP codebase was beyond patching. It had been built by an external company that had since mostly walked away from support. Custom framework, no real structure, no path forward for scaling. Lalo's take was direct: we can't build the future on top of this, especially on the backend. We agreed — a rewrite was the only real option.

Then came a meeting I still remember clearly. Seira laid it out: we need to migrate the backend to a new Node.js API. Timeline — one month. I was still in trial mode, still proving myself, still wanting this position badly enough that I swallowed what I actually thought. Inside I was stressed. That's not how you estimate engineering work. That's not a timeline — it's a wish. But I didn't say that. I just started working.

Those weeks had one rhythm: develop, climb, sleep. No family time, no rest, no margin. I gave everything to it — partly out of drive, partly out of the low-grade anxiety of being on trial with something to prove. I was lucky Seira mostly deferred to Lalo technically. Because Lalo and I were aligned: keep it simple, keep it fast.

### Building Something Clean From Something Broken

We went with Node.js and Koa — not Express. Koa's async-first design fit the way we thought about the middleware stack, and it kept things lighter. One early decision we locked in hard: no TypeScript. Neither of us wanted it. TypeScript adds a layer of ceremony that slows you down when you're trying to move, and at that point we weren't building a framework, we were building a product. We wanted to write what we meant and ship it.

The database approach was the same philosophy: no ORM. Just PostgreSQL, the native `pg` driver, and `sql-template-tag` for parameterized queries. We wrote a set of small utility functions — `filtering()`, `sorting()`, `textSearch()` — that sat on top of raw SQL and handled the repetitive parts without hiding what was actually happening. If you wanted to know what a query did, you read the query. No magic, no surprises.

The structure was domain-driven from the start: each feature area got its own route file, its own service layer, its own models. Routes handled HTTP in, services handled logic, models handled data out. Simple and explicit. The kind of architecture where a new developer can open any folder and immediately understand what lives there.

The repo is still live and maintained: [github.com/socious-io/socious-api](https://github.com/socious-io/socious-api). What we built in that frantic first month is the foundation it's still running on.

### The Team Split — and Putting the Brain in the Database

The division of labour was clean. I owned the backend entirely. Lalo and James covered the other side — James as the FE/mobile developer, working through the existing React app and refactoring it in parallel with the new API. Lalo sat above both of us: reviewing code, coordinating API contracts between my work and James's, and making the calls on direction. He handed off execution on both sides and focused on keeping us aligned.

That setup gave me a lot of freedom on the backend — and I used it. The part I'm most proud of from that period isn't the API itself, it's what I put inside PostgreSQL.

I'm a firm believer that the database should carry weight. Not all the weight — but real logic, the kind that needs to be reliable regardless of which service touches the data. So rather than doing everything in the application layer, I pushed a significant amount of the business logic down into the schema itself, through triggers and stored procedures. You can see the full result in [`src/sql/schema.sql`](https://github.com/socious-io/socious-api/blob/main/src/sql/schema.sql).

The schema ended up with 30+ trigger functions handling things that most teams would scatter across services. When a user followed another, a trigger updated follower and following counters atomically — no race condition, no separate service call. When a connection was made, a trigger automatically created bidirectional follows. When a mission changed status, a trigger cascaded that change to the related applicants and offers. When a post or comment was created, the tsvector search index was updated on the spot. Counters for likes, comments, shares — all maintained by triggers, consistent by definition.

There was also a full-text search layer built entirely in native PostgreSQL — `tsvector` columns on users, projects, posts, and organizations, populated automatically, queryable without Elasticsearch for the basic cases. The `identities` table was another deliberate pattern: a denormalized JSON mirror of user and organization metadata, kept in sync by triggers, so the most common access patterns hit one table instead of joining across several.

The schema also carried the dispute system — full event sourcing for conflict resolution, with evidence tracking and a voting model. Impact points with a history table. Multi-currency payment support across 28 currencies plus crypto. Credential verification tied to an external identity provider. All of this was in the database, enforced at the data layer.

Lalo reviewed everything. He had high standards and wasn't shy about pushing back on application code that wasn't clean. The SQL work got a different response — he called it out specifically as strong work. From someone with his bar, that landed.

### When the Team Got Smaller

It didn't last long. Tensions between Lalo and Seira started showing up in daily meetings — not loud, but visible. The kind of friction that doesn't resolve, it just builds. Eventually Lalo left the team. No drama announcement, he was just gone. That left me and James as the only engineers — each responsible for one side of the product, no CTO layer above us anymore.

Seira moved quickly to expand the frontend side. He had more work queued than James could carry alone, so he started pulling in FE developers from his network. On my side, he seemed satisfied — the backend was moving at a pace he could see, the API was taking shape, and he trusted what I was delivering. What he couldn't see was what it was costing me internally. I was already well past any reasonable commitment in hours per week, and it kept growing.

What kept it manageable was the culture. There were no set hours. The only hard requirement was the daily meeting — everything else was async. That gave me a rhythm I could actually live with. Mornings I wasn't productive anyway, so I'd go to the gym, climb, take care of myself. After lunch, a short nap, then I'd sit down and work until late into the night. Easily ten-plus hours most days, but on my own schedule and without anyone watching the clock. No complaints from either side — I delivered, they didn't ask how.

## Part II — Contracts, Team Churn, and Kish

### Sajad, a One-Month Promise, and Three Months of Waiting

After about a month, the API had surpassed the old PHP backend in clarity and capability. But it carried the scars of moving fast — e2e tests existed but didn't cover enough scenarios, some integrations were still rough, documentation was thin. We knew the debt was there. The second month was partly about chipping away at it: stabilizing integrations, filling gaps, making the API surface solid enough for James and the new FE developers to build against confidently.

We also found a tester — Azin, another Iranian on the team. She took on manual QA, working through flows methodically and surfacing the edge cases that automated tests weren't catching. Having a dedicated tester changed the dynamic noticeably. Issues that would have slipped into production started getting caught in staging.

The app at that point was running against the original design — functional but with real UX problems. Some flows were confusing, the information hierarchy wasn't clear, and certain paths felt like they needed to be figured out rather than followed. Seira brought in a designer to fix it — Minh, French but living in Japan, someone Seira had found through his network there. He was a good collaborator, easy to work with. What impressed us most was the outcome: Minh came back with a design that was close enough to the existing UI that we didn't need to tear down and rebuild the frontend. Changes were needed, but it was evolution rather than a rewrite. After the backend rewrite, that was exactly the kind of news we needed.

Around that time a new core developer joined the frontend — Sajad, Iranian, based in Isfahan, solid experience. He looked at the existing FE codebase and called it what it was: hard to read, harder to scale. He wasn't wrong. His proposal was to do a full frontend rewrite — and he said he could deliver it in one month.

I pushed back. I'd just lived through a backend rewrite and knew what "one month" actually looks like when you're rebuilding something from scratch while the product is still moving. Seira trusted Sajad's confidence. Three months later we still didn't have the new frontend at the level the old one was already at. I didn't say anything about it — there was no point. The timeline had already slipped and everyone could see it.

### Milkomeda, Hardhat, and Writing the Escrow Contract

While the frontend situation dragged on, I kept moving on the backend. E2E test coverage improved, the payment flow came together, and I started on the escrow smart contract work — which was the piece I was most interested in.

We already had a contract, but it wasn't properly aligned with our actual requirements. So I put Hardhat to work and rewrote it from scratch. Milkomeda was the target network — an EVM-compatible chain that wrapped Cardano, which made sense given Seira had already secured Catalyst funding and the roadmap committed us to Cardano-ecosystem payments. The contract went on-chain on Milkomeda testnet.

Milkomeda had problems. The testnet especially — transactions failing intermittently, network instability that made it hard to tell whether an issue was in our code or the chain itself. To separate our bugs from the network's, I deployed the same contract to Sepolia in parallel. Sepolia was stable and predictable. That comparison made it clear quickly: most of the failures weren't ours. The network just wasn't reliable enough yet. We documented it and worked around it.

### The Conflict That Got Us Sent to Kish

On the FE side, when I finally got a proper look at Sajad's new work, one thing stood out immediately: no CSS framework. Every style written from scratch. For a backend developer already stretched thin, being asked to reason about or contribute to that codebase was a real problem. I tried to bridge it — implemented RainbowKit for wallet connect, integrated the escrow dApp pieces into the frontend where I could — but it was slow going on ground I didn't own.

The friction between me and Sajad had been building for a while. His position was that my API documentation wasn't detailed enough — he needed full property definitions, descriptions, every field explained. My position was that the docs weren't bare — every endpoint had input types, enum definitions for both request and response fields, and a working call example you could run directly. The one honest gap was that response body shapes weren't formally exported as types. But with enums defined and a real example response for every call, reading what came back wasn't guesswork. If something was still unclear, asking me would resolve it in minutes. I was the only backend developer on the team. Writing exhaustive public-quality docs on top of everything else wasn't realistic, and I said so. He read that as obstruction. I read his silence as avoidance. We were both probably right in different ways.

Seira saw it and made a call: he bought all of us flights to Kish. Me and my wife, Sajad and his wife, Azin and her husband — six of us, meeting in person for the first time. Sajad and Azin were both from Isfahan, I came from Tehran, and we all landed at the same hotel on the island.

Something shifts when you meet people in person. The conflict didn't disappear, but it lost its edge. We did things together, had meals, got away from the screen. I told Sajad directly — everything between us is about work, nothing is personal. It landed. We didn't become best friends but we came back as people who respected each other. The communication issues didn't fully go away, but they got quieter, and when they came up we handled them differently.

### The Revolving Door

Back home, the search for more frontend help continued. I introduced a couple of developers — neither fit. Technically fine, but the communication pattern on the team was specific and not everyone adapted to it. After a while I introduced my sister Sanaz. She had three to four years of frontend experience and, more importantly, could actually communicate. She came in, got up to speed, and tried to make it work alongside Sajad.

She couldn't either. Same friction, different person. After a few months she had to resign. Shortly after, Sajad's own timelines — the ones he had set himself — kept slipping, and eventually he resigned too. The frontend had gone through a full cycle: rewrite promised, partially delivered, key developer gone.

James came back part-time to fill the gap. He already knew the codebase, knew the business, and could move without a long ramp-up. It wasn't a permanent fix but it kept things running.

Then Sanaz introduced someone from her network — Iman. He started strong. One of his first moves was bringing in Tailwind, which immediately gave the frontend a more consistent foundation than the hand-rolled CSS approach that had come before. I helped him onboard properly — and this time the dynamic was different. Iman and I could communicate directly and clearly. We moved fast together.

To make future frontend integration smoother I extracted all the API types and HTTP calls into a structured core package — [`src/core/api`](https://github.com/socious-io/web-app-v2/tree/main/src/core/api) in the web app repo. One place, typed, versioned alongside the API. It removed a whole category of integration friction that had caused problems with Sajad.

Seira found another frontend developer not long after. Iman ran the interview himself and gave the green light — that was Marjan. She was precise, reliable, the kind of developer who works best when the path and communication are clear. Give her that and she delivered without noise. The team finally had a stable frontend core.

### The PM Problem

With the engineering team in better shape, a different issue moved to the front: project management. Priorities shifted without clear reasoning. Some weeks the team was idle waiting for decisions; other weeks everything was urgent at once. Timelines appeared in meetings that had no grounding in what the team could actually deliver.

Seira was doing the PM work himself, on top of everything else a CEO carries. He was genuinely one of the hardest working people I've encountered — always on, always responsive. But attention split that many ways doesn't produce good prioritisation. It wasn't a character problem, it was a structural one. One person cannot own product strategy, fundraising, external relationships, team management, and sprint planning simultaneously and do all of them well. The team felt it. We started talking about bringing in a dedicated PM — someone whose only job was to sit between the business and the engineering side and keep the two in sync.

### The PM Who Made Things Worse

Ashkan joined as that PM. He came in, looked at the board, and tried to bring some structure to the sprints. The first couple of cycles he was involved in felt marginally more organised on the surface — but the underlying problems didn't move. Task definitions stayed vague. Priority calls still didn't reflect what the team actually needed to work on. If anything, the added process created more overhead without the clarity that should justify it.

Then something happened that I still think about. Ashkan had been watching Iman's output and apparently decided it wasn't fast enough. The way it played out — whether it was Ashkan pushing directly or working through Seira — the result was that Iman ended up on a PIP. Iman was one of the few people on the team I could work with cleanly. He communicated, he shipped, he made the frontend integration work in a way it hadn't before. Putting him on a performance plan was the wrong read. He felt the pressure, didn't see the point in fighting it, and resigned.

I didn't stay quiet about it. I told Seira and Ashkan directly how I felt — that we had just pushed out one of the better people on the team through a process that wasn't grounded in reality.

What happened next is one of the things I genuinely respected about how Seira ran the team. His hiring culture had a built-in check: every new person went through a one-month trial, and at the end the whole team submitted individual feedback ratings — privately, honestly. It was a real signal, not a formality. When Ashkan's trial period closed, me, Marjan, and Azin had all given negative feedback independently. Seira didn't override it. Ashkan was let go. The process worked exactly as it was supposed to — it just took a month and one unnecessary resignation to get there.

### The Team That Finally Held

After everything the frontend side had been through, me and Marjan were the stable core of engineering, with Azin covering QA. We ran interviews looking for another frontend developer but the bar had shifted — we'd learned the hard way that technical skill alone wasn't enough. Communication mattered as much as code. We also wanted someone who spoke Persian, which narrowed the pool but made day-to-day collaboration genuinely easier.

The answer was already in front of me. With Sajad gone and Marjan as a completely different working dynamic, I suggested bringing Sanaz back. She came back, settled in alongside Marjan quickly, and it worked. No friction, no territory. The team was finally in a shape that felt right.

## Part III — The Wallet and Cardano

### The Digital Identity Wallet — and a Technology That Wasn't Ready

With a stable team, we took on the most technically ambitious thing Socious had attempted: a self-sovereign identity wallet. The idea was to give Socious users a personal credential wallet — something they owned, that could hold verifiable claims about their work history, skills, and contributions, anchored on Cardano. Real digital identity, not just a profile page.

The infrastructure we built on was **Identus** — at the time still called Atala PRISM, IOG's decentralized identity platform, later contributed to Hyperledger and rebranded. Identus provides the full stack for self-sovereign identity: DID creation and resolution on Cardano as the verifiable data registry, verifiable credentials following W3C standards, and DIDComm v2 for secure peer-to-peer messaging between agents. Its SDK is split into modular components — Castor for DID operations, Pollux for credential handling, Mercury for messaging, Pluto for portable storage. Socious.io eventually became a listed contributor to the project. But when we were building on it, we were very much on the bleeding edge.

The honest assessment: the technology wasn't ready. Documentation had gaps that only became visible when you hit them mid-implementation. The SDK was actively evolving — updates dropped, APIs shifted, and parts of what we'd built needed refactoring before the feature was even complete. Services in the ecosystem had connection issues we couldn't control and couldn't always diagnose cleanly. Every step forward involved a debugging loop that was partly our code, partly the platform, and partly indistinguishable from either.

The harder truth underneath all of it: the users weren't asking for this. Activity on Socious was still low, and a credential wallet was a sophisticated feature for a platform still trying to reach critical mass of people doing basic things on it. We were building it because Catalyst funding had a roadmap attached, and the roadmap had a digital identity milestone. The feature was real work, genuinely interesting technically — but the timing was driven by grant deliverables, not user demand. That tension was starting to show.

### A New Developer, No Warning, and a Convention That Wasn't Negotiable

One morning in the daily meeting there was a new face. No prior conversation, no heads up — Seira had hired a backend developer and announced it after the fact. His name was Oledge, Russian, young, with real Solidity experience and a Node.js background. His task was the referral system: if someone referred a contributor who then got hired on a project, the escrow release needed to split the payment three ways — contributor's share, Socious platform fee, and a referral fee to whoever made the introduction.

On paper it sounds contained. In practice it touched a lot of places: backend logic, smart contract changes for the three-way distribution, a small frontend piece, and enough edge cases that a new joiner had to navigate the full codebase before writing a single line. I understood that. What I didn't accept was the PR that came back from it.

I reviewed Oledge's backend changes and left a comment on one specific thing: the referral was being modelled with a direct reference to the `users` table. Our convention across the entire codebase was to reference the `identities` table instead — a pattern I'd established from the beginning precisely because the system needed to handle both users and organizations interchangeably. The referral feature only dealt with users at that moment, but I'd been on this codebase for a year and a half and knew how quickly "only users" becomes "actually orgs too." Oledge pushed back and wouldn't change it.

I held the approval. That's when Seira decided to bring in an external consultant to weigh in.

That stung. I built the entire backend from zero. I'd been the only backend engineer for most of the project's life. And the question on the table was a naming convention — not an architectural debate, not a performance tradeoff. Getting a third party to arbitrate it felt like a signal that my judgment on my own codebase wasn't trusted. The consultant came in, looked at the situation, and said it plainly: Ehsan is fully onboarded, it's his call to approve or reject, and the convention he's describing is sound. Oledge updated the code, I approved the PR.

The smart contract side went through and got deployed to the chains. Then Oledge moved to the frontend integration — and hit the wall that backend changes often hide until someone tries to wire them into a real user flow. The core problem: the escrow contract needed the referrer's wallet address at distribution time to send the fee. But referrers weren't necessarily connected to a wallet when the payment triggered. A user who referred someone months ago might never have set up a wallet at all. The contract assumed an address that might not exist yet — and there was no graceful path for that in the UI.

Oledge's one-month trial closed around the same time. And as a footnote that I'll mention now because it belongs here: about seven or eight months later, Seira asked for organisations to be able to make referrals too, not just users. Because the backend was modelled against `identities` rather than `users` — the exact convention Oledge had refused to follow — the feature was already there. A few small frontend changes and it was done. No backend work, no contract changes. That's why conventions exist.

 Seira ran the usual feedback round. Most of the team rated him poorly. He was let go. The frontend PR stayed open, unmerged, the wallet address problem unsolved.

### The Thing I Couldn't Ignore Anymore

That whole episode — the referral system, the PR, the consultant call, Oledge's exit — crystallised something I'd been sensing for a while but hadn't fully named.

Seira's decisions were becoming hard to trust. Not because he wasn't trying — he was, visibly and constantly. But the pattern was revealing itself: features chosen not because users were asking for them, but because they looked good on a roadmap or unlocked the next funding round. And when things didn't go smoothly, the response was often to add process, add people, or call in outside opinion rather than step back and ask whether the thing was worth building at all.

The referral system was the clearest example yet. Who was it for? Socious at that point had a fundamental supply problem: in my entire time there, I counted maybe five or six positions that organisations had directly posted on the platform. Five or six. Users were joining, contributors were applying — but there was almost nothing to apply to. The marketplace was thin on the side that mattered most. Instead of attacking that problem — finding organisations, getting real projects posted, building the supply — we were building a referral fee mechanism for a hiring flow that barely existed. And before that, a credential wallet for users who weren't yet active enough to need one.

The platform needed traction, not features. But traction is harder to put on a grant deliverable than a smart contract deployment.

### Back in the Wallet — KYC, Mnemonics, and a CV in My Inbox

While that was all settling, I was still deep in the identity wallet work. We'd added a KYC layer to make the wallet genuinely meaningful — before a user could hold any credentials, they had to pass a third-party identity verification through Veriff. Once cleared, a KYC verifiable credential was issued to their wallet as the foundation. Only then could other credentials be added on top. It was the right design: a wallet full of unverified claims is just a profile page with extra steps.

The other hard piece was the backup system. Wallet recovery relied on a mnemonic — a seed phrase that derived the DID holding the user's assets. Getting that flow right, making it secure and usable for people who'd never touched a crypto wallet, was the kind of problem that looks simple from the outside and eats time from the inside.

In the middle of all this, Seira dropped a CV in my direction and asked for feedback. Elaine — American, blockchain developer, had been working on Uniswap, and was looking to relocate to Japan. My first read: strong blockchain background, but that alone wasn't what we needed. The codebase required Node.js, database work, dApp integration experience. A pure smart contract developer would be productive on one narrow slice and blocked everywhere else.

Seira's pitch was broader: she could be both a PM and a blockchain developer. She knew Haskell, which mattered because we needed to migrate the escrow from Milkomeda to native Cardano using Aiken — and Haskell knowledge transfers well to Aiken's functional model. He also mentioned she was strong at documentation and communicating between business and engineering.

The Haskell point made me think of something I'd noticed for a while. Seira had kept an open position for a Haskell developer almost the entire time I'd been at Socious. Many people applied. None were approved. I still don't fully understand what he was looking for there.

This time, unlike with Oledge, I actually met Elaine before any decision was made. Oledge arriving unannounced had left a mark. Elaine came across exactly as Seira described — native English speaker, clearly sharp, and when I asked her about the PM side she was honest that she'd been studying it seriously and felt comfortable taking it on. She talked through her previous experience well. I gave positive feedback. We badly needed a real PM, she had genuine technical depth, and she seemed like someone who could hold both roles without dropping either.

### Elaine, Part-Time and More Present Than Anyone Full-Time

Elaine joined while still finishing up at her previous job — part-time from the start. Within days it was obvious the board was in different hands. She restructured it, wrote proper ticket descriptions, and started tracking UI/UX issues with a level of attention the team hadn't had before. The gap between what Marjan and Sanaz were building and what the design actually specified had always been a source of slow drift — small mismatches that compounded. Elaine sat in that gap and closed it. She communicated between design intent and implementation reality constantly, catching things before they became rework.

She felt full-time. The output, the responsiveness, the way things moved — none of it reflected someone at half capacity. It was one of the cleaner additions the team had seen in a long time.

### The Move, the Illness, and a Role That Slowly Slipped Away

Her trial closed with positive feedback across the board — specifically on the PM side, which was the gap we needed filled. The plan was clear: move to Japan, settle in, then split her time between PM work and building the Aiken escrow contract to replace Milkomeda.

She took about two weeks off for the New York to Tokyo move. When she arrived she got sick — another week or two lost. By the time she was back on her feet and properly present, the momentum from the trial period had dissipated. The board drifted back toward its old state. Tickets lost their shape, flows got vague again. The PM function she'd brought in part-time didn't fully reassemble when she went full-time. It felt like we'd lost the PM again — except this time Elaine was still there, she'd just migrated toward Aiken and away from the coordination work.

There was also a project I only knew about peripherally — something called Harvest Flow, a contract Socious was developing for an external company. I never had full visibility into it. What I could see was that Elaine spent a significant part of her seven months there focused on it. She built the contract — but the integration work that had to follow, wiring it into actual transactions and getting wallet connect working inside our FE app, didn't come together. There was also an Aiken validation contract, though looking at it, it tracked closely to an existing example rather than being built from first principles.

After seven months Seira ran the team feedback session. The result was different from her trial. The feedback on both the code output and the PM work came back negative. She had been placed in a dual role — technical and organisational — and neither had landed the way the team needed. It wasn't a question of effort. It looked more like a mismatch between the role as it was defined and where her actual strengths were.

### The Wallet Ships, and Everything Piles Up

After seven or eight months the wallet was in a workable shape. Not perfect — the mediator would occasionally freeze, agent message delivery to the wallet would stall, connections sometimes dropped without clear reason. The kind of issues that are painful to debug because they live at the boundary between your code and a platform you don't control. But the core was there and functional.

That opened the door to the next project: Shin. The idea was a dashboard platform for organisations — a way to issue credentials to people and verify credentials presented to them. The wallet wasn't a side feature in Shin, it was the foundation. Everything Shin did assumed the wallet existed and worked.

At the same time the broader product was getting a full redesign. Socious was being rebuilt visually from the ground up, and a new version of the app was coming alongside it. Three frontend developers — Sanaz, Marjan, and whoever else — were already stretched handling the web side of it. Mobile was the gap nobody could fill. Neither Sanaz nor Marjan had built native apps. I could handle Android, but iOS was a hard stop — I couldn't build it on my environment. Iman came back to cover that side. He was the only one who could realistically own mobile given where the team was.

With Iman back we had more hands, but the backlog had grown quietly while I'd been heads-down in the wallet. Referral integration still had open edges. The dispute system had been sitting mostly on hold for months. Shin needed its own set of APIs. And now mobile deployment for both Socious and the wallet was on the list. The Aiken escrow contract was also still undelivered — Elaine hadn't been able to complete it, and the Catalyst fund release timeline was closing in. Seira asked me to pick it up and finish it.

Sanaz knew a developer who could help — MohammadHossein, someone with a solid DevOps background, good with Node.js, and familiar with Golang. Given where we were heading, that combination was useful.

Around this time Seira gave me the title of dev lead. All technical decisions sat with me — architecture, hiring input, code standards, what got built and how. It formalised what had largely been the reality for a while, but putting a name to it changed the weight of it.

### Finally, Golang — and Picking Up the Aiken Contract

The situation coming into this period was dense. Base Socious still had features to deliver. Shin needed to be built from scratch. The Aiken escrow contract was unfinished and blocking a Catalyst fund release. The wallet was off my plate in the sense that the core was done — we were moving forward with mediator and SDK updates that we hoped would resolve the remaining freeze and connection issues — but I was already carrying enough.

On the Aiken side, Seira's position was direct: we're not going to hire someone for this, learn it and get it done. By now I had technical decision authority, and I'd spent long enough working with low-community ecosystems and toolchains with thin documentation to know the cost. But the contract had to ship, so I picked it up.

For Shin I made a different call — one I'd wanted to make since day one. When I first joined Socious I'd have built the backend in Golang, but at that point I wasn't established enough to push it through. Now I was dev lead and Shin was a greenfield service. I chose Golang.

I built the base infrastructure with that in mind: clean package structure, internal libraries designed to be general enough to serve multiple platforms down the line — not just Shin, but whatever else Socious might need to spin up. Connection handling, common patterns, reusable components. The kind of foundation that pays forward rather than just solving the immediate problem.

MohammadHossein came in with clear ownership: the dispute system that had been on hold, the CI/CD pipelines that needed proper structure, and an AWS account migration — moving everything from the old account to new instances. I handled the early scaffolding of the migration and handed it off to him. He had the DevOps depth for it.

On the Shin frontend, Marjan and Iman picked up the design and started building. I told them not to wait for the real API — instead, build an API proxy layer, define their own types, and work against mock data. Once I had the actual API ready, the plan was to chain real data in and wrap the type differences with a transfer layer. Not a perfect architecture, but a deliberate tradeoff: I knew the Golang infrastructure would take time to get right, and if the frontend had to wait on actual API shapes before they could start, we'd miss the timeline. Running both in parallel, even with a seam to bridge later, was faster than serialising the work.

### The Best Period We Ever Had — and What Was Missing From It

The Golang structure came together. Shin's APIs took shape and I wrote them test-first — TDD throughout, which slowed the start but meant the surface was solid before anyone else touched it. Once the API layer was stable I called MohammadHossein to get the Shin dev environment pipeline ready, then switched to the frontend side myself — adding types, wiring up the API calls, and handing off to Marjan and Iman to connect the rest.

Meanwhile Sanaz was doing some of the cleanest work of the whole project. The wallet was getting a full visual rebuild — Minh had created a new design system for it, and Sanaz took that and refactored the entire UI while keeping the underlying logic intact. No regressions, new design, same behaviour. Exactly the kind of execution that only works when someone understands both the product and the codebase deeply.

For a stretch of weeks, the team was running at a level it hadn't reached before. Everyone had clear ownership, the work was moving, the dependencies were managed, the pipelines were clean. If you looked at the board and the velocity it was the best we'd ever been.

But underneath it there was something none of us were saying out loud. We were building well. We weren't sure we were building something people would actually come for. The doubt wasn't about our work — it was about whether any of it would matter. Socious, Shin, the wallet — these were real products, technically serious, genuinely built with care. But the user numbers hadn't moved in a way that matched the effort. The market wasn't responding the way the roadmaps assumed it would.

We pushed those thoughts aside. Seira believed in it. He'd been building toward this for years, had the network, had the funding, had the mission. We trusted his read of where it was going and kept our heads down. That's what you do when you respect a CEO and you've invested that much of yourself into the work. You push the doubt out and deliver what's asked. For a while, that's enough.

### Aiken, UTXO, and Learning a Completely Different Model

The Aiken contract was one of those tasks that looks contained from the outside and reveals its real size once you're inside it. Seira's position was clear: we're not hiring for this, learn it and ship it. I was dev lead now. That meant the call was mine, and the work was mine.

The first step was understanding what Elaine had actually delivered. Her Aiken work turned out to be a branch of an existing contract example from the ecosystem — the structure was familiar to anyone who'd looked at the reference material, with surface-level modifications applied on top. It wasn't a ground-up implementation built around our escrow requirements. I couldn't build on it confidently without understanding whether the choices underneath it were right for our use case. So I started from scratch.

On the frontend side the situation was worse. I went through Elaine's integration work expecting rough edges and found something that couldn't be salvaged. Transaction calls were happening in places that had no business triggering blockchain operations — components that handled display logic, not user intent. The timing of when a Cardano transaction should be triggered wasn't understood. Type errors throughout. The kind of code that tells you someone was pattern-matching against examples without a mental model of what was actually happening. I closed the PR and didn't merge it.

That left me with the full scope: learn Aiken, rewrite the contract, build the dApp integration from scratch.

The first thing I had to unlearn was everything I knew about EVM chains. On Ethereum, a smart contract is a deployed program living at an address, holding state in its own storage. You interact with it by calling functions, it updates its internal state, assets live inside it. The contract is the center of gravity.

Cardano is built on a fundamentally different model. There is no deployment in the traditional sense. You write a validator — a script that encodes the conditions under which a UTXO can be spent. The compiled script produces a hash, and that hash becomes the script address. Assets aren't stored in the contract, they're held in UTXOs sitting at that address. When someone wants to release funds, they build a transaction that spends those UTXOs, and the Cardano node runs your validator against it. If the validator approves, the transaction goes through. If not, it's rejected. The validator doesn't act — it only judges.

This changes everything about how you reason through a smart contract. There's no "call this function to release payment." There's "construct a transaction that spends the locked UTXO, attach the redeemer that proves intent, and let the validator decide." The logic isn't imperative, it's declarative. Aiken itself reflects this — it's a functional language, influenced by Elm and Haskell, designed to express validation logic cleanly. Once the model clicked, the language started making sense. But getting there took time.

### Handover, Conventions, and Clearing the Path for MohammadHossein

While I was deep in the Aiken learning curve, the broader Shin work was still moving. I'd made a deliberate call about how to handle MohammadHossein's onboarding — not just throw him into open tickets, but make sure he understood why things were built the way they were before he started changing them.

The codebase had conventions that weren't obvious from a quick read. The `identities` pattern — referencing the unified table rather than `users` or `organizations` directly — was one of them, and it had already caused one expensive disagreement. The Golang infrastructure in Shin had its own internal library design meant to scale across future services. Understanding those decisions wasn't optional. Someone who didn't understand them would make locally reasonable choices that created global problems, exactly like what had happened with Oledge.

So I walked him through the structure. Not documentation, not a wiki — a real conversation about why the architecture looked the way it did, what the existing Socious backend had taught us, and where Shin was supposed to go. He had the background to absorb it quickly. The dispute system work and the CI/CD pipeline work were both constrained enough that he could go deep without touching the parts that needed context he didn't have yet. It was a deliberate handover — give him ownership of the right things first, earn familiarity with the rest.

### The Real Hard Part: UTXOs, Locked Assets, and Knowing Exactly What to Spend

Understanding the UTXO model was one thing. Applying it to a real escrow flow was something else entirely.

On EVM chains, escrow is relatively straightforward: you deploy a contract, it holds the funds in its own storage, and you call a function to release them. The contract tracks everything. You ask it to pay out, it knows what it has and where it goes.

Cardano doesn't work like that. Funds aren't sitting inside a contract waiting to be released — they're locked in UTXOs at a script address, controlled by the validator. In our escrow model, the organization's payment was locked in a UTXO at the script address, with a datum attached describing the terms: who the contributor was, what the escrow was for, the conditions for release. The validator was the enforcement layer. It would inspect any transaction trying to spend that UTXO and decide whether the conditions were met.

The hard part wasn't writing those conditions. The hard part was building the release transaction correctly.

In an account-based chain you say "release the funds for this job." In Cardano you have to say "spend *this specific UTXO* — identified by transaction hash and output index — and here's the redeemer proving the release conditions are met." You can't approximate. You can't reference the escrow by job ID and let the chain figure out which UTXO that maps to. You need the exact UTXO. That meant the backend had to track every locked UTXO at the time of payment, store the reference, and surface it precisely when a release was triggered. If the UTXO reference was wrong or stale, the transaction would fail. No fallback, no retry with a different lookup.

This shaped the entire data model. The backend needed to know not just that a payment existed, but where it lived on-chain — the output reference that the spending transaction would need to consume. It also meant the release flow was sensitive to chain state in a way the EVM flow never was: if the UTXO had already been spent for any reason, the release would fail at submission and the backend needed to handle that gracefully.

Getting all of that right — the datum structure, the redeemer, the UTXO tracking, the transaction construction — was what took the time.

### CIP-30, RainbowKit, and a UX Problem Worth Solving

One thing I was determined not to let slip through was the wallet connection experience. We already had RainbowKit in place for EVM chains and it was clean — a consistent UI, broad wallet support, one flow for users regardless of what they were connecting. Splitting that into a separate Cardano-specific interface would have been the easy choice. It also would have made the product feel like two different apps stitched together.

The problem was that Cardano wallets speak CIP-30 — a browser extension standard that defines how wallets like Lace, Nami, and Eternl expose themselves to a dApp. And RainbowKit is built entirely on EIP-1193, the Ethereum provider standard. The two are not compatible: different method names, different transaction formats, different everything. RainbowKit had no concept of a CIP-30 wallet existing.

So I built a transformer — a CIP-30 to EIP-1193 adapter that wrapped the Cardano wallet API in an interface RainbowKit could treat as a standard provider. Under the hood it was translating between two completely different models. Above the seam, RainbowKit saw a wallet it understood. Lace appeared in the connector list alongside MetaMask. Users connected to Cardano the same way they connected to Ethereum. One flow, one UI, no branching in the frontend.

That part I was genuinely proud of. It's the kind of solution that disappears into the product — nobody notices it, which is exactly how it should feel. I extracted it into a standalone package, [`cardano-bridge`](https://github.com/socious-io/cardano-bridge), so it could be reused across Socious, Shin, and anything else that needed Cardano wallet support without pulling the complexity back into application code.

Two to three months after picking up the contract work, the beta was out.

## Part IV — Growth, War, and the End

### Growth Signals, Argentina, and a Team Starting to Fray

Around this period the business side was visibly accelerating. The treasury was growing — new funding rounds, new Catalyst tranches, the numbers moving in the right direction. Seira took the business team to Argentina to present Shin at universities, building partnerships, expanding the network. Expensive events toward the end of 2024. The kind of momentum that makes you feel like the inflection point is close.

From the outside it looked like growth. Inside engineering, the signals were different.

Marjan had migrated to Australia. And Socious couldn't make the numbers work for her there. She didn't want to leave — she knew the codebase, she'd been one of the most reliable people on the team — but the salary that had made sense in Iran didn't come close to covering life in Australia. She had no real choice.

That departure opened something I'd been half-aware of for a long time but hadn't fully examined. Engineer salaries at Socious were roughly half what comparable roles paid even in Japan — which isn't a high-salary market by global standards. That gap wasn't an accident. It was structural, and it had a name: we were Iranian.

Iran sits under some of the harshest international sanctions in the world. Most global payment platforms won't touch Iranian accounts. Most companies won't formally employ Iranian nationals. So the arrangement is what it has to be: the engineer works, and somewhere in the chain there's a workaround — a USDT transfer, a Bitcoin send, a cut taken by whoever is acting as the bridge between the engineer doing the work and the salary that eventually arrives. It's not unique to us. There's a whole shadow market built around it — people in other countries who will lend their identity to route payments, taking a percentage off the top for the service. You work for a foreign company, your salary lands in someone else's account in a country that can receive it, and they forward you what's left after their cut. In the meantime, you're legally invisible to the company that's benefiting from your work.

I found out during this period that Elaine — who had been part-time for much of her seven months, whose code I had closed and rewritten, whose PM work had dissolved after the move to Tokyo — was taking almost twice my salary. She was American, based in Japan, payable through normal channels. I don't know if Seira knew how that would land when I found out, or whether he thought about it. But it landed.

That's not a criticism of Elaine as a person. It's an observation about what the system does — and about who gets to benefit from the parts of that system that are invisible. The Iranian engineers I've worked with over my career have, on average, a depth of technical understanding that consistently surprises the people who hire them at a discount. We're not cheap because we're less capable. We're cheap because there's no other option, and the people setting the terms know it.

### The Announcement

Trying to hire again after Marjan left was its own frustration. Four open positions, including another frontend developer because the backlog wasn't getting smaller. Every time I found a candidate I felt good about, Seira would stall or redirect — other priorities, budget questions, something. The hires didn't come through.

That's when I decided to say something to the team.

I got everyone on a call and said it directly: stop worrying about timelines. Stop letting the business side pressure you into working beyond what you committed to. Do your best work within your weekly hours — not more. If something doesn't fit inside those hours, it waits.

I was the first person who needed to hear that. For more than two years I had been pushing past my own limits on the assumption that it would compound into something — that the growth would come, that the investment in the product would eventually show up in the numbers, that working harder was the right response to every gap. It hadn't worked that way. The product had grown technically. The user base hadn't grown proportionally. And nobody on the business side had matched the energy the engineering team had been putting in.

Saying it out loud to the team was also saying it to myself. We were not going to sprint our way to product-market fit. That's not how it works, and I'd spent long enough pretending otherwise.

### Joshua

The PM situation never fully stabilised. Seira had been trying to solve it by pulling people from the growth team into a coordination role — reasonable in theory, uneven in practice. Most of them didn't have the technical context to sit between engineering and product effectively, and adding a layer of process without that context just creates more noise.

Joshua was part of the growth team. He had no background in software engineering or project management — none. And for a while that showed. But then something shifted. He started following up on issues consistently. He was in the tickets, tracking blockers, writing clear task descriptions, making sure things didn't fall through the gap between a decision in a meeting and actual work getting scheduled. He communicated. He collaborated without trying to override.

He didn't become a technical PM. But he became something the team had rarely had: someone whose job was to make sure the engineering side wasn't blocked by the business side. That's a smaller thing than a full PM role, but it's not a small thing. When it's missing, engineers spend hours chasing decisions that should take minutes. When it's present, work actually flows.

Joshua turned out to be that person. It took a while to see it, but once it was visible it was hard to miss.

### Three Platforms, One Auth Layer, and a V3

The next wave of work arrived in two pieces that were separate on the surface but deeply connected underneath.

The first was Socious Fund — a new platform, and Sanaz and Iman picked it up the same way they'd taken on Shin: learn the design, build it out, coordinate with the backend as the APIs came together. At this point the team had the pattern down. Launching a new platform wasn't the unknown it once was.

The second piece was more architectural. There had been a requirement floating around for SSO — a single login across Socious, Shin, and now Fund. But as I thought through what that actually needed to be, a simple SSO felt like the wrong frame. We didn't just need shared login. We needed a shared identity. An Account Center — one place that held the user's core profile, owned authentication for all three platforms, and acted as the source of truth for anything identity-related. Each platform could have its own onboarding flow, its own shape of user data, its own product logic. But the person behind all of it would exist in one place.

That was a meaningfully different scope than "add SSO." The complication wasn't technical difficulty — it was the constraint we'd set for ourselves: no big refactors of the existing Socious Node.js backend, no disruption to Shin's working infrastructure. We wanted to thread Account Center through three live platforms with minimal modification to each one. In practice that meant defining a clean sync contract — when a user updated their profile in one platform, either that update propagated to the Account Center, or the Account Center was authoritative and platforms pulled from it. We landed on the latter: Account Center owns identity, platforms reflect it.

I started building Account Center myself.

The second piece was MohammadHossein taking a branch from Shin's Golang codebase and starting `socious-api-v3`. The reasoning was straightforward: Shin had established the internal library structure and conventions we wanted to carry forward. Rather than start fresh again, v3 would grow from that foundation.

The trigger for v3 wasn't just tidiness. There were real product requirements that the existing Node.js API couldn't absorb cleanly. The contract system needed a rethink — specifically around service profiles. Until now, users on Socious were either organisations posting work or contributors applying for it. But the product was evolving toward something more fluid: a user could also be a service provider, offering defined deliverables at different tiers to other users who came to them as customers. That was a different data model, a different contract flow, a different set of state transitions than the hiring model the original API was built for.

Rewriting that logic on top of the existing Node.js codebase would have meant untangling years of accumulated decisions. Better to build it correctly in the new system and leave the parts that were working in Node.js exactly where they were. V3 would handle new feature territory. The old API would keep running what it already ran.

Two parallel builds, one shared foundation.

### Socious Fund — Simple by Design, Complicated by Reality

Once the Account Center backend was stable enough to build against, I moved to Fund. The product itself was straightforward — a crowdfunding platform. I wired up the Account Center auth the same way I'd done for Shin, brought the core API package into the frontend using the same pattern, and we were moving quickly. The shape of the work was familiar by now.

The new piece was the donation system. Three rails: EVM, Cardano, and Stripe. Each with its own transaction flow, its own confirmation model, its own edge cases around failure and retry. All of it needed to be persisted — transaction state tracked from initiation through confirmation so nothing could fall through if a network stalled mid-submission. It wasn't complicated in the way the Aiken contract had been complicated, but it was wide. Getting all three rails solid and saving state correctly across them took real attention.

The other piece was impact points — a system that had existed in Socious proper for a while, tied to SDG cards and user behaviour. The idea was that contributing to impact-focused organisations earned you points, and those points reflected your standing in the ecosystem. Fund gave them a new role: your donation and your vote on a project were multiplied by your impact score. More points meant more weight. One impact point was also issued per donation, so participation built the very resource that made future participation more powerful.

It was an elegant loop on paper. The problem with it only became visible once the platform was live and we could look at who actually held points. Socious hadn't reached the user scale that would spread impact points across a real population. The team itself — Seira, the people around him, the early insiders — held a disproportionate share. Which meant that in a vote, a handful of people inside Socious could move a project from nowhere to the top. The system was designed for a world where the platform had thousands of active contributors accumulating points through real work. In the world we actually had, it was a lever that sat mostly in one set of hands. We didn't see that clearly enough before launch.

### Azin Leaves, Kish Again, and Shaunt

Azin had been our QA throughout — methodical, reliable, the person who caught the things automated tests couldn't. She migrated to Europe before Fund launched, and the gap was real. Manual testing had always been the safety net between staging and production, and losing it right before a launch wasn't ideal timing.

We worked through Christmas. Seira gave the team three days off, which he announced as a gesture. Given the delivery timeline we were on, it read more like arithmetic than generosity. But we'd taken a proper holiday not long before — a second trip to Kish, this time with the core team: me, MohammadHossein, Sanaz, Iman, Iman's partner, and my wife. Four people who had been through enough together that we didn't need to try to enjoy it. We just did. It's one of the best trips I can remember, and it made the end of the year easier to carry. We'd had that. The Christmas sprint didn't feel like theft.

Around this time I brought someone new to Seira's attention. I knew him from the climbing community — a smart, young, genuinely sharp person who was as passionate about coding as he was about the wall. We'd talked about stacks, about what he was building on his own, about how he thought about software. He had the kind of curiosity that doesn't need to be forced. I suggested to Seira to bring him on as a junior intern — not to build features, but to do what we'd needed for a long time: manual testing and, eventually, automated FE tests. Shaunt joined, started getting his hands into the apps, testing flows, poking at edge cases. After a while he was tracing bugs himself and fixing small issues independently. Exactly the trajectory I'd hoped for.

### The Nowruz Pilot

On Nowruz — Iranian new year — Seira announced the plan for Fund's pilot round: 10,000 dollars distributed to the top three winning projects, funded through donations collected on the platform itself.

I'll be honest: my first reaction was that the number didn't make sense. Ten thousand dollars is real money. The business team had one month to promote Fund well enough that organisations, donors, and users would collectively put that amount into a brand-new platform they'd never used before. I didn't say it out loud, but I didn't believe it was possible on that timeline.

We launched. It was Nowruz, which for Iranians is the most significant holiday of the year — the kind of thing that belongs to family and rest, not to delivery sprints. We'd just had a good trip the month before, which helped. The team didn't complain much. We got it out.

The timeline slipped almost immediately. One month became two. After two months the total raised was just under seven thousand dollars. Three thousand short of the target Seira had set in the announcement. He covered the gap himself, from the Socious treasury.

It worked, technically. The round ran, the winners were paid, the platform functioned. But the gap between what was promised publicly and what the platform could actually generate told the same story the user numbers had been telling for a long time. The business team could build events and generate momentum — Seira was genuinely skilled at that — but the platform underneath it wasn't deep enough yet to sustain what was being promised on top of it.

### Building Through a War

After the pilot, the work continued. Sanaz moved to Account Center's frontend — the interface that would let users manage their identity across all three platforms: update profile information, connect wallets, connect bank accounts, view their impact history. Everything that needed to exist in one place rather than scattered across Socious, Shin, and Fund. Iman stayed on Fund, working through the UX and UI improvements that had been noted during the pilot round and needed to be addressed before Round 1 launched for real.

Then Israel attacked Iran.

And then the internet went down.

This is something people outside Iran don't always understand: the shutdown isn't a side effect of conflict — it's a deliberate act. The Iranian regime has a documented pattern of cutting internet access during any event it doesn't want people to organise around — protests, strikes, military incidents. The infrastructure exists specifically for this purpose. There's a switch, effectively, and they use it. When the strikes came, the switch was thrown. Four days of near-complete blackout.

We found a way through. One datacenter inside Iran still had a connection — some routing path that hadn't been severed. We rented a VPS inside that datacenter, built a proxy channel through it, and forwarded all traffic to an OVH server we already had outside the country. Within a few days the whole team was back online. Not comfortable, not fast — but connected. Daily standups resumed. The work continued.

My wife was pregnant. Tehran wasn't the right place to be.

We drove north to Rasht. The idea was distance from the noise, somewhere quieter for her to wait out whatever came next. The first night there, Israel struck a military facility in the north.

I had never felt anything like it in Tehran. The sound hit before you could process it — not a bang, something lower and larger than that, the kind of pressure you feel before you hear it. Every window in the building flexed to the edge of breaking. My wife froze. The baby hadn't come yet and we were sitting in a city that had just shaken.

We stayed. What else do you do.

The team didn't scatter. We ended up in the same area — me, MohammadHossein, Sanaz, Iman — and instead of each sitting alone at home waiting for the next alert, we went to a café and worked together. Every day, same routine: find somewhere with a connection, open laptops, get on with it. Shaunt was the only one not with us — he'd stayed in Tehran — but the rest of us were together in a way the team rarely got to be outside of a planned trip.

There was something clarifying about it. No Discord delay, no waiting to sync — if someone was blocked you turned and said so. Sanaz pushing Account Center forward, Iman working through Fund's remaining issues, MohammadHossein on v3, all of us in the same room running on the same proxy connection through a datacenter that was somehow still online. Trying to ship software for a Japanese startup's crowdfunding platform while the windows occasionally shook.

When I look back at that stretch now, what I feel isn't pride exactly. It's something closer to disbelief. Not that we kept working — that part made sense, there was nothing else to do — but that the war actually pulled the team *closer*. The chaos outside drew a sharper boundary around the thing we could control. The standups were clear. The decisions were real. Nobody fell apart.

We got Fund ready for Round 1. Account Center moved forward. The code didn't know there was a war.

### Half a Million, Midnight, and the Worst Timing Possible

Round 1 closed with half a million dollars raised in three months. After a pilot that had barely scraped seven thousand, that number was genuinely shocking. Something had worked — the business push, the impact of the war on visibility, the projects that had registered through the platform mid-round, some combination of all of it. For a moment it felt like the inflection point everyone had been waiting for had actually arrived.

Seira had already lined up the next task for me before the round closed.

Midnight — [midnight.network](https://midnight.network/) — is a privacy-focused blockchain in the Cardano ecosystem, backed by IOG. The ask was to implement an escrow contract for it, same as we'd done with Aiken on Cardano and the EVM contract before that. A third chain, a third contract model, delivered as part of another Catalyst funding application Seira had put in.

The timing was the end of summer. My son's due date.

I was already operating at a kind of background stress level that I couldn't fully separate from the work. And then I opened the Midnight documentation.

It was some of the worst technical documentation I've encountered in a professional context. Not incomplete — actively misleading. Examples that didn't run. Concepts described in language that seemed designed to obscure rather than explain. They had invented their own toolchain, their own mental model, their own everything — and almost none of it was working reliably yet. The testnet wasn't fully up. The community was effectively nonexistent. There was no Stack Overflow thread to find, no Discord server with someone who'd solved the problem two months ahead of you, no blog post from someone who'd been through it. Just broken examples and documentation that pointed at itself in circles.

I raised all of this. The response from Socious was to deliver faster.

The only person who said something human was Joshua, calling from Japan. He told me directly: make time with your family, don't rush back. He was the only one.

My son was born. I took one week.

Then I went back to Midnight.

### The Round 1 Results and What Was Underneath Them

When Seira announced the Round 1 winners, the reaction in the general channel wasn't celebration. People were asking questions. Some were calling it a scam.

I pulled the data.

Total donations in Round 1: under ten thousand dollars. Despite half a million dollars announced — the gap was SOCIO tokens, the platform's own token, valued at ten thousand dollars each for the purpose of the round total. Real money from real users was still under ten thousand. The prize pool gap, same as the pilot, was going to be covered from the Socious treasury.

That was the first thing. The second thing was worse.

The project that won was sitting in fifth place by actual user votes and donations. A project the community had genuinely supported — put there by real people donating real money — did not win. The fifth-place project won because of Seira's vote.

Here's how: the impact point multiplier, the flaw we had quietly identified and never fully addressed, had played out exactly as the math predicted. Seira held a large share of SOCIO tokens — the platform's native token, counted at ten thousand dollars each for impact calculation purposes. He donated SOCIO to fill the prize pool gap. That donation generated impact points. Those impact points multiplied his vote weight. And with that weight alone, he moved a fifth-place project to first.

I don't believe it was malicious. I think Seira saw a prize pool that wouldn't close on its own and did what he'd always done — covered it himself, moved fast, solved the immediate problem. I don't think he modelled out what that action would do to the vote. But the result was that the platform's own crowdfunding round had its outcome determined not by its users, but by the person running the treasury.

The flaw we had seen early and left in place had just become visible to everyone.

### The End

People threatened legal action. Seira moved quickly — he announced the round was cancelled and refunded every single donation, personally. He followed through. But people also demanded the prize pool, and they were loud about it.

I had some sympathy for the frustration, but I had a harder time with the framing. Most of the people complaining barely understood what Socious Fund was. They had registered on a crowdfunding platform, donated money to projects they wanted to see funded, and now wanted guaranteed prize money as though they'd entered a lottery. The prize pool had been Seira's idea from the beginning — his way of generating participation on a platform that hadn't yet built enough organic energy to sustain itself. I'd never understood why he structured it that way. A platform that takes a fee on transactions and lets the community decide what it values doesn't need a prize pool. It needs real users doing real things. The prize pool was a substitute for that, and it had created exactly the expectations that now had people talking about lawyers.

Seira resigned as CEO of Socious and named Joshua as his replacement.

Joshua told me directly, not long after, that his situation was strange — he was being asked to lead but Seira was still directing things from behind him. He wasn't wrong. The structure had changed on paper. The reality hadn't fully followed.

Then Seira sent me a message. Direct, no preamble: we don't have money left. Complete the Midnight contract or we have to dismiss everyone. The team is moving too slow.

I said what I actually thought.

The treasury wasn't empty — it had been built from years of Catalyst funding. The problem wasn't money, it was where the money had been going. Round after round of prize pools drawn from the treasury, paying out to other organisations while the platform itself generated almost no revenue. The Midnight contract was one more grant deliverable. Even if I shipped it tomorrow, it wouldn't fix what was actually broken. The strategy was the problem. We were sitting on enough to generate real revenue right now, and instead of doing that we were burning it on prize pools to convince people the platform worked.

He didn't agree. Or maybe he couldn't afford to.

A month passed. I couldn't find focus anymore. I'd been carrying Midnight through the worst personal period of my life — my son had just been born, the country had been bombed, the documentation was useless, the community nonexistent, and the only thing coming from the project's sponsor was pressure. I told Seira and Joshua I wanted to resign.

The next day, the entire team was dismissed.

Fifteen days of everyone's work was held — not paid — contingent on the Midnight deliverable. So I helped finish what I could. We submitted two grant rounds for Midnight together, Seira and I, the applications that had been promised.

As of the day I'm writing this, I haven't heard back on either of them.

---

I spent almost three years inside Socious. I built the backend from nothing, rewrote it properly, shipped the wallet, wrote two escrow contracts on two different chains, led the team through a war, and helped launch three platforms. The people I worked with — MohammadHossein, Sanaz, Iman, Azin, Shaunt, Marjan — were some of the best I've been around professionally. That part was real. That part I don't regret.

What I couldn't fix was the thing underneath it all: the mission and the mechanism were never fully aligned. Seira believed in what he was building. I believed in him for a long time. But believing in a mission doesn't resolve the question of how you sustain it. And when the answer to that question is grant after grant after grant, with prize pools drawn from treasury to simulate traction that isn't there — eventually the math runs out before the mission does.

I should have said it louder, earlier. I said it at the end, when it no longer mattered.

The projects are still live. Make of that what you will.

---

*This is one perspective. I was an engineer, not a founder — I saw the product and the team clearly, but the business side had dimensions I never had full visibility into. Timelines blur in memory, sequences shift, and some of what I've written here may be imprecise in ways I can't fully account for. This is how I experienced it, not a complete record of what happened.*

## What I Actually Built

For anyone reading this as a portfolio reference — here is what shipped over almost three years:

- **Backend rewrite (Node.js/Koa, no ORM)** — Rebuilt the Socious platform from PHP from scratch. Business logic in PostgreSQL triggers and functions. Full-text search, atomic counters, dispute event sourcing — all in the schema. The repo is still maintained: [socious-io/socious-api](https://github.com/socious-io/socious-api).
- **Solidity escrow contract on Milkomeda** — Milkomeda is an EVM-compatible sidechain bridged to Cardano. First production smart contract I shipped at Socious.
- **Digital identity wallet** — Self-sovereign identity using W3C DIDs and Verifiable Credentials on Cardano, built on Identus (formerly Atala PRISM). KYC layer, mnemonic backup, credential issuance and presentation.
- **Backend migration to Golang** — Greenfield service (Shin) built in Go with an internal library structure designed to carry forward across future platforms.
- **Cardano escrow in Aiken** — Rewrote the escrow contract natively using Cardano's UTXO model. Full UTXO tracking on the backend to support precise transaction construction at release time.
- **CIP-30 to EIP-1193 adapter** — Built a transformer so Cardano wallets (Lace, Nami, Eternl) could connect through RainbowKit alongside MetaMask. Extracted as a standalone package: [socious-io/cardano-bridge](https://github.com/socious-io/cardano-bridge).
- **Three platforms, one Account Center** — Socious (hiring), Shin (credential dashboard), Socious Fund (crowdfunding). Unified auth layer across all three for V3.
- **Infrastructure** — AWS and GCP, Docker, CI/CD pipelines. Still running in production.
