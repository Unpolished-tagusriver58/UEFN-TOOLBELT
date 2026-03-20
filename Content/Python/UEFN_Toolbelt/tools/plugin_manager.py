"""
UEFN TOOLBELT — Plugin Management Tools
========================================
Helps developers validate their own Custom Plugins.
"""

from UEFN_Toolbelt.registry import register_tool, get_registry
from UEFN_Toolbelt import core

@register_tool(
    name="plugin_validate_all",
    category="Utilities",
    description="Validate all registered tools against the Toolbelt schema requirements.",
    tags=["plugin", "validate", "developer", "debug"],
)
def validate_all(**kwargs) -> list[str]:
    """Check all registered tools for schema and description requirements."""
    reg = get_registry()
    errors = reg.validate()
    if not errors:
        core.log_info("✓ All registered tools passed schema validation.")
    else:
        core.log_warning("Found validation errors:")
        for err in errors:
            core.log_warning(err)
    return errors


@register_tool(
    name="plugin_list_custom",
    category="Utilities",
    description="List all currently loaded third-party custom plugins.",
    tags=["plugin", "list", "developer"],
)
def list_custom(**kwargs) -> list[str]:
    """List tools that were loaded from the Saved/UEFN_Toolbelt/Custom_Plugins directory."""
    custom_tools = []
    reg = get_registry()
    for name, entry in reg._tools.items():
        # Normalize path separators for checking
        source_path = entry.source.replace("\\", "/")
        if "Custom_Plugins" in source_path:
            custom_tools.append(name)
            
    if not custom_tools:
        core.log_info("No custom plugins found in Saved/UEFN_Toolbelt/Custom_Plugins.")
    else:
        core.log_info(f"Loaded Custom Plugins ({len(custom_tools)}):")
        for name in custom_tools:
            core.log_info(f"  • {name}")
    return custom_tools
