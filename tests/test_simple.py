import arrangebpy as ar
import bpy


def test_simple_line():
    """Test that a simple linear chain can be laid out perfectly flat."""
    tree = bpy.data.node_groups.new("Geometry Node", type="GeometryNodeTree")
    tree.interface.new_socket(
        "Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    tree.interface.new_socket(
        "Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )
    mod = bpy.data.objects["Cube"].modifiers.new("GEOMETRY", type="NODES")
    mod.node_group = tree

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

    # Use Sugiyama layout with flat top and generous spacing
    ar.layout(
        ntree=tree,
        algorithm="sugiyama",
        settings=ar.LayoutSettings(
            align_top_layer=True,
            horizontal_spacing=200.0,  # Generous spacing for geometry nodes
        ),
    )
    bpy.ops.wm.save_mainfile(filepath="/Users/brady/Desktop/simplearrange.blend")

    locations = [n.location for n in tree.nodes]
    print(f"{locations=}")
    # All nodes should be at Y=0
    assert all([x[1] == 0 for x in locations]), f"Expected all Y=0, got {locations}"
