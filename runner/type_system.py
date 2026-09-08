from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SCALAR_TYPES = {"bool", "float", "int", "long", "string"}


@dataclass(frozen=True)
class TypeRef:
    name: str
    item: TypeRef | None = None


def parse_type(expression: str) -> TypeRef:
    expression = expression.strip().lower()
    if expression in SCALAR_TYPES:
        return TypeRef(expression)
    if expression.startswith("list[") and expression.endswith("]"):
        return TypeRef("list", parse_type(expression[5:-1]))
    raise ValueError(f"Unsupported canonical type: {expression!r}")


def java_type(type_ref: TypeRef) -> str:
    scalars = {
        "bool": "boolean",
        "float": "double",
        "int": "int",
        "long": "long",
        "string": "String",
    }
    if type_ref.name == "list":
        if type_ref.item is None:
            raise ValueError("A list type requires an item type")
        return f"{java_type(type_ref.item)}[]"
    return scalars[type_ref.name]


def java_expression(value: Any, type_ref: TypeRef) -> str:
    if type_ref.name == "list":
        if value is None:
            return "null"
        if not isinstance(value, list):
            raise TypeError(f"Expected a list for {type_ref}, got {type(value).__name__}")
        if type_ref.item is None:
            raise ValueError("A list type requires an item type")
        items = ", ".join(java_expression(item, type_ref.item) for item in value)
        return f"new {java_type(type_ref)}{{{items}}}"

    if type_ref.name == "bool":
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got {type(value).__name__}")
        return str(value).lower()
    if type_ref.name == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value).__name__}")
        return str(value)
    if type_ref.name == "long":
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Expected long, got {type(value).__name__}")
        return f"{value}L"
    if type_ref.name == "float":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Expected float, got {type(value).__name__}")
        return repr(float(value))
    if type_ref.name == "string":
        if value is None:
            return "null"
        if not isinstance(value, str):
            raise TypeError(f"Expected string, got {type(value).__name__}")
        return _java_string(value)
    raise ValueError(f"Cannot create a Java expression for {type_ref.name!r}")


def cpp_type(type_ref: TypeRef) -> str:
    scalars = {
        "bool": "bool",
        "float": "double",
        "int": "int",
        "long": "long long",
        "string": "std::string",
    }
    if type_ref.name == "list":
        if type_ref.item is None:
            raise ValueError("A list type requires an item type")
        return f"std::vector<{cpp_type(type_ref.item)}>"
    return scalars[type_ref.name]


def cpp_expression(value: Any, type_ref: TypeRef) -> str:
    if type_ref.name == "list":
        if not isinstance(value, list):
            raise TypeError(f"Expected a list for {type_ref}, got {type(value).__name__}")
        if type_ref.item is None:
            raise ValueError("A list type requires an item type")
        items = ", ".join(cpp_expression(item, type_ref.item) for item in value)
        return f"{cpp_type(type_ref)}{{{items}}}"

    if type_ref.name == "bool":
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got {type(value).__name__}")
        return str(value).lower()
    if type_ref.name == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value).__name__}")
        return str(value)
    if type_ref.name == "long":
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Expected long, got {type(value).__name__}")
        return f"{value}LL"
    if type_ref.name == "float":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Expected float, got {type(value).__name__}")
        return repr(float(value))
    if type_ref.name == "string":
        if not isinstance(value, str):
            raise TypeError(f"Expected string, got {type(value).__name__}")
        return _cpp_string(value)
    raise ValueError(f"Cannot create a C++ expression for {type_ref.name!r}")


def _java_string(value: str) -> str:
    escaped: list[str] = []
    for character in value:
        replacements = {
            '"': '\\"',
            "\\": "\\\\",
            "\b": "\\b",
            "\f": "\\f",
            "\n": "\\n",
            "\r": "\\r",
            "\t": "\\t",
        }
        if character in replacements:
            escaped.append(replacements[character])
        elif ord(character) < 0x20:
            escaped.append(f"\\u{ord(character):04x}")
        else:
            escaped.append(character)
    return f'"{"".join(escaped)}"'


def _cpp_string(value: str) -> str:
    return f"std::string({_java_string(value)})"

