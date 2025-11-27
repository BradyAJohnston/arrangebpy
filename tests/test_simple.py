import arrangebpy as ar
import bpy


def test_simple_line():
    """Test that a simple linear chain can be laid out perfectly flat."""
    tree = bpy.data.node_groups.new("Geometry Node", type="GeometryNodeTree")

    nodes = [
        "NodeGroupInput",
        "GeometryNodeSetPosition",
        "GeometryNodeJoinGeometry",
        "GeometryNodeStoreNamedAttribute",
        "NodeGroupOutput",
    ]
    for i, name in enumerate(nodes):
        node = tree.nodes.new(name)
        if i == 0:
            previous = node
            continue
        tree.links.new(previous.outputs[0], node.inputs[0])
        previous = node

    # Use topological layout with flatten mode for perfectly horizontal layout
    ar.layout(
        tree,
        algorithm="topological",
        settings=ar.TopologicalSettings(flatten=True, center_nodes=False),
    )

    locations = [n.location for n in tree.nodes]
    print(f"{locations=}")
    # All nodes should be at Y=0
    assert all([x[1] == 0 for x in locations]), f"Expected all Y=0, got {locations}"
