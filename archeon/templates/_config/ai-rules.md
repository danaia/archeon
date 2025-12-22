# Archeon AI Rules
# This file contains the shared rules for all AI assistants (Copilot, Cursor, Cline, Windsurf, Aider, etc.)
# These rules are injected into IDE-specific configuration files during `arc ai-setup`

## Archeon Architecture System

This project uses Archeon, a glyph-based architecture notation system.

### 🚨 CRITICAL: NEVER WRITE CODE WITHOUT UPDATING ARCHEON FILES

**BEFORE writing ANY new file, you MUST:**
1. ✅ Add the glyph chain to `archeon/ARCHEON.arcon`
2. ✅ Write the code file(s)
3. ✅ Update `archeon/ARCHEON.index.json` with the new file entry
4. ✅ Run `arc validate` to verify

**These steps are NOT optional. Code without glyphs is architectural drift. Every single file must be tracked.**

### ⚠️ MANDATORY: Glyph-Code-Index-Test Workflow

**Every feature MUST follow this exact workflow — NO EXCEPTIONS:**

1. **ADD GLYPH CHAIN** → Write the chain to `archeon/ARCHEON.arcon`
   ```
   @v1 NED:feature => CMP:Component => STO:Store => API:POST/path => OUT:success
   ```

2. **WRITE CODE** → Implement the code for each glyph in the chain

3. **UPDATE INDEX** → Add entry to `archeon/ARCHEON.index.json` for each new file
   ```json
   "CMP:Component": {
     "file": "client/src/components/Component.vue",
     "intent": "Description",
     "chain": "@v1",
     "sections": ["imports", "props_and_state", "handlers", "render"]
   }
   ```

4. **RUN VALIDATE** → Execute `arc validate` to test architecture
   ```bash
   arc validate
   ```

**If you skip steps 1, 3, or 4, you have violated Archeon principles. Never skip these steps.**

### Critical Files - READ FIRST
- `archeon/ARCHEON.arcon` - The knowledge graph defining all features
- `archeon/ARCHEON.index.json` - Semantic index mapping glyphs to files/sections
- `archeon/AI_README.md` - **Provisioning guide** (how to create new projects)
- `.archeonrc` - Project configuration (frontend, backend, paths)

### Creating New Projects
If the user asks to create a new application (React, Vue, etc.), read `archeon/AI_README.md` for shell commands:
```bash
mkdir project-name && cd project-name
arc init --frontend vue3  # or react (default)
arc ai-setup
```

### Glyph Notation
Features are defined as chains:
```
NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => MDL:user => OUT:dashboard
```

| Glyph | Meaning |
|-------|---------|
| `NED:` | User need/motivation |
| `TSK:` | User task/action |
| `CMP:` | UI Component |
| `STO:` | State store |
| `API:` | HTTP endpoint |
| `MDL:` | Data model (API schemas + database) |
| `FNC:` | Utility function |
| `EVT:` | Event handler |
| `OUT:` | Success outcome |
| `ERR:` | Error path |

### Edge Types
- `=>` Structural flow (no cycles)
- `~>` Reactive subscription (cycles OK)
- `->` Control/branching
- `::` Containment

### The Complete Workflow (REQUIRED)

**Step 1: Add Glyph Chain**
```bash
arc parse "NED:feature => CMP:Component => STO:Store => API:POST/path => MDL:model => OUT:result"
```
Or write directly to `archeon/ARCHEON.arcon`.

**Step 2: Implement Code**
Write code for each glyph in the chain.

**Step 3: Validate Architecture**
```bash
arc validate
```
This checks:
- All glyphs have corresponding code
- No boundary violations (CMP cannot access MDL)
- No cycles in structural edges
- API endpoints have error handlers

**Step 4: Run Tests**
```bash
cd client && npm test      # Frontend
cd server && pytest        # Backend
```

### Writing Glyph Chains
You CAN and SHOULD write glyph chains directly to `archeon/ARCHEON.arcon`.

**Chain Format:**
```
@v1 NED:feature => CMP:Component => STO:Store => API:METHOD/path => MDL:model => OUT:result
```

**Writing Rules:**
1. Add new chains under `# === AGENT CHAINS ===` section
2. Use incremental version tags: if `@v1 NED:login` exists, next version is `@v2 NED:login`
3. Chains must start with `NED:` or `TSK:` and end with `OUT:` or `ERR:`
4. Use PascalCase for components/stores: `CMP:LoginForm`, `STO:AuthStore`
5. Use METHOD/path for APIs: `API:POST/auth/login`, `API:GET/users/{id}`
6. Add comments above chains to describe the feature

**Example - Adding a new feature:**
```
# User registration with email verification
@v1 NED:register => CMP:RegisterForm => STO:Auth => API:POST/auth/register => MDL:user => EVT:sendVerificationEmail => OUT:checkEmail
```

