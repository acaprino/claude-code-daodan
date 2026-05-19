# Design: add Rust support to deep-dive-analysis

**Date:** 2026-05-19
**Plugin:** `deep-dive-analysis`
**Version target:** 1.8.1 -> 1.9.0 (minor: new language)

## Goal

Add Rust as the 7th supported language to the `languages/` adapter layer, following the same pattern established for Python, Java, JavaScript, TypeScript, SQL, PL/SQL.

## Scope

In:
- New `languages/rust.py` adapter (~400 LOC)
- Hook into dispatch (`__init__.py`), tree-sitter loader (`_treesitter.py`), comment lexer (`comments.py`), classifier (`classifier.py`), comment rewriter (`comment_rewriter.py`), and SKILL.md
- 10 inline smoke tests
- Version bump + commit + push

Out:
- No new agents, commands, or test suites
- No changes to existing adapters
- No new external dependencies beyond what `tree-sitter-language-pack` already provides

## Rust-specific decisions

### File extensions
- `.rs` only. `.rlib` is a binary artifact, not source.

### Comment syntax
- Line: `//`, `///` (outer doc), `//!` (inner doc)
- Block: `/* */`, `/** */` (outer doc), `/*! */` (inner doc)
- Doc-block detection: `///` + `//!` set `is_doc_block=True` on line-style tokens (different from C-style where `is_doc_block` is block-only). The comment lexer adds a `_RUST_SYNTAX` with two line markers (one regular `//`, one doc `///`, one inner-doc `//!`). The state machine needs minor enhancement to set `is_doc_block` for the longer line markers.

