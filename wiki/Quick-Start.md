# Quick Start

This guide will walk you through creating your first Archeon project in under 5 minutes.

## Prerequisites

Make sure you have Archeon installed:

```bash
# Install Archeon
git clone git@github.com:danaia/archeon.git
cd archeon
pip install -e .

# Verify
arc --version
```

If already installed, see [Installation](Installation) for details.

## Choose Your Path

Archeon offers **two distinct workflows**:

|                  | **IDE AI Rules**                 | **Architecture Shapes**                       |
| ---------------- | -------------------------------- | --------------------------------------------- |
| **Best for**     | Existing projects, minimal setup | New projects, complete scaffolding            |
| **Setup time**   | < 1 minute                       | 2-3 minutes                                   |
| **What you get** | Glyph rules for your IDE         | Full project structure + pre-built components |
| **Command**      | `arc init` + `arc ai-setup`      | `arc init --arch nextjs-express`              |

---

## Path 1: IDE AI Rules (Lightweight)

**Best for:** Existing projects or minimal scaffolding.

```bash
# Navigate to your project (or create new directory)
cd ..
mkdir my-app && cd my-app

# Initialize minimal structure
arc init

# Generate IDE rules
arc ai-setup --cursor      # For Cursor
arc ai-setup --copilot     # For GitHub Copilot
arc ai-setup               # Or all at once
```

**Now just chat with your IDE** — it reads `ARCHEON.arcon` and proposes architecture.

---

## Path 2: Architecture Shapes (Complete Scaffolding)

**Best for:** New projects wanting complete setup.

```bash
# Navigate to parent directory
cd ..

# Create project directory
mkdir my-app && cd my-app

# Initialize with a complete architecture
arc init --arch nextjs-express     # Next.js 14 + Express + TypeScript (RECOMMENDED)
arc init --arch vue3-fastapi       # Vue 3 + FastAPI + MongoDB
arc init --arch react-fastapi      # React + FastAPI + MongoDB

# Optional: Add IDE rules too
arc ai-setup
```

This creates:

```
my-app/
├── archeon/
│   └── ARCHEON.arcon           # Knowledge graph
├── client/
│   ├── src/
│   │   ├── components/
│   │   ├── stores/
│   │   └── App.vue
│   └── package.json
├── server/
│   ├── src/
│   │   ├── api/
│   │   ├── models/
│   │   └── main.py
│   └── requirements.txt
└── README.md
```

### Framework Options

**Frontend:**

- `react` - React 18 with Zustand
- `vue` - Vue 2
- `vue3` - Vue 3 with Pinia (recommended)

**Backend:**

- `fastapi` - FastAPI (recommended)
- `express` - Express.js (coming soon)

## Step 2: Define Your First Feature

Use natural language to describe what you want:

```bash
arc i "User wants to login with email and password"
```

Archeon will propose a chain:

```
╭─ Proposal 1 ─────────────────────────────────────────╮
│ NED:login => TSK:submit => CMP:LoginForm => STO:Auth │
│     => API:POST/auth/login => MDL:user.verify        │
│     => OUT:redirect('/dashboard')                    │
│                                                      │
│ Confidence: HIGH                                     │
╰──────────────────────────────────────────────────────╯

Suggested error paths:
  → API:POST/auth/login -> ERR:auth.invalidCredentials
  → API:POST/auth/login -> ERR:network.timeout

Action [a/e/r/s]:
```

**Actions:**

- `a` - Approve and add to graph
- `e` - Edit the chain
- `r` - Reject and try again
- `s` - Suggest additional error paths

Type `a` and press Enter to approve.

## Step 3: Generate Code

```bash
arc gen
```

Archeon generates all the files:

```
✓ Generated CMP:LoginForm → client/src/components/LoginForm.vue
✓ Generated STO:Auth → client/src/stores/AuthStore.js
✓ Generated API:POST/auth/login → server/src/api/routes/auth_login.py
✓ Generated MDL:user → server/src/models/user.py
```

## Step 4: Review Generated Code

Let's look at what was created:

### LoginForm.vue

