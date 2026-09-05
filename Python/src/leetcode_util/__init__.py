"""Reusable data structures and JSON adapters for LeetCode problems."""

from .adapters import (
    from_json_value,
    list_node_to_list,
    list_to_list_node,
    list_to_tree_node,
    to_json_value,
    tree_node_to_list,
)
from .list_node import ListNode
from .tree_node import TreeNode

__all__ = [
    "ListNode",
    "TreeNode",
    "from_json_value",
    "to_json_value",
    "list_to_list_node",
    "list_node_to_list",
    "list_to_tree_node",
    "tree_node_to_list",
]
