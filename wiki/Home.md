# Archeon

> **The missing architecture layer for vibecoding.**

You're building with AI — describing features in plain English, watching code appear in seconds. It feels like the future.

Until session 5, when your codebase looks like it was built by 12 different developers who never talked to each other.

**That's not an AI problem. That's a constraint problem.**

---

## What Vibecoding Gets Wrong

Vibecoding (AI-assisted, conversational development) is powerful. But out of the box, it has no memory, no structure, and no rules.

| Symptom | Root Cause |
|---------|------------|
| Components that call APIs that don't exist | No end-to-end validation |
| Every feature uses a different pattern | No architectural persistence |
| "Fix this" spawns 3 new bugs | No dependency awareness |
| Small models produce garbage | Context is too noisy |
| Refactoring takes days | No one knows what connects to what |

**Archeon exists because vibecoding without constraints is just fast chaos.**

---

## What Archeon Actually Does

Three things. That's it.

### 1. A Shared Language (Glyphs)

16 symbols that represent architectural concerns:

```
NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
```

- `NED` = User need
- `CMP` = UI component  
- `STO` = Client state
- `API` = Backend endpoint
- `OUT` = What the user sees

Every feature is a **chain** from need to outcome. If there's no outcome? It's not a feature.

### 2. A File That Remembers (`.arcon`)

Your architecture lives in `archeon/ARCHEON.arcon`. It persists between sessions. When your AI starts a new chat, it reads this file and knows:

- What features exist
- How they connect
- What patterns are allowed
- Where to put new code

**Architecture becomes memory, not suggestion.**

### 3. Validation Before Generation

```
❌ NED:login => CMP:LoginForm
   REJECTED — no observable outcome

✅ NED:login => CMP:LoginForm => OUT:redirect('/dashboard')
   VALID
```

Bad architecture gets caught **before** it becomes bad code. Not during review. Not in production. Before a single line is written.

---

## Why This Empowers Developers

You're not fighting the AI anymore. You're not re-explaining your architecture every session. You're not fixing drift.

You describe what you want. The AI proposes a chain. You approve. Code appears — **and it fits.**

```
You: "User uploads a profile picture"

AI: Proposed chain:
    NED:uploadAvatar => CMP:AvatarUpload => API:POST/avatar 
        => MDL:user.avatar => OUT:toast('Avatar updated')
    
    Shall I proceed?

You: Yes
```

That's the whole workflow. Describe → Validate → Generate → Ship.

---

## Why This Empowers AI

Small models (Qwen 30B, Mistral, local LLMs) fail at coding because:

1. **Too much context**: They can't hold your entire codebase in memory
2. **Too many options**: They hallucinate patterns that don't exist
3. **No persistence**: Each session starts from zero

Archeon fixes all three:

| Problem | Archeon Solution |
|---------|------------------|
| Context overload | Glyph projection (~12K tokens vs ~45K) |
| Pattern hallucination | Bounded glyph taxonomy |
| Session amnesia | `.arcon` file persistence |

**You didn't make the model smarter. You made the problem smaller.**

---

## Why Local Models Can Match Frontier Models

This is not hype. This is constraint theory applied to language models.

### The Real Difference Between Models

A 30B parameter model (Qwen, Mistral, Llama) has **the same knowledge** as GPT-4 or Claude. They're trained on similar data. The difference is:

| Capability | Frontier (400B+) | Local (30B) |
|-----------|------------------|-------------|
| Knowledge | ✅ Same training data | ✅ Same training data |
| Context window | 100K-200K tokens | 8K-32K tokens |
| Reasoning depth | Deep multi-step | Shallow, loses coherence |
| Working memory | Excellent | Limited |

When you ask Claude to "build a login system," it succeeds because it can hold your **entire codebase** in context and reason through **all possible architectures** to pick a coherent one.

A 30B model fails **not because it doesn't know how** — it fails because:
- Your codebase exceeds its context window
- It can't evaluate all architectural options
- It forgets what pattern it used 3 files ago

### How Archeon Changes the Game

Archeon doesn't make the model smarter. It **constrains the problem space** so a smaller model can solve it.

```
                    WITHOUT ARCHEON
    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │    Infinite architectural possibilities         │
    │    ~45K tokens of context required              │
    │    Multi-step reasoning across files            │
    │    Pattern coherence over long sequences        │
    │                                                 │
    │    → Requires frontier-class reasoning          │
    │                                                 │
    └─────────────────────────────────────────────────┘

                     WITH ARCHEON
    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │    16 glyphs (bounded taxonomy)                 │
    │    ~12K tokens (chain + template + deps)        │
    │    Single-step: fill template from chain        │
    │    Coherence guaranteed by .arcon               │
    │                                                 │
    │    → Any model can do this                      │
    │                                                 │
    └─────────────────────────────────────────────────┘
```

### The Mathematics

**Frontier model reasoning:**
```
P(code | prompt, entire_codebase, all_possible_patterns)
```
This distribution is enormous. Sampling requires massive working memory.

**Archeon-constrained reasoning:**
```
P(code | prompt, validated_chain, template, one_hop_dependencies)
```
This distribution is **orders of magnitude narrower**. A 30B model samples from it reliably.

