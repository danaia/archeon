# Natural Language Intent

Using plain English to generate architecture chains.

## Overview

> **🎯 PRIMARY METHOD: You describe features in your IDE chat (Windsurf, Cursor, VS Code). The AI reads `ARCHEON.arcon`, proposes chains, and implements everything. No commands to memorize.**

The **Natural Language Intent Parser** converts plain English descriptions into proposed glyph chains. This happens **automatically in your IDE** when you chat with your AI assistant.

**How It Actually Works:**

```
You (in IDE): "User needs to login with email and password"
         ↓
IDE AI reads ARCHEON.arcon rules
         ↓
Proposes: NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
         ↓
You: "Looks good"
         ↓
AI: Adds chain to .arcon + generates all code
```

**Two Ways to Use This:**

1. **💬 IDE Chat (95% of users)** - Just describe features, AI handles everything
2. **🔧 CLI `arc intent` (5% - automation)** - For scripts, CI/CD, batch operations

**This guide covers both, but most people only use #1.**

**Key Philosophy:**

> **The intent parser proposes, humans approve.**

This keeps you in control while letting you work in natural language. The AI can't hallucinate — it can only compose within the glyph taxonomy.

---

## 🚀 IDE Chat: Your Daily Workflow

> **This is how you'll actually use Archeon - through natural conversation in your IDE.**

### In Windsurf, Cursor, or VS Code

Open your IDE, start chatting with the AI assistant:

**Example 1: Simple Feature**

```
You: "User wants to register with email and password, then see their dashboard"

AI: I'll create this Archeon chain:
**Use cases for CLI:**
- **Automation**: Process requirements docs in build scripts
- **CI/CD**: Validate proposed chains in pipelines
- **Batch operations**: Generate multiple chains from specs
- **Debugging**: Test intent parsing edge cases

**For daily development, use your IDE chat instead.**

---

## How the Intent Parser Works

Regardless of whether you use IDE chat or CLI, the same parsing engine runs underneath.ister => MDL:user.create => OUT:redirect('/dashboard')

Confidence: HIGH
Reasoning:
  • Found need: register
  • Found task: submit  
  • Detected form component
  • Found outcome: dashboard redirect

Suggested error paths:
  → API:POST/register -> ERR:validation.emailTaken
  → API:POST/register -> ERR:validation.invalidEmail

Shall I proceed?

You: Yes

AI: ✓ Added chain to archeon/ARCHEON.arcon
    ✓ Generated CMP:RegisterForm → client/src/components/RegisterForm.vue
    ✓ Generated STO:Auth → client/src/stores/AuthStore.js
    ✓ Generated API:POST/register → server/src/api/routes/register.py
    ✓ Generated MDL:user → server/src/models/user.py
    ✓ Updated semantic index
    
    Done! Registration flow is ready.
```

**Example 2: Iterative Refinement**

```
You: "Add profile editing"

AI: Proposed chain:

@v1 NED:editProfile => CMP:ProfileForm => OUT:result

Confidence: MEDIUM - no API or storage detected

You: "Save to database through API"

AI: Updated chain:

@v1 NED:editProfile => CMP:ProfileForm 
    => API:PUT/profile => MDL:user.update => OUT:toast('Profile saved')

Better?

You: "Also add image upload for avatar"

AI: Final chain:

@v1 NED:editProfile => V:ProfilePage @ CMP:ProfileForm, CMP:AvatarUpload
    => TSK:submit => API:PUT/profile => MDL:user.update 
    => OUT:toast('Profile saved')

Plus upload chain:
@v1 NED:uploadAvatar => CMP:AvatarUpload => FNC:validateImage
    => API:POST/upload/avatar => OUT:display

Implementing now...
```

**No `arc` commands. Just conversation.** The AI knows the rules because it read `ARCHEON.arcon`.

### Why IDE Chat Works Better

| Traditional AI Chat | Archeon + IDE |
|---------------------|---------------|
| "Build login" → random structure | "Build login" → follows `.arcon` rules |
| Forgets architecture next session | Rules persist in `.arcon` file |
| Hallucinations common | Constrained to glyph taxonomy |
| Inconsistent across devs | Everyone follows same `.arcon` |
| No approval step | AI proposes, you approve |

