from __future__ import annotations

from collections import deque
from dataclasses import asdict, is_dataclass
from typing import Any


def to_json_value(value: Any) -> Any:
    """Normalize common LeetCode return values into JSON-compatible values."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): to_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_value(item) for item in value]
    if is_dataclass(value):
        return to_json_value(asdict(value))
    if hasattr(value, "val") and hasattr(value, "next"):
        return _linked_list_to_list(value)
    if all(hasattr(value, attribute) for attribute in ("val", "left", "right")):
        return _tree_to_list(value)
    raise TypeError(f"Cannot serialize return value of type {type(value).__name__}")


def _linked_list_to_list(head: Any) -> list[Any]:
    result: list[Any] = []
    visited: set[int] = set()
    current = head
    while current is not None:
        identity = id(current)
        if identity in visited:
            raise ValueError("Cannot serialize a cyclic linked list")
        visited.add(identity)
        result.append(to_json_value(current.val))
        current = current.next
    return result


def _tree_to_list(root: Any) -> list[Any]:
    result: list[Any] = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            result.append(None)
            continue
        result.append(to_json_value(node.val))
        queue.extend((node.left, node.right))

    while result and result[-1] is None:
        result.pop()
    return result