### Hard Rules
1. **🚨 ALWAYS add chains to ARCHEON.arcon BEFORE writing code** - No code without a glyph chain
2. **🚨 ALWAYS update ARCHEON.index.json AFTER creating files** - Every file must be indexed
3. **Always read ARCHEON.arcon first** before generating any code
4. **Always read ARCHEON.index.json** before generating any code for context
5. **You can and MUST add chains** - write new chains following the format above
6. **Never invent architecture outside the graph** - add the chain first, then implement
7. **Respect layer boundaries** - CMP cannot directly access MDL
8. **All features must have outcomes** - chains end with OUT: or ERR:
9. **Increment versions** - when modifying a feature, create `@v2`, `@v3`, etc.
10. **🚨 ALWAYS validate** - run `arc validate` after every code change

### ⚠️ MANDATORY: File Headers and Semantic Sections

**EVERY generated code file MUST include Archeon headers.** This enables AI-native code navigation via the semantic index.

#### File Header Format (REQUIRED at top of every file)

**Vue/HTML files:**
```vue
<!-- @archeon:file -->
<!-- @glyph CMP:LoginForm -->
<!-- @intent User login input and submission -->
<!-- @chain @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard -->
```

**JavaScript/TypeScript files:**
```javascript
// @archeon:file
// @glyph STO:Auth
// @intent Authentication state management
// @chain @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
```

**Python files:**
```python
# @archeon:file
# @glyph API:POST./auth/login
# @intent Authentication endpoint for user login
# @chain @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth/login => OUT:dashboard
```

#### Section Markers (REQUIRED to wrap code blocks)

Wrap logical code blocks in section markers:

```javascript
// @archeon:section imports
import { ref } from 'vue';
// @archeon:endsection

// @archeon:section props_and_state
const email = ref('');
// @archeon:endsection

// @archeon:section handlers
async function submit() { /* ... */ }
// @archeon:endsection
```

#### Standard Sections by Glyph Type

| Glyph | Sections |
|-------|----------|
| `CMP` | `imports`, `props_and_state`, `handlers`, `render`, `styles` |
| `STO` | `imports`, `state`, `actions`, `selectors` |
| `API` | `imports`, `models`, `endpoint`, `helpers` |
| `FNC` | `imports`, `implementation`, `helpers` |
| `EVT` | `imports`, `channels`, `handlers` |
| `MDL` | `imports`, `schema`, `methods`, `indexes` |

### ⚠️ MANDATORY: Index Updates

**You MUST update `archeon/ARCHEON.index.json` in these situations:**

1. **When creating a new file** - Add the glyph entry with file path, intent, chain, and sections
2. **When adding a new section** - If you add a function, handler, or code block that warrants a new `@archeon:section`, add that section name to the glyph's `sections` array
3. **When modifying sections** - If you rename or remove a section, update the index accordingly
4. **When changing file location** - Update the `file` path in the index

**Index Update Rules:**
- Every `@archeon:section` marker in code MUST be reflected in the index
- Section names must match exactly between code and index
- New functions/handlers that represent distinct concerns should get their own section
- The index is the AI's map to navigate the codebase - keep it accurate

**Index Format:**
```json
{
  "version": "1.0",
  "project": "ProjectName",
  "glyphs": {
    "CMP:LoginForm": {
      "file": "client/src/components/LoginForm.vue",
      "intent": "User login input and submission",
      "chain": "@v1",
      "sections": ["imports", "props_and_state", "handlers", "render"]
    }
  }
}
```

**Example - Adding a new section:**
If you add a new `validation` section to a component:
```javascript
// @archeon:section validation
function validateEmail(email) { /* ... */ }
// @archeon:endsection
```

Then update the index:
```json
"CMP:LoginForm": {
  "sections": ["imports", "props_and_state", "handlers", "render", "validation"]
}
```

**Or run:** `arc index build` to scan and rebuild automatically.

**The index MUST stay in sync with the code. Every section in code = entry in index.**

**Files without headers are INVISIBLE to Archeon.**

### Backend Route Registration (CRITICAL)
When creating API endpoints, you MUST also update `server/src/main.py`:

```python
# Import the new route module
from server.src.api.routes import auth_login

# Register the router
app.include_router(auth_login.router)
```

**Every API glyph requires:**
1. Create route file: `server/src/api/routes/{name}.py`
2. Import in `server/src/main.py`
3. Call `app.include_router(module.router)`
4. Run `arc validate`

### Commands
- `arc intent "description"` - Propose new feature from natural language
- `arc parse "chain"` - Add glyph chain directly  
- `arc gen` - Generate code from knowledge graph
- `arc status` - Show graph statistics
- `arc validate` - **Check architecture integrity (REQUIRED after every change)**
- `arc index build` - Rebuild the semantic index from file headers
