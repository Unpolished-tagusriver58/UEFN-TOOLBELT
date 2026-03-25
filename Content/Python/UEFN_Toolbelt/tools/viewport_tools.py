"""
UEFN TOOLBELT — Viewport Navigation Tools
========================================
Teleport the viewport camera to any world coordinate or actor instantly.

The UEFN assistant will tell you: "you cannot jump to coordinates directly,
place a temp prop, press F…" — these tools do it in one command.

Use cases:
  • Jump to a known spawn coordinate after placing something programmatically
  • Focus on a named actor by label
  • Return to a saved camera position
  • Quickly orbit between key locations in a large map
"""

from __future__ import annotations

import unreal
from ..registry import register_tool
from ..core import log_info, log_error, log_warning


def _get_camera() -> tuple:
    """Return (location, rotation) of the current viewport camera."""
    return unreal.EditorLevelLibrary.get_level_viewport_camera_info()


def _set_camera(location: unreal.Vector, rotation: unreal.Rotator) -> None:
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(location, rotation)


# ── Tools ──────────────────────────────────────────────────────────────────────

@register_tool(
    name="viewport_goto",
    category="Viewport",
    description=(
        "Instantly move the viewport camera to any world coordinate. "
        "One command replaces the UEFN 'place a temp prop + press F' workaround."
    ),
    tags=["viewport", "camera", "navigate", "goto", "coordinates", "teleport"],
)
def run_viewport_goto(
    x: float = 0.0,
    y: float = 0.0,
    z: float = 500.0,
    pitch: float = -20.0,
    yaw: float = 0.0,
    **kwargs,
) -> dict:
    """
    Teleport the viewport camera to the given world coordinates.

    Args:
        x:     World X coordinate (default 0)
        y:     World Y coordinate (default 0)
        z:     World Z coordinate (default 500 — slightly above ground)
        pitch: Camera pitch angle in degrees (default -20 — looking slightly down)
        yaw:   Camera yaw (compass heading) in degrees (default 0 — facing +X)
    """
    try:
        loc = unreal.Vector(x, y, z)
        rot = unreal.Rotator(pitch, yaw, 0)
        _set_camera(loc, rot)
        log_info(f"viewport_goto: camera moved to ({x}, {y}, {z}) pitch={pitch} yaw={yaw}")
        return {
            "status": "ok",
            "location": [x, y, z],
            "rotation": {"pitch": pitch, "yaw": yaw},
        }
    except Exception as e:
        log_error(f"viewport_goto failed: {e}")
        return {"status": "error", "error": str(e)}


@register_tool(
    name="viewport_focus_actor",
    category="Viewport",
    description=(
        "Select and focus the viewport camera on any actor by name. "
        "Partial label match supported — e.g. 'Cube' finds 'SM_Cube_001'."
    ),
    tags=["viewport", "camera", "focus", "actor", "select", "navigate"],
)
def run_viewport_focus_actor(
    label: str = "",
    **kwargs,
) -> dict:
    """
    Find an actor by label (partial match), select it, and move the camera to it.
    Uses UEFN's native 'Move Camera to Object' viewport command — no roll corruption.

    Args:
        label: Partial actor label to search for (case-insensitive)
    """
    if not label:
        return {"status": "error", "error": "label is required. Provide a partial actor name to search for."}

    try:
        actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors = actor_sub.get_all_level_actors()
        matches = [a for a in all_actors if label.lower() in a.get_actor_label().lower()]

        if not matches:
            return {"status": "error", "error": f"No actor found matching '{label}'. Check the label in the World Outliner."}

        target = matches[0]
        loc = target.get_actor_location()

        # Select the actor — required for the native camera command to know the target
        actor_sub.set_selected_level_actors([target])

        # Use UEFN's native "Move Camera to Object" command.
        # This is the same operation as Camera Movement > Move Camera to Object in the
        # viewport menu. No manual rotation math, no roll corruption.
        world = unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(world, "CAMERA ALIGN")

        log_info(f"viewport_focus_actor: focused on '{target.get_actor_label()}' at ({loc.x:.0f}, {loc.y:.0f}, {loc.z:.0f})")
        return {
            "status": "ok",
            "actor": target.get_actor_label(),
            "location": [round(loc.x, 1), round(loc.y, 1), round(loc.z, 1)],
            "matches_found": len(matches),
        }
    except Exception as e:
        log_error(f"viewport_focus_actor failed: {e}")
        return {"status": "error", "error": str(e)}


@register_tool(
    name="viewport_move_to_camera",
    category="Viewport",
    description=(
        "Move selected actors to the current camera position. "
        "Navigate to a spot in the viewport, then run this to place your selection there."
    ),
    tags=["viewport", "camera", "move", "placement", "teleport"],
)
def run_viewport_move_to_camera(**kwargs) -> dict:
    """
    Move all selected actors to the current viewport camera position.
    Workflow: fly to where you want something → select it → run this tool.
    """
    try:
        loc, _rot = _get_camera()
        actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        actors = actor_sub.get_selected_level_actors()
        if not actors:
            return {"status": "error", "error": "No actors selected. Select the actors you want to move, then run this."}

        with unreal.ScopedEditorTransaction("Move Selection to Camera"):
            for actor in actors:
                actor.set_actor_location(loc)

        log_info(f"viewport_move_to_camera: moved {len(actors)} actor(s) to ({loc.x:.0f}, {loc.y:.0f}, {loc.z:.0f})")
        return {
            "status": "ok",
            "actors_moved": len(actors),
            "location": [round(loc.x, 1), round(loc.y, 1), round(loc.z, 1)],
        }
    except Exception as e:
        log_error(f"viewport_move_to_camera failed: {e}")
        return {"status": "error", "error": str(e)}


@register_tool(
    name="viewport_camera_get",
    category="Viewport",
    description="Return the current viewport camera location and rotation — useful for saving a position to return to.",
    tags=["viewport", "camera", "get", "position", "save"],
)
def run_viewport_camera_get(**kwargs) -> dict:
    """Return the current viewport camera position and rotation."""
    try:
        loc, rot = _get_camera()
        return {
            "status": "ok",
            "location": [round(loc.x, 1), round(loc.y, 1), round(loc.z, 1)],
            "rotation": {"pitch": round(rot.pitch, 1), "yaw": round(rot.yaw, 1), "roll": round(rot.roll, 1)},
            "tip": "Use viewport_goto with these values to return here later.",
        }
    except Exception as e:
        log_error(f"viewport_camera_get failed: {e}")
        return {"status": "error", "error": str(e)}
