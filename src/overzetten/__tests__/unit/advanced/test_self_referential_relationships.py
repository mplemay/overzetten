from typing import List, Optional

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.sqlalchemy_models import Node


def test_self_referential_relationship_mapping():
    """Test handling of self-referential relationships with explicit DTO mapping."""

    class NodeDTO(DTO[Node]):
        config = DTOConfig(
            include_relationships=True,
            mapped={
                Node.parent_node: Optional["NodeDTO"],
                Node.child_nodes: List["NodeDTO"],
            },
        )

    # Test that NodeDTO correctly includes parent_node and child_nodes
    node_fields = NodeDTO.model_fields
    assert "parent_node" in node_fields
    assert node_fields["parent_node"].annotation is Optional[NodeDTO]
    assert "child_nodes" in node_fields
    assert node_fields["child_nodes"].annotation is List[NodeDTO]

    # Test instantiation (no infinite recursion)
    root_node = NodeDTO(id=1, name="Root")
    child_node = NodeDTO(id=2, name="Child", parent_node=root_node)
    root_node.child_nodes = [child_node]

    assert root_node.id == 1
    assert root_node.name == "Root"
    assert root_node.parent_node is None
    assert len(root_node.child_nodes) == 1
    assert root_node.child_nodes[0].id == 2
    assert root_node.child_nodes[0].name == "Child"
    assert root_node.child_nodes[0].parent_node.id == 1
