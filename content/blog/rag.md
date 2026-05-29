---
title: "Building a Personal RAG Chatbot in a Few Days: Learning by Engineering"
date: 2026-05-29
draft: false
description: "How I built a small personal RAG chatbot using FastAPI, PostgreSQL, and Docker as a practical engineering exercise."
tags:
  - python
  - fastapi
  - postgresql
  - docker
  - rag
  - ai
  - backend
---

# Building a Personal RAG Chatbot in a Few Days: Learning by Engineering

Recently, I built a small personal Retrieval-Augmented Generation (RAG) chatbot.

It was not a long research project.

It was not something I spent weeks architecting.

And it definitely was not built from years of prior AI engineering experience.

It was a compact engineering exercise built over a few days, mostly through reading, experimenting, and applying engineering fundamentals to a domain I had not worked in before.

That is exactly why I wanted to write about it.

This project reminded me of something I strongly believe:

> Engineering is rarely about already knowing the exact technology.  
> It is about being able to decompose unfamiliar systems fast enough to build useful solutions.

The goal was simple.

I wanted a chatbot that could answer questions using my own technical writing and project documentation instead of relying purely on generic model knowledge.

---

# The Problem

Large language models are powerful.

But they have an obvious limitation when you want domain-specific answers.

If someone asks:

**"Tell me about your backend engineering experience"**

a general model can generate something plausible.

But plausibility is not accuracy.

I wanted responses grounded in:

- My project documentation
- Technical notes
- Markdown-based writing
- Structured knowledge I control

This meant I needed retrieval.

Instead of expecting the model to already know my data, I wanted it to fetch relevant context dynamically.

That naturally led to Retrieval-Augmented Generation.

---

# Why RAG?

The obvious alternative was fine-tuning.

At first glance, that sounds attractive.

Train the model directly on your data and let it internalize your knowledge.

But for this use case, it would have introduced unnecessary complexity:

- Longer experimentation cycles
- Retraining after updates
- Higher compute cost
- Harder debugging

RAG offered something much simpler.

It separates knowledge storage from generation.

That means updating the system is as simple as updating documents and re-indexing.

No retraining required.

For a lightweight personal knowledge system, that architectural simplicity mattered.

---

# System Architecture

The system follows a simple pipeline:

```text
Markdown Documents
      ↓
Document Parser
      ↓
Chunking
      ↓
Embeddings
      ↓
PostgreSQL Storage
      ↓
Semantic Retrieval
      ↓
Prompt Construction
      ↓
LLM Response
```

Each layer has one responsibility.

This separation made iteration much easier.

If responses were weak, I could inspect retrieval.

If retrieval was weak, I could inspect chunking.

Keeping concerns isolated made debugging straightforward.

---

# Why FastAPI

Coming from Flask and Django experience, FastAPI felt like the right tool.

It provided:

- Strong request validation
- Async support
- Clean structure
- Explicit typing

A typical request model looked like:

```python
class ChatRequest(BaseModel):
    message: str
    user_hash: str
```

FastAPI also made the project easy to organize:

```text
app/
  api/
  services/
  models/
  retrieval/
  config/
```

That modularity became very useful as the system evolved.

---

# Why PostgreSQL

A common question is:

**Why not use a dedicated vector database?**

Tools like Pinecone and Weaviate are excellent.

But this project had different priorities.

I wanted:

- Low operational complexity
- Minimal infrastructure overhead
- Familiar tooling
- Easy deployment

PostgreSQL offered the right balance.

This project was about understanding retrieval mechanics, not building hyperscale search infrastructure.

It reinforced an important engineering lesson:

> The best tool is often the simplest one that solves the actual problem.

---

# The Real Challenge: Chunking

One of the most interesting lessons was how important chunking is.

At first, I tried fixed-length chunking.

It worked, but retrieval quality was inconsistent.

Why?

Because semantic meaning often spans logical sections.

Breaking content purely by character count often destroys context.

A better approach was preserving:

- Section boundaries
- Paragraph grouping
- Topic continuity

This dramatically improved retrieval quality.

It quickly became clear that many “model quality” problems are actually retrieval preparation problems.

---

# Retrieval Flow

When a user sends a query, the system follows this process:

## 1. Validate request

The API receives and normalizes the query.

## 2. Generate query embeddings

The query is converted into vector representation.

## 3. Search semantically similar chunks

PostgreSQL retrieves the closest matches.

## 4. Construct prompt context

Relevant chunks are assembled into the context window.

## 5. Generate response

The model responds using retrieved context.

Conceptually simple.

Practically, the challenge is tuning each stage well enough that the final context remains useful.

---

# Prompt Engineering

Retrieval alone is not enough.

The model still needs behavioral constraints.

My early prompts were too permissive.

That caused:

- Unsupported assumptions
- Overconfident answers
- Context stretching

The solution was stronger grounding rules:

```text
Answer only using retrieved context.
If information is unavailable, explicitly say so.
Do not fabricate details.
```

That single change noticeably improved trustworthiness.

---

# Dockerized Deployment

I wanted consistency between local development and deployment.

Docker solved that cleanly.

It provided:

- Environment reproducibility
- Dependency isolation
- Easier deployment workflows

This reduced friction significantly during iteration.

---

# Challenges I Hit

Even for a small project, several practical challenges appeared.

## Retrieval tuning

Small chunking changes produced very different behavior.

This required several iterations.

## Prompt strictness

Loose prompts made the system sound smarter than it actually was.

Tighter constraints improved reliability.

## Deployment details

Reverse proxy routing, container orchestration, and infrastructure edge cases still needed attention.

These are often the least glamorous parts of engineering, but they are what make systems usable.

---

# What This Reinforced

The biggest takeaway was not about RAG itself.

It was about engineering.

This project reminded me that learning unfamiliar domains is usually not about waiting until you feel ready.

It is about:

- Understanding system boundaries
- Breaking problems into layers
- Reading enough to move forward
- Building fast feedback loops
- Iterating quickly

I had never built a retrieval-augmented system before.

That did not matter.

The same engineering process applied.

And that is exactly what makes software engineering transferable.

---

# What’s Next

If I continue iterating on this project, I would explore:

- Hybrid search
- Reranking layers
- Streaming responses
- Conversational memory
- Retrieval benchmarking
- Better observability

There is still a lot to improve.

But as a compact engineering exercise, it achieved exactly what I wanted.

It helped me learn by building.

---

# Final Thoughts

This project was intentionally small.

It was built quickly.

It was exploratory.

And that is what made it valuable.

Sometimes the fastest way to learn an unfamiliar technical domain is not endless theory.

It is building something real.

Even if small.

This chatbot was exactly that.

A practical example of learning by engineering.

---

## Source Code

https://github.com/jeyem/personal-chatbot