---

## 🔧 CLI Alternative: `arc intent` (For Automation)

> **Most developers never use this - it's for scripts, CI/CD, and batch operations.**

If you need to work from the command line instead of IDE chat:

### Basic Command

```bash
arc intent "User needs to login with email and password"
```

Short form:

```bash
arc i "User logs in with email and password"
```

### Example Session

```bash
$ arc i "User wants to register with email and password, then see their dashboard"

╭─ Proposal 1 ─────────────────────────────────────────────────────────────────╮
│ NED:register => TSK:submit => CMP:RegisterForm => STO:Auth                   │
│     => API:POST/register => MDL:user.create => OUT:redirect('/dashboard')    │
│                                                                              │
│ Confidence: HIGH                                                             │
│ Reasoning:                                                                   │
│   • Found need: register                                                     │
│   • Found task: submit                                                       │
│   • Detected form component                                                  │
│   • Found outcome: dashboard redirect                                        │
╰──────────────────────────────────────────────────────────────────────────────╯

Suggested error paths:
  → API:POST/register -> ERR:auth.emailExists
  → API:POST/register -> ERR:validation.invalid

Action [a/e/r/s] (r): a
✓ Added chain to graph
```

## How It Works

### Processing Flow

```
Natural Language → Intent Parser → Proposed Chain → Human Approval → Knowledge Graph
```

1. **Parse** - Keywords map to glyphs
2. **Propose** - Chain generated with confidence level
3. **Approve** - You decide: approve, edit, reject, or suggest errors
4. **Add** - Approved chains written to `ARCHEON.arcon`
5. **Generate** - Run `arc gen` to create code

### Never Auto-Adds

**Important:** The intent parser **never** automatically adds chains to your knowledge graph. Every proposal requires explicit approval. This ensures you maintain architectural control.

## Keyword Mapping

The parser uses keyword dictionaries to map natural language to glyphs.

### Need Keywords (NED:)

Maps user intentions to needs:

| Keywords | Glyph | Description |
|----------|-------|-------------|
| login, log in, sign in, authenticate | `NED:login` | User wants to login |
| register, sign up, signup, create account | `NED:register` | User wants to register |
| logout, log out, sign out | `NED:logout` | User wants to logout |
| view profile, see profile | `NED:viewProfile` | User wants to see their profile |
| edit profile, update profile | `NED:editProfile` | User wants to edit profile |
| search, find | `NED:search` | User wants to search |
| browse, explore | `NED:browse` | User wants to browse |
| purchase, buy | `NED:purchase` | User wants to buy |
| checkout | `NED:checkout` | User wants to checkout |
| upload | `NED:upload` | User wants to upload |
| download | `NED:download` | User wants to download |
| share | `NED:share` | User wants to share |
| message, chat | `NED:message` | User wants to message |
| comment | `NED:comment` | User wants to comment |
| post, create | `NED:create` | User wants to create |
| delete, remove | `NED:delete` | User wants to delete |
| update | `NED:update` | User wants to update |
| reset password, forgot password | `NED:resetPassword` | User forgot password |
| change password | `NED:changePassword` | User wants new password |
| settings, configure | `NED:configure` | User wants to configure |
| dashboard | `NED:dashboard` | User wants dashboard |

### Task Keywords (TSK:)

Maps user actions to tasks:

| Keywords | Glyph | Description |
|----------|-------|-------------|
| click, tap | `TSK:click` | User clicks/taps |
| submit, enter | `TSK:submit` | User submits form |
| type, fill | `TSK:fill` | User fills input |
| select, choose | `TSK:select` | User selects option |
| drag, drop | `TSK:drag` | User drags item |
| scroll, swipe | `TSK:scroll` | User scrolls |
| toggle | `TSK:toggle` | User toggles switch |
| open, close | `TSK:open` | User opens/closes |
| confirm, accept | `TSK:confirm` | User confirms |
| cancel, dismiss, reject | `TSK:cancel` | User cancels |

### Output Keywords (OUT:)

Maps results to outputs:

