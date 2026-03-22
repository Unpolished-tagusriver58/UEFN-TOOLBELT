# 🧩 UEFN Technical Quirks & "Deep Lore"

This document records the non-obvious, often undocumented behaviors of the UEFN Python and Verse APIs discovered during the development of the Toolbelt.

---

## 1. The "Invisiblity" of Verse Classes (Breakthrough: Phase 19)

### The Problem
When a Verse device is placed in a level, the UEFN Python API (`actor.get_class()`) often identifies it only as a generic **`VerseDevice_C`**. The link to the user's specific script (e.g., `hello_world_device`) is frequently hidden from `dir()` and `get_editor_property()`.

### The "Named Auto-Link" Solution
The Toolbelt implements a fuzzy resolution fallback. If the API returns a generic class, the tool normalizes the **Actor Label** (e.g., `"hello world device"` -> `"hello_world_device"`) and matches it against the project's Verse schema (`.digest` files). 
**Takeaway**: Keeping your Outliner labels consistent with your Verse class names is the key to robust Python automation.

---

## 2. The "Main Thread Lock" 

### The Problem
UEFN runs the Python interpreter on the same thread as the editor's main render loop. Using `time.sleep()` or long synchronous loops will **freeze the entire editor**.

### The "Ghost File" Quirk
If you trigger an engine action that takes time (like saving a file or taking a high-res screenshot), you **cannot** wait for that file's existence in the same Python block. Unreal needs to "tick" to actually write the file, but it cannot tick because Python is still blocking the thread.
**Takeaway**: Trigger the action and exit. Use a UI callback or a later execution block to verify the result.

---

## 3. Circular Imports in Tool Registration

### The Problem
Adding diagnostic or helper tools that need to call the main `registry` or `core` can easily trigger circular imports because `tools/__init__.py` imports everything.

### The Solution: `diagnostics.py` Pattern
Keep diagnostic tools in a separate file (`diagnostics.py`) and import them directly in the top-level `__init__.py` rather than the `tools/` subpackage. This decouples the "Health and Debug" layer from the "Operational" layer.

---

## 4. `inspect.getmembers()` SystemError

### The Problem
Running `inspect.getmembers()` on certain `unreal.*` objects (especially Blueprints or Verse devices) can trigger a `SystemError: error return without exception set` within the Python C-API. This is likely due to a malformed `getattr` implementation on the engine side.

### The Solution
Use a safe combination of `dir(obj)` and a `try-except` wrapped `getattr(obj, name)` for all property audits.

---

## 5. Asset Registry Path Sensitivity

### The Problem
Searching for assets in `/Game` works for standard content, but project-specific Verse assets often live in a virtual path like `/ProjectName/_Verse`.

### The Solution
Always audit the **Asset Registry** using a recursive filter on the project root package (e.g., `/TOOL_TEST`) to find the true `VerseClass` assets.
