t"""
Data Factory MCP Server.

Exposes factories/ builders for test data generation.
"""

from __future__ import annotations

import dataclasses
import importlib
import inspect
import random
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional, Union, get_args, get_origin, get_type_hints

from fastmcp import FastMCP

try:
    from faker import Faker
except ImportError:  # pragma: no cover - Faker is listed in requirements
    Faker = None  # type: ignore[assignment]

mcp = FastMCP("data-factory")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FACTORIES_MODULE = "factories"
MAX_BATCH_SIZE = 100

OVERRIDE_PREFIXES = ("with_", "for_", "as_", "checking_", "of_", "without_")

ALIAS_MAP = {
    "room_type": ["of_type"],
    "room_name": ["with_room_number", "with_name"],
    "check_in": ["checking_in"],
    "check_out": ["checking_out"],
    "total_price": ["with_price"],
}

_FACTORY_CACHE: Optional[dict[str, type]] = None
_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}


def _seed_random(seed: Optional[int]) -> None:
    if seed is None:
        return
    random.seed(seed)
    if Faker is not None:
        try:
            Faker.seed(seed)
        except Exception:
            pass


def _load_factories() -> tuple[dict[str, type], list[str]]:
    warnings: list[str] = []
    try:
        factories = importlib.import_module(FACTORIES_MODULE)
    except Exception as exc:
        return {}, [f"Failed to import factories module: {exc}"]

    names = getattr(factories, "__all__", None)
    if not names:
        names = [name for name in dir(factories) if name.endswith("Builder")]
        if not names:
            warnings.append("No factories discovered")

    discovered: dict[str, type] = {}
    for name in names:
        try:
            factory_cls = getattr(factories, name)
        except AttributeError:
            warnings.append(f"Factory '{name}' not found in module")
            continue
        if not isinstance(factory_cls, type):
            continue
        if not name.endswith("Builder"):
            continue
        discovered[name] = factory_cls

    return discovered, warnings


def _get_factories() -> tuple[dict[str, type], list[str]]:
    global _FACTORY_CACHE
    if _FACTORY_CACHE is not None:
        return _FACTORY_CACHE, []
    factories, warnings = _load_factories()
    _FACTORY_CACHE = factories
    return factories, warnings


def _get_product_type(builder_cls: type) -> str:
    try:
        hints = get_type_hints(builder_cls.build)
    except Exception:
        hints = {}
    product = hints.get("return")
    if hasattr(product, "__name__"):
        return product.__name__
    name = builder_cls.__name__
    return name[: -len("Builder")] if name.endswith("Builder") else name


def _get_product_class(builder_cls: type, product_type: str) -> Optional[type]:
    module = inspect.getmodule(builder_cls)
    if not module:
        return None
    candidate = getattr(module, product_type, None)
    if isinstance(candidate, type):
        return candidate
    for value in vars(module).values():
        if isinstance(value, type) and dataclasses.is_dataclass(value):
            if value.__name__ == product_type:
                return value
    return None


def _type_to_str(type_hint: Any) -> str:
    origin = get_origin(type_hint)
    if origin is None:
        return getattr(type_hint, "__name__", str(type_hint))
    if origin is list:
        args = get_args(type_hint)
        inner = _type_to_str(args[0]) if args else "Any"
        return f"list[{inner}]"
    if origin is dict:
        args = get_args(type_hint)
        key = _type_to_str(args[0]) if len(args) > 0 else "Any"
        value = _type_to_str(args[1]) if len(args) > 1 else "Any"
        return f"dict[{key}, {value}]"
    if origin is tuple:
        args = get_args(type_hint)
        inner = ", ".join(_type_to_str(arg) for arg in args) if args else "Any"
        return f"tuple[{inner}]"
    if origin is Union:
        args = [arg for arg in get_args(type_hint)]
        if type(None) in args:
            args = [arg for arg in args if arg is not type(None)]
            inner = _type_to_str(args[0]) if len(args) == 1 else " | ".join(
                _type_to_str(arg) for arg in args
            )
            return f"{inner} | None"
        return " | ".join(_type_to_str(arg) for arg in args)
    return str(type_hint)


def _get_default_repr(field: dataclasses.Field[Any]) -> Any:
    if field.default is not dataclasses.MISSING:
        return field.default
    if field.default_factory is not dataclasses.MISSING:  # type: ignore[comparison-overlap]
        if field.default_factory is list:  # type: ignore[comparison-overlap]
            return []
        return "generated"
    return "random"


