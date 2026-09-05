"""Small Python-native replacement for Java TypeAdapter/TypeAdapters classes."""

from __future__ import annotations

from collections import deque
from typing import Any, Optional

from .list_node import ListNode
from .tree_node import TreeNode


def list_to_list_node(values: list[int]) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    for value in values:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next


def list_node_to_list(head: Optional[ListNode]) -> list[int]:
    values: list[int] = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


def list_to_tree_node(values: list[Optional[int]]) -> Optional[TreeNode]:
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    index = 1
    while queue and index < len(values):
        node = queue.popleft()
        if values[index] is not None:
            node.left = TreeNode(values[index])
            queue.append(node.left)
        index += 1
        if index < len(values) and values[index] is not None:
            node.right = TreeNode(values[index])
            queue.append(node.right)
        index += 1
    return root


def tree_node_to_list(root: Optional[TreeNode]) -> list[Optional[int]]:
    if root is None:
        return []
    values: list[Optional[int]] = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            values.append(None)
        else:
            values.append(node.val)
            queue.extend((node.left, node.right))
    while values and values[-1] is None:
        values.pop()
    return values


def from_json_value(value: Any) -> Any:
    """Recursively decode JSON, including explicitly tagged LeetCode nodes."""
    if isinstance(value, list):
        return [from_json_value(item) for item in value]
    if isinstance(value, dict):
        value_type = value.get("type")
        if value_type == "ListNode":
            return list_to_list_node(value.get("value", []))
        if value_type == "TreeNode":
            return list_to_tree_node(value.get("value", []))
        return {key: from_json_value(item) for key, item in value.items()}
    return value


def to_json_value(value: Any) -> Any:
    """Convert return values to JSON-compatible values for comparison."""
    if isinstance(value, ListNode):
        return list_node_to_list(value)
    if isinstance(value, TreeNode):
        return tree_node_to_list(value)
    if isinstance(value, tuple):
        return [to_json_value(item) for item in value]
    if isinstance(value, list):
        return [to_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: to_json_value(item) for key, item in value.items()}
    return value
