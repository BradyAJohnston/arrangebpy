# bpynodearrange

**Automatic layout of nodes for Blender node trees** - A clean, library-focused Python module implementing the Sugiyama hierarchical graph layout algorithm.

Ported from the excellent [node-arrange](https://github.com/JacquesLucke/node_arrange) Blender add-on, redesigned as a standalone module for use in other add-ons and tools.

## Features

✨ **Complete Sugiyama Implementation**
- Hierarchical node layout with minimal edge crossings
- Frame-aware layout (respects Blender's node frames)
- Multi-input socket handling
- Reroute node optimization

🎛️ **Highly Configurable**
- **5 layout directions**: Balanced, Left-Up, Right-Down, etc.
- **3 socket alignment modes**: None, Moderate, Full
- **Node stacking**: Automatically stack collapsed math nodes
- **Iterative refinement**: Better layouts for complex frame hierarchies
- **Adjustable spacing**: Control horizontal and vertical spacing

🔧 **Clean API Design**
- Settings-based configuration (no global state)
- Type-safe with full type hints
- Well-documented with examples
- Designed for embedding in other add-ons

## Installation

```bash
pip install bpynodearrange
```

Or with uv:
```bash
uv add bpynodearrange
```

## Quick Start

```python
from bpynodearrange import LayoutSettings
from bpynodearrange.arrange.sugiyama import sugiyama_layout

# Simple usage with defaults
sugiyama_layout(node_tree)

# Custom settings
settings = LayoutSettings(
    direction="BALANCED",
    socket_alignment="MODERATE",
    horizontal_spacing=60.0,
    vertical_spacing=30.0,
)
sugiyama_layout(node_tree, settings)
```

## Usage Examples

### Default Layout

```python
from bpynodearrange.arrange.sugiyama import sugiyama_layout

# Uses sensible defaults
sugiyama_layout(material.node_tree)
```

### Shader Node Trees (with stacking)

```python
from bpynodearrange import LayoutSettings
from bpynodearrange.arrange.sugiyama import sugiyama_layout

settings = LayoutSettings(
    # Stack collapsed math nodes
    stack_collapsed=True,
    stack_margin_y_factor=0.4,
    
    # Full socket alignment for cleaner connections
    socket_alignment="FULL",
    
    # Balanced direction
    direction="BALANCED",
    
    # Tight spacing
    horizontal_spacing=50.0,
    vertical_spacing=20.0,
)

sugiyama_layout(shader_node_tree, settings)
```

### Geometry Node Trees

```python
settings = LayoutSettings(
    # More spacing for larger nodes
    horizontal_spacing=70.0,
    vertical_spacing=30.0,
    
    # Left-to-right flow
    direction="RIGHT_DOWN",
    
    # Moderate socket alignment
    socket_alignment="MODERATE",
    
    # High quality layout
    iterations=20,
    crossing_reduction_sweeps=48,
)

sugiyama_layout(geometry_node_tree, settings)
```

## Configuration

All configuration through the `LayoutSettings` dataclass:

```python
from bpynodearrange import LayoutSettings

settings = LayoutSettings(
    # Spacing
    horizontal_spacing=50.0,      # Horizontal spacing between columns
    vertical_spacing=25.0,        # Vertical spacing between nodes
    
    # Layout algorithm
    direction="BALANCED",         # Layout direction
    socket_alignment="MODERATE",  # Socket alignment mode
    iterations=20,                # BK algorithm refinement iterations
    crossing_reduction_sweeps=24, # Edge crossing minimization passes
    
    # Features
    add_reroutes=True,           # Add reroute nodes for clean routing
    stack_collapsed=False,       # Stack collapsed math nodes
    stack_margin_y_factor=0.5,   # Spacing factor for stacks (0-1)
)
```

### Direction Options

- `"BALANCED"` - Combines all 4 directions (default, best results)
- `"LEFT_DOWN"` - Top-left alignment  
- `"RIGHT_DOWN"` - Bottom-right alignment
- `"LEFT_UP"` - Bottom-left alignment
- `"RIGHT_UP"` - Top-right alignment

### Socket Alignment Options

- `"NONE"` - Only align node tops (fastest)
- `"MODERATE"` - Smart alignment based on node heights (default)
- `"FULL"` - Always align sockets (cleanest connections)

## Use in Blender Add-ons

```python
import bpy
from bpynodearrange import LayoutSettings
from bpynodearrange.arrange.sugiyama import sugiyama_layout

class MY_OT_ArrangeNodes(bpy.types.Operator):
    bl_idname = "node.my_arrange"
    bl_label = "Arrange Nodes"
    
    def execute(self, context):
        ntree = context.space_data.edit_tree
        
        # Configure based on node tree type
        if ntree.bl_idname == 'ShaderNodeTree':
            settings = LayoutSettings(
                stack_collapsed=True,
                socket_alignment="FULL",
            )
        else:
            settings = LayoutSettings()
        
        sugiyama_layout(ntree, settings)
        return {'FINISHED'}
```

## How It Works

Implements the Sugiyama hierarchical graph layout framework:

1. **Graph Construction** - Build directed graph from node tree
2. **Ranking** - Assign nodes to horizontal layers
3. **Crossing Minimization** - Reduce edge crossings via median heuristic  
4. **Coordinate Assignment** - Place nodes using Brandes-Köpf algorithm
5. **Edge Routing** - Add bend points for clean connections
6. **Realization** - Apply positions back to Blender

## Architecture

```
bpynodearrange/
├── settings.py              # Configuration
├── arrange/
│   ├── sugiyama.py         # Main orchestration
│   ├── graph.py            # Graph construction
│   ├── ranking.py          # Rank assignment
│   ├── ordering.py         # Crossing minimization
│   ├── placement/
│   │   ├── bk.py           # Brandes-Köpf algorithm
│   │   └── linear_segments.py
│   ├── coordinates.py      # X-coordinate assignment  
│   ├── routing.py          # Edge routing
│   ├── stacking.py         # Node stacking
│   └── ...
└── utils.py
```

## Development

```bash
git clone https://github.com/BradyAJohnston/bpynodearrange.git
cd bpynodearrange

# Install
uv sync

# Run tests
uv run pytest tests/
```

## License

GPL-3.0-or-later

## Credits

Based on [node-arrange](https://github.com/JacquesLucke/node_arrange) by Jacques Lucke.

Implements algorithms from Sugiyama et al., Brandes & Köpf, and others.
