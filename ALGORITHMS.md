# Layout Algorithms Guide

arrangebpy provides four different layout algorithms, each optimized for different use cases.

## Quick Reference

| Algorithm | Speed | Quality | Best For |
|-----------|-------|---------|----------|
| **Sugiyama** | Medium | Highest | Most node trees, production use |
| **Topological** | Fastest | Good | Development, very large graphs |
| **Grid** | Fast | N/A | Organization, collections |
| **Orthogonal** | Medium | High | Presentations, documentation |

## Detailed Comparison

### Sugiyama (Hierarchical Layout)

The default algorithm, implementing the complete Sugiyama framework for hierarchical graph drawing.

**Algorithm**: Sugiyama framework with Brandes-Köpf coordinate assignment
- Rank assignment (layering nodes)
- Crossing reduction (median heuristic)
- Coordinate assignment (BK algorithm)
- Edge routing with reroute nodes

**Strengths**:
- Minimal edge crossings
- Respects node frames/clusters
- Socket-level alignment
- Node stacking for collapsed math nodes
- Iterative refinement for complex hierarchies

**Settings**: `LayoutSettings`
```python
from arrangebpy import layout, LayoutSettings

layout(ntree, algorithm="sugiyama", settings=LayoutSettings(
    # Spacing
    horizontal_spacing=50.0,
    vertical_spacing=25.0,

    # Algorithm behavior
    direction="BALANCED",           # or LEFT_DOWN, RIGHT_DOWN, etc.
    socket_alignment="MODERATE",    # or NONE, FULL
    iterations=20,                  # BK refinement iterations
    crossing_reduction_sweeps=24,   # More = fewer crossings

    # Features
    add_reroutes=True,
    stack_collapsed=True,           # Stack collapsed math nodes
    stack_margin_y_factor=0.5
))
```

**Use Cases**:
- ✅ Shader node trees (especially with stacking)
- ✅ Geometry node trees
- ✅ Complex node networks
- ✅ Production-quality layouts
- ❌ Real-time/interactive layout (too slow)

---

### Topological (Fast Layered Layout)

A simplified layered layout that skips crossing reduction for speed.

**Algorithm**: Topological sort + layer assignment
- Computes topological layers (longest path from sources)
- Optionally sorts nodes by degree within layers
- Assigns coordinates directly

**Strengths**:
- Very fast (3-10x faster than Sugiyama)
- Simple and predictable
- Good for linear graphs
- No crossing reduction overhead

**Weaknesses**:
- More edge crossings than Sugiyama
- No socket alignment
- No frame/cluster support
- No reroute handling

**Settings**: `TopologicalSettings`
```python
from arrangebpy import layout, TopologicalSettings

layout(ntree, algorithm="topological", settings=TopologicalSettings(
    horizontal_spacing=50.0,
    vertical_spacing=25.0,
    sort_by_degree=True,    # Sort nodes by connection count
    center_nodes=True,      # Center layers vertically
    flatten=False           # Force all nodes to Y=0 (flat horizontal)
))
```

**Special Feature - Flatten Mode**:
```python
# Perfect horizontal layout for linear chains
layout(ntree, algorithm="topological", settings=TopologicalSettings(
    flatten=True  # All nodes at Y=0
))
```

**Use Cases**:
- ✅ Quick layouts during development
- ✅ Very large graphs (1000+ nodes)
- ✅ Simple linear workflows
- ✅ Preview/thumbnail generation
- ✅ **Perfectly flat horizontal layouts** (with `flatten=True`)
- ❌ Complex interconnected graphs
- ❌ Professional presentations (use Sugiyama or Orthogonal instead)

---

### Grid (Regular Grid Layout)

Arranges nodes in a regular grid pattern, optionally grouping them.

**Algorithm**: Simple grid placement
- Groups nodes by type or cluster (optional)
- Arranges in row-major or column-major order
- Places nodes in grid cells

**Strengths**:
- Extremely fast
- Predictable, organized appearance
- Great for grouping similar nodes
- Compact or fixed-size cells

**Weaknesses**:
- Ignores graph structure completely
- Can create very long connections
- No edge routing

