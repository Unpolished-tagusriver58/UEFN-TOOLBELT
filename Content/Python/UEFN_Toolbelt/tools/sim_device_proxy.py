"""
UEFN TOOLBELT — Verse Simulation Proxies
========================================
Test Verse logic in-editor without full sessions. 
Uses the schema to mirror Verse device APIs.
"""

from __future__ import annotations
import unreal
from ..core import log_info, log_error, undo_transaction, require_selection
from ..registry import register_tool
from .. import schema_utils
from . import verse_schema

def _resolve_verse_class(actor: unreal.Actor) -> str:
    """
    Extract the specific Verse class name from a generic VerseDevice_C.
    e.g. 'hello_world_device' from a DEVICE_UAID_..._C.
    """
    cls = actor.get_class()
    name = cls.get_name()
    path = cls.get_path_name()
    
    # In UEFN, user Verse devices appear as VerseDevice_C or name_UAID..._C
    if "_Verse." in path:
        return path.split(".")[-1]
    
    # Try getting the specific Verse class if it's a VerseDevice instance
    if name == "VerseDevice_C" or "VerseDevice" in name:
        # Check for common Verse internal properties
        for p in ["verse_class", "VerseClass", "ScriptClass"]:
            try:
                v_type = actor.get_editor_property(p) 
                if v_type:
                    return str(v_type).split(".")[-1]
            except Exception:
                pass
        
        # FINAL FALLBACK: Fuzzy Match based on Actor Label
        # If the user renamed the actor to match their Verse class (default behavior)
        label = actor.get_actor_label()
        normalized = label.lower().replace(" ", "_")
        # Remove common UEFN suffixes
        normalized = normalized.split("_C_")[0].split("_UAID_")[0]
        return normalized

    return name.replace("_C", "")

@register_tool(
    name="sim_generate_proxy",
    category="Simulation",
    description="Generate a Python simulation proxy for a selected Verse device.",
    tags=["sim", "verse", "proxy", "automation"],
)
def run_generate_proxy(**kwargs) -> None:
    actors = require_selection(min_count=1)
    if not actors:
        return

    actor = actors[0]
    cls_raw = actor.get_class().get_name()
    v_cls = _resolve_verse_class(actor)
    
    log_info(f"Analyzing {actor.get_actor_label()} (Class: {v_cls})")

    # 1. Try Dynamic Verse Schema (Project-specific)
    info = verse_schema._parser.get_schema(v_cls)
    
    # 2. Try Static Reference Schema (Engine-standard)
    if not info:
        info = schema_utils.get_class_info(v_cls)
        
    if not info:
        log_error(f"Class '{v_cls}' not found in any schema.")
        log_info("Tip: Ensure your Verse code is compiled and you've run 'Sync Level Schema'.")
        return

    log_info(f"Generating Simulation Proxy for {v_cls}...")
    
    # Logic to generate actual proxy scripts will go here in next steps
    # For now, we validate that we can read the Verse properties
    props = info.get("properties", {})
    methods = info.get("methods", [])
    
    log_info(f"Found {len(props)} properties and {len(methods)} methods in schema.")


@register_tool(
    name="sim_trigger_method",
    category="Simulation",
    description="Trigger a discoverable method on a Verse device via the Python API.",
    tags=["sim", "verse", "trigger", "method"],
)
def run_trigger_method(method_name: str = "", **kwargs) -> None:
    """
    Simulates calling a Verse function by executing its Python equivalent.
    """
    actors = require_selection(min_count=1)
    if not actors or not method_name:
        return

    actor = actors[0]
    if hasattr(actor, method_name):
        log_info(f"Simulating: {actor.get_actor_label()}.{method_name}()")
        with undo_transaction(f"Sim: Trigger {method_name}"):
            try:
                getattr(actor, method_name)()
            except Exception as e:
                log_error(f"Failed to trigger {method_name}: {e}")
    else:
        log_error(f"Method '{method_name}' not found on this actor.")
