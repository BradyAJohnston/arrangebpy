# SPDX-License-Identifier: GPL-2.0-or-later

"""
Layout Settings

This module defines the settings dataclass for configuring the Sugiyama layout algorithm.
All settings are passed as function parameters rather than using global state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Direction = Literal["LEFT_DOWN", "RIGHT_DOWN", "LEFT_UP", "RIGHT_UP", "BALANCED"]
SocketAlignment = Literal["NONE", "MODERATE", "FULL"]


@dataclass
class LayoutSettings:
    """
    Configuration settings for the Sugiyama layout algorithm.

    All parameters have sensible defaults matching the original node-arrange add-on.
    """

    # Spacing
    horizontal_spacing: float = 50.0
    """Horizontal spacing between node columns"""

    vertical_spacing: float = 25.0
    """Vertical spacing between nodes in the same column"""

    # Algorithm behavior
    direction: Direction = "BALANCED"
    """
    Layout direction:
    - "BALANCED": Combine four extreme layouts, evening out directional tendencies
    - "LEFT_DOWN", "RIGHT_DOWN", "LEFT_UP", "RIGHT_UP": Use specific direction
    """

    socket_alignment: SocketAlignment = "MODERATE"
    """
    Socket alignment mode:
    - "NONE": Only try to align the tops of nodes
    - "MODERATE": Align sockets or node tops depending on node heights (default)
    - "FULL": Always try to align sockets with other sockets
    """

    iterations: int = 20
    """
    Number of iterations for BK algorithm refinement (for frame gap detection).
    Higher values may produce better layouts for complex frame hierarchies.
    Set to 1 for single-pass (faster but less refined).
    """

    crossing_reduction_sweeps: int = 24
    """
    Number of median heuristic sweeps for crossing reduction.
    More sweeps reduce crossings but take longer.
    """

    # Reroute handling
    add_reroutes: bool = True
    """If True, add reroute nodes to clean up edge routing"""

    keep_reroutes_outside_frames: bool = False
    """
    If True, always attach reroutes to the lowest common frame of the nodes they connect.
    If False, allow reroutes to be placed inside frames when beneficial.
    """

    # Node stacking
    stack_collapsed: bool = False
    """
    If True, stack collapsed math and vector math nodes on top of each other.
    This creates more compact layouts for shader node trees.
    """

    stack_margin_y_factor: float = 0.5
    """
    Factor for vertical spacing between stacked nodes (0.0 to 1.0).
    Lower values create tighter stacks.
    Only used when stack_collapsed is True.
    """

    def __post_init__(self):
        """Validate settings after initialization."""
        if self.iterations < 1:
            raise ValueError("iterations must be at least 1")
        if self.crossing_reduction_sweeps < 1:
            raise ValueError("crossing_reduction_sweeps must be at least 1")
        if not 0 <= self.stack_margin_y_factor <= 1:
            raise ValueError("stack_margin_y_factor must be between 0 and 1")
