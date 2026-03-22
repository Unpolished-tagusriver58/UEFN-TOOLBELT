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

## 6. The "Invalid Flags" Selection Warning

### The Problem
`LogActorLevelEditorSelection: Warning: SelectActor: The requested operation could not be completed because the actor has invalid flags.`
This happens when you spawn an actor (e.g., a Cube or a Teleporter) and immediately try to select it before the engine has finished registering its object flags (like `RF_Transactional`).

### The Solution
Wrap your spawning and selection in a **`ScopedEditorTransaction`**. This forces the engine to treat the operation as a single undoable unit and ensures flags are correctly updated before the transaction closes.

---

## 7. `get_editor_property` vs. `getattr()`

### The Problem
Traditional Unreal Python advice says to use `actor.get_editor_property("PropertyName")`. However, for many Verse-driven properties, this will raise an `Exception` because the properties aren't technically marked as "Editor Properties" in the C++ sense.

### The Solution
Use **`getattr(actor, "PropertyName")`** or `dir(actor)` first. Many Verse properties are reflected into the Python object's dictionary even if they aren't part of the formal Editor Property system.

---

## 8. Virtual Packaging: The `_Verse` Folder

### The Problem
Verse code doesn't live in the standard `/Game/` path. It lives in a virtual project-specific package like `/YourProjectName/_Verse`.

### The Solution
When using the `AssetRegistry`, always search specifically in the project root. The `_Verse` folder is where you'll find the `VerseClass` definitions and "task" objects (like `on_begin` callbacks).

---

## 9. The "Ghost" Subsystem Quirk

### The Problem
Some subsystems like `EditorActorSubsystem` can return `None` if accessed too early in the `init_unreal.py` startup sequence.

### The Solution
Use `unreal.get_editor_subsystem(unreal.EditorActorSubsystem)` as a late-initialization call inside your tool's function, rather than storing it as a global module-level variable.

---

## 10. Dashboard v2: The `_title` Signature Bug

### The Problem
When migrating large dashboard classes to a dynamic **`builder()`** pattern, a subtle `NameError` can occur if the internal helper functions (like `_build_header`) attempt to access `self._title` before it is defined by the builder context. 

### The Solution
Ensure your dashboard builder pattern explicitly passes the **`title`** variable into the component builders, rather than relying on class state. The Toolbelt now uses a `builder(R, title)` pattern to avoid this initialization race condition.

---

## 11. Deprecation: `EditorLevelLibrary` vs. `EditorActorSubsystem`

### The Problem
Many UEFN tutorials from 2024-2025 use `unreal.EditorLevelLibrary.get_selected_level_actors()`. In the 2026 update, this is often marked as legacy or behaves inconsistently with Verse actors.

### The Solution
Always migrate to **`unreal.EditorActorSubsystem`**. It provides better world-context awareness and handles the "Dirty State" and "Undo Transactions" more reliably for Verse-backed devices.
