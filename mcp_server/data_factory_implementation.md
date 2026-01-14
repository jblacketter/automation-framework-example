# A2. Data Factory Server - Implementation Plan

**Date:** 2026-01-13
**Status:** For Codex Review

---

## Overview

Implement the Data Factory MCP server to expose `factories/` for test data generation.

**Existing Factories:**
| Builder | Dataclass | Has `to_api_payload()` | Has `build_many()` |
|---------|-----------|------------------------|---------------------|
| `BookingBuilder` | `Booking` | ✅ Yes | ✅ Yes |
| `GuestBuilder` | `Guest` | ❌ No | ✅ Yes |
| `RoomBuilder` | `Room` | ✅ Yes | ✅ Yes |

**Builder Patterns Observed:**
- Fluent API: `with_name()`, `with_price()`, `for_nights()`, etc.
- All have `build()` → dataclass and `build_many(count)` → list
- Use Faker for random data generation
- Some methods set multiple fields (e.g., `as_suite()` sets type + price range)

---

## File Structure

```
mcp_server/
├── __init__.py
├── test_runner_server.py      # Existing
├── data_factory_server.py     # NEW - main server
└── data_factory_implementation.md  # This plan
```

Single file implementation (`data_factory_server.py`) - no separate modules needed for this scope.

---

## Tool Implementations

### 1. `list_factories`

**Purpose:** Return available factory classes from `factories/`.

**Implementation Approach:**
```python
def list_factories() -> dict[str, Any]:
    """Scan factories/ module and return builder classes."""

    # 1. Import factories module
    # 2. Iterate through factories.__all__ or dir(factories)
    # 3. For each class ending in "Builder":
    #    - Get module path
    #    - Check for build_many() to determine batch support
    #    - Check if product has to_api_payload() for payload support
    # 4. Return structured list
```

**Key Logic:**
- Use `factories.__all__` (already defined: `["BookingBuilder", "GuestBuilder", "RoomBuilder"]`)
- Determine `product_type` by calling `build()` and checking `type(result).__name__`
- Check `supports_payload` by checking `hasattr(product, 'to_api_payload')`
- Check `supports_batch` by checking `hasattr(builder, 'build_many')`

**Edge Cases:**
- Factory import fails → skip, add to warnings
- Empty `__all__` → return empty list with warning

---

### 2. `get_factory_schema`

**Purpose:** Inspect a factory and return its fields, defaults, and override keys.

**Implementation Approach:**
```python
def get_factory_schema(factory: str) -> dict[str, Any]:
    """Introspect builder class and product dataclass."""

    # 1. Get builder class by name
    # 2. Get product dataclass by calling build() once
    # 3. Extract fields from dataclass using dataclasses.fields()
    # 4. Extract builder methods that look like setters (with_*, for_*, as_*)
    # 5. Map fields to types, required status, defaults
```

**Key Logic:**

**Field Extraction (from dataclass):**
```python
import dataclasses

product = builder_class().build()
product_type = type(product)

fields = []
for f in dataclasses.fields(product_type):
    field_info = {
        "name": f.name,
        "type": _type_to_str(f.type),  # e.g., "str", "int", "list[str]"
        "required": f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING,
        "default": _get_default_repr(f),  # "random" for generated, actual value, or null
    }
    fields.append(field_info)
```

**Override Keys (from builder methods):**
```python
# Scan builder methods for setter patterns
override_patterns = ["with_", "for_", "as_", "checking_", "of_"]
overrides = []
for method_name in dir(builder_class):
    if any(method_name.startswith(p) for p in override_patterns):
        if not method_name.startswith("_"):
            overrides.append(method_name)
```

**Edge Cases:**
- Unknown factory name → `{"error": "Factory not found"}`
- Non-dataclass product → return partial schema with warning
- Builder method introspection fails → skip method, add warning

---

### 3. `generate_data`

**Purpose:** Generate a single record using a factory with optional overrides.

**Implementation Approach:**
```python
def generate_data(
    factory: str,
    overrides: Optional[dict[str, Any]] = None,
    seed: Optional[int] = None,
) -> dict[str, Any]:
    """Build one record, applying overrides to builder methods."""

    # 1. Get builder class
    # 2. Create builder instance
    # 3. Apply overrides by calling builder methods
    #    Precedence: exact method name > alias map > smart mapping
    # 4. Call build()
    # 5. Serialize result (to_api_payload or dataclass → dict)
```

