---
title: "How Fanout Broadcasting Powers Millions of Concurrent WebSocket Connections"
slug: "fanout-architecture-millions-concurrent-websockets"
date: 2026-08-16
draft: false
description: "A deep dive into the fanout pattern: the architectural pattern that lets you handle millions of concurrent WebSocket connections. No distributed consensus. No global locks. Just local sharding and Redis."
subtitle: "The pattern that makes millions of public chats possible"
tags:
  - Go
  - WebSocket
  - System Design
  - Architecture
  - Scalability
  - Redis
  - Backend
  - Concurrency
  - Broadcasting
---

# How Fanout Broadcasting Powers Millions of Concurrent WebSocket Connections

I've been working on a chat platform that handles millions of concurrent public chat participants. Early on, I faced the fundamental question every real-time platform asks:

> How do you broadcast a single message to 10,000 people on the same chat simultaneously, across multiple servers, without everything collapsing?

The answer turned out to be simpler than I expected. Not simpler in implementation—the implementation is thoughtful—but simpler in *concept*. The pattern is called **fanout broadcasting**, and I want to walk through it because it's one of those designs where understanding the shape immediately makes you understand why it scales.

I've built production systems using this pattern, and I want to share the architecture and the thinking behind it so you can apply it to your own real-time systems.

---

# The Scale Problem

Let me start with the constraints.

A public chat room on your platform can hold millions of people. Each person is a WebSocket connection. A message needs to reach every connection in that room within 50 milliseconds. You have multiple servers. Each server can only see the connections it directly holds.

The naive approaches fail immediately:

- **Central broker**: One server routes every message to every other server. Becomes the bottleneck instantly.
- **Mesh**: Every server talks to every other server about every message. O(n²) complexity. Doesn't scale.
- **Database writes**: Every message hits the database. Database becomes the bottleneck.

These all fall into the same trap: they try to make the routing part intelligent. They fail because routing is O(n) no matter what—you have to reach every connection.

The fanout pattern doesn't try to be clever. It accepts that every connection needs touching, then optimizes *that* to be as simple as possible.

---

# The Pattern, in 30 Seconds

```
Message published to Redis Pub/Sub
        ↓
Subscriber receives it
        ↓
Broadcaster looks up all connections for the session
        ↓
Queues jobs to worker pool
        ↓
Workers send to their assigned connections
        ↓
Done (non-blocking)
```

The magic: The broadcaster returns immediately. Workers handle delivery in the background. No blocking. No coordination. Just efficient work distribution.

---

# The System Architecture

Here's how all the pieces fit together:

```
Redis Pub/Sub
    ↓
Subscriber (receives messages)
    ↓
Broadcaster (non-blocking)
    ├─ Job Queue (bounded, drops if full)
    ↓
Worker Pool (1,000+ workers)
    ├─ W1, W2, W3 ... W1024
    ├─ Independent, parallel processing
    ├─ 25ms timeout per send
    ↓
Session Registry (sharded)
    ├─ Shard 0: session → [conn1, conn2, ...]
    ├─ Shard 1: session → [conn3, conn4, ...]
    └─ Shard N: session → [...]
    ↓
WebSocket Connections
    ├─ Connection 1 (outbound queue, reader, writer)
    ├─ Connection 2 (outbound queue, reader, writer)
    └─ Connection N
```

---

# Layer 1: The Session Registry (Sharded Lookup)

The server maintains an in-memory map of which connections belong to each session:

```
registry.shards[64]
  ├─ shard[0] → map[sessionID]map[connID]Conn
  ├─ shard[1] → map[sessionID]map[connID]Conn
  └─ ...
```

When a WebSocket connects, it registers itself. When it disconnects, it unregisters. Simple.

**The key insight**: Use sharding to eliminate lock contention. Instead of one global lock protecting all sessions, you have 64 independent locks. When a message arrives for session #42, you hash it once, grab one lock, and you're done. 