### Kind taxonomy additions
Extend `Kind` Literal in `base.py`:
- `"struct"` (Rust struct)
- `"trait"` (Rust trait)
- `"impl"` (Rust impl block; name = type being impl'd, optionally with trait)
- `"mod"` (Rust module declaration)
- `"union"` (Rust union; rare but supported)

### functions vs classes[*].methods
- Top-level `fn` -> `functions[]`
- Methods inside `impl Foo` block -> `classes[*].methods` where the `ClassInfo` has `kind="impl"` and `name="Foo"` (or `name="Foo for Bar"` for trait impls)
- This is consistent with the convention documented in `base.py:ParseResult` docstring after v1.8.1.

### Visibility mapping
- `pub` -> `"public"`
- `pub(crate)`, `pub(super)`, `pub(in path)` -> `"protected"`
- (default, no modifier) -> `"private"`

### Internal vs external imports
- Internal: `use crate::*`, `use super::*`, `use self::*`
- External: everything else (`use std::*`, `use tokio::*`, `use serde::*`, etc.). Rust stdlib AND crates.io packages are both external from the project's perspective.

### External call categories
Pattern-based scanning on receiver paths:
- **database**: `sqlx::*`, `diesel::*`, `tokio_postgres::*`, `redis::*`, `mongodb::*`, `rusqlite::*`
- **network**: `reqwest::*`, `hyper::*`, `std::net::*`, `tokio::net::*`, `actix_web::*`, `axum::*`
- **filesystem**: `std::fs::*`, `tokio::fs::*`, `std::path::Path::*`
- **messaging**: `tokio::sync::mpsc::*`, `tokio::sync::broadcast::*`, `crossbeam::*`, `lapin::*`, `rdkafka::*`
- **ipc**: `std::process::*`, `tokio::process::*`, `std::sync::mpsc::*`, `std::thread::*`

### Complexity patterns
Add to `classifier.COMPLEXITY_PATTERNS_PER_LANG["rust"]`:
- `\\basync\\s+fn\\b`, `\\bawait\\b`
- `\\bunsafe\\b`
- `\\bArc<`, `\\bMutex<`, `\\bRwLock<`, `\\bRefCell<`, `\\bCell<`
- `tokio::spawn`, `std::thread::spawn`
- `mpsc::channel`, `oneshot::channel`, `broadcast::channel`
- `Box<dyn\\s+Future`, `\\bPin<`
- `\\bSend\\s*\\+\\s*Sync\\b`

### Tree-sitter integration
- Add `"rust": "rust"` to `_LANG_PACK_ALIASES`
- Add `"rust": "tree_sitter_rust"` to strategy 3 import map
- `tree-sitter-language-pack` already bundles `tree-sitter-rust`, so no new requirement entry.

## Implementation notes

### Tree-sitter walker scope
Rust's tree-sitter grammar uses these top-level node types:
- `function_item` -> top-level `functions[]`
- `struct_item`, `enum_item`, `trait_item`, `impl_item`, `mod_item`, `union_item`, `type_item` -> `classes[]` with appropriate `kind`
- `use_declaration` -> `imports[]`
- `const_item`, `static_item` -> `constants[]` if name matches `^[A-Z_]+$`

Methods inside `impl_item.body` are extracted into `ClassInfo.methods`.

### Regex fallback scope
Same shape as the tree-sitter path, but using regex over the source text. Patterns:
- `^\\s*(?P<vis>pub(?:\\([^)]*\\))?\\s+)?(?:async\\s+|const\\s+|unsafe\\s+)*fn\\s+(?P<name>\\w+)\\s*(?:<[^>]*>)?\\s*\\((?P<params>[^)]*)\\)`
- `^\\s*(?P<vis>pub(?:\\([^)]*\\))?\\s+)?(struct|enum|trait|union|mod)\\s+(?P<name>\\w+)`
- `^\\s*impl(?:<[^>]*>)?\\s+(?P<name>[\\w:<>, ]+?)(?:\\s+for\\s+(?P<target>[\\w:<>, ]+?))?\\s*\\{`
- `^\\s*use\\s+(?P<path>[\\w:\\*{},\\s]+);`
- `^\\s*(?P<vis>pub(?:\\([^)]*\\))?\\s+)?(?:const|static)\\s+(?P<name>[A-Z_][A-Z0-9_]*)\\s*:`

### Comment syntax wiring
`_RUST_SYNTAX = CommentSyntax(line_markers=("///", "//!", "//"), block_open="/*", block_close="*/", doc_block_open="/**", string_delimiters=...)`.

Order matters: longer markers first so `///` doesn't get matched as `//`. The state machine already checks `for marker in syntax.line_markers` in order, so listing the doc markers first is sufficient. But the lexer also needs to know which line marker matched so it can set `is_doc_block=True` for `///` and `//!`. Add this logic.

For block comments, `/*!` (inner doc block) joins `/**` as a doc-block-open marker. Add a `doc_block_open_inner` field to `CommentSyntax` and update the state machine to check both.

Alternative simpler approach: keep `CommentSyntax` unchanged, write a custom `extract_rust_comments` that wraps `extract_c_style_comments` and post-processes to flag `///`/`//!`/`/*!` tokens as doc.

**Decision**: alternative approach (post-processing). Smaller surface area, no breaking change to `CommentSyntax`.

## Smoke tests (10)

1. `detect_language(Path("foo.rs"))` -> `"rust"`
2. `parse_content(src, "lib.rs")` finds 1 struct, 1 trait, 1 impl, 2 functions
3. Async fn is correctly tagged `is_async=True`
4. `use crate::foo` -> `is_internal=True`
5. `use tokio::fs` -> `is_internal=False`, classified as `filesystem` external call
6. `pub fn` -> `visibility="public"`, `pub(crate) fn` -> `"protected"`, plain `fn` -> `"private"`
7. `///` and `//!` comments tagged as `is_doc_block=True`
8. Constants `const MAX: u32 = 100;` extracted into `constants[]`
9. `unsafe` block triggers complexity pattern
10. Smoke test on the rust adapter file itself (it's a Python file, but verify it parses cleanly via Python adapter — sanity check that we didn't break anything else)

## Acceptance criteria

- All 10 smoke tests pass
- `analyze_file.py --file foo.rs` works end-to-end
- Existing 6 adapters unchanged (verified by running their smoke tests too)
- `comment_rewriter.py scan` on a directory containing `.rs` files now processes them
- Marketplace metadata.version bumped to 6.19.0, plugin version 1.9.0

## Risk

- Comment lexer post-processing for `///`/`//!` could double-classify if a `///` doc comment is on the same line as code (very rare in Rust style). Post-processing should only re-flag, not re-emit, so this is safe.
- Tree-sitter-rust grammar produces `impl_item` nodes whose name comes from `type_identifier` children, not `name` field. The walker needs grammar-aware extraction; if the grammar version changes, the field names may shift. Regex fallback insulates against this.

## Out of scope (for this commit)

- Test suite (still tracked as P5 tech debt from the v1.8.1 review)
- Cargo workspace awareness (treating `crates/*/src/lib.rs` differently)
- Macro expansion (Rust macros are not parsed beyond their declaration site)