**Override Application Logic:**
```python
builder = builder_class()
warnings = []

if overrides:
    for key, value in overrides.items():
        # Try direct method: with_{key}(value)
        method_name = f"with_{key}"
        if hasattr(builder, method_name):
            method = getattr(builder, method_name)
            builder = method(value)
        # Try other patterns: for_{key}, as_{key}
        elif hasattr(builder, f"for_{key}"):
            builder = getattr(builder, f"for_{key}")(value)
        elif hasattr(builder, f"as_{key}"):
            builder = getattr(builder, f"as_{key}")()  # Usually no-arg
        else:
            warnings.append(f"Unknown override: {key}")

product = builder.build()
```

**Serialization Logic:**
```python
def _serialize_product(product) -> tuple[dict, str]:
    """Serialize product to JSON-safe dict."""

    # Priority 1: to_api_payload() if available
    if hasattr(product, 'to_api_payload'):
        return product.to_api_payload(), "to_api_payload"

    # Priority 2: dataclass → asdict
    if dataclasses.is_dataclass(product):
        return _dataclass_to_dict(product), "dataclass"

    # Priority 3: __dict__
    return vars(product), "dict"

def _dataclass_to_dict(obj) -> dict:
    """Convert dataclass to dict, handling nested objects and dates."""
    result = {}
    for f in dataclasses.fields(obj):
        value = getattr(obj, f.name)
        if dataclasses.is_dataclass(value):
            value = _dataclass_to_dict(value)
        elif isinstance(value, date):
            value = value.isoformat()
        result[f.name] = value
    return result
```

**Edge Cases:**
- Unknown factory → `{"error": "Factory not found"}`
- Invalid override type (e.g., string for int) → catch TypeError, return error
- Override method raises → catch, return error with details
- Unknown override keys → ignore, add to warnings
- `deposit_paid` maps to `with_deposit()`/`without_deposit()` only for boolean values

---

### 4. `generate_batch`

**Purpose:** Generate multiple records using a factory.

**Implementation Approach:**
```python
def generate_batch(
    factory: str,
    count: int = 5,
    overrides: Optional[dict[str, Any]] = None,
    seed: Optional[int] = None,
) -> dict[str, Any]:
    """Build multiple records."""

    # Option A: Use build_many() if overrides are None
    # Option B: Loop and call generate_data() for each

    # For consistency with overrides, use loop approach:
    results = []
    for _ in range(count):
        result = _build_single(builder_class, overrides)
        results.append(result)
```

**Count Limits:**
```python
MAX_BATCH_SIZE = 100

if count <= 0:
    return {"error": "count must be > 0"}
if count > MAX_BATCH_SIZE:
    count = MAX_BATCH_SIZE
    warnings.append(f"count capped at {MAX_BATCH_SIZE}")
```

**Edge Cases:**
- `count <= 0` → error
- `count > MAX_BATCH_SIZE` → cap and warn
- Factory not found → error (same as generate_data)

---

## Helper Functions

```python
# Type conversion for schema
def _type_to_str(type_hint) -> str:
    """Convert type hint to readable string."""
    # Handle Optional, list, etc.
    origin = get_origin(type_hint)
    if origin is Union:
        # Optional[X] → "X" or "X | None"
        ...
    if origin is list:
        args = get_args(type_hint)
        return f"list[{_type_to_str(args[0])}]" if args else "list"
    return getattr(type_hint, '__name__', str(type_hint))

# Default representation
def _get_default_repr(field: dataclasses.Field) -> Any:
    """Get default value representation."""
    if field.default is not dataclasses.MISSING:
        return field.default
    if field.default_factory is not dataclasses.MISSING:
        return "[]" if "list" in str(field.type) else "generated"
    return "random"  # Generated by Faker in builder
```

---

## Server Setup

```python
from fastmcp import FastMCP

mcp = FastMCP("data-factory")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FACTORIES_MODULE = "factories"

# Lazy import factories to avoid import errors at startup
_factories_cache: Optional[dict] = None

def _get_factories() -> dict[str, type]:
    """Lazy load and cache factory classes."""
    global _factories_cache
    if _factories_cache is None:
        import factories
        _factories_cache = {
            name: getattr(factories, name)
            for name in factories.__all__
        }
    return _factories_cache
```

---

## Override Aliases

Add a small alias map for project-specific naming differences:
- `room_type` → `of_type`
- `room_name` → `with_name` / `with_room_number`
- `check_in` → `checking_in`
- `check_out` → `checking_out`
- `total_price` → `with_price`
- `deposit_paid` → `with_deposit` / `without_deposit` (bool only)

