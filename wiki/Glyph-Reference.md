# Glyph Reference

Archeon uses a **closed vocabulary** of 16 glyph types. Each glyph represents a specific architectural concern and follows strict rules about what it can connect to.

## Glyph Taxonomy

### Meta Layer (User Experience)

These glyphs represent the user's perspective and observable outcomes.

#### NED (Need)

**Purpose:** User need or goal  
**Semantic:** What the user wants to accomplish  
**Usage:** Always starts a chain

```
NED:login
NED:register
NED:search
NED:checkout
NED:profile
```

**Rules:**
- Must be first in a chain
- Flows to → `TSK`, `CMP`, `V`
- Cannot be terminal

**Examples:**
```
NED:login => TSK:submit => CMP:LoginForm
NED:search => TSK:query => CMP:SearchBar
NED:checkout => V:CheckoutFlow
```

---

#### TSK (Task)

**Purpose:** Specific user action  
**Semantic:** What the user does  
**Usage:** Bridges needs to implementation

```
TSK:submit
TSK:click
TSK:select
TSK:upload
TSK:edit
```

**Rules:**
- Flows from → `NED`, `CMP`, `V`
- Flows to → `CMP`, `STO`, `API`, `FNC`
- Can be repeated in a chain

**Examples:**
```
NED:login => TSK:submit => CMP:LoginForm
CMP:FileUploader => TSK:upload => API:POST/files
```

---

#### OUT (Outcome)

**Purpose:** Observable result  
**Semantic:** What the user sees/experiences  
**Usage:** Terminal node showing success state

```
OUT:redirect('/dashboard')
OUT:toast('Saved successfully')
OUT:modal('Confirmation')
OUT:download('report.pdf')
OUT:focus('#email')
```

**Rules:**
- Must be terminal (ends a chain)
- Flows from → Any glyph
- Takes arguments in parentheses

**Examples:**
```
API:POST/auth/login => OUT:redirect('/dashboard')
FNC:generateReport => OUT:download('report.pdf')
```

---

#### ERR (Error)

**Purpose:** Error state with user affordance  
**Semantic:** What happens when something fails  
**Usage:** Terminal node showing failure state

```
ERR:auth.invalidCredentials
ERR:validation.required
ERR:network.timeout
ERR:auth.sessionExpired
ERR:permission.denied
```

**Rules:**
- Must be terminal
- Uses dot-notation for namespacing
- Flows from → `API`, `FNC`, `MDL`
- Connects to → `OUT` for user feedback

**Examples:**
```
API:POST/auth/login -> ERR:auth.invalidCredentials => OUT:toast('Invalid password')
FNC:processPayment -> ERR:payment.declined => OUT:modal('Payment Failed')
```

---

### View Layer (Structure)

#### V (View/Container)

**Purpose:** Structural component (layout, page, section)  
**Semantic:** Containers that hold other components  
**Usage:** Composition and routing

```
V:DashboardPage
V:CheckoutFlow
V:Sidebar
V:Modal
V:Layout
```

**Rules:**
- Can contain → `CMP`, other `V` glyphs
- Uses `@` syntax for containment
- Flows from → `NED`, `OUT`

**Examples:**
```
V:DashboardPage @ CMP:Header, CMP:Stats, CMP:ActivityFeed
V:CheckoutFlow @ CMP:Cart, CMP:Shipping, CMP:Payment
```

---

### Frontend Layer

#### CMP (Component)

**Purpose:** Interactive UI component  
**Semantic:** Reusable interface elements  
**Usage:** Forms, buttons, inputs, displays

```
CMP:LoginForm
CMP:SearchBar
CMP:UserCard
CMP:DataTable
CMP:FileUploader
```

**Modifiers:**
- `[stateful]` - Has local state
- `[pure]` - Pure/presentational
- `[async]` - Handles async operations

**Rules:**
- Flows from → `NED`, `TSK`, `V`
- Flows to → `STO`, `API`, `FNC`, `OUT`
- Can emit → `TSK`

**Examples:**
```
CMP:LoginForm => STO:Auth => API:POST/auth/login
CMP:SearchBar => TSK:query => API:GET/search
CMP:UserCard[pure] => OUT:display
```

---

#### STO (Store)

**Purpose:** Client-side state management  
**Semantic:** Reactive data stores  
**Usage:** Pinia, Zustand, Redux stores

```
STO:Auth
STO:Cart
STO:User
STO:Theme
STO:Notifications
```

**Modifiers:**
- `[persistent]` - Persists to localStorage
- `[global]` - Global state
- `[scoped]` - Scoped to feature

**Rules:**
- Flows from → `CMP`, `API`, `FNC`
- Flows to → `CMP`, `API`, `OUT`
- Bidirectional with → `CMP` (reactive)

**Examples:**
```
CMP:LoginForm => STO:Auth => API:POST/auth/login
API:GET/user => STO:User => CMP:Profile
STO:Theme[persistent] ~> CMP:*
```

---

### Backend Layer

#### FNC (Function)

