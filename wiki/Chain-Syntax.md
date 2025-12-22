# Chain Syntax

Chains are the core of Archeon. They describe complete user journeys from need to outcome, encoding both the "what" (architecture) and the "why" (intent).

## Basic Chain Structure

```
NED:need => TSK:action => CMP:component => API:endpoint => OUT:result
```

### Anatomy of a Chain

```
NED:login => TSK:submit => CMP:LoginForm => STO:Auth 
    => API:POST/auth/login => MDL:user.verify => OUT:redirect('/dashboard')
    
│   │     │  │      │  │           │  │               │        │
│   │     │  │      │  │           │  │               │        └─ Argument
│   │     │  │      │  │           │  │               └─ Action verb
│   │     │  │      │  │           │  └─ Qualified name
│   │     │  │      │  │           └─ Glyph type
│   │     │  │      │  └─ Operator (flow)
│   │     │  │      └─ Qualified name
│   │     │  └─ Glyph type
│   │     └─ Operator (flow)
│   └─ Task verb
└─ Need domain
```

## Operators

### `=>` Flow (Sequence)

Represents **data flow** or **control flow** from left to right:

```
CMP:SearchBar => API:GET/search => STO:Results => CMP:ResultsList
```

**Meaning:** SearchBar triggers API call, results populate store, store updates ResultsList.

---

### `->` Branch (Error Path)

Represents an **alternative path** taken on error:

```
API:POST/auth/login -> ERR:auth.invalidCredentials => OUT:toast('Login failed')
```

**Meaning:** If login fails, show error toast.

**Multiple Error Paths:**
```
API:POST/payment 
    -> ERR:payment.declined => OUT:modal('Card Declined')
    -> ERR:payment.timeout => OUT:toast('Network error')
    -> ERR:validation.invalid => OUT:focus('#cardNumber')
```

---

### `~>` Reference (Reactive Dependency)

Represents a **reactive relationship** or **dependency**:

```
STO:Theme ~> CMP:Button
STO:Theme ~> CMP:Card
STO:Theme ~> CMP:Input
```

**Meaning:** When theme changes, all these components reactively update.

**Shorthand:**
```
STO:Theme ~> CMP:*
```

---

### `@` Containment

Represents **parent-child composition**:

```
V:DashboardPage @ CMP:Header, CMP:Stats, CMP:RecentActivity
```

**Meaning:** DashboardPage contains these three components.

**Nested Containment:**
```
V:Layout @ CMP:Sidebar, V:Main
V:Main @ CMP:Header, CMP:Content, CMP:Footer
```

---

### `::` System Definition

Used in the orchestrator layer to define system architecture:

```
ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent
```

This is **not used in application chains**, only in `ARCHEON.arcon` header.

---

## Chain Patterns

### Linear Flow (Happy Path)

Simple sequence from need to outcome:

```
NED:search => TSK:query => CMP:SearchBar => API:GET/search 
    => STO:Results => CMP:ResultsList => OUT:display
```

---

### Branching (With Error Handling)

Main flow with error paths:

```
NED:login => TSK:submit => CMP:LoginForm => STO:Auth 
    => API:POST/auth/login -> ERR:auth.invalid => OUT:toast('Failed')
    => MDL:user.verify 
    => OUT:redirect('/dashboard')
```

---

### Fan-Out (One-to-Many)

One action triggers multiple outcomes:

```
API:POST/order 
    => MDL:order.create
    => EVT:order.created
    => OUT:redirect('/confirmation')

EVT:order.created 
    => STO:Orders
    => CMP:OrderConfirmation
```

---

### Aggregation (Many-to-One)

Multiple sources feed one component:

```
API:GET/user => STO:User
API:GET/orders => STO:Orders
API:GET/activity => STO:Activity

STO:User ~> CMP:DashboardStats
STO:Orders ~> CMP:DashboardStats
STO:Activity ~> CMP:DashboardStats
```

---

### Composition (Container + Children)

```
V:CheckoutFlow @ CMP:Cart, CMP:Shipping, CMP:Payment

NED:checkout => V:CheckoutFlow
CMP:Cart => STO:CartItems
CMP:Shipping => STO:ShippingInfo
CMP:Payment => TSK:submit => API:POST/orders => OUT:redirect('/confirmation')
```

---

## Versioning Chains

Chains can be versioned when requirements change:

### Version Syntax

```
@v1 NED:login => CMP:LoginForm => API:POST/auth => OUT:redirect
@v2 NED:login => CMP:LoginForm => API:POST/auth/v2 => OUT:modal('Welcome')
```

### Deprecation

Old versions are marked deprecated:

```
# @deprecated Replaced by @v2
@v1 NED:login => CMP:LoginForm => API:POST/auth
```

### Querying Versions

```bash
# List all versions of a chain
arc history NED:login

# Generate specific version
arc gen --version v1
```

---

## Modifiers

Add modifiers in brackets to provide hints:

```
CMP:Form[stateful] => STO:FormData
STO:Cache[persistent] => CMP:Results
API:GET/data[cached] => STO:Data
FNC:calculate[memoized] => OUT:display
```

**Common Modifiers:**
- `[stateful]` - Component has internal state
- `[pure]` - Pure/presentational component
- `[async]` - Handles async operations
- `[persistent]` - Persists to storage
- `[cached]` - Uses cache
- `[memoized]` - Memoized function

---

## Qualified Names

Use dot-notation for namespacing:

```
FNC:auth.validatePassword
FNC:auth.hashPassword
FNC:cart.calculateTotal
FNC:cart.applyDiscount

MDL:user.create
MDL:user.findById
MDL:user.updatePassword
```