Precedence: exact method name > alias map > smart mapping.

---

## Randomness / Seeding

If `seed` is provided:
- Seed Python's `random` and any local `Faker` instances.
- Seed applies per call only; it should not be stored globally.
  
If `seed` is not provided, behavior remains fully random.

---

## Testing Approach

### Manual Testing
```bash
# Start server
cd mcp_server && python data_factory_server.py

# Test via MCP inspector or Claude Desktop
```

### Automated Tests (Optional - if time permits)
```python
# tests/test_data_factory_server.py

def test_list_factories():
    result = list_factories()
    assert "factories" in result
    assert len(result["factories"]) == 3
    names = [f["name"] for f in result["factories"]]
    assert "BookingBuilder" in names

def test_get_factory_schema_booking():
    result = get_factory_schema("BookingBuilder")
    assert result["factory"] == "BookingBuilder"
    assert "fields" in result
    field_names = [f["name"] for f in result["fields"]]
    assert "guest" in field_names
    assert "check_in" in field_names

def test_generate_data_with_overrides():
    result = generate_data("RoomBuilder", {"price": 999, "room_type": "Suite"})
    assert result["data"]["roomPrice"] == 999  # to_api_payload key

def test_generate_batch_caps_count():
    result = generate_batch("GuestBuilder", count=200)
    assert len(result["data"]) == 100
    assert "count capped" in result["warnings"][0]
```

---

## Implementation Order

1. **Server skeleton** - FastMCP setup, imports, constants
2. **`list_factories`** - Factory discovery (simplest tool)
3. **`get_factory_schema`** - Introspection logic
4. **`generate_data`** - Core generation with overrides
5. **`generate_batch`** - Batch wrapper
6. **Manual testing** - Test all tools against real factories
7. **Edge case handling** - Error paths, warnings

---

## Codex Review Decisions

### 1. Override Mapping Strategy
**Decision:** Smart matching with signature checks + alias map; still allow exact method names.

**Alias Map (project-specific):**
```python
OVERRIDE_ALIASES = {
    # RoomBuilder
    "room_type": "of_type",
    "room_name": "with_name",
    # BookingBuilder
    "check_in": "checking_in",
    "check_out": "checking_out",
    "total_price": "with_price",
    "deposit_paid": "_deposit_flag",  # Special handling: True→with_deposit(), False→without_deposit()
    "nights": "for_nights",
    "days_from_now": "starting_in_days",
    # GuestBuilder
    "firstname": "with_firstname",
    "lastname": "with_lastname",
}
```

**Signature-Aware Logic:**
```python
def _apply_override(builder, key: str, value: Any) -> tuple[Any, Optional[str]]:
    """Apply override, respecting method signatures."""

    # Resolve alias
    method_name = OVERRIDE_ALIASES.get(key, f"with_{key}")

    # Special case: deposit_paid boolean
    if key == "deposit_paid":
        method_name = "with_deposit" if value else "without_deposit"
        value = None  # No-arg call

    if not hasattr(builder, method_name):
        # Try other patterns
        for pattern in [f"for_{key}", f"as_{key}", key]:
            if hasattr(builder, pattern):
                method_name = pattern
                break
        else:
            return builder, f"Unknown override: {key}"

    method = getattr(builder, method_name)
    sig = inspect.signature(method)
    params = [p for p in sig.parameters.values() if p.name != 'self']

    # No-arg method (e.g., as_suite, with_deposit)
    if len(params) == 0:
        if value is not None:
            return builder, f"Method {method_name}() takes no arguments, ignoring value"
        return method(), None

    # Method expects argument
    if value is None:
        return builder, f"Method {method_name}() requires a value"

    return method(value), None
```

### 2. Nested Override Support
**Decision:** Support `guest` only for `BookingBuilder`; warn on other nested structures.

```python
def _apply_overrides(builder, builder_name: str, overrides: dict) -> tuple[Any, list[str]]:
    warnings = []

    for key, value in overrides.items():
        if isinstance(value, dict):
            # Only support guest nested override
            if builder_name == "BookingBuilder" and key == "guest":
                guest = GuestBuilder()
                for gk, gv in value.items():
                    guest, warn = _apply_override(guest, gk, gv)
                    if warn:
                        warnings.append(f"guest.{gk}: {warn}")
                builder = builder.for_guest(guest.build())
            else:
                warnings.append(f"Nested override '{key}' not supported (only 'guest' for BookingBuilder)")
        else:
            builder, warn = _apply_override(builder, key, value)
            if warn:
                warnings.append(warn)

    return builder, warnings
```