**Purpose:** Business logic function  
**Semantic:** Pure or utility functions  
**Usage:** Validation, transformation, utilities

```
FNC:auth.validateCredentials
FNC:cart.calculateTotal
FNC:string.slugify
FNC:date.formatRelative
```

**Rules:**
- Uses dot-notation for namespacing
- Flows from → `TSK`, `CMP`, `API`, `MDL`
- Flows to → `OUT`, `ERR`, other `FNC`
- Should be pure when possible

**Examples:**
```
CMP:PasswordInput => FNC:auth.validatePassword -> ERR:validation.weak
API:POST/products => FNC:product.sanitize => MDL:product.create
```

---

#### EVT (Event)

**Purpose:** Event handler or pub/sub channel  
**Semantic:** Asynchronous messaging  
**Usage:** WebSockets, server events, pub/sub

```
EVT:chat.message
EVT:notification.received
EVT:order.statusChanged
```

**Rules:**
- Flows from → `API`, `STO`
- Flows to → `CMP`, `STO`, `OUT`
- Uses dot-notation for channels

**Examples:**
```
EVT:chat.message => STO:Messages => CMP:ChatWindow
API:POST/order => EVT:order.created => CMP:OrderConfirmation
```

---

#### API (Endpoint)

**Purpose:** HTTP endpoint  
**Semantic:** RESTful or GraphQL API  
**Usage:** Network requests

```
API:GET/users
API:POST/auth/login
API:PUT/products/:id
API:DELETE/cart/:itemId
API:PATCH/user/profile
```

**Rules:**
- Uses HTTP method prefix
- Flows from → `CMP`, `STO`, `TSK`
- Flows to → `MDL`, `FNC`, `STO`, `OUT`, `ERR`
- Can have path parameters (`:id`)

**Examples:**
```
CMP:LoginForm => API:POST/auth/login => MDL:user.verify
API:GET/products => STO:Products => CMP:ProductList
API:PUT/user/:id => MDL:user.update => OUT:toast('Saved')
```

---

#### MDL (Model)

**Purpose:** Data model or database entity  
**Semantic:** Schema and data operations  
**Usage:** ORM models, database operations

```
MDL:user
MDL:user.create
MDL:user.verify
MDL:product.findById
MDL:order.calculateTotal
```

**Rules:**
- Uses dot-notation for methods
- Flows from → `API`, `FNC`
- Flows to → `OUT`, `ERR`, `STO`
- Represents database layer

**Examples:**
```
API:POST/users => MDL:user.create => OUT:redirect('/welcome')
API:GET/users/:id => MDL:user.findById => STO:User
FNC:auth.hash => MDL:user.updatePassword
```

---

## Edge Types

Archeon uses different operators to show relationships:

### `=>` Flow (Sequence)

Data flows from left to right:
```
CMP:Form => STO:Data => API:POST/save
```

### `->` Branch (Error Path)

Alternative path on failure:
```
API:POST/login -> ERR:auth.invalid => OUT:toast('Failed')
```

### `~>` Reference (Dependency)

Reactive or dependency relationship:
```
STO:Theme ~> CMP:Button
```

### `@` Containment

Parent contains children:
```
V:Page @ CMP:Header, CMP:Content, CMP:Footer
```

### `::` Definition

System architecture (in ARCHEON.arcon header):
```
ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent
```

---

## Boundary Rules

Certain transitions are **forbidden** to enforce separation of concerns:

❌ **Frontend → Backend Direct**
```
CMP:Form => MDL:user.create  # Wrong! Must go through API
```

✅ **Correct:**
```
CMP:Form => API:POST/users => MDL:user.create
```

❌ **Backend → Frontend Direct**
```
MDL:user => CMP:Profile  # Wrong! Must go through store
```

✅ **Correct:**
```
API:GET/user => STO:User => CMP:Profile
```

❌ **Skipping User Outcomes**
```
TSK:submit => API:POST/save  # Wrong! No observable outcome
```

✅ **Correct:**
```
TSK:submit => API:POST/save => OUT:toast('Saved')
```

---

## Qualified Names

Glyphs can have qualified names for organization:

```
FNC:auth.validatePassword
FNC:auth.hashPassword
FNC:cart.calculateTotal
FNC:cart.applyDiscount
```

Benefits:
- Namespacing prevents conflicts
- Groups related functionality
- Easier to navigate codebase

---

## Modifiers

Add modifiers in brackets:

```
CMP:Form[stateful]
STO:Cache[persistent]
API:GET/data[cached]
FNC:heavy[memoized]
```

Modifiers are hints for code generation and don't affect graph structure.

---

## Arguments

Some glyphs take arguments:

```
OUT:redirect('/dashboard')
OUT:toast('Success', 'green')
OUT:download('report.pdf', 'application/pdf')
ERR:validation.required => OUT:focus('#email')
```

---

## Next Steps

- 🔗 [Chain Syntax](Chain-Syntax) - Learn to compose glyphs
- 💻 [CLI Commands](CLI-Commands) - Generate code from glyphs
- 🎨 [Templates](Templates) - Customize glyph templates