| Keywords | Glyph | Description |
|----------|-------|-------------|
| show, display, render | `OUT:display` | Show content |
| redirect, navigate | `OUT:redirect` | Navigate to page |
| toast, notification, alert | `OUT:toast` | Show notification |
| message | `OUT:message` | Display message |
| error | `OUT:error` | Show error |
| success | `OUT:success` | Show success |
| loading, spinner | `OUT:loading` | Show loading |
| modal, popup | `OUT:modal` | Show modal |
| download | `OUT:download` | Trigger download |
| refresh, update | `OUT:refresh` | Refresh view |

## Pattern Matching

Beyond simple keywords, the parser uses **regex patterns** to detect components and APIs.

### Component Patterns

| Pattern | Example | Generates |
|---------|---------|-----------|
| `{name} form` | "login form" | `CMP:LoginForm` |
| `{name} button` | "submit button" | `CMP:SubmitButton` |
| `{name} modal` | "confirm modal" | `CMP:ConfirmModal` |
| `{name} dialog` | "settings dialog" | `CMP:SettingsDialog` |
| `{name} card` | "user card" | `CMP:UserCard` |
| `{name} list` | "product list" | `CMP:ProductList` |
| `{name} table` | "data table" | `CMP:DataTable` |
| `{name} page` | "dashboard page" | `V:DashboardPage` |
| `{name} view` | "profile view" | `V:ProfileView` |

**Example:**

```bash
$ arc i "User fills out registration form and clicks submit button"

# Generates:
NED:register => TSK:fill => CMP:RegistrationForm 
    => TSK:click => CMP:SubmitButton => OUT:result
```

### API Patterns

| Pattern | Example | Generates |
|---------|---------|-----------|
| `post to /path` | "post to /auth/login" | `API:POST/auth/login` |
| `get from /path` | "get from /users" | `API:GET/users` |
| `update via /path` | "update via /profile" | `API:PUT/profile` |
| `delete from /path` | "delete from /posts/123" | `API:DELETE/posts/123` |
| `call /path api` | "call /register api" | `API:POST/register` |
| `api /path` | "api /checkout" | `API:POST/checkout` |

**Example:**

```bash
$ arc i "User submits form, post to /register endpoint, then redirect to dashboard"

# Generates:
NED:register => TSK:submit => CMP:Form 
    => API:POST/register => OUT:redirect('/dashboard')
```

## Confidence Levels

Every proposal has a confidence level:

| Level | Criteria | Meaning |
|-------|----------|---------|
| **HIGH** | 3+ glyphs detected, includes NED and OUT | Strong match, high confidence |
| **MEDIUM** | 2 glyphs detected | Moderate match, review carefully |
| **LOW** | 1 glyph detected | Weak match, likely needs editing |

**Example:**

```bash
$ arc i "login"

╭─ Proposal 1 ─────────────────────────────╮
│ NED:login => OUT:result                  │
│ Confidence: LOW                          │
╰──────────────────────────────────────────╯

# LOW confidence - only detected need, no components or tasks
```

```bash
$ arc i "User logs in with email and password form, then sees dashboard"

╭─ Proposal 1 ─────────────────────────────────────────────╮
│ NED:login => CMP:LoginForm => OUT:redirect('/dashboard') │
│ Confidence: HIGH                                         │
╰──────────────────────────────────────────────────────────╯

# HIGH confidence - detected need, component, and specific outcome
```

## Auto-Suggest Errors

Use `--auto-errors` to automatically suggest error paths:

```bash
$ arc i "User logs in" --auto-errors

╭─ Proposal 1 ─────────────────────────────╮
│ NED:login => CMP:LoginForm => OUT:result │
│ Confidence: MEDIUM                       │
╰──────────────────────────────────────────╯

Suggested error paths:
  → API:POST/auth -> ERR:auth.invalidCreds
  → API:POST/auth -> ERR:auth.accountLocked
  → API:POST/auth -> ERR:auth.rateLimited
```

Error suggestions are context-aware:

