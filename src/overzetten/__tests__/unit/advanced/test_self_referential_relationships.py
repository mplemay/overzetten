"""Tests for self-referential relationship handling in DTO generation."""

from typing import Optional

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import Node


def test_self_referential_relationship_mapping() -> None:
    """Test handling of self-referential relationships with explicit DTO mapping."""

    class NodeDTO(DTO[Node]):
        config = DTOConfig(
            include_relationships=True,
            mapped={
                Node.parent_node: Optional["NodeDTO"],
                Node.child_nodes: list["NodeDTO"],
            },
        )

    # Test that NodeDTO correctly includes parent_node and child_nodes
    node_fields = NodeDTO.model_fields  # type: ignore[attr-defined]
    assert "parent_node" in node_fields
    assert node_fields["parent_node"].annotation == NodeDTO | None
    assert "child_nodes" in node_fields
    assert node_fields["child_nodes"].annotation == list[NodeDTO]

    # Test instantiation (no infinite recursion)
    root_node_data = {"id": 1, "name": "Root"}
    root_node = NodeDTO.model_validate(root_node_data)  # type: ignore[attr-defined]

    child_node_data = {"id": 2, "name": "Child", "parent_node": root_node}
    child_node = NodeDTO.model_validate(child_node_data)  # type: ignore[attr-defined]

    root_node.child_nodes = [child_node]  # type: ignore[attr-defined]

    assert root_node.id == 1  # type: ignore[attr-defined]
    assert root_node.name == "Root"  # type: ignore[attr-defined]
    assert root_node.parent_node is None  # type: ignore[attr-defined]
    assert len(root_node.child_nodes) == 1  # type: ignore[attr-defined]
    assert root_node.child_nodes[0].id == 2  # type: ignore[attr-defined]
    assert root_node.child_nodes[0].name == "Child"  # type: ignore[attr-defined]
    assert root_node.child_nodes[0].parent_node.id == 1  # type: ignore[attr-defined]