### 3. Randomness Control
**Decision:** Add optional `seed` parameter for deterministic outputs.

```python
def generate_data(
    factory: str,
    overrides: Optional[dict[str, Any]] = None,
    seed: Optional[int] = None,  # NEW
) -> dict[str, Any]:
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)
    # ... rest of implementation
```

### 4. Caching
**Decision:** Cache class/schema lookups; never cache anything derived from random instances.

```python
_factory_classes: dict[str, type] = {}  # Cached at startup
_schema_cache: dict[str, dict] = {}     # Cached after first introspection

def _get_factory_class(name: str) -> Optional[type]:
    if not _factory_classes:
        import factories
        for cls_name in factories.__all__:
            _factory_classes[cls_name] = getattr(factories, cls_name)
    return _factory_classes.get(name)
```

---

## Refined Implementation Details

### Type Inference Without Calling build()

**Problem:** Original plan called `build()` to get product type, which has side effects.

**Solution:** Use return type hints or name mapping.

```python
def _get_product_type(builder_class: type) -> Optional[type]:
    """Infer product type without instantiating."""

    # Option 1: Check build() return type hint
    build_method = getattr(builder_class, 'build', None)
    if build_method:
        hints = get_type_hints(build_method)
        if 'return' in hints:
            return hints['return']

    # Option 2: Name convention (BookingBuilder → Booking)
    class_name = builder_class.__name__
    if class_name.endswith('Builder'):
        product_name = class_name[:-7]  # Remove "Builder"
        # Look for dataclass in same module
        module = inspect.getmodule(builder_class)
        if hasattr(module, product_name):
            return getattr(module, product_name)

    return None
```

### Batch Generation Optimization

```python
def generate_batch(
    factory: str,
    count: int = 5,
    overrides: Optional[dict[str, Any]] = None,
    seed: Optional[int] = None,
) -> dict[str, Any]:
    # Validate overrides once
    builder_class = _get_factory_class(factory)
    if not builder_class:
        return {"error": "Factory not found"}

    # Use build_many when no overrides
    if not overrides:
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        builder = builder_class()
        products = builder.build_many(min(count, MAX_BATCH_SIZE))
        return {
            "factory": factory,
            "count": len(products),
            "data": [_serialize_product(p)[0] for p in products],
            "warnings": [] if count <= MAX_BATCH_SIZE else [f"count capped at {MAX_BATCH_SIZE}"]
        }

    # With overrides: validate once, apply to each
    test_builder = builder_class()
    _, validation_warnings = _apply_overrides(test_builder, factory, overrides)

    results = []
    for i in range(min(count, MAX_BATCH_SIZE)):
        if seed is not None:
            random.seed(seed + i)  # Vary seed per item
            Faker.seed(seed + i)
        builder = builder_class()
        builder, _ = _apply_overrides(builder, factory, overrides)  # Warnings already captured
        product = builder.build()
        results.append(_serialize_product(product)[0])

    warnings = validation_warnings.copy()
    if count > MAX_BATCH_SIZE:
        warnings.append(f"count capped at {MAX_BATCH_SIZE}")

    return {
        "factory": factory,
        "count": len(results),
        "data": results,
        "warnings": warnings
    }
```

---

## Estimated Complexity (Revised)

| Component | Lines of Code | Effort |
|-----------|---------------|--------|
| Server setup + helpers | ~60 | Low |
| `list_factories` | ~40 | Low |
| `get_factory_schema` | ~70 | Medium |
| `generate_data` | ~90 | Medium |
| `generate_batch` | ~50 | Low |
| Override mapping + aliases | ~60 | Medium |
| Error handling + edge cases | ~40 | Low |
| **Total** | ~410 | **Medium** |

---

## Decision Log

| Question | Decision | Rationale |
|----------|----------|-----------|
| Type inference | Return hints + name mapping, no build() call | Avoid side effects |
| Override mapping | Smart + alias map + signature-aware | User-friendly, safe |
| Nested overrides | `guest` only for BookingBuilder | Scoped MVP, warn on others |
| Randomness | Optional `seed` param | Low effort, useful for deterministic tests |
| Caching | Cache classes/schema, not random data | Performance without stale data |
| Batch mode | Use `build_many` when no overrides | Efficient, validate once |
