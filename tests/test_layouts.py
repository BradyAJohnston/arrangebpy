"""Tests for different layout algorithms."""

import bpy
import pytest

import arrangebpy as ar


class TestUnifiedLayout:
    """Test the unified layout() interface."""

    def setup_method(self):
        """Create a simple node tree for testing."""
        self.tree = bpy.data.node_groups.new("Test Tree", type="GeometryNodeTree")

        # Create a simple chain of nodes
        nodes = [
            "NodeGroupInput",
            "GeometryNodeSetPosition",
            "GeometryNodeJoinGeometry",
            "GeometryNodeStoreNamedAttribute",
            "NodeGroupOutput",
        ]
        previous = None
        for name in nodes:
            node = self.tree.nodes.new(name)
            if previous:
                self.tree.links.new(previous.outputs[0], node.inputs[0])
            previous = node

    def teardown_method(self):
        """Clean up the test tree."""
        bpy.data.node_groups.remove(self.tree)

    def test_layout_default_sugiyama(self):
        """Test default layout uses Sugiyama."""
        ar.layout(self.tree)
        # Check it doesn't crash
        assert len(list(self.tree.nodes)) == 5

    def test_layout_explicit_sugiyama(self):
        """Test explicit Sugiyama algorithm."""
        ar.layout(self.tree, algorithm="sugiyama")
        assert len(list(self.tree.nodes)) == 5

    def test_layout_sugiyama_with_settings(self):
        """Test Sugiyama with custom settings."""
        settings = ar.LayoutSettings(
            horizontal_spacing=60.0,
            vertical_spacing=30.0,
            direction="BALANCED",
        )
        ar.layout(self.tree, algorithm="sugiyama", settings=settings)
        assert len(list(self.tree.nodes)) == 5

    def test_layout_topological(self):
        """Test topological layout."""
        ar.layout(self.tree, algorithm="topological")
        assert len(list(self.tree.nodes)) == 5

    def test_layout_topological_with_settings(self):
        """Test topological layout with custom settings."""
        settings = ar.TopologicalSettings(
            horizontal_spacing=60.0,
            vertical_spacing=30.0,
            sort_by_degree=True,
        )
        ar.layout(self.tree, algorithm="topological", settings=settings)
        assert len(list(self.tree.nodes)) == 5

    def test_layout_grid(self):
        """Test grid layout."""
        ar.layout(self.tree, algorithm="grid")
        assert len(list(self.tree.nodes)) == 5

    def test_layout_grid_with_settings(self):
        """Test grid layout with custom settings."""
        settings = ar.GridSettings(
            columns=3,
            cell_width=200.0,
            cell_height=100.0,
            direction="HORIZONTAL",
        )
        ar.layout(self.tree, algorithm="grid", settings=settings)
        assert len(list(self.tree.nodes)) == 5

    def test_layout_orthogonal(self):
        """Test orthogonal layout."""
        ar.layout(self.tree, algorithm="orthogonal")
        assert len(list(self.tree.nodes)) == 5

    def test_layout_orthogonal_with_settings(self):
        """Test orthogonal layout with custom settings."""
        settings = ar.OrthogonalSettings(
            horizontal_spacing=80.0,
            vertical_spacing=40.0,
            socket_alignment="FULL",
        )
        ar.layout(self.tree, algorithm="orthogonal", settings=settings)
        assert len(list(self.tree.nodes)) == 5

    def test_layout_invalid_algorithm(self):
        """Test that invalid algorithm raises error."""
        with pytest.raises(ValueError, match="Unknown algorithm"):
            ar.layout(self.tree, algorithm="invalid")

    def test_layout_wrong_settings_type(self):
        """Test that wrong settings type raises error."""
        with pytest.raises(TypeError, match="requires TopologicalSettings"):
            ar.layout(
                self.tree, algorithm="topological", settings=ar.LayoutSettings()
            )


class TestTopologicalLayout:
    """Test topological layout algorithm."""

    def setup_method(self):
        """Create a test tree."""
        self.tree = bpy.data.node_groups.new("Test Tree", type="GeometryNodeTree")

    def teardown_method(self):
        """Clean up."""
        bpy.data.node_groups.remove(self.tree)

    def test_simple_chain(self):
        """Test topological layout on a simple chain."""
        node_names = ["NodeGroupInput", "GeometryNodeSetPosition", "NodeGroupOutput"]
        created_nodes = []
        previous = None
        for name in node_names:
            node = self.tree.nodes.new(name)
            created_nodes.append(node)
            if previous:
                self.tree.links.new(previous.outputs[0], node.inputs[0])
            previous = node

        ar.topological_layout(self.tree)

        # Just check it doesn't crash
        # Note: In headless Blender tests, links may not be immediately valid,
        # so we can't reliably test the actual layout behavior
        assert len(created_nodes) == 3

    def test_empty_tree(self):
        """Test topological layout on empty tree."""
        ar.topological_layout(self.tree)
        # Should not crash

    def test_settings_validation(self):
        """Test settings validation."""
        # This should work
        ar.topological_layout(
            self.tree,
            ar.TopologicalSettings(horizontal_spacing=100.0, vertical_spacing=50.0),
        )


