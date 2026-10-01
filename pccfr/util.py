"""Small standard-library helpers."""
from __future__ import annotations

import json
import os
import resource
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Tuple


class StrictJSONError(ValueError):
    """Raised for duplicate keys or non-finite JSON constants."""


def _unique_object(pairs: Iterable[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise StrictJSONError(f"non-finite JSON number is not permitted: {token}")


def write_json(path: str | Path, value: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def read_json(path: str | Path) -> Any:
    try:
        return json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, StrictJSONError) as exc:
        raise StrictJSONError(f"invalid strict JSON in {path}: {exc}") from exc


def measure(call: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    before_cpu = time.process_time()
    before_wall = time.monotonic()
    value = call()
    usage = resource.getrusage(resource.RUSAGE_SELF)
    value["resource"] = {
        "cpu_seconds": time.process_time() - before_cpu,
        "wall_seconds": time.monotonic() - before_wall,
        "peak_rss_kib": usage.ru_maxrss,
        "workers": 1,
    }
    return value


def atomic_write(path: str | Path, data: bytes) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, p)