**Settings**: `GridSettings`
```python
from arrangebpy import layout, GridSettings

layout(ntree, algorithm="grid", settings=GridSettings(
    cell_width=200.0,
    cell_height=100.0,
    columns=5,                    # or None for auto
    direction="HORIZONTAL",       # or VERTICAL
    grouping="TYPE",              # or NONE, CLUSTER
    center_in_cells=True,
    compact=False                 # Use node sizes for cell sizes
))
```

**Use Cases**:
- ✅ Material libraries (group by shader type)
- ✅ Node collections/inventories
- ✅ Reference sheets
- ✅ Before/after comparisons
- ❌ Showing data flow
- ❌ Complex networks

---

### Orthogonal (Clean Edge Routing)

Uses Sugiyama for node placement but routes edges with only horizontal/vertical segments.

**Algorithm**: Sugiyama + orthogonal edge routing
- Same node placement as Sugiyama
- Routes edges with stairstep or grid-based pathfinding
- Creates reroute nodes at bend points

**Strengths**:
- Professional "blueprint" appearance
- Easier to follow connections
- All Sugiyama features for node placement
- Clean, geometric look

**Weaknesses**:
- Requires more horizontal space
- More complex edge routing
- Potentially more edge bends
- Currently simplified routing (no obstacle avoidance)

**Settings**: `OrthogonalSettings`
```python
from arrangebpy import layout, OrthogonalSettings

layout(ntree, algorithm="orthogonal", settings=OrthogonalSettings(
    # Same Sugiyama settings
    horizontal_spacing=80.0,      # More space for routing
    vertical_spacing=30.0,
    direction="BALANCED",
    socket_alignment="MODERATE",
    iterations=20,
    crossing_reduction_sweeps=24,
    stack_collapsed=False,

    # Orthogonal-specific
    min_segment_length=20.0,
    route_through_grid=True       # Grid vs stairstep routing
))
```

**Use Cases**:
- ✅ Documentation screenshots
- ✅ Tutorials and presentations
- ✅ Professional diagrams
- ✅ Publication figures
- ❌ Very dense node trees (too much routing space)

---

## Algorithm Selection Guide

### By Use Case

**Interactive Editor**: Sugiyama (best quality) or Topological (if speed matters)

**Batch Processing**: Topological (fastest for large batches)

**Documentation**: Orthogonal (cleanest appearance)

**Organization**: Grid (most organized)

**Production/Final**: Sugiyama (highest quality)

### By Node Tree Type

**Shader Trees**:
1. Sugiyama with `stack_collapsed=True` (best)
2. Orthogonal with stacking (for docs)
3. Topological (if very large)

**Geometry Nodes**:
1. Sugiyama with high `crossing_reduction_sweeps` (best)
2. Orthogonal (for presentations)
3. Topological (for quick previews)

**Compositor**:
1. Sugiyama (best general purpose)
2. Topological (for large composites)

**Material Libraries**:
1. Grid with `grouping="TYPE"` (best for organization)
2. Sugiyama (to show relationships)

### By Graph Properties

**Linear chains**: Topological or Sugiyama

**Dense interconnections**: Sugiyama only

**Many similar nodes**: Grid

**Hierarchical structure**: Sugiyama or Orthogonal

**Cyclic graphs**: Sugiyama (handles cycles)

---

## Performance Characteristics

Approximate timing for different graph sizes (typical hardware):

| Nodes | Sugiyama | Topological | Grid | Orthogonal |
|-------|----------|-------------|------|------------|
| 10 | 10ms | 2ms | 1ms | 12ms |
| 50 | 50ms | 8ms | 3ms | 60ms |
| 100 | 150ms | 15ms | 5ms | 180ms |
| 500 | 1s | 60ms | 20ms | 1.2s |
| 1000+ | 3s+ | 120ms | 40ms | 3.5s+ |

*Note: Actual performance varies based on graph structure, settings, and hardware*

---

## Migration from node-arrange

If you're migrating from the original node-arrange add-on:

```python
# Old node-arrange (via Blender operator)
bpy.ops.node.arrange()

# New arrangebpy (Sugiyama with same defaults)
from arrangebpy import layout
layout(context.space_data.edit_tree)

# With all the original features
from arrangebpy import layout, LayoutSettings
layout(ntree, algorithm="sugiyama", settings=LayoutSettings(
    direction="BALANCED",
    socket_alignment="MODERATE",
    stack_collapsed=True,
    add_reroutes=True
))
```

All original features are available, plus new algorithms!