Lock contention becomes imperceptible. With 40,000 connections across 1,000 sessions, you're distributing that load across 64 buckets—each bucket sees ~15,625 connections. Contention scales down, not up.

---

# Layer 2: The Message Bus (Redis Pub/Sub)

A shared message bus (Redis Pub/Sub) sits between publishers and the broadcaster. The flow is:

```
Publisher publishes: PUBLISH chat:room-123 '{"id":"msg-42","text":"hello"}'
    ↓
Redis delivers to all subscribers instantly
    ↓
Each subscriber (broadcaster instance) receives the message
    ↓
Each processes independently, fanning out to its own connections
```

This is the crucial decoupling. The publisher doesn't know how many subscribers exist. Each subscriber doesn't coordinate with others. Redis just replicates the message to every listener.

No distributed consensus. No leader election. No coordination protocol. Just pub/sub.

---

# Layer 3: The Broadcaster + Worker Pool

When a message arrives from Redis, the broadcaster doesn't immediately send to all connections. That would block.

Instead, it creates **send jobs** and queues them to a **worker pool**:

```
Message arrives
    ↓
Look up all connections for this session
    ↓
Queue one job per connection to jobQueue
    ↓
Return immediately (non-blocking)
    ↓
Workers process queue independently
    ↓
Each worker attempts to send (with timeout)
```

**The broadcaster is fast**—it just enqueues and returns. It doesn't wait.

**Workers run independently**—Typically 1,000+ workers, each pulling from the shared queue. If one connection is slow, that worker waits on it, but the other workers keep going. Slow connections don't stall the system.

**Graceful degradation under load**—If the queue fills, the broadcaster *drops the message*. It doesn't block. It doesn't apply backpressure. It just moves on. In a live chat, a dropped message is better than a hung system.

---

# Layer 4: The Connection Writer (Per-Socket Handling)

Each WebSocket connection has a writer that pulls messages from a queue and writes them to the socket.

When a worker wants to send a message, it attempts to write to the connection's queue. Critically, this is non-blocking with a timeout:

```
Worker attempts to send message to connection queue:
    ├─ If queue has space → message enqueued (success)
    ├─ If queue is full → timeout after ~25ms → drop
    └─ Writer handles the queue → sends to socket asynchronously
```

Why 25 milliseconds? It's short enough that a slow connection never stalls a worker (who can retry another job), but long enough that normal network jitter won't cause false drops.

**Key insight**: The connection never closes its queue. When a connection dies, the queue stays open. This means workers don't need to check if the queue is closed before sending. No panic-on-closed-channel errors. No close-notification protocol. The writer just exits when the connection dies, but the queue itself stays valid. Simple.

---

# Why This Scales

The pattern wins on three fundamental dimensions:

**O(n) not O(n²)**
Broadcast time is linear in session size: to reach 10,000 people takes roughly 10x the time of 1,000 people. But you're doing it in parallel across workers, so that time is amortized. The broadcaster itself returns immediately; workers process in the background.

**Lock contention → 1/M**
Sharding into 64 buckets means lock contention drops 64x. One writer vs. 64 writers to the registry. Even at millions of connections, contention per bucket stays bounded and predictable.

**Memory is linear in connections**
Each idle connection costs roughly 20-25 KB (buffers + goroutines). 100,000 connections = ~2-2.5 GB of process memory. Scales linearly, not exponentially. No surprise explosions.

**Worker throughput scales with pool size**
Adding workers directly multiplies throughput. Each worker is just making channel sends—no syscalls, no I/O, no locks. Lightweight. 1,000 workers can process millions of queue operations per second.

---

# The Trade-offs

This pattern is not magic. It makes specific choices:

**At-most-once delivery**: Messages in memory are lost if the server crashes before delivery. Acceptable for chat. Not acceptable for financial transactions.

**No global ordering**: Messages from different publishers may arrive in different orders. Acceptable for chat (the UI reorders anyway). Not acceptable for systems that need strict global ordering.

