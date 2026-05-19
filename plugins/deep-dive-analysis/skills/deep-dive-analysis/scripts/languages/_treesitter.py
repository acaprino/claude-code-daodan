"""
Optional tree-sitter loader.

Returns a (parser, language) pair or None if tree-sitter or the requested
grammar is unavailable. Adapters call this and fall back to regex parsing
when it returns None.

We prefer `tree-sitter-language-pack` (modern, single dependency, bundles
many grammars) and fall back to per-grammar packages
(`tree-sitter-python`, `tree-sitter-java`, etc.) if the user has installed
those directly.

## Caching

`get_parser` is `@lru_cache`-decorated. **Both success and failure are
cached** for the process lifetime. If you install tree-sitter mid-process
(e.g. from a REPL), call `reset_cache()` to drop the negative entries so the
next `get_parser(language)` re-probes the install state.

## Thread-safety

Tree-sitter's C bindings (per all current Python wrappers) are NOT safe for
concurrent `parser.parse(src)` calls from multiple threads. The cache here
returns a SHARED parser instance per language, so callers using
ThreadPoolExecutor over many files will corrupt parse state. Either
serialize calls, or wrap the cache in a `threading.local()` if you must
parallelize -- but the regex-fallback adapters are already pure-Python and
GIL-safe, which is the recommended path for parallel parsing.
"""

from __future__ import annotations

import functools
from typing import Any

__all__ = ["get_parser", "reset_cache", "TreeSitterUnavailable"]


class TreeSitterUnavailable(RuntimeError):
    """
    Raised when an explicit tree-sitter load is requested but no strategy
    succeeds. Not raised by `get_parser` (which returns None for the
    fallback flow); callers wanting a hard error should call
    `require_parser` instead.
    """


# Aliases used by tree-sitter-language-pack.
_LANG_PACK_ALIASES = {
    "python": "python",
    "java": "java",
    "javascript": "javascript",
    "typescript": "typescript",
    "tsx": "tsx",
    "sql": "sql",
}


@functools.lru_cache(maxsize=None)
def get_parser(language: str) -> tuple[Any, Any] | None:
    """
    Return (parser, language_obj) for the requested language, or None if
    tree-sitter is not installed or the grammar is unavailable.

    Result is cached. Call `reset_cache()` after a mid-process install to
    re-probe.
    """
    pack_name = _LANG_PACK_ALIASES.get(language)
    if pack_name is None:
        return None

    # Strategy 1: tree-sitter-language-pack (preferred).
    try:
        from tree_sitter_language_pack import get_parser as _ts_get_parser  # type: ignore
        from tree_sitter_language_pack import get_language as _ts_get_lang  # type: ignore

        parser = _ts_get_parser(pack_name)
        lang_obj = _ts_get_lang(pack_name)
        return parser, lang_obj
    except (ImportError, ModuleNotFoundError, AttributeError):
        pass

    # Strategy 2: tree-sitter-languages (older bundled package).
    try:
        from tree_sitter_languages import get_parser as _ts_get_parser  # type: ignore
        from tree_sitter_languages import get_language as _ts_get_lang  # type: ignore

        parser = _ts_get_parser(pack_name)
        lang_obj = _ts_get_lang(pack_name)
        return parser, lang_obj
    except (ImportError, ModuleNotFoundError, AttributeError):
        pass

    # Strategy 3: individual tree-sitter-<lang> + tree-sitter core.
    try:
        from tree_sitter import Language, Parser  # type: ignore

        # Map our canonical names to import names.
        import_name = {
            "python": "tree_sitter_python",
            "java": "tree_sitter_java",
            "javascript": "tree_sitter_javascript",
            "typescript": "tree_sitter_typescript",
            "tsx": "tree_sitter_typescript",
            "sql": "tree_sitter_sql",
        }.get(pack_name)
        if import_name is None:
            return None
        mod = __import__(import_name)
        # tree-sitter-typescript exposes both language_typescript and language_tsx.
        if pack_name == "typescript":
            lang_capsule = mod.language_typescript()
        elif pack_name == "tsx":
            lang_capsule = mod.language_tsx()
        else:
            lang_capsule = mod.language()
        lang_obj = Language(lang_capsule)
        parser = Parser(lang_obj)
        return parser, lang_obj
    except (ImportError, ModuleNotFoundError, AttributeError):
        return None


def reset_cache() -> None:
    """
    Clear cached parser/language pairs. Use this if tree-sitter was installed
    after the first `get_parser` call and you want subsequent calls to
    re-probe instead of returning the cached `None`.
    """
    get_parser.cache_clear()


def require_parser(language: str) -> tuple[Any, Any]:
    """
    Like `get_parser` but raises `TreeSitterUnavailable` on failure. Use
    when the caller cannot proceed without a tree-sitter parser.
    """
    pair = get_parser(language)
    if pair is None:
        raise TreeSitterUnavailable(
            f"No tree-sitter parser available for {language!r}. "
            f"Install `tree-sitter-language-pack`, `tree-sitter-languages`, "
            f"or the per-language grammar package."
        )
    return pair


def node_text(node: Any, source_bytes: bytes) -> str:
    """Return the source text covered by a tree-sitter node."""
    try:
        return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
    except Exception:
        return ""