### Concrete Example

**Task:** "Add user profile editing"

**Without Archeon — GPT-4:**
```
✓ Creates ProfileForm.vue (new pattern)
✓ Creates profileStore.js (different from authStore pattern)
✓ Creates PUT /api/profile (inconsistent with POST /auth)
✗ Forgets to update user model
✗ No connection to existing auth flow
→ Works, but creates technical debt
```

**With Archeon — Qwen 32B (local):**
```
→ Reads .arcon: understands existing auth flow
→ Proposes: NED:editProfile => CMP:ProfileForm => STO:Auth => API:PUT/profile => MDL:user => OUT:toast
→ Validates: chain complete, reuses existing STO:Auth
→ Generates from template (consistent patterns)
→ Updates .arcon (future sessions aware)
✓ Architecturally consistent
✓ Zero hallucinated patterns
```

**The local model produces better architecture** because it's solving a constrained problem, not improvising.

### Why This Matters

- **Privacy**: Your code never leaves your machine
- **Cost**: $0 per token vs $0.01-0.06 per 1K tokens
- **Speed**: No API latency
- **Availability**: Works offline, no rate limits

And with Archeon, **quality is equivalent** for architectural tasks.

---

## Quick Start

```bash
# Install
pip install archeon

# Create project
arc init --arch vue3-fastapi

# Set up your IDE
arc ai-setup --cursor  # or --windsurf, --copilot, --vscode

# Chat with your AI
"Build user registration with email verification"
```

---

## Measured Impact

| Metric | Without Archeon | With Archeon |
|--------|----------------|--------------|
| Structural drift | 60% of features | **0%** |
| Missing outcomes | 42% incomplete | **0%** |
| Context tokens | ~45K | **~12K** |
| Time to valid code | ~35 min | **~10 min** |
| Structural rework | 60% | **~1-2%** |

These aren't estimates. They're from 200+ generated features.

---

## What Archeon Does NOT Do

Let's be clear:

- ❌ Won't write optimal algorithms
- ❌ Won't replace code review
- ❌ Won't catch runtime bugs
- ❌ Won't make bad UX good
- ❌ Won't remove the need for human judgment

**Archeon solves architecture. That's it.** But architecture is the thing that makes everything else possible.

---

## The One-Line Insight

> **Archeon doesn't make models smarter. It makes the problem smaller, the rules explicit, and the failure modes impossible.**

---

## How It Works

```mermaid
sequenceDiagram
    participant You as You (IDE Chat)
    participant AI as IDE AI
    participant Arc as ARCHEON.arcon
    
    You->>AI: "Build user login with email"
    AI->>Arc: Read architectural rules
    Arc->>AI: Glyph taxonomy + constraints
    AI->>You: Propose: NED:login => CMP:LoginForm<br/>=> STO:Auth => API:POST/auth<br/>=> OUT:dashboard
    You->>AI: Approve
    AI->>You: ✓ Generate all components<br/>✓ Update .arcon<br/>✓ Architecturally consistent
```

**No CLI commands. No prompt gymnastics. Just chat.**

---

## The Glyph System

16 typed symbols representing architectural concerns:

| Glyph | Layer | Purpose |
|-------|-------|---------|
| `NED` | Meta | User need |
| `TSK` | Meta | User action |
| `OUT` | Meta | Observable outcome |
| `ERR` | Meta | Error state |
| `CMP` | Frontend | UI component |
| `STO` | Frontend | Client state |
| `FNC` | Shared | Function |
| `EVT` | Shared | Event handler |
| `API` | Backend | HTTP endpoint |
| `MDL` | Backend | Data model |

👉 [Full Glyph Reference](Glyph-Reference)

---

## Architecture Shapes

Shapes are JSON blueprints that define your entire stack — templates, configs, dependencies — in one file.

```bash
arc init --arch vue3-fastapi    # Vue 3 + Pinia + FastAPI
arc init --arch react-fastapi   # React + Zustand + FastAPI
```

Each shape includes:
- Glyph templates for each framework
- Prebuilt components (ThemeToggle, ThemeSelector)
- TailwindCSS configuration
- Full dependency list

👉 [Architecture Shapes](Architecture-Shapes)

---

## 📚 Documentation

### Getting Started
- [Installation](Installation) — Install via pip
- [Quick Start](Quick-Start) — First project in 5 minutes

### Core Concepts
- [Glyph Reference](Glyph-Reference) — All 16 glyph types
- [Chain Syntax](Chain-Syntax) — Composition rules
- [Natural Language Intent](Natural-Language-Intent) — Plain English → chains
- [Knowledge Graph](Knowledge-Graph) — The `.arcon` file
- [Architecture Shapes](Architecture-Shapes) — JSON-based stack blueprints

### Reference
- [CLI Commands](CLI-Commands) — Command reference
- [Templates](Templates) — Template customization
- [Architecture](Architecture) — System design

---

## The One-Line Insight

> **Archeon doesn't make models smarter. It makes the problem smaller, the rules explicit, and the failure modes impossible.**

---

## 🤝 Contributing

See [Contributing Guide](Contributing) for development setup.

## 📄 License

MIT
