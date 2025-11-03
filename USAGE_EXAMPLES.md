# bpynodearrange Usage Examples

This document shows how to use the new features added to bpynodearrange.

## Basic Usage (Backwards Compatible)

```python
from bpynodearrange.arrange.sugiyama import sugiyama_layout

# Simple usage with defaults
sugiyama_layout(ntree)

# Custom spacing (same as before)
sugiyama_layout(ntree, vertical_spacing=30.0, horizontal_spacing=60.0)
```

## Using LayoutSettings for Full Control

```python
from bpynodearrange import LayoutSettings
from bpynodearrange.arrange.sugiyama import sugiyama_layout

# Create custom settings
settings = LayoutSettings(
    # Spacing
    horizontal_spacing=60.0,
    vertical_spacing=30.0,

    # Layout direction
    direction="BALANCED",  # or "LEFT_DOWN", "RIGHT_DOWN", "LEFT_UP", "RIGHT_UP"

    # Socket alignment
    socket_alignment="MODERATE",  # or "NONE", "FULL"

    # Algorithm tuning
    iterations=20,  # BK algorithm refinement iterations
    crossing_reduction_sweeps=24,  # More sweeps = fewer crossings

    # Reroute handling
    add_reroutes=True,
    keep_reroutes_outside_frames=False,

    # Node stacking (for shader node trees)
    stack_collapsed=True,
    stack_margin_y_factor=0.5,
)

# Apply layout with custom settings
sugiyama_layout(ntree, settings)
```

## Feature Examples

### 1. Node Stacking for Shader Trees

Stack collapsed math nodes to create more compact layouts:

```python
settings = LayoutSettings(
    stack_collapsed=True,
    stack_margin_y_factor=0.3,  # Tight stacking
)
sugiyama_layout(shader_node_tree, settings)
```

### 2. Different Layout Directions

```python
# Top-left alignment
settings = LayoutSettings(direction="LEFT_UP")
sugiyama_layout(ntree, settings)

# Bottom-right alignment
settings = LayoutSettings(direction="RIGHT_DOWN")
sugiyama_layout(ntree, settings)

# Balanced (combines all 4 directions)
settings = LayoutSettings(direction="BALANCED")
sugiyama_layout(ntree, settings)
```

### 3. Socket Alignment Modes

Control how sockets align between nodes:

```python
# No socket alignment - only align node tops
settings = LayoutSettings(socket_alignment="NONE")
sugiyama_layout(ntree, settings)

# Full socket alignment - always align sockets
settings = LayoutSettings(socket_alignment="FULL")
sugiyama_layout(ntree, settings)

# Moderate - smart alignment based on node heights (default)
settings = LayoutSettings(socket_alignment="MODERATE")
sugiyama_layout(ntree, settings)
```

### 4. Iterative Refinement for Better Frame Layouts

For complex node trees with many frames, increase iterations:

```python
settings = LayoutSettings(
    iterations=20,  # More iterations for better frame gap detection
)
sugiyama_layout(ntree, settings)
```

### 5. Crossing Reduction

Reduce edge crossings with more sweeps:

```python
settings = LayoutSettings(
    crossing_reduction_sweeps=48,  # More sweeps = cleaner layout (but slower)
)
sugiyama_layout(ntree, settings)
```

### 6. Disable Reroute Nodes

If you don't want reroute nodes added:

```python
settings = LayoutSettings(
    add_reroutes=False,
)
sugiyama_layout(ntree, settings)
```

## Complete Example for Shader Node Trees

```python
from bpynodearrange import LayoutSettings
from bpynodearrange.arrange.sugiyama import sugiyama_layout

# Optimized settings for shader node trees
shader_settings = LayoutSettings(
    # Tighter spacing for shader nodes
    horizontal_spacing=50.0,
    vertical_spacing=20.0,

    # Use balanced direction
    direction="BALANCED",

    # Full socket alignment for cleaner connections
    socket_alignment="FULL",

    # Stack collapsed math nodes
    stack_collapsed=True,
    stack_margin_y_factor=0.4,

    # More iterations for complex frame hierarchies
    iterations=15,
    crossing_reduction_sweeps=32,

    # Add reroutes for clean routing
    add_reroutes=True,
)

# Apply to shader node tree
sugiyama_layout(material.node_tree, shader_settings)
```

## Complete Example for Geometry Node Trees

```python
# Optimized settings for geometry node trees
geometry_settings = LayoutSettings(
    # More spacing for geometry nodes (they're larger)
    horizontal_spacing=70.0,
    vertical_spacing=30.0,

    # Left-to-right flow
    direction="RIGHT_DOWN",

    # Moderate socket alignment
    socket_alignment="MODERATE",

    # Don't stack nodes
    stack_collapsed=False,

    # High quality layout
    iterations=20,
    crossing_reduction_sweeps=48,

    # Add reroutes for complex trees
    add_reroutes=True,
)

# Apply to geometry nodes
sugiyama_layout(geometry_nodes.node_tree, geometry_settings)
```

## Programmatic Use in Other Add-ons

```python
# In your Blender add-on operator

import bpy
from bpynodearrange import LayoutSettings
from bpynodearrange.arrange.sugiyama import sugiyama_layout

class MY_OT_ArrangeNodes(bpy.types.Operator):
    bl_idname = "node.my_arrange"
    bl_label = "Arrange Nodes"

    def execute(self, context):
        ntree = context.space_data.edit_tree

        # Create settings based on node tree type
        if ntree.bl_idname == 'ShaderNodeTree':
            settings = LayoutSettings(
                stack_collapsed=True,
                socket_alignment="FULL",
            )
        elif ntree.bl_idname == 'GeometryNodeTree':
            settings = LayoutSettings(
                horizontal_spacing=70.0,
                socket_alignment="MODERATE",
            )
        else:
            settings = LayoutSettings()  # Defaults

        # Apply layout
        sugiyama_layout(ntree, settings)

        return {'FINISHED'}
```

## Default Settings

If you don't provide any settings, these defaults are used:

```python
LayoutSettings(
    horizontal_spacing=50.0,
    vertical_spacing=25.0,
    direction="BALANCED",
    socket_alignment="MODERATE",
    iterations=20,
    crossing_reduction_sweeps=24,
    add_reroutes=True,
    keep_reroutes_outside_frames=False,
    stack_collapsed=False,
    stack_margin_y_factor=0.5,
)
```

## Migration from Old API

Old code using just spacing parameters still works:

```python
# Old API (still works)
sugiyama_layout(ntree, vertical_spacing=30.0, horizontal_spacing=60.0)

# New API (more control)
settings = LayoutSettings(
    vertical_spacing=30.0,
    horizontal_spacing=60.0,
    direction="LEFT_UP",  # Now you can also specify direction!
)
sugiyama_layout(ntree, settings)
```