```vue
<!-- @archeon:file -->
<!-- @glyph CMP:LoginForm -->
<!-- @intent User login input and submission -->

<script setup>
// @archeon:section imports
import { ref } from "vue";
import { useAuthStore } from "@/stores/AuthStore";
// @archeon:endsection

// @archeon:section props_and_state
const authStore = useAuthStore();
const email = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");
// @archeon:endsection

// @archeon:section handlers
async function handleSubmit() {
  loading.value = true;
  error.value = "";

  try {
    await authStore.login(email.value, password.value);
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
// @archeon:endsection
</script>

<template>
  <!-- @archeon:section render -->
  <div class="login-form">
    <h2>Login</h2>
    <form @submit.prevent="handleSubmit">
      <input v-model="email" type="email" placeholder="Email" required />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <button type="submit" :disabled="loading">
        {{ loading ? "Logging in..." : "Login" }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
  <!-- @archeon:endsection -->
</template>
```

### AuthStore.js (Pinia)

```javascript
// @archeon:file
// @glyph STO:Auth
// @intent Authentication state management

import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  // @archeon:section state
  const user = ref(null);
  const token = ref(localStorage.getItem("token"));
  // @archeon:endsection

  // @archeon:section actions
  async function login(email, password) {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) throw new Error("Invalid credentials");

    const data = await response.json();
    token.value = data.token;
    user.value = data.user;
    localStorage.setItem("token", data.token);

    // Navigate to dashboard
    window.location.href = "/dashboard";
  }

  function logout() {
    user.value = null;
    token.value = null;
    localStorage.removeItem("token");
  }
  // @archeon:endsection

  // @archeon:section selectors
  const isAuthenticated = computed(() => !!token.value);
  // @archeon:endsection

  return { user, token, isAuthenticated, login, logout };
});
```

## Step 5: Check Status

```bash
arc status
```

```
Knowledge Graph Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chains: 1
Glyphs: 7

Recent Chains:
  @v1 NED:login => TSK:submit => CMP:LoginForm => STO:Auth
      => API:POST/auth/login => MDL:user.verify => OUT:redirect

Generated Files: 4
Missing Files: 0
```

## Step 6: Add Error Handling

Let's add an error path:

```bash
arc parse "API:POST/auth/login -> ERR:auth.invalidCredentials => OUT:toast('Invalid email or password')"
```

Then regenerate:

```bash
arc gen
```

The error handling code will be added to the existing files.

## Next Steps

### Add More Features

```bash
# Registration
arc i "New user wants to create an account"

# Password reset
arc i "User forgot password and needs to reset it"

# Profile management
arc i "User wants to update their profile information"
```

### Customize Templates

Templates are located in `archeon/templates/`. Edit them to match your coding style:

```bash
# Edit Vue component template
vim archeon/templates/CMP/vue3.vue

# Changes take effect immediately (if installed with -e)
arc gen
```

### View the Knowledge Graph

```bash
cat archeon/ARCHEON.arcon
```

See all your chains in one place.

### Validate Architecture

```bash
arc validate
```

Checks for:

- Orphaned glyphs
- Missing error paths
- Incomplete user journeys
- Boundary violations

## Common Workflows

### From Requirements Document

```bash
arc i --file requirements.md
```

Archeon will parse the file and propose chains for each feature.

### Auto-Suggest Error Paths

```bash
arc i "User checks out their cart" --auto-errors
```

Archeon suggests common error scenarios.

### Edit a Chain

```bash
arc parse "@v1 NED:login => TSK:submit => CMP:LoginForm => STO:Auth => API:POST/auth/login => OUT:dashboard" --version v2
```

Creates version 2, deprecates version 1.

## Learn More

- 🔤 [Glyph Reference](Glyph-Reference) - All 16 glyph types explained
- 🔗 [Chain Syntax](Chain-Syntax) - Advanced chain composition
- 💻 [CLI Commands](CLI-Commands) - Complete command reference
- 🎨 [Templates](Templates) - Customize code generation
- 🏗️ [Architecture](Architecture) - System design principles
