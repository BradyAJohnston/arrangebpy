# Comparison: node-arrange vs bpynodearrange

This document outlines the key differences between the original `node-arrange` Blender add-on and the `bpynodearrange` Python module.

## Architecture Differences

### Module Organization

**node-arrange (add-on)**:
```
source/
├── __init__.py (register/unregister)
├── operators.py (Blender operators)
├── properties.py (user settings)
├── keymaps.py (keyboard shortcuts)
├── ui.py (UI panels)
├── config.py (global state)
├── utils.py
└── arrange/
    ├── sugiyama.py
    ├── graph.py
    ├── ranking.py
    ├── ordering.py
    ├── x_coords.py
    ├── y_coords.py
    ├── stacking.py  ← Not in bpynodearrange
    ├── realize.py
    └── structs.py
```

**bpynodearrange (module)**:
```
bpynodearrange/
├── __init__.py (clean module exports)
├── config.py (simplified, no settings)
├── utils.py
└── arrange/
    ├── sugiyama.py
    ├── graph.py
    ├── ranking.py
    ├── ordering.py
    ├── coordinates.py (combines x/y coords)
    ├── reroute.py (extracted from realize)
    ├── routing.py (extracted from x_coords)
    ├── multi_input.py (extracted from realize)
    ├── placement/
    │   ├── bk.py (simplified BK algorithm)
    │   └── linear_segments.py
    └── structs.py
```

## Missing Features in bpynodearrange

### 1. **Node Stacking** ❌
The original has a sophisticated feature to stack collapsed math nodes on top of each other (`stacking.py`):
- Detects collapsed `ShaderNodeMath` and `ShaderNodeVectorMath` nodes
- Uses bipartite matching to create optimal stacking groups
- Configurable vertical spacing between stacked nodes (`stack_margin_y_fac`)

**Impact**: bpynodearrange cannot stack collapsed math nodes.

### 2. **User-Configurable Settings** ❌
The original has extensive user settings via `properties.py`:

| Setting | Original | bpynodearrange |
|---------|----------|----------------|
| **Spacing (margin)** | User-configurable XY | Hardcoded params (50, 25) |
| **Direction** | 5 options (LEFT_UP, RIGHT_UP, LEFT_DOWN, RIGHT_DOWN, BALANCED) | Always BALANCED |
| **Socket Alignment** | 3 modes (NONE, MODERATE, FULL) | Simplified (no inner_shift) |
| **Crossing Iterations** | User-configurable (default: 25) | Hardcoded (24 sweeps) |
| **Add Reroutes** | Toggle on/off | Always on |
| **Keep Reroutes Outside Frames** | Toggle | Not supported |
| **Stack Collapsed** | Toggle | Not supported |

### 3. **Additional Operators** ❌
The original provides multiple Blender operators:
- `NA_OT_ArrangeSelected` - Arrange selected nodes
- `NA_OT_BatchArrange` - Arrange all node trees in .blend file
- `NA_OT_RecenterSelected` - Recenter selected nodes (3 origin modes)
- `NA_OT_BatchRecenter` - Recenter all node trees

**bpynodearrange** only provides the core `sugiyama_layout()` function.

### 4. **Keymaps and UI** ❌
- No keyboard shortcuts
- No UI panels
- Pure programmatic interface

## Algorithm Simplifications

### BK Y-Coordinate Assignment

**Original (`y_coords.py`)**:
```python
def bk_assign_y_coords(G, T):
    # 4 layouts (RIGHT_DOWN, RIGHT_UP, LEFT_DOWN, LEFT_UP)
    for dir_x in (-1, 1):
        for dir_y in (-1, 1):
            i = 0
            marked_nodes = set()

            # Iterative refinement (up to 20 iterations)
            while i < _ITER_LIMIT:
                i += 1
                horizontal_alignment(G, marked_edges, marked_nodes)
                inner_shift(G, dir_x == 1, is_up)  # ← Socket alignment
                vertical_compaction(G, is_up)

                # Check for large gaps in frames
                if new_marked_nodes := get_marked_nodes(G, T, marked_nodes, is_up):
                    marked_nodes.update(new_marked_nodes)
                    for v in G:
                        v.bk_reset()
                else:
                    break

            layouts.append([v.y * -dir_y for v in G])

    # Apply user preference
    if config.SETTINGS.direction == 'BALANCED':
        balance(G, layouts)
        for i, v in enumerate(G):
            values = [l[i] for l in layouts]
            values.sort()
            v.y = fmean(values[1:3])  # Average of middle two
    else:
        # Use specific direction
        i = _DIRECTION_TO_IDX[config.SETTINGS.direction]
        for v, y in zip(G, layouts[i]):
            v.y = y
```