**Benefits:**
- Organizes related glyphs
- Prevents naming conflicts
- Maps to file structure

---

## Arguments

Some glyphs accept arguments:

### OUT Arguments

```
OUT:redirect('/dashboard')
OUT:toast('Saved successfully', 'success')
OUT:modal('Confirm Delete', { confirmText: 'Delete' })
OUT:download('report.pdf', 'application/pdf')
OUT:focus('#emailInput')
```

### Error + Outcome

```
ERR:validation.required => OUT:focus('#email')
ERR:auth.expired => OUT:redirect('/login')
```

---

## Comments

Add context to chains:

```
# User authentication flow
@v1 NED:login => TSK:submit => CMP:LoginForm => STO:Auth
    => API:POST/auth/login => MDL:user.verify 
    => OUT:redirect('/dashboard')

# Alternative for OAuth
@v2 NED:login => CMP:OAuthButton => API:GET/auth/google
    => STO:Auth => OUT:redirect('/dashboard')
```

---

## Multi-Line Chains

For readability, break long chains across lines:

```
NED:checkout 
    => TSK:submit 
    => CMP:CheckoutForm 
    => FNC:cart.validateItems -> ERR:cart.empty => OUT:toast('Cart is empty')
    => FNC:cart.calculateTotal
    => API:POST/orders -> ERR:payment.declined => OUT:modal('Payment Failed')
    => MDL:order.create
    => EVT:order.created
    => OUT:redirect('/confirmation')
```

**Rules:**
- Indent continuation lines
- One operator per line (recommended)
- Error branches on separate lines

---

## Sections in ARCHEON.arcon

Organize chains into sections:

```
# === USER AUTHENTICATION ===
@v1 NED:login => TSK:submit => CMP:LoginForm => OUT:redirect
@v1 NED:register => TSK:submit => CMP:RegisterForm => OUT:redirect
@v1 NED:resetPassword => TSK:submit => CMP:PasswordResetForm => OUT:toast

# === PRODUCT CATALOG ===
@v1 NED:search => TSK:query => CMP:SearchBar => API:GET/search => OUT:display
@v1 NED:filter => TSK:select => CMP:FilterPanel => STO:Filters => OUT:update
```

---

## Validation Rules

Archeon validates chains automatically:

### Required Elements

✅ **Valid:**
```
NED:login => CMP:Form => OUT:redirect
```

❌ **Invalid - No outcome:**
```
NED:login => CMP:Form
```

---

### Boundary Violations

❌ **Invalid - Frontend to backend direct:**
```
CMP:Form => MDL:user.create
```

✅ **Valid - Through API:**
```
CMP:Form => API:POST/users => MDL:user.create
```

---

### Circular Dependencies

❌ **Invalid:**
```
CMP:A => STO:Data => CMP:B => STO:Data  # Circular
```

---

### Orphaned Glyphs

❌ **Invalid:**
```
NED:login => CMP:Form
# LoginForm exists but no chain shows what it does
```

Run `arc validate` to check for issues.

---

## Best Practices

### 1. Start with Needs

Every chain should start with `NED:` or be a sub-chain of one:

```
NED:editProfile => V:ProfilePage
V:ProfilePage @ CMP:AvatarUpload, CMP:InfoForm
CMP:InfoForm => TSK:submit => API:PUT/user => OUT:toast
```

### 2. Always Include Outcomes

Users must see results:

```
API:POST/save => OUT:toast('Saved')  # Good
API:POST/save => MDL:data.save        # Bad - no feedback
```

### 3. Handle Errors

Anticipate failure modes:

```
API:POST/order 
    -> ERR:payment.declined => OUT:modal('Payment Failed')
    -> ERR:inventory.outOfStock => OUT:toast('Out of stock')
    -> ERR:network.timeout => OUT:toast('Network error')
    => OUT:redirect('/confirmation')
```

### 4. Use Meaningful Names

```
# Good
NED:purchaseProduct
CMP:ProductCard
API:POST/orders

# Bad
NED:thing
CMP:comp1
API:POST/do
```

### 5. Group Related Chains

```
# === SHOPPING CART ===
@v1 NED:addToCart => ...
@v1 NED:removeFromCart => ...
@v1 NED:updateQuantity => ...
```

---

## Examples

### Complete Authentication System

```
# === AUTHENTICATION ===

# Login
@v1 NED:login => TSK:submit => CMP:LoginForm => STO:Auth
    => API:POST/auth/login -> ERR:auth.invalidCredentials => OUT:toast('Failed')
    => MDL:user.verify
    => OUT:redirect('/dashboard')

# Register
@v1 NED:register => TSK:submit => CMP:RegisterForm
    => FNC:auth.validatePassword -> ERR:validation.weak => OUT:focus('#password')
    => API:POST/users -> ERR:auth.emailExists => OUT:toast('Email taken')
    => MDL:user.create
    => STO:Auth
    => OUT:redirect('/welcome')

# Logout
@v1 NED:logout => TSK:click => STO:Auth.clear
    => API:POST/auth/logout
    => OUT:redirect('/login')

# Password Reset
@v1 NED:resetPassword => TSK:submit => CMP:PasswordResetForm
    => API:POST/auth/reset -> ERR:auth.emailNotFound => OUT:toast('Email not found')
    => OUT:toast('Reset link sent')
```

---

## Next Steps

- 🔤 [Glyph Reference](Glyph-Reference) - Detailed glyph documentation
- 💻 [CLI Commands](CLI-Commands) - Parse and generate from chains
- 🏗️ [Architecture](Architecture) - System design principles