**Per-session latency**: Broadcasting to a large session takes time proportional to the number of connections. A session with 100,000 people might take 50-100ms to broadcast to. This is unavoidable—you have to reach every connection.

---

# Resource Requirements

When built correctly, the pattern delivers predictable resource usage:

**Memory per connection**: ~20-25 KB (for buffers + goroutines, excluding kernel socket buffers)
- 10,000 connections → ~200-250 MB
- 100,000 connections → ~2-2.5 GB
- 1,000,000 connections → ~20-25 GB

This scales linearly. No surprises.

**CPU characteristics**: Broadcast time is O(session size), not O(connection count). Broadcasting to 10,000 people takes maybe 10-50ms depending on implementation. This happens in parallel with other operations via workers.

**Worker queue saturation**: With 1,000 workers and typical queue depths, you can comfortably handle millions of broadcast operations per second. The bottleneck is not the broadcaster—it's the network I/O to clients.

**Lock contention**: With 64-bucket sharding, contention stays bounded even at millions of connections. The registry becomes a non-bottleneck—reading and writing connections is fast enough that it's never the limiting factor.

---

# The Architecture Pieces

The system breaks into five straightforward components:

**Session Registry** (in-memory, sharded)
- Keeps track of which connections belong to each session
- Sharded to reduce lock contention
- No persistence, no synchronization needed

**Message Bus** (Redis Pub/Sub)
- Single source of truth for published messages
- Every broadcaster instance subscribes
- Decouples publisher from delivery

**Broadcaster**
- Receives messages from Redis
- Looks up connections for the session
- Queues send jobs to workers
- Returns immediately (non-blocking)

**Worker Pool**
- 1,000+ independent workers
- Pull jobs from queue
- Attempt to send with timeout
- Drop on timeout or queue full

**Connection Handler**
- Per-connection reader and writer
- Writer pulls from outbound queue
- Reader handles incoming WebSocket messages

That's it. No frameworks. No distributed consensus. Just straightforward patterns applied intentionally. The simplicity is the strength—complexity is the enemy of correctness at scale.

## Message Flow

```
Client → Registry (add connection)
  ↓
Redis PUBLISH chat:room-123
  ↓
Subscriber → Broadcaster.Broadcast()
  ↓
Look up connections → Queue jobs
  ↓
Return immediately
  ↓
Workers process queue (25ms timeout per send)
  ↓
WebSocket writers send to clients
```

---

# Why This Matters

I could have used an off-the-shelf solution: Socket.io, Pusher, Firebase, etc. Those work fine for small scales and you should use them if they fit your budget and constraints.

But I wanted to understand the shape. I wanted to know what the fundamentals were, where the bottlenecks lived, and how to tune them. And I wanted a system that could scale to millions without calling someone else's API or hitting someone else's rate limits.

The fanout pattern is the answer I found. It's not new—it's been used for years in production systems—but understanding it deeply taught me more than reading about it ever would. And now when I see systems struggling with broadcast latency or connection capacity, I recognize the pattern and know exactly where to look.

---

# The Core Principles

The pattern scales because of four deliberate choices:

**1. Sharding for lock-free scaling**
Instead of global locks, distribute across many independent buckets. Contention becomes O(1/M) where M is the number of shards.

**2. Bounded queues with drop semantics**
Never apply backpressure upstream. Accept that messages can be dropped under extreme load. A dropped message is better than a hung system.

**3. Non-blocking sends with timeouts**
Never wait indefinitely for a slow connection. Use timeouts so slow clients can't stall workers.

**4. Decoupled architecture**
Publisher doesn't know about subscribers. Each subscriber processes independently. No coordination protocol. No consensus. Just pub/sub.

These principles work across languages and platforms. Understand them, apply them to your specific constraints, measure the results.

The hardest part isn't implementing the code—it's having the discipline to keep it simple, to accept graceful degradation under load, and to measure what actually matters.

If you're hitting concurrency walls in a real-time system, this pattern is worth stealing.