**bpynodearrange (`placement/bk.py`)**:
```python
def bk_assign_y_coords(G, vertical_spacing=50.0):
    # 4 layouts (same directions)
    for dir_x in (-1, 1):
        for dir_y in (-1, 1):
            horizontal_alignment(G, marked_edges)
            precompute_cells(G)  # Optimization
            vertical_compaction(G, dir_y == 1, vertical_spacing)
            layouts.append([v.y * -dir_y for v in G])

            # Single pass, no iterations
            for v in G:
                v.reset()

    # Always BALANCED
    balance(layouts)
    for i, v in enumerate(G):
        values = [layout[i] for layout in layouts]
        values.sort()
        v.y = fmean(values[1:3])
```

**Key differences**:
1. **No iterative refinement** - bpynodearrange does single pass, original can iterate up to 20 times
2. **No `inner_shift`** - Socket alignment is simplified
3. **No `marked_nodes`** - Frame gap detection removed
4. **Always balanced** - No direction selection

### Socket Alignment (inner_shift)

**Original** has sophisticated socket alignment based on user settings:
```python
def should_use_inner_shift(v, w, is_right):
    if v.is_reroute or w.is_reroute:
        return True

    if config.SETTINGS.socket_alignment == 'NONE':
        return False  # Only align node tops

    if config.SETTINGS.socket_alignment == 'FULL':
        return True   # Always align sockets

    # MODERATE: Smart decision based on node heights
    if v.cluster != w.cluster or Kind.STACK in {v.type, w.type}:
        return True

    if v.height > w.height and not getattr(w.node, 'hide', False):
        return False

    return abs(v.height - w.height) > fmean((v.height, w.height)) / 2
```

**bpynodearrange**: Uses simplified cell-based separation without socket-level alignment.

## Naming Differences

| Original | bpynodearrange |
|----------|----------------|
| `Node` | `GNode` (Graph Node) |
| `Kind` | `GType` (Graph Type) |
| `bk_reset()` | `reset()` |
| `FROM_SOCKET`/`TO_SOCKET` | Same |
| `y_coords.py` | `placement/bk.py` |
| `x_coords.py` + routing | `coordinates.py` + `routing.py` |
| `realize.py` | `coordinates.py` + `reroute.py` + `multi_input.py` |

## Advantages of bpynodearrange

### 1. **Cleaner Module Structure**
- Better code organization with `placement/` subdirectory
- Separation of concerns (routing, reroute, multi_input as separate files)
- No dependency on Blender operators/UI

### 2. **Simplified API**
```python
from bpynodearrange.arrange.sugiyama import sugiyama_layout

# Simple to use in other add-ons
sugiyama_layout(
    ntree,
    vertical_spacing=25.0,
    horizontal_spacing=50.0
)
```

### 3. **Better Testability**
- Works in headless mode
- Unit tests included
- No UI dependencies

### 4. **Optimizations**
- `precompute_cells()` for faster block placement
- Simplified inner calculations
- Better null safety

### 5. **Documentation**
- Docstrings on all major functions
- Type hints throughout
- Clear module structure

## Advantages of Original node-arrange

### 1. **More Features**
- Node stacking
- Multiple layout directions
- Configurable socket alignment
- Batch operations

### 2. **User Control**
- Extensive settings via UI
- Iterative refinement for better frame layouts
- Fine-tuned spacing control

### 3. **Integration**
- Keyboard shortcuts
- UI panels
- Undo/redo support
- Selection-aware

### 4. **Refinement**
- Iterative marked nodes for better frame layouts
- Gap detection in frames
- More sophisticated socket alignment

## Recommendations

### For bpynodearrange to reach feature parity:

1. **Add optional settings parameter**:
   ```python
   @dataclass
   class LayoutSettings:
       margin: tuple[float, float] = (50, 25)
       direction: str = 'BALANCED'
       socket_alignment: str = 'MODERATE'
       iterations: int = 1
       add_reroutes: bool = True
       stack_collapsed: bool = False

   def sugiyama_layout(ntree, settings: LayoutSettings | None = None):
       ...
   ```

2. **Port stacking.py** - This is a significant feature for shader node trees

3. **Add iterative refinement** - Optional iterations for better frame handling

4. **Add direction selection** - Allow choosing specific layout directions

5. **Restore inner_shift** - Better socket alignment for tall nodes

### For use cases:

**Use node-arrange when**:
- You need full user control via UI
- Stacking collapsed math nodes is important
- You want batch operations
- You prefer specific layout directions

**Use bpynodearrange when**:
- You're building another add-on
- You need programmatic control
- Simpler API is preferred
- Headless operation is required
- Testing is important

## Conclusion

**bpynodearrange** is a cleaner, more modular reimplementation optimized for use as a library. It sacrifices some advanced features (stacking, socket alignment modes, iterative refinement) for simplicity and better code organization.

The core Sugiyama algorithm is implemented in both, but the original has more sophisticated refinements for edge cases, especially around node frames and socket alignment.