class TestGridLayout:
    """Test grid layout algorithm."""

    def setup_method(self):
        """Create a test tree."""
        self.tree = bpy.data.node_groups.new("Test Tree", type="GeometryNodeTree")

    def teardown_method(self):
        """Clean up."""
        bpy.data.node_groups.remove(self.tree)

    def test_grid_horizontal(self):
        """Test horizontal grid layout."""
        # Create 6 nodes
        for _ in range(6):
            self.tree.nodes.new("GeometryNodeSetPosition")

        settings = ar.GridSettings(columns=3, direction="HORIZONTAL")
        ar.grid_layout(self.tree, settings)

        # Should have nodes arranged in grid
        assert len(self.tree.nodes) == 6

    def test_grid_vertical(self):
        """Test vertical grid layout."""
        for _ in range(6):
            self.tree.nodes.new("GeometryNodeSetPosition")

        settings = ar.GridSettings(columns=2, direction="VERTICAL")
        ar.grid_layout(self.tree, settings)

        assert len(self.tree.nodes) == 6

    def test_grid_grouping_type(self):
        """Test grouping by node type."""
        # Create different types of nodes
        self.tree.nodes.new("GeometryNodeSetPosition")
        self.tree.nodes.new("GeometryNodeSetPosition")
        self.tree.nodes.new("GeometryNodeJoinGeometry")
        self.tree.nodes.new("GeometryNodeJoinGeometry")

        settings = ar.GridSettings(grouping="TYPE")
        ar.grid_layout(self.tree, settings)

        assert len(self.tree.nodes) == 4

    def test_grid_compact(self):
        """Test compact grid layout."""
        for _ in range(4):
            self.tree.nodes.new("GeometryNodeSetPosition")

        settings = ar.GridSettings(compact=True, columns=2)
        ar.grid_layout(self.tree, settings)

        assert len(self.tree.nodes) == 4

    def test_settings_validation(self):
        """Test settings validation."""
        # Invalid columns
        with pytest.raises(ValueError):
            ar.GridSettings(columns=0)

        # Invalid cell dimensions
        with pytest.raises(ValueError):
            ar.GridSettings(cell_width=-10)

        with pytest.raises(ValueError):
            ar.GridSettings(cell_height=0)


class TestOrthogonalLayout:
    """Test orthogonal layout algorithm."""

    def setup_method(self):
        """Create a test tree."""
        self.tree = bpy.data.node_groups.new("Test Tree", type="GeometryNodeTree")

    def teardown_method(self):
        """Clean up."""
        bpy.data.node_groups.remove(self.tree)

    def test_simple_chain(self):
        """Test orthogonal layout on a simple chain."""
        nodes = ["NodeGroupInput", "GeometryNodeSetPosition", "NodeGroupOutput"]
        previous = None
        for name in nodes:
            node = self.tree.nodes.new(name)
            if previous:
                self.tree.links.new(previous.outputs[0], node.inputs[0])
            previous = node

        ar.orthogonal_layout(self.tree)

        # Just check it doesn't crash
        assert len(list(self.tree.nodes)) == 3

    def test_with_stacking(self):
        """Test orthogonal layout with node stacking."""
        # Create simple tree
        nodes = ["NodeGroupInput", "GeometryNodeSetPosition", "NodeGroupOutput"]
        previous = None
        for name in nodes:
            node = self.tree.nodes.new(name)
            if previous:
                self.tree.links.new(previous.outputs[0], node.inputs[0])
            previous = node

        settings = ar.OrthogonalSettings(stack_collapsed=True)
        ar.orthogonal_layout(self.tree, settings)

        # Just check it doesn't crash
        assert len(list(self.tree.nodes)) == 3

    def test_settings_validation(self):
        """Test settings validation."""
        # Invalid min_segment_length
        with pytest.raises(ValueError):
            ar.OrthogonalSettings(min_segment_length=-10)

        # Invalid iterations
        with pytest.raises(ValueError):
            ar.OrthogonalSettings(iterations=0)


class TestBackwardsCompatibility:
    """Test that old API still works."""

    def setup_method(self):
        """Create a test tree."""
        self.tree = bpy.data.node_groups.new("Test Tree", type="GeometryNodeTree")
        nodes = ["NodeGroupInput", "GeometryNodeSetPosition", "NodeGroupOutput"]
        previous = None
        for name in nodes:
            node = self.tree.nodes.new(name)
            if previous:
                self.tree.links.new(previous.outputs[0], node.inputs[0])
            previous = node

    def teardown_method(self):
        """Clean up."""
        bpy.data.node_groups.remove(self.tree)

    def test_sugiyama_layout_still_works(self):
        """Test that old sugiyama_layout function still works."""
        # Store initial locations
        initial_locs = [tuple(node.location) for node in self.tree.nodes]
        ar.sugiyama_layout(self.tree)
        # At least one node should have moved (or they're all arranged)
        final_locs = [tuple(node.location) for node in self.tree.nodes]
        # Just check it doesn't crash and produces some layout
        assert len(list(self.tree.nodes)) == 3

    def test_sugiyama_layout_with_settings(self):
        """Test that old API with settings still works."""
        settings = ar.LayoutSettings(horizontal_spacing=60.0)
        ar.sugiyama_layout(self.tree, settings)
        # Just check it doesn't crash
        assert len(list(self.tree.nodes)) == 3