| Context | Suggested Errors |
|---------|-----------------|
| auth, login, password | `ERR:auth.invalidCreds`, `ERR:auth.accountLocked`, `ERR:auth.rateLimited` |
| register, signup | `ERR:validation.emailTaken`, `ERR:validation.weakPassword`, `ERR:validation.invalidEmail` |
| api, endpoint | `ERR:system.serverError`, `ERR:system.timeout`, `ERR:system.rateLimited` |
| validation, form | `ERR:validation.malformed`, `ERR:validation.required`, `ERR:validation.invalid` |
| payment | `ERR:payment.declined`, `ERR:payment.insufficientFunds`, `ERR:payment.expired` |
| upload | `ERR:upload.tooLarge`, `ERR:upload.invalidType`, `ERR:upload.failed` |

## Parsing Requirements Documents

Parse an entire requirements document:

```bash
arc i --file requirements.md
```

### Supported Formats

The parser extracts chains from:

**1. Code Blocks:**

````markdown
```archeon
NED:login => CMP:LoginForm => API:POST/auth => OUT:redirect('/dashboard')
```
````

**2. User Stories:**

```markdown
As a user, I want to login with email and password so that I can access my account.
```

**3. Requirements:**

```markdown
- User wants to view their profile
- User should be able to edit profile information
- When user clicks save, profile should update
```

**4. Bullet Lists:**

```markdown
* Allow user to search for products
* Display search results in a grid
* User can click product to view details
```

### Example Markdown

```markdown
# User Authentication

As a user, I want to register with email and password so that I can create an account.

Requirements:
- User fills registration form
- System validates email uniqueness
- User redirects to dashboard on success
- Show error if email already exists
```

```bash
$ arc i --file requirements.md

╭─ Proposal 1 ─────────────────────────────────────────────────────╮
│ NED:register => TSK:fill => CMP:RegistrationForm                 │
│     => API:POST/register => OUT:redirect('/dashboard')            │
│ Confidence: HIGH                                                 │
│ Source: "As a user, I want to register..."                       │
╰──────────────────────────────────────────────────────────────────╯

╭─ Proposal 2 ─────────────────────────────────────────────────────╮
│ NED:register => CMP:RegistrationForm => API:POST/register        │
│     => ERR:validation.emailTaken                                  │
│ Confidence: MEDIUM                                               │
│ Source: "Show error if email already exists"                     │
╰──────────────────────────────────────────────────────────────────╯

Review all proposals? [y/n]
```

## Interactive Actions

When presented with a proposal, you have 4 options:

### [a] Approve

Accept the proposal and add to knowledge graph:

```bash
Action [a/e/r/s]: a
✓ Added to archeon/ARCHEON.arcon
```

### [e] Edit

Modify the chain using natural language or glyph notation:

```bash
Action [a/e/r/s]: e

Describe what to add or change:
> add a store for auth state

╭─ Updated Proposal ───────────────────────────────────────────────╮
│ NED:login => CMP:LoginForm => STO:Auth                           │
│     => API:POST/auth => OUT:redirect('/dashboard')               │
╰──────────────────────────────────────────────────────────────────╯

Action [a/e/r/s]: a
✓ Added to archeon/ARCHEON.arcon
```

You can edit with:
- **Natural language**: "add a store", "include API endpoint", "save to database"
- **Glyph notation**: "=> STO:Auth => API:POST/login"

### [r] Reject

Skip this proposal:

```bash
Action [a/e/r/s]: r
✗ Skipped proposal
```

### [s] Suggest Errors

View and add suggested error paths:

```bash
Action [a/e/r/s]: s

Suggested error paths:
  1. API:POST/auth -> ERR:auth.invalidCreds
  2. API:POST/auth -> ERR:auth.accountLocked
  3. API:POST/auth -> ERR:auth.rateLimited

Add which errors? (comma-separated, or 'all'): 1,3

╭─ Updated Proposal ───────────────────────────────────────────────╮
│ NED:login => CMP:LoginForm => API:POST/auth                      │
│     => OUT:redirect('/dashboard')                                │
│                                                                  │
│ Error paths:                                                     │
│ API:POST/auth -> ERR:auth.invalidCreds                           │
│ API:POST/auth -> ERR:auth.rateLimited                            │
╰──────────────────────────────────────────────────────────────────╯

Action [a/e/r/s]: a
✓ Added to archeon/ARCHEON.arcon
```