def _serialize_value(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        result = {}
        for field in dataclasses.fields(value):
            result[field.name] = _serialize_value(getattr(value, field.name))
        return result
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize_value(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    return value


def _serialize_product(product: Any) -> tuple[dict[str, Any], str]:
    if hasattr(product, "to_api_payload"):
        payload = product.to_api_payload()
        return _serialize_value(payload), "to_api_payload"
    if dataclasses.is_dataclass(product):
        return _serialize_value(product), "dataclass"
    if hasattr(product, "__dict__"):
        return _serialize_value(vars(product)), "dict"
    raise ValueError("Unsupported product type for serialization")


def _coerce_date(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return value
    return value


def _invoke_method(builder: Any, method_name: str, value: Any) -> tuple[bool, Any, Optional[str]]:
    method = getattr(builder, method_name, None)
    if method is None or not callable(method):
        return False, builder, None

    signature = inspect.signature(method)
    params = [p for p in signature.parameters.values() if p.name != "self"]
    required = [
        p
        for p in params
        if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]

    try:
        if not params:
            if value is True or value is None:
                result = method()
            else:
                return False, builder, None
        elif len(params) == 1:
            result = method(value)
        else:
            if isinstance(value, dict):
                result = method(**value)
            elif isinstance(value, (list, tuple)) and len(value) >= len(required):
                result = method(*value)
            else:
                return False, builder, None
    except Exception as exc:
        return False, builder, f"Override '{method_name}' failed: {exc}"

    if result is not None and isinstance(result, builder.__class__):
        builder = result
    return True, builder, None


def _apply_guest_override(
    builder: Any, overrides: dict[str, Any], warnings: list[str]
) -> tuple[Any, Optional[str]]:
    try:
        from factories.guest_builder import GuestBuilder, Guest
    except Exception as exc:
        return builder, f"Failed to import GuestBuilder: {exc}"

    if isinstance(overrides, Guest):
        return builder.for_guest(overrides), None
    if not isinstance(overrides, dict):
        warnings.append("guest override must be a dict or Guest instance")
        return builder, None

    guest_builder = GuestBuilder()
    guest_builder, guest_warnings, error = _apply_overrides(
        guest_builder, overrides, allow_guest=False
    )
    if error:
        return builder, error
    for warning in guest_warnings:
        warnings.append(f"guest.{warning}")
    guest = guest_builder.build()
    return builder.for_guest(guest), None


def _apply_alias_override(
    builder: Any, key: str, value: Any
) -> tuple[bool, Any, Optional[str]]:
    if key == "deposit_paid":
        if value is True:
            return _invoke_method(builder, "with_deposit", None)
        if value is False:
            return _invoke_method(builder, "without_deposit", None)
        return False, builder, "deposit_paid must be a boolean"

    if key == "room_name":
        if isinstance(value, int):
            return _invoke_method(builder, "with_room_number", value)
        if isinstance(value, str) and value.isdigit():
            return _invoke_method(builder, "with_room_number", int(value))
        return _invoke_method(builder, "with_name", value)

    if key in ("check_in", "check_out"):
        value = _coerce_date(value)

    for method_name in ALIAS_MAP.get(key, []):
        handled, builder, error = _invoke_method(builder, method_name, value)
        if handled or error:
            return handled, builder, error

    return False, builder, None


def _apply_overrides(
    builder: Any, overrides: Optional[dict[str, Any]], allow_guest: bool = True
) -> tuple[Any, list[str], Optional[str]]:
    warnings: list[str] = []
    if not overrides:
        return builder, warnings, None

    for key, value in overrides.items():
        handled, builder, error = _invoke_method(builder, key, value)
        if error:
            return builder, warnings, error
        if handled:
            continue

        if allow_guest and key == "guest" and builder.__class__.__name__ == "BookingBuilder":
            builder, error = _apply_guest_override(builder, value, warnings)
            if error:
                return builder, warnings, error
            continue

        handled, builder, error = _apply_alias_override(builder, key, value)
        if error:
            return builder, warnings, error
        if handled:
            continue

        for prefix in OVERRIDE_PREFIXES:
            method_name = f"{prefix}{key}"
            handled, builder, error = _invoke_method(builder, method_name, value)
            if error:
                return builder, warnings, error
            if handled:
                break

        if not handled:
            warnings.append(f"Unknown override: {key}")

    return builder, warnings, None


def _get_builder_methods(builder_cls: type) -> list[str]:
    methods = []
    for name, value in inspect.getmembers(builder_cls, predicate=callable):
        if name.startswith("_"):
            continue
        if name.startswith(OVERRIDE_PREFIXES):
            methods.append(name)
    return sorted(set(methods))


@mcp.tool()
def list_factories() -> dict[str, Any]:
    factories, warnings = _get_factories()
    results = []
    for name, builder_cls in factories.items():
        product_type = _get_product_type(builder_cls)
        product_cls = _get_product_class(builder_cls, product_type)
        supports_payload = bool(product_cls and hasattr(product_cls, "to_api_payload"))
        supports_batch = callable(getattr(builder_cls, "build_many", None))
        results.append(
            {
                "name": name,
                "module": builder_cls.__module__,
                "product_type": product_type,
                "supports_batch": supports_batch,
                "supports_payload": supports_payload,
            }
        )
    return {"factories": results, "warnings": warnings}


@mcp.tool()
def get_factory_schema(factory: str) -> dict[str, Any]:
    if factory in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[factory]

    factories, warnings = _get_factories()
    builder_cls = factories.get(factory)
    if not builder_cls:
        return {"error": "Factory not found"}

    product_type = _get_product_type(builder_cls)
    product_cls = _get_product_class(builder_cls, product_type)

    fields: list[dict[str, Any]] = []
    if product_cls and dataclasses.is_dataclass(product_cls):
        for field in dataclasses.fields(product_cls):
            fields.append(
                {
                    "name": field.name,
                    "type": _type_to_str(field.type),
                    "required": field.default is dataclasses.MISSING
                    and field.default_factory is dataclasses.MISSING,
                    "default": _get_default_repr(field),
                }
            )
    else:
        warnings.append("Product type is not a dataclass; field metadata unavailable")

    override_keys = {field["name"] for field in fields}
    override_keys.update(ALIAS_MAP.keys())

    schema = {
        "factory": factory,
        "product_type": product_type,
        "fields": fields,
        "overrides": sorted(override_keys),
        "override_methods": _get_builder_methods(builder_cls),
        "notes": [
            "Overrides map to builder methods when available",
            "Exact method names take precedence over aliases",
        ],
        "warnings": warnings,
    }

    _SCHEMA_CACHE[factory] = schema
    return schema


@mcp.tool()
def generate_data(
    factory: str,
    overrides: Optional[dict[str, Any]] = None,
    seed: Optional[int] = None,
) -> dict[str, Any]:
    factories, _warnings = _get_factories()
    builder_cls = factories.get(factory)
    if not builder_cls:
        return {"error": "Factory not found"}

    _seed_random(seed)
    builder = builder_cls()
    builder, warnings, error = _apply_overrides(builder, overrides)
    if error:
        return {"error": error}

    try:
        product = builder.build()
        data, source = _serialize_product(product)
    except Exception as exc:
        return {"error": f"Failed to build product: {exc}"}

    return {
        "factory": factory,
        "source": source,
        "data": data,
        "warnings": warnings,
    }


@mcp.tool()
def generate_batch(
    factory: str,
    count: int = 5,
    overrides: Optional[dict[str, Any]] = None,
    seed: Optional[int] = None,
) -> dict[str, Any]:
    if count <= 0:
        return {"error": "count must be > 0"}

    warnings: list[str] = []
    if count > MAX_BATCH_SIZE:
        warnings.append(f"count capped at {MAX_BATCH_SIZE}")
        count = MAX_BATCH_SIZE

    factories, _warnings = _get_factories()
    builder_cls = factories.get(factory)
    if not builder_cls:
        return {"error": "Factory not found"}

    _seed_random(seed)

    if overrides is None:
        try:
            builder = builder_cls()
            products = builder.build_many(count)
        except Exception as exc:
            return {"error": f"Failed to build batch: {exc}"}
        data = [_serialize_product(product)[0] for product in products]
        return {"factory": factory, "count": count, "data": data, "warnings": warnings}

    data = []
    builder = builder_cls()
    builder, override_warnings, error = _apply_overrides(builder, overrides)
    if error:
        return {"error": error}
    warnings.extend(override_warnings)

    for _ in range(count):
        try:
            product = builder.build()
            data.append(_serialize_product(product)[0])
        except Exception as exc:
            return {"error": f"Failed to build product: {exc}"}

    return {"factory": factory, "count": count, "data": data, "warnings": warnings}


if __name__ == "__main__":
    mcp.run()