## Chain Extension

Extend an existing chain using natural language:

```bash
# Original chain (already in graph)
NED:login => CMP:LoginForm => OUT:result

# Extend it
$ arc i "add auth store and API endpoint to login chain"

╭─ Extended Chain ─────────────────────────────────────────────────╮
│ NED:login => CMP:LoginForm => STO:Auth                           │
│     => API:POST/login => OUT:result                              │
│ Reasoning:                                                       │
│   • Starting from: NED:login => CMP:LoginForm => OUT:result      │
│   • Adding store: STO:Auth                                       │
│   • Adding API endpoint: API:POST/login                          │
╰──────────────────────────────────────────────────────────────────╯
```

Extension keywords:

| Keyword | Action | Example |
|---For IDE Chat (Recommended)

**Be Specific**

❌ **Too vague:**
```
You: "user does stuff"
```

✅ **Specific:**
```
You: "user logs in with email and password, then sees dashboard"
```

**Include Outcomes**

❌ **No outcome:**
```
You: "user fills login form"
```

✅ **With outcome:**
```
You: "user fills login form and submits, then redirects to dashboard"
```

**Use Domain Language**

❌ **Generic:**
```
You: "user clicks thing"
```

✅ **Domain-specific:**
```
You: "user selects product and adds to cart"
```

**Start with Needs**

❌ **Implementation-first:**
```
You: "create a form component"
```

✅ **Need-first:**
```
You: "user needs to register with email and password"
```

**Describe Complete User Journeys**

✅ **Complete flow:**
```
You: "user searches for product, views results, clicks product to see details, adds to cart"
```

AI generates:
```
NED:search => TSK:submit => CMP:SearchForm 
    => OUT:display => CMP:ProductGrid 
    => TSK:click => V:ProductDetailPage 
    => TSK:click => STO:Cart => OUT:toast('Added to cart')
```

### For CLI Users----|---------|
| store, state, persist | Add `STO:` glyph | "add auth store" |
| api, endpoint, backend | Add `API:` glyph | "add API endpoint" |
| database, model, db | Add `MDL:` glyph | "save to database" |
| function, helper, validate | Add `FNC:` glyph | "add validation function" |
| event, emit, publish | Add `EVT:` glyph | "emit event" |
| redirect, navigate | Update `OUT:` glyph | "redirect to dashboard" |

## Best Practices

### Be Specific

❌ **Too vague:**
```bash
arc i "user does stuff"
```

✅ **Specific:**
```bash
arc i "user logs in with email and password, then sees dashboard"
```

### Include Outcomes

❌ **No outcome:**
```bash
arc i "user fills login form"
```

✅ **With outcome:**
```bash
arc i "user fills login form and submits, then redirects to dashboard"
```

### Use Domain Language

❌ **Generic:**
```bash
arc i "user clicks thing"
```

✅ **Domain-specific:**
```bash
arc i "user selects product and adds to cart"
```

### Start with Needs

❌ **Implementation-first:**
```bash
arc i "create a form component"
```

✅ **Need-first:**
```bash
arc i "user needs to register with email and password"
```

### Describe User Journeys

✅ **Complete flow:**
```bash
arc i "user searches for product, views results, clicks product to see details, adds to cart"
```

This generates:
```
NED:search => TSK:submit => CMP:SearchForm 
    => OUT:display => CMP:ProductGrid 
    => TSK:click => V:ProductDetailPage 
    => TSK:click => STO:Cart => OUT:toast('Added to cart')
```

## Advanced Examples

### E-commerce Checkout

```bash
arc i "User wants to checkout their cart. They review items, enter shipping address, \
enter payment details, and complete purchase. Show confirmation page on success."
```

Generates:
```
NED:checkout => V:CheckoutPage @ CMP:CartReview, CMP:ShippingForm, CMP:PaymentForm
    => TSK:submit => API:POST/checkout => MDL:order.create 
    => OUT:redirect('/order/confirmation')
```

### Social Media Post

```bash
arc i "User creates a post with text and image. Post saves to database, \
publishes to feed, and notifies followers."
```

Generates:
```
NED:create => CMP:PostEditor => STO:Posts 
    => API:POST/posts => MDL:post.create 
    => EVT:post.published => EVT:notify.followers 
    => OUT:redirect('/feed')
```

### File Upload

```bash
arc i "User uploads profile photo. Validate file type and size. \
Show progress spinner. Update profile picture on success." --auto-errors
```

Generates:
```
NED:upload => CMP:FileUploader => FNC:validateFile 
    => OUT:loading => API:POST/upload 
    => MDL:user.updatePhoto => OUT:success('Photo updated')

# Suggested errors:
API:POST/upload -> ERR:upload.tooLarge
API:POST/upload -> ERR:upload.invalidType
API:POST/upload -> ERR:upload.failed
```

## Workflow Integration

### 1. Requirements → Chains

```bash
# Convert requirements doc to chains
arc i --file requirements.md > proposed-chains.txt

# Review and approve each one
arc i --file requirements.md
```

### 2. Iterative Refinement

```bash
# Start with high-level intent
arc i "user manages their profile"

# Refine by editing
# [e] "user can view and edit profile fields, save changes to database"

# Add error handling
# [s] Select validation errors
```

### 3. Chain First, Code Second

```bash
# Define architecture first
arc i "user authentication flow with email and password"

# Approve chain
# [a]

# Generate code
arc gen
```

## Limitations

### What the Parser Can Do

✅ Map common keywords to glyphs  
✅ Detect component and API patterns  
✅ Suggest logical chain order  
✅ Recommend error paths  
✅ Parse requirements documents  

### What the Parser Cannot Do

❌ Understand complex business logic  
❌ Infer non-standard component names  
❌ Detect all edge cases  
❌ Generate perfect chains every time  

**That's why human approval is required.** The parser is a **proposal engine**, not an autonomous decision maker.

## Troubleshooting

### In IDE Chat

**Problem:** AI proposes wrong chain structure.

**Solution:** Provide more detail in your description:

```
Instead of:  "login"
Try:         "user logs in with email and password form, then sees dashboard"
```

**Problem:** AI missed a component you need.

**Solution:** Just tell it:

```
You: "Also add a loading spinner while authenticating"

AI: Updated chain with OUT:loading state
```

**Problem:** Want to use custom component name.

**Solution:** Be explicit:

```
You: "Use ProfileEditor instead of ProfileForm"

AI: Updated: CMP:ProfileEditor
```

### CLI Troubleshooting

**Low Confidence Proposals**

Parser only detects 1-2 glyphs.

**Solution:** Add more detail:

```bash
# Instead of:
arc i "login"

# Try:
arc i "user logs in with email and password form, then sees dashboard"
```

**No Proposals Generated**

Parser didn't recognize any keywords.

**Solution:** Use explicit glyph notation:

```bash
arc parse "NED:customFlow => CMP:CustomComponent => OUT:result"
```

**Wrong Component Names**

Parser generated `CMP:UserForm` but you want `CMP:ProfileForm`.

**Solution:** Use [e]dit action:

```bash
Action [a/e/r/s]: e
> change UserForm to ProfileForm
```

---

## The Reality: You'll Mostly Use Your IDE

**95% of your Archeon usage looks like this:**

```
Open Windsurf/Cursor/VS Code
→ Chat with AI: "Build X feature"  
→ AI: "Here's the chain, approve?"
→ You: "Yes"
→ Done
```

**The other 5%:**
- Running `arc validate` in CI/CD
- Batch processing requirements docs
- Debugging specific edge cases

**That's it.** No complex CLI syntax to memorize. Just natural conversation with your IDE's AI, guided by the rules in `ARCHEON.arcon`.

## Next Steps

- 📖 [Knowledge Graph](Knowledge-Graph) - How `.arcon` guides your IDE AI
- 🔤 [Glyph Reference](Glyph-Reference) - Learn all glyph types
- 🔗 [Chain Syntax](Chain-Syntax) - Master chain composition
- 💻 [CLI Commands](CLI-Commands) - CLI reference (for automation)
